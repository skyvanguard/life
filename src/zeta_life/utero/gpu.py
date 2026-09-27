"""
El Útero en GPU — motor por lotes (docs/EL_UTERO.md, §38).

`UteroCreciente` es un intérprete en Python puro, celda por celda: exacto y
lento, y ocupa todos los núcleos de la máquina. `UteroGPU` corre TODOS los
mundos de un experimento a la vez como tensores (B mundos × N celdas) en la
GPU, con el VM de `nivel2.execute` vectorizado.

QUÉ CONSERVA (idéntico a CPU, verificado por test contra `execute`):
  el VM (10 ops, registros [vl, v, vr, R3, S1, S2], recorte a ±REG_CLIP,
  MUTO/COPY sobre el código próximo y READ/COPY sobre el actual, el último
  SPAWN gana), la sonda de ceguera, la materia toroidal, la memoria, los
  registros lentos, la energía con luz finita, la difusión conservativa, el
  parto costoso, la invasión de tejido asentado, el germinal (opcode o fila
  entera, con tasa), el congelado, y las perillas heredables θ, s, g.

QUÉ CAMBIA (mano declarada): el ORDEN. El orden asincrónico celda por celda
no se puede paralelizar. Aquí cada tick son dos medios pasos en DAMERO:
primero actúan las celdas de una paridad y después las de la otra (la
paridad que empieza se sortea por mundo y por tick, sembrado). Dentro de un
medio paso ninguna celda activa es vecina de otra activa, así que cada una
ve a sus vecinas en un estado coherente, como en el orden asincrónico. Dos
madres que reclaman el mismo lugar: gana una al azar (sembrado), como gana
la primera en el orden aleatorio de CPU. No es byte-idéntico a CPU: es otra
encarnación, y se valida reproduciendo resultados establecidos (§26, §34)
antes de usarla para preguntas nuevas.

QUÉ NO SOPORTA: crecimiento por los bordes (sólo mundos CERRADOS, n0 = max_n),
materia no toroidal, percepción, perillas escribibles, recombinación, tierra
quemada, sombra, sol_sonda/acople/disolución, muerte por equilibrio, la vara
de novedad de genomas. Todo eso sigue en CPU.
"""

from __future__ import annotations

import math

import numpy as np
import torch

from .nivel2 import ARG_RANGE, N_OPS, PROBE_EPS, REG_CLIP, K

NOP, ADD, SUB, MUL, THR, CONST, READ, MUTO, COPY, SPAWN = range(N_OPS)
PHI = 0.6180339887498949
REFLEJO_TAU = 200.0
M_REG = 6                      # vl, v, vr, R3, S1, S2


def _por_mundo(x, b: int, device, dtype) -> torch.Tensor:
    """Escalar o secuencia de largo B -> tensor (B, 1)."""
    t = torch.as_tensor(x, device=device)
    if t.ndim == 0:
        t = t.expand(b)
    assert t.shape[0] == b, "el parametro por mundo debe tener largo B"
    return t.to(dtype).reshape(b, 1)


def vm(code: torch.Tensor, r: torch.Tensor, code_l: torch.Tensor, code_r: torch.Tensor,
       has_l: torch.Tensor, has_r: torch.Tensor, total: torch.Tensor, frozen: torch.Tensor) -> dict:
    """VM vectorizado. code, code_l, code_r: (B, N, K, 4) int64. r: (V, B, N, M) float64
    (la variante 0 es la ejecución real; las demás son fantasmas para la sonda).
    has_l/has_r: (B, N) bool — la vecina existe y está viva. total/frozen: (B, 1) bool.
    Devuelve r final, own_next, y el SPAWN (has, side, mpos, fila nueva).

    Los registros evolucionan en K pasos secuenciales (no hay otra forma). Las escrituras
    sobre el código próximo se resuelven de una vez: para cada (fila, campo) gana la ÚLTIMA
    instrucción que lo escribe — lo mismo que aplicar MUTO y COPY en orden."""
    nv = r.shape[0]
    m = r.shape[-1]
    dt = r.dtype
    op, a, b, c = code[..., 0], code[..., 1], code[..., 2], code[..., 3]
    pos = b % K
    pos4 = pos.unsqueeze(-1).expand(-1, -1, -1, 4)
    rows_l = code_l.gather(2, pos4)                       # fila b%K de cada origen, por instrucción
    rows_s = code.gather(2, pos4)
    rows_r = code_r.gather(2, pos4)
    src = a % 3
    hl, hr = has_l.unsqueeze(-1), has_r.unsqueeze(-1)
    pres = torch.where(src == 0, hl, torch.where(src == 1, torch.ones_like(hl), hr))
    s4 = src.unsqueeze(-1)
    copyrow = torch.where(s4 == 0, rows_l, torch.where(s4 == 1, rows_s, rows_r))
    read_val = torch.where(pres, copyrow[..., 0], torch.zeros_like(op)).to(dt) / N_OPS
    estatico = torch.where(op == CONST, (a.to(dt) - 8.0) / 4.0, read_val)
    es_est = (op == CONST) | (op == READ)
    es_mul = op == MUL
    es_thr = op == THR
    sgn = torch.where(op == SUB, -1.0, 1.0).to(dt)
    escribe = (op >= ADD) & (op <= READ)
    am = (a % m).unsqueeze(0).unsqueeze(-1).expand(nv, -1, -1, -1, 1)      # (V, B, N, K, 1)
    bm = (b % m).unsqueeze(0).unsqueeze(-1).expand(nv, -1, -1, -1, 1)
    cm = (c % m).unsqueeze(0).unsqueeze(-1).expand(nv, -1, -1, -1, 1)
    idx4 = (b.unsqueeze(-1) + torch.arange(4, device=code.device)) % m     # (B, N, K, 4): b, b+1, b+2, b+3
    fotos = []
    for k in range(K):
        ra = r.gather(-1, am[..., k, :]).squeeze(-1)
        rb = r.gather(-1, bm[..., k, :]).squeeze(-1)
        arit = torch.where(es_mul[..., k], ra * rb, ra + sgn[..., k] * rb).clamp(-REG_CLIP, REG_CLIP)
        res = torch.where(es_est[..., k], estatico[..., k], torch.where(es_thr[..., k], (ra > rb).to(dt), arit))
        fotos.append(r[0].gather(-1, idx4[..., k, :]))   # registros que leería un MUTO/SPAWN en k
        ck = cm[..., k, :]
        r = r.scatter(-1, ck, torch.where(escribe[..., k], res, r.gather(-1, ck).squeeze(-1)).unsqueeze(-1))
    foto = torch.stack(fotos, dim=2)                                       # (B, N, K, 4)
    escala = torch.tensor([N_OPS, ARG_RANGE, ARG_RANGE, ARG_RANGE], device=code.device)
    fila = torch.floor(foto.abs() * escala).long() % escala               # fila que escribiría k
    tot3 = total.unsqueeze(-1)                                             # (B, 1, 1)
    vivo3 = (~frozen).unsqueeze(-1)
    es_muto = (op == MUTO) & vivo3
    es_copy = (op == COPY) & vivo3 & pres
    tgt = torch.where(es_muto, a % K, c % K)
    kidx = torch.arange(K, device=code.device).expand_as(op)
    basura = torch.full_like(tgt, K)

    def ultimo(escritor):
        base = torch.full((*op.shape[:2], K + 1), -1, dtype=torch.long, device=code.device)
        return base.scatter_reduce(-1, torch.where(escritor, tgt, basura), kidx, reduce="amax",
                                   include_self=True)[..., :K]

    u0 = ultimo(es_muto | es_copy)                       # último que escribe el opcode de cada fila
    u1 = ultimo((es_muto & tot3) | es_copy)              # último que escribe los operandos
    campos = []
    for f in range(4):
        u = u0 if f == 0 else u1
        kk = u.clamp_min(0)
        val = torch.where(es_muto.gather(-1, kk), fila[..., f].gather(-1, kk), copyrow[..., f].gather(-1, kk))
        campos.append(torch.where(u >= 0, val, code[..., f]))
    own = torch.stack(campos, dim=-1)
    ksp = torch.where(op == SPAWN, kidx, torch.full_like(kidx, -1)).amax(dim=-1)
    has_spawn = ksp >= 0
    kk = ksp.clamp_min(0).unsqueeze(-1)
    side = (a % 2).gather(-1, kk).squeeze(-1)
    mpos = (c % K).gather(-1, kk).squeeze(-1)
    nuevo = fila.gather(2, kk.unsqueeze(-1).expand(-1, -1, 1, 4)).squeeze(2)
    solo_op = torch.tensor([True, False, False, False], device=code.device)
    nuevo = torch.where(tot3 | solo_op, nuevo, torch.zeros_like(nuevo))
    return dict(r=r, own=own, has_spawn=has_spawn, side=side, mpos=mpos, nuevo=nuevo)


class UteroGPU:
    """B mundos cerrados de N celdas en un dispositivo torch. Ver el docstring del módulo."""

    def __init__(self, seeds, n: int, sol: np.ndarray, *, device: str | None = None,
                 memoria: bool = True, germinal: bool = True, invasion: bool = True,
                 eq_eps: float = 1e-9, eq_window: int = 100,
                 luz_finita: float = 14.0, e0: float = 2.0, e_mant: float = 0.01, e_dif: float = 0.25,
                 e_parto: float = 0.5, e_costo: float = 1.0, lentos: float = 0.02,
                 escritura_total=False, tasa_germinal=1.0, congelado=False,
                 parametros: float = 0.0, escala: bool = False, theta_fijo=False, reflejo: float = 0.0,
                 ultraestable=0, orden_seed: int = 0):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        dt = torch.float64
        self.dt = dt
        seeds = list(seeds)
        b = len(seeds)
        self.b, self.n = b, n
        sol = np.asarray(sol, dtype=np.float64)
        assert sol.shape[0] == b, "sol debe ser (B, T)"
        self.sol = torch.as_tensor(sol, device=self.device, dtype=dt)
        self.memoria, self.germinal, self.invasion = memoria, germinal, invasion
        self.eq_eps, self.eq_window = eq_eps, eq_window
        self.luz_finita, self.e0, self.e_mant = luz_finita, e0, e_mant
        self.e_dif, self.e_parto, self.e_costo, self.lentos = e_dif, e_parto, e_costo, lentos
        self.parametros, self.escala, self.reflejo = parametros, escala, reflejo
        self.total = _por_mundo(escritura_total, b, self.device, torch.bool)
        self.tasa = _por_mundo(tasa_germinal, b, self.device, dt)
        self.frozen = _por_mundo(congelado, b, self.device, torch.bool)
        # ULTRAESTABILIDAD (Ashby 1948; §43): la celda aplica sus auto-reescrituras (MUTO, COPY) sólo
        # cuando le va MAL —su ingreso de luz de este tick no cubre su mantenimiento: déficit
        # metabólico propio— y conserva su regla cuando le va bien. Aprender en vida sin maestro ni
        # datos: las consecuencias vuelven sobre la reescritura. (No se usa la tendencia de la
        # energía: un parto le cuesta energía a la madre y la daría por "mal" cuando le va bien.)
        # Por mundo: 0 = apagado (reescribe siempre, el útero original); 1 = ultraestable;
        # -1 = INVERTIDO (reescribe sólo cuando le va bien: control adversarial).
        self.ultra = _por_mundo(ultraestable, b, self.device, torch.long)
        self._historia = reflejo > 0.0
        self.fijo = _por_mundo(theta_fijo, b, self.device, torch.bool)
        # la sopa: el mismo sorteo que UteroCreciente (v, opcodes, operandos, theta)
        v = np.zeros((b, n))
        code = np.zeros((b, n, K, 4), dtype=np.int64)
        theta = np.zeros((b, n))
        for i, s in enumerate(seeds):
            rng = np.random.default_rng(int(s))
            v[i] = rng.uniform(0.0, 1.0, size=n)
            code[i, :, :, 0] = rng.integers(0, 10, size=(n, K))
            code[i, :, :, 1:] = rng.integers(0, 16, size=(n, K, 3))
            if parametros > 0.0:
                theta[i] = rng.uniform(0.0, 1.0, size=n)
        d = self.device
        self.v = torch.as_tensor(v, device=d, dtype=dt)
        self.code = torch.as_tensor(code, device=d)
        self.theta = torch.as_tensor(theta, device=d, dtype=dt)
        self.alive = torch.ones((b, n), dtype=torch.bool, device=d)
        self.mem = torch.zeros((b, n), dtype=dt, device=d)
        self.e = torch.full((b, n), float(e0), dtype=dt, device=d)
        self.e_lenta = torch.full((b, n), float(e0), dtype=dt, device=d)
        self.S = torch.zeros((b, n, 2), dtype=dt, device=d)
        self.esc = torch.ones((b, n), dtype=dt, device=d)
        self.g = torch.zeros((b, n), dtype=dt, device=d)
        self.eq = torch.zeros((b, n), dtype=torch.long, device=d)
        self.idx = torch.arange(n, device=d).unsqueeze(0).expand(b, -1)
        self.gen = torch.Generator(device=d)
        self.gen.manual_seed(int(orden_seed))
        self.tick = 0

    # ------------------------------------------------------------------ utilidades
    def _vecinas(self, x: torch.Tensor, relleno) -> tuple:
        """Valor de la vecina izquierda y derecha de cada celda (relleno fuera del mundo)."""
        izq = torch.roll(x, 1, dims=1)
        der = torch.roll(x, -1, dims=1)
        if x.ndim == 2:
            izq[:, 0] = relleno
            der[:, -1] = relleno
        else:
            izq[:, 0] = relleno
            der[:, -1] = relleno
        return izq, der

    def _medio_paso(self, activa: torch.Tensor, vac: torch.Tensor, ingreso: torch.Tensor) -> tuple:
        dt = self.dt
        al_l, al_r = self._vecinas(self.alive, False)
        v_l, v_r = self._vecinas(self.v, 0.0)
        vl = torch.where(al_l, v_l, vac)
        vr = torch.where(al_r, v_r, vac)
        code_l, code_r = self._vecinas(self.code, 0)
        mi = self.mem if self.memoria else torch.zeros_like(self.mem)
        cero = torch.zeros_like(self.v)
        h = torch.full_like(self.v, PHI)
        r = torch.stack([
            torch.stack([vl, self.v, vr, mi, self.S[..., 0], self.S[..., 1]], dim=-1),
            torch.stack([cero, cero, cero, mi, self.S[..., 0], self.S[..., 1]], dim=-1),
            torch.stack([h, h, h, mi, self.S[..., 0], self.S[..., 1]], dim=-1)], dim=0)
        mal = ingreso < self.e_mant                       # déficit metabólico propio en este tick
        quieta_regla = self.frozen | ((self.ultra == 1) & ~mal) | ((self.ultra == -1) & mal)     # (B, N)
        o = vm(self.code, r, code_l, code_r, al_l, al_r, self.total, quieta_regla)
        rf = o["r"]
        raw = rf[0, ..., 3]
        out = raw % 1.0
        p1 = rf[1, ..., 3] % 1.0
        p2 = rf[2, ..., 3] % 1.0
        # registros lentos: S <- S + lambda (w - S) sólo si la regla escribió
        if self.lentos > 0.0:
            w = rf[0, ..., 4:6]
            escrito = (w != self.S) & activa.unsqueeze(-1)
            self.S = torch.where(escrito, self.S + self.lentos * (w - self.S), self.S)
        ciega = ((out - p1).abs() < PROBE_EPS) & ((out - p2).abs() < PROBE_EPS) & ((p1 - p2).abs() < PROBE_EPS)
        muere = activa & (ciega | ~torch.isfinite(out))
        viva = activa & ~muere
        # expresión: perillas heredables
        v_new = out
        if self.parametros > 0.0:
            th = self.theta
            if self.reflejo > 0.0:
                th = (th + self.g * torch.tanh((self.e_lenta - self.e) / max(self.e0, 1e-9))) % 1.0
            v_new = (th + self.esc * out) % 1.0 if self.escala else (out + th) % 1.0
        quieta = (v_new - self.v).abs() < self.eq_eps
        self.eq = torch.where(viva, torch.where(quieta, self.eq + 1, torch.zeros_like(self.eq)), self.eq)
        # energía
        e_new = self.e - self.e_mant + ingreso
        hambre = viva & (e_new <= 0.0)
        viva = viva & ~hambre
        muertes = (muere | hambre)
        self.e = torch.where(viva, e_new, self.e)
        if self._historia:
            self.e_lenta = torch.where(viva, self.e_lenta + (self.e - self.e_lenta) / REFLEJO_TAU, self.e_lenta)
        self.v = torch.where(viva, v_new, self.v)
        self.code = torch.where(viva.reshape(*viva.shape, 1, 1), o["own"], self.code)
        self.mem = torch.where(viva, raw, self.mem)
        self._vaciar(muertes, energia=hambre)
        # ---------------------------------------------------------------- partos
        madre = viva & o["has_spawn"]
        if self.e_costo > 0.0:
            madre = madre & (self.e > self.e_costo)
            self.e = torch.where(madre, self.e - self.e_costo, self.e)     # el parto cuesta aunque fracase
        escribe = (self.tasa >= 1.0) | (((raw.abs() * 97.0) % 1.0) < self.tasa)
        ger = madre & escribe & ~self.frozen & self.germinal
        mp4 = o["mpos"].reshape(*madre.shape, 1, 1).expand(-1, -1, 1, 4)
        campo = torch.stack([ger, ger & self.total, ger & self.total, ger & self.total], dim=-1).unsqueeze(2)
        hija = o["own"].scatter(2, mp4, torch.where(campo, o["nuevo"].unsqueeze(2), o["own"].gather(2, mp4)))
        th_h, sc_h, g_h = self.theta, self.esc, self.g
        if self.parametros > 0.0:
            varia = ~self.fijo
            th_h = torch.where(varia, (self.theta + self.parametros * (2.0 * ((raw.abs() * 131.0) % 1.0) - 1.0)) % 1.0,
                               self.theta)
            if self.escala:
                sc_h = torch.where(varia, (self.esc + self.parametros * (2.0 * ((raw.abs() * 173.0) % 1.0) - 1.0)
                                           ).clamp(0.0, 1.0), self.esc)
            if self.reflejo > 0.0:
                g_h = torch.where(varia, (self.g + self.reflejo * (2.0 * ((raw.abs() * 197.0) % 1.0) - 1.0)
                                          ).clamp(-2.0, 2.0), self.g)
        a_der = madre & (o["side"] == 1)
        a_izq = madre & (o["side"] == 0)
        # el lugar j recibe de la madre j-1 (que pare a la derecha) o de la madre j+1 (que pare a la izquierda)
        de_izq = torch.roll(a_der, 1, dims=1)
        de_izq[:, 0] = False
        de_der = torch.roll(a_izq, -1, dims=1)
        de_der[:, -1] = False
        libre = ~self.alive
        invadible = self.alive & (self.eq > self.eq_window) if self.invasion else torch.zeros_like(self.alive)
        apto = libre | invadible
        de_izq, de_der = de_izq & apto, de_der & apto
        ambos = de_izq & de_der
        moneda = torch.rand(ambos.shape, generator=self.gen, device=self.device) < 0.5
        de_izq = de_izq & ~(ambos & ~moneda)
        de_der = de_der & ~(ambos & moneda)
        recibe = de_izq | de_der
        nac = recibe.sum(dim=1)
        src = torch.where(de_izq, self.idx - 1, self.idx + 1).clamp(0, self.n - 1)

        def de_madre(x):
            return x.gather(1, src)

        e_m = de_madre(self.e)
        e_h = self.e_parto * e_m
        codigo_h = hija.gather(1, src.reshape(*src.shape, 1, 1).expand(-1, -1, K, 4))
        self.code = torch.where(recibe.reshape(*recibe.shape, 1, 1), codigo_h, self.code)
        self.v = torch.where(recibe, de_madre(self.v), self.v)
        self.theta = torch.where(recibe, de_madre(th_h), self.theta)
        self.esc = torch.where(recibe, de_madre(sc_h), self.esc)
        self.g = torch.where(recibe, de_madre(g_h), self.g)
        self.alive = self.alive | recibe
        self.eq = torch.where(recibe, torch.zeros_like(self.eq), self.eq)
        self.mem = torch.where(recibe, torch.zeros_like(self.mem), self.mem)
        self.S = torch.where(recibe.unsqueeze(-1), torch.zeros_like(self.S), self.S)
        self.e = torch.where(recibe, e_h, self.e)
        self.e_lenta = torch.where(recibe, e_h, self.e_lenta)
        resta = torch.zeros_like(self.e).scatter_add(1, src, torch.where(recibe, e_h, torch.zeros_like(e_h)))
        self.e = self.e - resta
        return muertes.sum(dim=1), nac

    def _vaciar(self, m: torch.Tensor, energia: torch.Tensor) -> None:
        self.alive = self.alive & ~m
        self.v = torch.where(m, torch.zeros_like(self.v), self.v)
        self.code = torch.where(m.reshape(*m.shape, 1, 1), torch.zeros_like(self.code), self.code)
        self.eq = torch.where(m, torch.zeros_like(self.eq), self.eq)
        self.mem = torch.where(m, torch.zeros_like(self.mem), self.mem)
        self.e = torch.where(energia, torch.zeros_like(self.e), self.e)
        self.S = torch.where(energia.unsqueeze(-1), torch.zeros_like(self.S), self.S)

    def cortar(self, ini: int, fin: int) -> None:
        """Ablación (§44): vacía el tramo [ini, fin) de TODOS los mundos, como un corte a mano en los
        enjambres de Carrillo-Zapata. Las celdas cortadas quedan vacías, sin energía ni memoria."""
        m = torch.zeros_like(self.alive)
        m[:, ini:fin] = True                      # todo el tramo (también los huecos que ya había)
        self._vaciar(m, energia=m)

    # ------------------------------------------------------------------ un tick
    @torch.no_grad()
    def step(self) -> dict:
        t = min(self.tick, self.sol.shape[1] - 1)
        vac = self.sol[:, t].unsqueeze(1)                               # (B, 1)
        self.tick += 1
        viva0 = self.alive.clone()
        d = (self.v - vac).abs()
        w = torch.where(self.alive, torch.minimum(d, 1.0 - d) + 0.05, torch.zeros_like(d))
        tot = w.sum(dim=1, keepdim=True)
        ingreso = torch.where(tot > 0, self.luz_finita * vac * w / tot.clamp_min(1e-300), torch.zeros_like(w))
        primera = torch.randint(0, 2, (self.b, 1), generator=self.gen, device=self.device)
        muertes = torch.zeros(self.b, dtype=torch.long, device=self.device)
        partos = torch.zeros_like(muertes)
        for mitad in (0, 1):
            activa = viva0 & self.alive & (((self.idx + primera + mitad) % 2) == 0)
            mu, na = self._medio_paso(activa, vac, ingreso)
            muertes += mu
            partos += na
        if self.e_dif > 0.0:
            par = self.alive[:, :-1] & self.alive[:, 1:]
            flujo = torch.where(par, self.e_dif * 0.5 * (self.e[:, :-1] - self.e[:, 1:]),
                                torch.zeros_like(self.e[:, 1:]))
            self.e[:, :-1] -= flujo
            self.e[:, 1:] += flujo
        return dict(muertes=muertes, partos=partos, vac=vac.squeeze(1))

    # ------------------------------------------------------------------ puntos de control
    _ESTADO = ("v", "code", "theta", "alive", "mem", "e", "e_lenta", "S", "esc", "g", "eq")

    def estado(self) -> dict:
        """Todo lo necesario para reanudar exactamente: tensores, tick y el estado del sorteo."""
        d = {k: getattr(self, k).cpu() for k in self._ESTADO}
        d["tick"] = self.tick
        d["gen"] = self.gen.get_state().cpu()
        return d

    def restaurar(self, d: dict) -> None:
        for k in self._ESTADO:
            setattr(self, k, d[k].to(self.device))
        self.tick = int(d["tick"])
        self.gen.set_state(d["gen"])

    # ------------------------------------------------------------------ correr con lecturas
    @torch.no_grad()
    def correr(self, ticks: int, banda: float = 0.4, checkpoint: str | None = None, cada: int = 5000) -> dict:
        """Corre `ticks` y devuelve series (T, B) en numpy: vivas, muertes, partos, w (peso de luz
        medio de las vivas), banda (fracción a distancia >= banda del sol), s, g, gpos, R (concentración
        circular de theta).

        checkpoint: ruta de un punto de control. Si existe, la corrida se REANUDA desde él (estado
        exacto + series acumuladas); cada `cada` ticks se reescribe de forma atómica. En una máquina
        compartida un corte cuesta como mucho `cada` ticks. El resultado es idéntico al de una
        corrida sin cortes (test)."""
        nombres = ("vivas", "muertes", "partos", "w", "banda", "s", "g", "gpos", "R")
        ser = {k: torch.full((ticks, self.b), float("nan"), dtype=torch.float32, device=self.device)
               for k in nombres}
        t_ini = 0
        ruta = None
        if checkpoint is not None:
            from pathlib import Path
            ruta = Path(checkpoint)
            if ruta.exists():
                ck = torch.load(ruta, map_location="cpu", weights_only=False)
                assert ck["ticks"] == ticks and ck["b"] == self.b and ck["n"] == self.n, "punto de control de otra corrida"
                self.restaurar(ck["estado"])
                t_ini = int(ck["t"])
                for k in nombres:
                    ser[k][:t_ini] = ck["series"][k].to(self.device)
        for t in range(t_ini, ticks):
            if ruta is not None and t > t_ini and t % cada == 0:
                tmp = ruta.with_suffix(ruta.suffix + ".tmp")
                torch.save(dict(estado=self.estado(), t=t, ticks=ticks, b=self.b, n=self.n,
                                series={k: v[:t].cpu() for k, v in ser.items()}), tmp)
                tmp.replace(ruta)
            r = self.step()
            al = self.alive
            n = al.sum(dim=1).to(self.dt)
            ok = n > 0
            den = n.clamp_min(1.0)
            vac = r["vac"].unsqueeze(1)
            d = (self.v - vac).abs()
            d = torch.minimum(d, 1.0 - d)
            z = torch.zeros_like(d)

            def media(x):
                return torch.where(ok, torch.where(al, x, z).sum(dim=1) / den, torch.full_like(den, float("nan")))

            ser["vivas"][t] = n
            ser["muertes"][t] = r["muertes"]
            ser["partos"][t] = r["partos"]
            ser["w"][t] = media(d) + 0.05
            ser["banda"][t] = media((d >= banda).to(self.dt))
            ser["s"][t] = media(self.esc)
            ser["g"][t] = media(self.g)
            ser["gpos"][t] = media((self.g > 0).to(self.dt))
            ang = 2.0 * math.pi * self.theta
            ser["R"][t] = torch.sqrt(media(torch.cos(ang)) ** 2 + media(torch.sin(ang)) ** 2)
        return {k: v.cpu().numpy() for k, v in ser.items()}

"""
§45 — TEJIDO PLÁSTICO (prototipo): ¿aprende en vida, y generaliza, un tejido
cuya regla es continua y cambia según el propio bienestar de cada celda?
(docs/PLAN_INTELIGENCIA.md §44–§45; ledger 2026-09-27; enmiendas 2026-10-25
en docs/ESTADO_DEL_ARTE_APRENDER_EN_VIDA.md §4.1 y §6)

QUÉ ES Y QUÉ NO. Es un prototipo fuera del útero (numpy, un núcleo), con la
misma ecología cerrada: una línea de N lugares, el vacío lleva la materia del
sol, luz finita L0·sol repartida por distancia de la materia al sol,
mantenimiento, muerte por energía, parto costoso hacia un lugar vacío. Lo que
cambia es la física de la celda: en lugar de un programa discreto de 16
instrucciones, una regla CONTINUA (una red mínima de pesos W), para tener
localidad (§44–§45: un cambio chico de la regla produce un cambio chico de lo
que hace).

LA CELDA. Lee x = [cos, sen de la materia izquierda, propia y derecha (en un
hueco, el sol), dos variables internas h, 1]. Produce:
  u = tanh(W0·x) + σ·ξ   motor: mueve su materia, v ← (v + κ·u) mod 1;
  h ← (1−τh)·h + τh·tanh(W1..2·x)   memoria (τh = 0.1; 0.005 en el brazo h_lento);
  pare si tanh(W3·x) > 0 y su energía supera el costo del parto.

HERENCIA (ENMENDADA 2026-10-25). Cada celda lleva dos juegos de pesos: su
GENOTIPO Wn (los pesos con que nació) y su regla actual Wt (lo que aprendió en
vida encima del genotipo). La cría hereda Wn[madre] + ε·ruido y arranca con
Wt = Wn: LO APRENDIDO MUERE CON LA CELDA (computación mortal; Hinton 2022,
Ororbia y Friston 2023). La versión original (2026-09-27) hacía heredar
Wt[madre]: herencia lamarckiana, que confundía "aprendió en vida" con "heredó
lo aprendido y la persistencia lo acumuló" y contaminaba la vara G. Esa
versión se conserva como brazo declarado (`lamarck`) para medir cuánto de la
señal venía de ahí. La evolución sobre genotipos actúa en TODOS los brazos.

EL APRENDIZAJE EN VIDA (sólo la fila del motor). Perturbación de nodo
(Fiete y Seung 2006; Dalm, van Gerven y Ahmad 2023), que es REINFORCE con
línea base (Williams 1992): la celda explora con ruido ξ en su acción y lleva
una traza de elegibilidad El ← λ·El + ξ·x. Su señal es su propio ingreso de
este tick frente a su propio promedio reciente, m = (r − r̄)/r̄. Actualiza
W0 ← W0 + η·m·El. Sin maestro, sin datos, sin objetivo externo. La regla no es
nueva; lo que se prueba es dónde corre: sin optimizador afuera, con la
persistencia como único juez, en un entorno con orden aprendible.

BRAZOS (misma exploración σ en todos; misma herencia genotípica salvo lamarck):
  plastico         m propio.
  invertido        −m (control adversarial).
  barajado         m de otra celda del mismo mundo al azar (misma cantidad de
                   cambio, sin crédito).
  sin_plasticidad  η = 0 (sólo evolución de genotipos).
  --- agregados 2026-10-25 (lecturas secundarias, pre-registradas abajo) ---
  lamarck          plastico con la herencia original (la cría hereda Wt).
  lesion           plastico hasta la mitad de la corrida; η = 0 desde ahí.
  ultra            ultraestabilidad pura (Ashby 1952; Di Paolo 2000): sin
                   traza ni dirección; cuando m < 0, W0 ← W0 + η·|m|·ζ con
                   ζ ~ N(0,1); cuando m ≥ 0, nada.
  h_lento          η = 0 y τh = 0.005 (≈ 200 ticks, escala de estación): ¿basta
                   un estado interno lento con una regla fija? (cognición basal).

CALIBRACIÓN (declarada; sobre OTRA condición): con el sol constante en 0.3,
se elige η, σ tales que el brazo plástico supere al sin_plasticidad en
cosecha. Es el control positivo de la regla de aprendizaje. RESULTADO de la
calibración ORIGINAL (herencia lamarckiana;
results/utero_tejido_plastico_calibracion_run.txt; 16 mundos por brazo, 20000
ticks): la regla funciona en los SEIS puntos (η ∈ {0.01, 0.05, 0.2} × σ ∈
{0.1, 0.3}): plástico 0.48–0.53 contra sin_plasticidad 0.32–0.33 y barajado
0.30–0.32 (el máximo posible es 0.55: materia en el punto opuesto al sol); el
invertido aprende lo contrario (0.08–0.29). Se fijó η = 0.05, σ = 0.3.
RE-CALIBRACIÓN (2026-10-25, herencia genotípica, mismos seis puntos, los
cuatro brazos originales; results/utero_tejido_plastico_calibracion2_run.txt):
se corre ANTES de la prueba. Regla declarada: si en (0.05, 0.3) el plástico
sigue superando al sin_plasticidad, η y σ no se tocan; si no, se elige el
punto del barrido con mayor cosecha plástica y se declara acá antes de correr.

PRUEBA (estaciones, sol seed 0 cíclico; 16 mundos por brazo; N = 256; L0 = 7;
60000 ticks; lecturas en la segunda mitad; pareado por mundo):
  COSECHA  peso de luz medio de las vivas (distancia de la materia al sol
           + 0.05; 0.30 es el valor de una materia al azar; 0.55 el oráculo).
  REGRET   (0.55 − cosecha)/(0.55 − 0.30): fracción de la mejora posible que
           se pierde (Medvid et al. 2026). 0 = oráculo, 1 = azar.
  DENSIDAD vivas medias (confusor de §30–§31).
  GENERALIZACIÓN G: por cada estación nueva, (cosecha en sus primeros 50
           ticks − 0.30) / (cosecha media de toda la estación − 0.30), sólo
           donde el denominador es > 0.02; mediana por mundo. G ≈ 1: llega a
           la estación nueva sabiendo qué hacer; G ≈ 0: la re-aprende.
VEREDICTO PRIMARIO (escrito antes de correr la prueba; sin cambios):
  APRENDE EN VIDA  si plastico supera a invertido, barajado y
                   sin_plasticidad en cosecha en ≥ 75% de los pares (p signo
                   < 0.05) con vivas ≥ 0.9 × las del control.
  ... Y GENERALIZA si además G ≥ 0.8 en ≥ 75% de los mundos plásticos donde
                   está definido.
  NADA             en otro caso.
LECTURAS SECUNDARIAS (pre-registradas 2026-10-25; informan, no deciden):
  MORTAL      plastico > lesion en cosecha de la 2a mitad en ≥ 75% de los
              pares (p < 0.05): lo aprendido se pierde con el recambio de
              celdas; el aprendizaje en vida tiene que seguir ocurriendo.
              Si no: FIJADO (lo que había quedó en los genotipos o en h).
  HERENCIA    lamarck > plastico en ≥ 75%: la señal de la calibración original
              venía en parte de heredar lo aprendido.
  AZAR BASTA  ultra > sin_plasticidad en ≥ 75%: el gate de Ashby alcanza.
  DIRECCION   plastico > ultra en ≥ 75%: la dirección (traza) agrega algo
              sobre el azar gated.
  ESTADO      h_lento > sin_plasticidad en ≥ 75%: un estado lento con regla
              fija ya rinde.

§45b — ESTACIONES LARGAS (pre-registrado 2026-10-26 00:55, tras leer el sol
seed 0 y ANTES de leer la réplica). El resultado con sol seed 0 fue APRENDE EN
VIDA SIN GENERALIZAR con efecto chico (regret 0.88): dentro de cada estación
el plástico sube de 0.29 a 0.34 en ~600 ticks, y las estaciones duran 357–884.
Con sol constante llega a 0.52 en 20000 ticks. Hipótesis mecánica: el ser
aprende más lento de lo que el mundo cambia. Prueba: el mismo protocolo con
duraciones 10× (dur 3000–9000; 120000 ticks; brazos plastico, invertido,
barajado, sin_plasticidad, ultra; sol seed 0). Lecturas pre-registradas:
  TIEMPO        regret del plástico (2a mitad) < 0.5: con tiempo, el aprendizaje
                en vida recupera más de la mitad de lo posible. Si no: el
                límite no era el tiempo (es la regla o el blanco móvil).
  REACTOR       G sigue < 0.8 en ≥ 75% de los mundos: con tiempo aprende más
                pero sigue re-aprendiendo cada estación (no lleva nada de una a
                la siguiente). Es lo esperado: nada en la celda puede llevarlo.
  ESPECIALISTA  sin_plasticidad: cosecha en A ≥ 1.3× su cosecha en B y C: la
                evolución de genotipos sigue produciendo un especialista de la
                hambruna, y el plástico un generalista chato.
El veredicto primario se aplica igual (misma regla) pero no decide nada nuevo:
§45b informa el mecanismo del §45, no lo reemplaza.

    PYTHONPATH=src python experiments/utero/exp_utero_tejido_plastico.py            # prueba (sol seed 0)
    PYTHONPATH=src python experiments/utero/exp_utero_tejido_plastico.py calibrar   # re-calibración (herencia genotípica)
    PYTHONPATH=src python experiments/utero/exp_utero_tejido_plastico.py replica 1  # réplica con otro sol
    PYTHONPATH=src python experiments/utero/exp_utero_tejido_plastico.py largo      # §45b estaciones 10x
"""

from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

N = 256
W = 16
TICKS = 60000
L0, E0, E_MANT, E_DIF, E_PARTO, E_COSTO = 7.0, 2.0, 0.01, 0.25, 0.5, 1.0
KAPPA, LAMBDA, TAU_R, EPS_W = 0.1, 0.8, 20.0, 0.02
ETA, SIGMA = 0.05, 0.3                  # CALIBRADOS (ver docstring); se fijan antes de la prueba
TASA_H, TASA_H_LENTO = 0.1, 0.005
ORACULO, AZAR = 0.55, 0.30
N_IN, N_OUT = 9, 4
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
MODO = {"plastico": 0, "invertido": 1, "barajado": 2, "sin_plasticidad": 3,
        "lamarck": 4, "lesion": 5, "ultra": 6, "h_lento": 7}
ARMS = tuple(MODO)
ORIGINALES = ARMS[:4]
CONTROLES = ("invertido", "barajado", "sin_plasticidad")
LARGO_ARMS = ("plastico", "invertido", "barajado", "sin_plasticidad", "ultra")
LARGO_TICKS, LARGO_DUR = 120000, (3000, 9000)
TEMPRANO = 50
RESULTS = HERE.parents[1] / "results"
DATA = HERE.parents[1] / "data"
NAME = "utero_tejido_plastico"


def circ(m: np.ndarray) -> tuple:
    a = 2.0 * math.pi * m
    return np.cos(a), np.sin(a)


class Tejido:
    def __init__(self, modos: np.ndarray, rng: np.random.Generator, eta: float, sigma: float,
                 lesion_desde: int | None = None):
        b = len(modos)
        self.rng, self.eta, self.sigma = rng, eta, sigma
        self.modo = modos
        self.lesion_desde = lesion_desde
        self.t = 0
        self.alive = np.ones((b, N), dtype=bool)
        self.v = rng.uniform(0, 1, (b, N))
        self.h = np.zeros((b, N, 2))
        self.Wt = rng.normal(0.0, 0.5, (b, N, N_OUT, N_IN))
        self.Wn = self.Wt.copy()                            # genotipo: los pesos de nacimiento
        self.el = np.zeros((b, N, N_IN))
        self.e = np.full((b, N), E0)
        self.rbar = np.full((b, N), 0.02)

    def _x(self, vac: np.ndarray) -> np.ndarray:
        al = self.alive
        vl = np.where(np.roll(al, 1, axis=1), np.roll(self.v, 1, axis=1), vac)
        vr = np.where(np.roll(al, -1, axis=1), np.roll(self.v, -1, axis=1), vac)
        vl[:, 0] = vac[:, 0]
        vr[:, -1] = vac[:, 0]
        cl, sl = circ(vl)
        cv, sv = circ(self.v)
        cr, sr = circ(vr)
        return np.stack([cl, sl, cv, sv, cr, sr, self.h[..., 0], self.h[..., 1], np.ones_like(cv)], axis=-1)

    def _eta(self) -> np.ndarray:
        eta = np.full(len(self.modo), self.eta)
        apagado = np.isin(self.modo, [MODO["sin_plasticidad"], MODO["ultra"], MODO["h_lento"]])
        if self.lesion_desde is not None and self.t >= self.lesion_desde:
            apagado |= self.modo == MODO["lesion"]
        return np.where(apagado, 0.0, eta)[:, None]

    def paso(self, vac: np.ndarray) -> tuple:
        al = self.alive
        modo = self.modo
        x = self._x(vac)                                                    # (B, N, 9)
        a = np.tanh(np.einsum("bnoi,bni->bno", self.Wt, x))                 # (B, N, 4)
        xi = self.rng.normal(0.0, 1.0, al.shape)
        u = a[..., 0] + self.sigma * xi
        self.v = np.where(al, (self.v + KAPPA * u) % 1.0, self.v)
        tasa_h = np.where(modo == MODO["h_lento"], TASA_H_LENTO, TASA_H)[:, None, None]
        self.h = np.where(al[..., None], (1.0 - tasa_h) * self.h + tasa_h * a[..., 1:3], self.h)
        self.el = np.where(al[..., None], LAMBDA * self.el + xi[..., None] * x, self.el)
        d = np.abs(self.v - vac)
        dd = np.minimum(d, 1.0 - d)
        w = np.where(al, dd + 0.05, 0.0)
        tot = w.sum(axis=1, keepdims=True)
        ing = np.where(tot > 0, L0 * vac * w / np.maximum(tot, 1e-300), 0.0)
        # aprendizaje en vida: señal propia, relativa a su propio promedio
        m = np.where(al, (ing - self.rbar) / np.maximum(self.rbar, 1e-4), 0.0)
        self.rbar = np.where(al, self.rbar + (ing - self.rbar) / TAU_R, self.rbar)
        m = np.clip(m, -5.0, 5.0)
        mb = m.copy()
        for i in np.flatnonzero(modo == MODO["barajado"]):                  # barajado: la señal de otra celda
            idx = np.flatnonzero(al[i])
            if len(idx) > 1:
                mb[i, idx] = m[i, self.rng.permutation(idx)]
        signo = np.where(modo == MODO["invertido"], -1.0, 1.0)[:, None]
        mu = np.where((modo == MODO["barajado"])[:, None], mb, m) * signo
        dW0 = (self._eta() * mu)[..., None] * self.el
        es_ultra = modo == MODO["ultra"]
        if es_ultra.any():                                                  # Ashby: azar gated por el deficit propio
            zeta = self.rng.normal(0.0, 1.0, self.el.shape)
            dU = (self.eta * np.clip(-m, 0.0, 5.0))[..., None] * zeta
            dW0 = np.where(es_ultra[:, None, None], dU, dW0)
        self.Wt[..., 0, :] = np.clip(self.Wt[..., 0, :] + np.where(al[..., None], dW0, 0.0), -5.0, 5.0)
        # energía
        e = self.e - E_MANT + ing
        muere = al & (e <= 0.0)
        al = al & ~muere
        self.e = np.where(al, e, 0.0)
        # partos
        intenta = al & (a[..., 3] > 0.0) & (self.e > E_COSTO)
        self.e = np.where(intenta, self.e - E_COSTO, self.e)
        lado = self.rng.random(al.shape) < 0.5
        partos = np.zeros(al.shape[0])
        lamarck = (modo == MODO["lamarck"])[:, None, None, None]
        for der in (True, False):
            madre = intenta & (lado == der)
            llega = np.zeros_like(al)
            if der:
                llega[:, 1:] = madre[:, :-1]
            else:
                llega[:, :-1] = madre[:, 1:]
            llega &= ~al
            if not llega.any():
                continue
            src = np.roll(np.arange(N), 1 if der else -1)
            eh = E_PARTO * self.e[:, src]
            base = np.where(lamarck, self.Wt[:, src], self.Wn[:, src])     # genotipo (lamarck: lo aprendido)
            nuevoW = base + EPS_W * self.rng.normal(0.0, 1.0, self.Wt.shape)
            self.Wt = np.where(llega[..., None, None], nuevoW, self.Wt)
            self.Wn = np.where(llega[..., None, None], nuevoW, self.Wn)
            self.v = np.where(llega, self.v[:, src], self.v)
            self.h = np.where(llega[..., None], 0.0, self.h)
            self.el = np.where(llega[..., None], 0.0, self.el)
            self.rbar = np.where(llega, self.rbar[:, src], self.rbar)
            self.e = np.where(llega, eh, self.e)
            dona = np.zeros_like(al)
            if der:
                dona[:, :-1] = llega[:, 1:]
            else:
                dona[:, 1:] = llega[:, :-1]
            self.e = np.where(dona, self.e - E_PARTO * self.e, self.e)
            al = al | llega
            partos += llega.sum(axis=1)
        par = al[:, :-1] & al[:, 1:]
        flujo = np.where(par, E_DIF * 0.5 * (self.e[:, :-1] - self.e[:, 1:]), 0.0)
        self.e[:, :-1] -= flujo
        self.e[:, 1:] += flujo
        self.alive = al
        self.t += 1
        n = al.sum(axis=1)
        wm = np.where(n > 0, np.where(al, dd, 0).sum(axis=1) / np.maximum(n, 1), np.nan) + 0.05
        return muere.sum(axis=1), n, wm, partos


def signo_p(k: int, n: int) -> float:
    return float(sum(math.comb(n, j) * 0.5 ** n for j in range(k, n + 1))) if n > 0 else 1.0


def correr(soles: np.ndarray, ticks: int, eta: float, sigma: float, semilla: int, arms: tuple) -> tuple:
    modos = np.repeat(np.array([MODO[a] for a in arms]), W)
    t = Tejido(modos, np.random.default_rng(semilla), eta, sigma, lesion_desde=ticks // 2)
    w_ser = np.zeros((ticks, len(modos)), dtype=np.float32)
    viv = np.zeros((ticks, len(modos)), dtype=np.float32)
    for k in range(ticks):
        _, n, wm, _ = t.paso(soles[:, k:k + 1])
        w_ser[k], viv[k] = wm, n
    return w_ser, viv


def calibrar() -> None:
    ticks = 20000
    arms = ORIGINALES
    soles = np.full((len(arms) * W, ticks), 0.3)
    lines = ["RE-CALIBRACION (herencia genotipica, 2026-10-25) con sol constante 0.3: cosecha media (segunda mitad) por brazo"]
    print(lines[0], flush=True)
    for eta in (0.01, 0.05, 0.2):
        for sigma in (0.1, 0.3):
            w_ser, viv = correr(soles, ticks, eta, sigma, 7, arms)
            m = np.nanmean(w_ser[ticks // 2:], axis=0).reshape(len(arms), W)
            vv = viv[ticks // 2:].mean(axis=0).reshape(len(arms), W)
            s = f"  eta={eta:<5} sigma={sigma:<4} " + "  ".join(f"{a} {np.median(m[i]):.3f}/{np.median(vv[i]):.0f}" for i, a in enumerate(arms))
            print(s, flush=True)
            lines.append(s)
    (RESULTS / f"{NAME}_calibracion2_run.txt").write_text(chr(10).join(lines), encoding="utf-8")


def _pares(out, etiqueta: str, a: np.ndarray, b: np.ndarray, texto: str) -> bool:
    k = int(np.sum(a > b))
    ok = k / W >= 0.75 and signo_p(k, W) < 0.05
    out(f"  {etiqueta:<10} {texto}: {k}/{W} (p {signo_p(k, W):.3f}) -> {'SI' if ok else 'no'}")
    return ok


def figura(sol: Sol, w_ser: np.ndarray, arms: tuple, path: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover
        print(f"(sin figura: {exc})")
        return
    paso = 100
    t = np.arange(0, w_ser.shape[0], paso)
    fig, ax = plt.subplots(figsize=(14, 5))
    colores = {"A": "#f4d7d7", "B": "#d7e8f4", "C": "#e3f4d7"}
    for nombre, ini, fin in sol.estaciones:
        ax.axvspan(ini, fin, color=colores.get(nombre, "#eee"), lw=0)
    for i, a in enumerate(arms):
        med = np.nanmedian(w_ser[::paso, i * W:(i + 1) * W], axis=1)
        ax.plot(t, med, lw=1.2, label=a)
    ax.axhline(AZAR, color="k", ls=":", lw=0.8)
    ax.axhline(ORACULO, color="k", ls="--", lw=0.8)
    ax.axvline(w_ser.shape[0] // 2, color="gray", lw=0.8)
    ax.set_xlabel("tick")
    ax.set_ylabel("cosecha (mediana de 16 mundos)")
    ax.set_title("§45 tejido plastico, herencia genotipica: cosecha por brazo bajo las estaciones (A rosa, B celeste, C verde)")
    ax.legend(ncol=4, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def main(sol_seed: int = 0, largo: bool = False) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    arms = LARGO_ARMS if largo else ARMS
    ticks = LARGO_TICKS if largo else TICKS
    dur = LARGO_DUR if largo else (300, 900)
    sufijo = ("_largo" if largo else "") + ("" if sol_seed == 0 else f"_sol{sol_seed}")
    sol = Sol(seed=sol_seed, ticks=ticks, regimenes=REGS, dur_min=dur[0], dur_max=dur[1])
    soles = np.tile(sol.serie, (len(arms) * W, 1))
    out("=" * 80)
    out("TEJIDO PLASTICO (prototipo fuera del utero): regla continua que cambia en vida segun el propio ingreso de cada celda")
    out("Herencia GENOTIPICA (enmienda 2026-10-25): lo aprendido muere con la celda; brazo lamarck = herencia original")
    if largo:
        out("§45b ESTACIONES LARGAS (10x): ¿le faltaba tiempo al aprendiz? (pre-registrado 2026-10-26)")
    out("=" * 80)
    out(f"N={N}; {W} mundos por brazo; brazos {list(arms)}; eta={ETA}; sigma={SIGMA}; kappa={KAPPA}; {ticks} ticks; sol seed {sol_seed}; "
        f"duraciones {dur}; lesion desde {ticks // 2}; veredicto pre-registrado (docstring)")
    out("")
    t0 = time.time()
    w_ser, viv = correr(soles, ticks, ETA, SIGMA, 2032 + sol_seed, arms)
    out(f"corrida: {(time.time() - t0) / 60:.1f} min")
    DATA.mkdir(exist_ok=True)
    np.savez_compressed(DATA / f"{NAME}{sufijo}_series.npz", w_ser=w_ser, viv=viv, arms=np.array(arms),
                        estaciones=np.array([(n, i, f) for n, i, f in sol.estaciones], dtype=object))
    mitad = ticks // 2
    res = {}
    for i, a in enumerate(arms):
        sl = slice(i * W, (i + 1) * W)
        G = []
        for j in range(sl.start, sl.stop):
            gs = []
            for nombre, ini, fin in sol.estaciones:
                if ini < mitad or fin > ticks or fin - ini < 2 * TEMPRANO:
                    continue
                den = float(np.nanmean(w_ser[ini:fin, j])) - AZAR
                if den > 0.02:
                    gs.append((float(np.nanmean(w_ser[ini:ini + TEMPRANO, j])) - AZAR) / den)
            G.append(float(np.median(gs)) if gs else np.nan)
        res[a] = dict(w=np.nanmean(w_ser[mitad:, sl], axis=0), vivas=viv[mitad:, sl].mean(axis=0),
                      w1=np.nanmean(w_ser[:mitad, sl], axis=0), G=np.array(G))
    out("-" * 80)
    out("ESTADO por brazo (medianas)")
    out(f"  {'brazo':<16} {'vivas':>6} {'cosecha 1a mitad':>16} {'cosecha 2a mitad':>16} {'regret':>7} {'G (generaliza)':>15} {'mundos con G':>12}")
    for a, r in res.items():
        w2 = float(np.nanmedian(r["w"]))
        regret = (ORACULO - w2) / (ORACULO - AZAR)
        out(f"  {a:<16} {np.median(r['vivas']):>6.0f} {np.nanmedian(r['w1']):>16.3f} {w2:>16.3f} {regret:>7.2f} "
            f"{np.nanmedian(r['G']) if np.any(~np.isnan(r['G'])) else float('nan'):>15.2f} {int(np.sum(~np.isnan(r['G']))):>12}")
    out("")
    out("-" * 80)
    out("PRIMARIO: PLASTICO contra cada control (cosecha 2a mitad, pareado por mundo)")
    supera = {}
    for c in CONTROLES:
        u, x = res["plastico"], res[c]
        k = int(np.sum(u["w"] > x["w"]))
        dens = float(np.median(u["vivas"]) / max(np.median(x["vivas"]), 1e-9))
        supera[c] = k / W >= 0.75 and signo_p(k, W) < 0.05 and dens >= 0.9
        out(f"  vs {c:<16} cosecha mayor en {k}/{W} (p {signo_p(k, W):.3f}); vivas {dens:.2f} -> {'SUPERA' if supera[c] else 'no'}")
    g = res["plastico"]["G"]
    g = g[~np.isnan(g)]
    kg = int(np.sum(g >= 0.8))
    generaliza = len(g) >= 4 and kg / len(g) >= 0.75
    out(f"  generalizacion: G >= 0.8 en {kg}/{len(g)} mundos plasticos donde esta definido -> {'si' if generaliza else 'no'}")
    out("")
    out("-" * 80)
    out("POR ESTACION (cosecha media por tipo de estacion, 2a mitad)")
    por_est = {}
    for a in arms:
        j = arms.index(a)
        sl = slice(j * W, (j + 1) * W)
        por_est[a] = {nm: float(np.mean([np.nanmean(w_ser[i:f, sl]) for n_, i, f in sol.estaciones if n_ == nm and i >= mitad] or [np.nan]))
                      for nm in "ABC"}
        out(f"  {a:<16} " + "  ".join(f"{nm} {por_est[a][nm]:.3f}" for nm in "ABC"))
    out("")
    out("-" * 80)
    if largo:
        out("LECTURAS §45b (pre-registradas 2026-10-26; informan el mecanismo)")
        regret_p = (ORACULO - float(np.nanmedian(res["plastico"]["w"]))) / (ORACULO - AZAR)
        out(f"  TIEMPO        regret plastico {regret_p:.2f} -> {'SI, le faltaba tiempo' if regret_p < 0.5 else 'no: el limite no era el tiempo'}")
        kr = int(np.sum(g < 0.8))
        out(f"  REACTOR       G < 0.8 en {kr}/{len(g)} mundos plasticos -> {'SI, re-aprende cada estacion' if len(g) and kr / len(g) >= 0.75 else 'no'}")
        fz = por_est["sin_plasticidad"]
        esp = fz["A"] >= 1.3 * max(fz["B"], fz["C"])
        out(f"  ESPECIALISTA  sin_plasticidad A/B {fz['A'] / fz['B']:.2f}, A/C {fz['A'] / fz['C']:.2f} -> {'SI' if esp else 'no'}")
        _pares(out, "AZAR BASTA", res["ultra"]["w"], res["sin_plasticidad"]["w"], "ultra > sin_plasticidad")
        _pares(out, "DIRECCION", res["plastico"]["w"], res["ultra"]["w"], "plastico > ultra")
    else:
        out("SECUNDARIAS (pre-registradas 2026-10-25; informan, no deciden)")
        mortal = _pares(out, "MORTAL", res["plastico"]["w"], res["lesion"]["w"], "plastico > lesion (2a mitad)")
        caida = float(np.nanmedian(res["lesion"]["w1"])) - float(np.nanmedian(res["lesion"]["w"]))
        out(f"             lesion: cosecha 1a mitad {np.nanmedian(res['lesion']['w1']):.3f} -> 2a mitad {np.nanmedian(res['lesion']['w']):.3f} (caida {caida:+.3f}); "
            f"{'MORTAL: lo aprendido se pierde con el recambio' if mortal else 'FIJADO: lo que habia quedo en genotipos o en h'}")
        _pares(out, "HERENCIA", res["lamarck"]["w"], res["plastico"]["w"], "lamarck > plastico")
        _pares(out, "AZAR BASTA", res["ultra"]["w"], res["sin_plasticidad"]["w"], "ultra > sin_plasticidad")
        _pares(out, "DIRECCION", res["plastico"]["w"], res["ultra"]["w"], "plastico > ultra")
        _pares(out, "ESTADO", res["h_lento"]["w"], res["sin_plasticidad"]["w"], "h_lento > sin_plasticidad")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if all(supera.values()) and generaliza:
        out("=> APRENDE EN VIDA Y GENERALIZA: llega a cada estacion nueva sabiendo que hacer. Replicar con otro sol antes de creerlo.")
    elif all(supera.values()):
        out("=> APRENDE EN VIDA (sin generalizar): mejora con su propia experiencia, pero re-aprende cada estacion.")
    else:
        out("=> NADA: la regla plastica no supera a sus controles.")
    (RESULTS / f"{NAME}{sufijo}_run.txt").write_text(chr(10).join(lines), encoding="utf-8")
    figura(sol, w_ser, arms, RESULTS / f"{NAME}{sufijo}.png")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "calibrar":
        calibrar()
    elif len(sys.argv) > 2 and sys.argv[1] == "replica":
        main(int(sys.argv[2]))
    elif len(sys.argv) > 1 and sys.argv[1] == "largo":
        main(0, largo=True)
    else:
        main()

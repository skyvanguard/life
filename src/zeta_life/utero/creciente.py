"""
El Útero creciente — v1: asincronía + espacio que se abre desde adentro.

El Nivel 2 síncrono en anillo fijo cayó en ciclos límite (20/20): determinismo
+ espacio fijo + sincronía ⇒ recurrencia. Esta encarnación ataca la jaula con
las dos direcciones que el boceto dejó abiertas (docs/EL_UTERO.md):

1. **Asincronía**: una celda actúa por vez, en orden aleatorio sembrado, y sus
   efectos (materia, código, colonización) se aplican DE INMEDIATO. El orden
   es azar sin dirección: perturba, no elige.

2. **Espacio creciente**: el mundo es una LÍNEA con dos fronteras, no un
   anillo. Cuando una física en el borde hace SPAWN hacia el más-allá, el
   mundo CRECE una celda y su código la habita. No hay regla nuestra de
   crecimiento: el espacio se abre sólo donde la física lo abre — el sistema
   genera su propia variable adyacente (la elección de Fran), al menos en lo
   espacial. El vacío interior sigue siendo colonizable por SPAWN.

El lenguaje de reglas es el mismo del Nivel 2 (10 ops totales, MUTO/COPY
reescriben la propia forma). Sin ruido inyectado sobre el código.

La vara de la novedad (anti-ilusión): con orden aleatorio, "no ciclar" ya no
prueba nada. El criterio honesto es acuñar GENOMAS NUNCA VISTOS: código nuevo
sólo puede nacer de eventos de escritura (MUTO/COPY), no del azar del orden.
Medimos genomas nuevos por tramo — ¿la novedad se sostiene o se seca?

Manos visibles:
  - el orden aleatorio sembrado (perturbación sin dirección)
  - max_n (la pared de la placa de Petri — límite físico, no meta)
  - la sonda de muerte ciega-a-la-materia (heredada del Nivel 2)
  - el vacío / el más-allá aportan v=0 y lectura nula (frío)
"""

from __future__ import annotations

import math

import numpy as np

from zeta_life.utero.nivel2 import PROBE_EPS, F, K, _output_only, execute, huella

N0 = 16
MAX_N = 256

# Umbrales de OBSERVACIÓN (sólo describen el veredicto)
THERMAL_ALIVE_FRAC = 0.05
FROZEN_VALUE_EPS = 1e-7


class UteroCreciente:
    """Línea 1-D asincrónica que crece donde su física la abre."""

    def __init__(self, n0: int = N0, seed: int = 0, max_n: int = MAX_N,
                 germinal: bool = False, toroidal: bool = False,
                 muerte_equilibrio: bool = False, eq_eps: float = 1e-9,
                 eq_window: int = 100, memoria: bool = False,
                 log_events: bool = False, shadow_deaths=None,
                 invasion: str | None = None, recombina: bool = False,
                 sol=None, sol_sonda: bool = False, sol_acople: float = 0.0):
        """germinal=True (v2): SPAWN no copia exacto — la cría nace con UNA
        instrucción reescrita desde la materia del momento del parto (campos
        b,c del SPAWN + registro; la misma función de MUTO). La variación sale
        del estado del mundo, no de un RNG nuestro. False = v1 (copia exacta),
        byte-idéntica a los resultados commiteados.

        toroidal=True (v3): la materia vive en un círculo — v' = R3 mod 1 en
        vez de sigmoid. El wrap permite mapas expansivos (caos expresable de
        verdad), atacando la causa raíz de v2: la materia congelada. La sonda
        de muerte usa separación irracional (0 y 0.618…) porque 0 y 1 son el
        MISMO punto del toro (con la sonda vieja, todo mapa lineal colapsaría
        y mataría física sana).

        muerte_equilibrio=True (v4): extensión del principio 3 — «cristal =
        muerto de pie». Una celda cuya materia queda quieta (|Δv| < eq_eps)
        durante eq_window ticks seguidos se vuelve VACÍO. Lo que deja de
        devenir, deja de ser (Schrödinger: lejos del equilibrio o muerto).
        No es meta ni recompensa: completa el filtro de persistencia, que ya
        mataba a la física ciega a la materia, matando también a la materia
        quieta. Manos declaradas: eq_eps, eq_window.

        memoria=True (v5): la DIMENSIÓN que Fran no había tocado. Cada celda
        retiene su R3 crudo (el potencial interno, antes de envolver — NO la
        materia observable v, que es su proyección con pérdida) y lo re-inyecta
        como R3 inicial el tick siguiente. Recurrencia / integración temporal:
        estado oculto tipo potencial de membrana. Da dinámica de 2º orden, que
        ensancha el borde-del-caos. La cría nace SIN recuerdos (mem=0). Sin
        manos nuevas.

        log_events=True: OBSERVACIÓN pura (byte-idéntico). Tras cada step(),
        `self.events` = {coord: stats de execute()} para cada celda que actuó
        y `self.spawns` = [(coord_madre, coord_cría)] de ese tick (interior y
        borde). Coordenadas estables (índice − left_grown).

        shadow_deaths: la CORRIDA SOMBRA (Bedau & Packard): lista con el número
        de muertes por tick de una corrida real; en vez de la sonda (selección
        por persistencia de la ley) mueren ESE número de celdas al azar por
        tick (RNG propio, sembrado aparte: el orden de actuación queda igual).
        Todo lo demás idéntico. Mide qué novedad produce la deriva sola.

        invasion (v6): el vacío deja de ser la única tierra colonizable.
        "asentada": un SPAWN dirigido a una celda VIVA cuya materia lleva
        eq_window ticks quieta (|Δv| < eq_eps) la REEMPLAZA (código de la
        cría, materia de la madre, sin memoria) en vez de no hacer nada. Lo
        que deja de devenir puede ser reescrito — reemplazo, no muerte (v4
        mató las llanuras y dejó un desierto; aquí siguen siendo sustrato).
        Es interacción regla↔regla con efecto neto en tejido asentado, la
        pieza que la medición de interacción mostró ausente. "siempre":
        cualquier vecino vivo es reemplazable (sin umbral; control). None =
        byte-idéntico a v5. Manos declaradas: eq_eps, eq_window (las de v4).

        recombina=True (v7): RECOMBINACIÓN al nacer. La mortalidad infantil
        mostró que la mutación germinal (v2) es un mapa determinista del
        estado quieto de la madre y cae siempre en la misma cría, que es
        letal: las llanuras son estériles en estado estacionario. Con
        recombina, la cría toma además UNA instrucción del OTRO progenitor —
        el vecino de la madre del lado opuesto al parto— en el locus b%K del
        SPAWN, si ese vecino vive y su genoma difiere del de la madre. Dos
        progenitores, cero RNG: la variación sale del contacto entre reglas
        distintas (la respuesta de Evoloop/Sexyloop al mismo problema). En
        una llanura clonal no cambia nada; en los bordes entre dominios, sí.
        False = byte-idéntico.

        sol (plan de inteligencia): un ENTORNO. Si se pasa un `Sol` (callable
        t -> materia en [0,1)), la materia del VACÍO —interior y más allá, que
        hasta aquí vale 0 (frío)— sigue `sol(t)`: el sol ilumina todo lo que no
        es tejido y el tejido se da sombra a sí mismo. El tejido no puede leer
        código del sol ni saber cuándo cambia: sólo siente la materia donde
        linda con el vacío. None = byte-idéntico (vacío = 0).

        sol_sonda=True: el clima CUENTA para la persistencia. La sonda de
        ceguera deja de comparar contra referencias fijas (0 y h=0.618…) y
        compara contra la materia ACTUAL del vacío, v0=sol(t), y v0+h (mod 1):
        una física que no distingue estar inmersa en el mundo de hoy de estar
        inmersa en otro es ciega. Sigue siendo el principio 3 (nada de meta ni
        recompensa) con una referencia menos arbitraria que la razón áurea; la
        consecuencia es que cada estación mata físicas distintas, y persistir a
        través de las estaciones exige regularse (Ashby). Sin sol, v0=0 y la
        sonda es la de siempre: byte-idéntico.

        sol_acople=κ (0 = apagado): el sol CALIENTA la superficie. Una celda
        que linda con el vacío recibe materia del sol tras aplicar su regla:
        v ← (1−κ)·v' + κ·sol(t). Acople físico, no lectura opcional: la
        superficie sigue al clima quiera o no, y el interior sólo a través de
        las reglas. Mano declarada: κ. Sin sol o κ=0: byte-idéntico."""
        self.sol_acople = float(sol_acople)
        self.sol_sonda = sol_sonda
        self.sol = sol
        self.recombina = recombina
        if invasion not in (None, "asentada", "siempre"):
            raise ValueError("invasion debe ser None, 'asentada' o 'siempre'")
        self.invasion = invasion
        self.log_events = log_events
        self.shadow = None if shadow_deaths is None else list(shadow_deaths)
        self._shadow_rng = np.random.default_rng(seed + 7919)
        self._tick = 0
        self.events: dict = {}
        self.spawns: list = []
        self.germinal = germinal
        self.toroidal = toroidal
        self.muerte_eq = muerte_equilibrio
        self.eq_eps = eq_eps
        self.eq_window = eq_window
        self.eq_count = np.zeros(n0, dtype=np.int64)
        self.memoria = memoria
        self.mem = np.zeros(n0, dtype=np.float64)     # R3 crudo persistente
        # materias de prueba de la sonda ciega-a-la-materia (mano declarada)
        self._probe_hi = 0.6180339887498949 if toroidal else 1.0
        self.max_n = max_n
        self.rng = np.random.default_rng(seed)
        self.v = self.rng.uniform(0.0, 1.0, size=n0)
        self.code = np.zeros((n0, K, F), dtype=np.int64)
        self.code[:, :, 0] = self.rng.integers(0, 10, size=(n0, K))
        self.code[:, :, 1:] = self.rng.integers(0, 16, size=(n0, K, F - 1))
        self.alive = np.ones(n0, dtype=bool)
        self.left_grown = 0                # celdas añadidas por la izquierda
        self.seen: set = set()             # genomas vistos (para la novedad)
        self._register_genomes()

    @property
    def n(self) -> int:
        return len(self.v)

    def genomas(self) -> dict:
        """{coord: huella del genoma} de las celdas vivas (coord = índice − left_grown)."""
        return {int(i) - self.left_grown: huella(self.code[i]) for i in np.flatnonzero(self.alive)}

    def superficie(self) -> tuple:
        """(materia de las celdas vivas, máscara 'linda con vacío') alineadas."""
        idx = np.flatnonzero(self.alive)
        left = np.zeros(len(idx), dtype=bool)
        right = np.zeros(len(idx), dtype=bool)
        left[idx > 0] = self.alive[idx[idx > 0] - 1]
        right[idx < self.n - 1] = self.alive[idx[idx < self.n - 1] + 1]
        return self.v[idx], ~(left & right)

    def vaciar(self, coord: int) -> None:
        """Volver VACÍO la celda de esa coordenada (para ablaciones externas)."""
        i = int(coord) + self.left_grown
        if 0 <= i < self.n and self.alive[i]:
            self.alive[i] = False
            self.v[i] = 0.0
            self.code[i] = 0
            self.eq_count[i] = 0
            self.mem[i] = 0.0

    def _register_genomes(self) -> int:
        new = 0
        for i in np.flatnonzero(self.alive):
            g = huella(self.code[i])
            if g not in self.seen:
                self.seen.add(g)
                new += 1
        return new

    def _vacio(self) -> float:
        """Materia del VACÍO (interior y más allá): 0 (frío) o el sol. El sol
        ilumina todo lo que no es tejido; el tejido se da sombra a sí mismo. En
        1-D el borde son dos celdas: sin esto el entorno casi no tendría
        superficie de contacto (verificado: con sol sólo en los dos extremos la
        materia de la seed 13 no cambia en 600 ticks)."""
        return 0.0 if self.sol is None else float(self.sol(self._tick - 1))

    def _ctx(self, i: int) -> tuple:
        n = self.n
        cl = self.code[i - 1] if i > 0 and self.alive[i - 1] else None
        cr = self.code[i + 1] if i < n - 1 and self.alive[i + 1] else None
        vl = float(self.v[i - 1]) if i > 0 and self.alive[i - 1] else self._vacio()
        vr = float(self.v[i + 1]) if i < n - 1 and self.alive[i + 1] else self._vacio()
        return (cl, self.code[i], cr), vl, vr

    def step(self) -> dict:
        """Un tick asincrónico: cada celda viva (orden aleatorio) actúa sobre
        el mundo ACTUAL. El borde crece si una física escribe en el más-allá."""
        n0_tick = self.n
        prev_v = self.v.copy()
        prev_code = self.code.copy()
        prev_alive = self.alive.copy()

        edge_left = None   # (code_copy, v, coord_madre) — primer reclamo gana
        edge_right = None
        colonized = 0
        deaths = 0
        invaded = 0
        lg = self.left_grown             # constante dentro del bucle
        self.events = {}
        self.spawns = []
        doomed: set = set()
        if self.shadow is not None:      # sombra: muertes al azar, sin sonda
            d = self.shadow[self._tick] if self._tick < len(self.shadow) else 0
            alive_idx = np.flatnonzero(self.alive)
            if d > 0 and len(alive_idx) > 0:
                doomed = set(int(k) for k in self._shadow_rng.choice(
                    alive_idx, size=min(int(d), len(alive_idx)), replace=False))
        self._tick += 1

        for i in self.rng.permutation(np.flatnonzero(self.alive)):
            i = int(i)
            if not self.alive[i]:          # murió antes de su turno
                continue
            if i in doomed:
                self.alive[i] = False
                self.v[i] = 0.0
                self.code[i] = 0
                self.eq_count[i] = 0
                self.mem[i] = 0.0
                deaths += 1
                continue
            ctx, vl, vr = self._ctx(i)
            mi = float(self.mem[i]) if self.memoria else 0.0
            stats: dict | None = {} if self.log_events else None
            v_new, own_next, spawn, raw = execute(
                self.code[i], vl, float(self.v[i]), vr, ctx,
                wrap=self.toroidal, r3_init=mi, stats=stats)
            if stats is not None:
                self.events[i - lg] = stats
            # persistencia: la física ciega a la materia muere (sonda, misma
            # memoria fija -> prueba de sensibilidad a la MATERIA sola)
            if self.shadow is None:
                v0 = self._vacio() if self.sol_sonda else 0.0
                h = (v0 + self._probe_hi) % 1.0 if (self.sol_sonda and self.toroidal)                     else self._probe_hi
                p1 = _output_only(self.code[i], v0, v0, v0, ctx,
                                  wrap=self.toroidal, r3_init=mi)
                p2 = _output_only(self.code[i], h, h, h, ctx,
                                  wrap=self.toroidal, r3_init=mi)
                blind = (abs(v_new - p1) < PROBE_EPS
                         and abs(v_new - p2) < PROBE_EPS
                         and abs(p1 - p2) < PROBE_EPS)
            else:
                blind = False
            if not math.isfinite(v_new) or blind:
                self.alive[i] = False
                self.v[i] = 0.0
                self.code[i] = 0
                self.eq_count[i] = 0
                self.mem[i] = 0.0
                deaths += 1
                continue
            # v4: muerte por equilibrio — lo que deja de devenir, deja de ser
            # (v6 usa el mismo contador de quietud para decidir qué es invadible)
            if self.muerte_eq or self.invasion is not None:
                if abs(v_new - float(self.v[i])) < self.eq_eps:
                    self.eq_count[i] += 1
                else:
                    self.eq_count[i] = 0
                if self.muerte_eq and self.eq_count[i] > self.eq_window:
                    self.alive[i] = False
                    self.v[i] = 0.0
                    self.code[i] = 0
                    self.eq_count[i] = 0
                    self.mem[i] = 0.0
                    continue
            # async: efectos inmediatos
            if self.sol is not None and self.sol_acople > 0.0:
                borde = ((i == 0 or not self.alive[i - 1])
                         or (i == self.n - 1 or not self.alive[i + 1]))
                if borde:
                    v_new = (1.0 - self.sol_acople) * v_new + self.sol_acople * self._vacio()
            self.v[i] = v_new
            self.code[i] = own_next
            self.mem[i] = raw            # memoria: R3 crudo persistente
            if spawn is None:
                continue
            side, mpos, mop, locus = spawn
            child = own_next.copy()
            if self.germinal:               # v2: nace con UNA instrucción
                child[mpos, 0] = mop        # reescrita desde la materia
            if self.recombina:              # v7: una instrucción del otro progenitor
                o = i + 1 if side == 0 else i - 1
                if 0 <= o < self.n and self.alive[o] and not np.array_equal(
                        self.code[o], self.code[i]):
                    child[locus] = self.code[o][locus]
            t = i - 1 if side == 0 else i + 1
            if t < 0:                       # escribe en el más-allá izquierdo
                if edge_left is None:
                    edge_left = (child, v_new, i - lg)
            elif t >= self.n:               # más-allá derecho
                if edge_right is None:
                    edge_right = (child, v_new, i - lg)
            elif not self.alive[t]:         # vacío interior: colonización
                self.code[t] = child
                self.v[t] = v_new
                self.alive[t] = True
                self.eq_count[t] = 0
                self.mem[t] = 0.0           # la cría nace sin recuerdos
                colonized += 1
                self.spawns.append((i - lg, t - lg))
            elif self.invasion is not None and (
                    self.invasion == "siempre" or self.eq_count[t] > self.eq_window):
                self.code[t] = child        # v6: invasión de tejido asentado
                self.v[t] = v_new
                self.eq_count[t] = 0
                self.mem[t] = 0.0
                invaded += 1
                self.spawns.append((i - lg, t - lg))

        # crecimiento del mundo (fin de tick; tope = la placa de Petri)
        grown = 0
        grew_left = False
        if edge_right is not None and self.n < self.max_n:
            c, val, madre = edge_right
            self.spawns.append((madre, self.n - lg))
            self.v = np.concatenate([self.v, [val]])
            self.code = np.concatenate([self.code, c[None]])
            self.alive = np.concatenate([self.alive, [True]])
            self.eq_count = np.concatenate([self.eq_count, [0]])
            self.mem = np.concatenate([self.mem, [0.0]])
            grown += 1
        if edge_left is not None and self.n < self.max_n:
            c, val, madre = edge_left
            self.spawns.append((madre, -(lg + 1)))
            self.v = np.concatenate([[val], self.v])
            self.code = np.concatenate([c[None], self.code])
            self.alive = np.concatenate([[True], self.alive])
            self.eq_count = np.concatenate([[0], self.eq_count])
            self.mem = np.concatenate([[0.0], self.mem])
            self.left_grown += 1
            grown += 1
            grew_left = True

        # métricas descriptivas (observar, no premiar) — comparar las celdas
        # que existían al inicio del tick (índices corridos si creció a la izq)
        shift = 1 if grew_left else 0
        cur_v = self.v[shift:shift + n0_tick]
        cur_code = self.code[shift:shift + n0_tick]
        cur_alive = self.alive[shift:shift + n0_tick]
        both = prev_alive & cur_alive
        code_change = (float((cur_code[both] != prev_code[both]).mean())
                       if both.any() else 0.0)
        value_change = (float(np.abs(cur_v[both] - prev_v[both]).mean())
                        if both.any() else 0.0)
        new_genomes = self._register_genomes()
        n_alive = int(self.alive.sum())
        return {
            "alive_frac": float(self.alive.mean()),
            "n_world": self.n,
            "code_change": code_change,
            "value_change": value_change,
            "colonized": colonized,
            "grown": grown,
            "deaths": deaths,
            "invaded": invaded,
            "new_genomes": new_genomes,
            "diversity": (len({self.code[i].tobytes()
                               for i in np.flatnonzero(self.alive)})
                          if n_alive else 0),
        }


def run_history(n0: int = N0, seed: int = 0, ticks: int = 2000,
                max_n: int = MAX_N, germinal: bool = False,
                toroidal: bool = False,
                muerte_equilibrio: bool = False, memoria: bool = False) -> dict:
    """Correr un útero creciente registrando historia + frames alineados."""
    u = UteroCreciente(n0=n0, seed=seed, max_n=max_n, germinal=germinal,
                       toroidal=toroidal, muerte_equilibrio=muerte_equilibrio,
                       memoria=memoria)
    keys = ("alive_frac", "n_world", "code_change", "value_change",
            "colonized", "grown", "new_genomes", "diversity")
    hist: dict = {k: [] for k in keys}
    raw = [(np.where(u.alive, u.v, np.nan).copy(), u.left_grown)]
    for _ in range(ticks):
        m = u.step()
        for k in keys:
            hist[k].append(m[k])
        raw.append((np.where(u.alive, u.v, np.nan).copy(), u.left_grown))
    # alinear frames por coordenada (el mundo crece hacia ambos lados)
    lf = u.left_grown
    frames = np.full((len(raw), u.n), np.nan)
    for t, (vals, l_t) in enumerate(raw):
        start = lf - l_t
        frames[t, start:start + len(vals)] = vals
    hist["frames"] = frames
    hist["total_genomes"] = len(u.seen)
    return hist


def verdict(hist: dict, window: int = 100) -> str:
    """'termica' | 'cristal' | 'pulso' (sólo describe la ventana final)."""
    af = np.array(hist["alive_frac"][-window:])
    cc = np.array(hist["code_change"][-window:])
    vc = np.array(hist["value_change"][-window:])
    if af.mean() < THERMAL_ALIVE_FRAC:
        return "termica"
    if cc.max() == 0.0 and vc.max() < FROZEN_VALUE_EPS:
        return "cristal"
    return "pulso"

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
                 sol=None, sol_sonda: bool = False, sol_acople: float = 0.0,
                 sol_eq_eps: float = 0.0, sol_eq_window: int = 20,
                 energia: bool = False, e0: float = 1.0, e_mant: float = 0.01,
                 e_gan: float = 0.2, e_dif: float = 0.25, e_parto: float = 0.5,
                 percepcion: bool = False, energia_luz: bool = False,
                 luz_finita: float = 0.0, lentos: float = 0.0, e_costo: float = 0.0,
                 refractario: int = 0, escritura_total: bool = False,
                 congelado: bool = False, orden_seed: int | None = None,
                 tasa_germinal: float = 1.0, parametros: float = 0.0,
                 theta_fijo: bool = False, escala: bool = False,
                 perillas: bool = False):
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
        las reglas. Mano declarada: κ. Sin sol o κ=0: byte-idéntico.

        sol_eq_eps=ε, sol_eq_window=W (0 = apagado): LO QUE SE VUELVE IGUAL AL
        VACÍO ES VACÍO. Una celda cuya materia coincide con la del entorno
        (distancia en el toro < ε) durante más de W ticks seguidos deja de ser
        distinguible del vacío y se vacía. Es la variable esencial que el clima
        amenaza (Ashby): con el sol que calienta empujando la superficie hacia
        sol(t), sólo persisten en la superficie las físicas que empujan de
        vuelta, y como sol(t) cambia por estación, lo que es seguro cambia con
        él. v4 mató la materia QUIETA (absoluto) y dejó un desierto; esto mata
        la materia DISUELTA en el entorno (relativo). Manos: ε, W.

        energia=True (v9, METABOLISMO): persistir CUESTA. Cada celda lleva una
        energía e (nace con e0). Por tick paga mantenimiento e_mant; si linda
        con el vacío cosecha e_gan·|v − vacío| (la distancia en el toro entre su
        materia y la del entorno: sólo el DESEQUILIBRIO con el mundo alimenta;
        con sol, el gradiente cambia por estación); la energía se difunde
        entre vecinas vivas (intercambio simétrico con coeficiente e_dif,
        conservativo); al parir, la madre cede e_parto de su energía a la
        cría. e ≤ 0 → vacío. Es la conservación de Flow-Lenia/Kruszewski y el
        decaimiento de Stringmol: la única presión que la literatura muestra
        sostenida sin juez. Seis entornos sin costo dieron tejidos maduros
        inertes a su mundo. Manos declaradas: e0, e_mant, e_gan, e_dif,
        e_parto — se calibran por vivas, nunca por las varas de inteligencia.
        energia=False: byte-idéntico.

        percepcion=True (v10, la tercera dimensión del boceto: PERCEPCIÓN del
        propio estado): la energía de la celda entra a su física como un 5º
        registro de sólo lectura (los campos indexan mod 5). Es la única
        variable interna LENTA del sustrato (τ≈e0/e_mant) — la memoria se
        reescribe cada tick y las estaciones duran 300–900 ticks (medido: τ de
        la materia interior 6–150 ticks). Sin una variable que recuerde la
        estación y una física que la lea no hay anticipación posible.
        Requiere energia=True. False: byte-idéntico.

        energia_luz=True (v11, FOTOSÍNTESIS): la luz cae sobre TODO el tejido,
        no sólo sobre la superficie. Cada celda viva cosecha e_gan·|v − sol(t)|
        (distancia en el toro entre su materia y la del clima). Con la cosecha
        sólo en la superficie (v9) el interior se moría de hambre por
        geometría y el recambio (3–7% por tick, vidas de 20–30 ticks) lo ponía
        la forma del tejido, no el clima; así nada vivía una estación entera
        (300–900 ticks) y no había qué aprender. Con luz en todas partes, lo
        que decide el ingreso de cada celda es la relación entre SU materia y
        LA ESTACIÓN: al cambiar la estación cambia quién come, con el retraso
        de la reserva (τ≈e0/e_mant) — la muerte llega tras el cambio y la
        anticipación tendría valor. Requiere energia=True. False: byte-idéntico.

        luz_finita=L0 (v12, CAPACIDAD DE CARGA; 0 = apagado): la luz de cada tick
        es FINITA, L = L0·sol(t) (sin sol, L0·0.25), y se reparte entre las
        celdas vivas en proporción a w_i = |v_i − sol(t)| + 0.05 (la materia
        lejos del clima absorbe más; el piso evita que nadie coma nada). Con
        ingreso individual (energia_luz) el sistema sólo tiene dos destinos:
        inmortalidad o extinción. Con un recurso compartido la población se
        autorregula hacia N* = L/e_mant, la capacidad de carga, que cambia con
        la estación: A (sol bajo) es hambruna, B abundancia. Mortandad al
        entrar en A, floración en B, y valor selectivo real para quien guarde
        energía o deje de parir ANTES de la hambruna. Es el escenario mínimo
        de la ecología donde anticipar paga. Requiere energia=True. Manos: L0,
        el piso 0.05. luz_finita=0: byte-idéntico.

        lentos=λ (v13, REGISTROS LENTOS; 0 = apagado): dos registros más por
        celda, S1 y S2, que la física LEE como cualquier registro y a los que
        sólo puede EMPUJAR despacio: si la regla escribe w, el sustrato aplica
        S ← S + λ·(w − S); si no escribe, S no cambia. Una regla que escribe
        una constante carga S exponencialmente con τ = 1/λ: un reloj o un
        integrador a la escala de la estación (medido: la memoria interna del
        tejido dura 6–150 ticks; las estaciones 300–900; sin dónde guardar
        estado a esa escala no hay anticipación posible). Como el VM no tiene
        condicionales, la regla puede usar S vía MUTO (reescribir su propio
        SPAWN según |S|): control de flujo por auto-reescritura. La cría nace
        con S=0. Los campos indexan mod (4 + extras). λ=0: byte-idéntico.

        e_costo=c (0 = apagado): PARIR CUESTA. La madre quema c de energía en
        cada parto (además de ceder e_parto a la cría); si no tiene c, no pare.
        La invasión desde raro mostró que, con partos gratis, "reproducirse en
        la crisis" le gana a "ahorrar antes de la crisis" (34 partos/100 ticks
        en la hambruna). En ecología la latencia y el ahorro sólo evolucionan
        cuando reproducirse cuesta. Requiere energia=True. Mano: c.

        refractario=T (v15, TIERRA QUEMADA; 0 = apagado): el lugar de una celda
        que muere queda incolonizable durante T ticks (ni colonización ni
        invasión; el crecimiento por los bordes no se toca). Motivo (PLAN §12–
        §14): en esta ecología sobrevivir a la hambruna no otorga descendencia
        porque el vacío se rellena igual de rápido desde cualquier
        superviviente; con el vacío refractario, conservar el lugar durante la
        hambruna es la única forma de tener territorio en la abundancia
        (selección K en vez de r). Un SPAWN dirigido a tierra quemada fracasa
        como si el vecino estuviera ocupado (paga e_costo igual). T=0:
        byte-idéntico. Mano: T."""
        self.refractario = int(refractario)
        # v16 (ESCRITURA TOTAL): MUTO y el germinal escriben la instrucción entera
        # (op, a, b, c) desde los registros. Rompe la clausura de operandos (los
        # tríos (a,b,c) de un mundo estaban congelados en la sopa inicial: la
        # cuarta jaula, PLAN §15). Sin RNG nuestro: la materia escribe el programa
        # completo. False: byte-idéntico.
        self.escritura_total = bool(escritura_total)
        # §17 (CONGELADO): sin herencia de cambios — MUTO y COPY inertes y el
        # germinal no escribe: las crías son copias exactas. Misma física,
        # ecología y demografía que el brazo vivo; el único nulo real para
        # "¿evoluciona?". False: byte-idéntico.
        self.congelado = bool(congelado)
        # §21 (orden_seed): RNG aparte para el ORDEN de actualización, dejando la
        # sopa inicial fija por `seed`. Permite réplicas del mismo mundo con otro
        # azar de orden (¿gana el mismo genoma?). None: byte-idéntico.
        self.orden_seed = orden_seed
        # §22 (tasa_germinal = p): la cría recibe la escritura germinal sólo si
        # frac(|R3 crudo de la madre| · 97) < p — determinista desde la materia,
        # sin RNG nuestro; mano declarada. Con p = 1 la escritura ocurre en cada
        # parto (≈1 mutación por generación: régimen de umbral de error). 1.0:
        # byte-idéntico.
        self.tasa_germinal = float(tasa_germinal)
        # v17 (PARÁMETROS HEREDABLES; §32/§33): la quinta jaula es que el mapa
        # programa→materia no tiene localidad (ningún cambio pequeño del programa
        # produce un cambio pequeño y dirigido de la materia). Respuesta: un
        # desplazamiento continuo heredable θ por celda, sumado a la salida de
        # materia DESPUÉS de la sonda (v' = (salida + θ) mod 1; la sonda ve la
        # salida cruda, así que θ no puede legalizar ni matar un programa). La
        # cría hereda θ con una perturbación ε·(2·frac(|R3 madre|·131) − 1):
        # determinista desde la materia, sin RNG nuestro. MUTO no lo toca; el
        # theta_fijo lo copia exacto. Sólo con toroidal. parametros=0: byte-idéntico.
        self.parametros = float(parametros)
        # theta_fijo=True: θ presente (sorteado en la sopa) pero NUNCA perturbado: el
        # nulo de v17 (misma materia inicial, sin herencia de cambios en θ).
        self.theta_fijo = bool(theta_fijo)
        # v17b (ESCALA; §33/§34): un desplazamiento no cambia la distancia media al
        # sol de una materia pseudoaleatoria; el rasgo que el gradiente premia es la
        # DISPERSIÓN. Con escala=True la materia visible es (θ + s·salida) mod 1, con
        # s ∈ [0, 1] heredable (nace en 1: byte-idéntico a sólo-θ hasta que varía),
        # perturbado al nacer con ±ε·(2·frac(|R3 madre|·173) − 1) y recortado a [0, 1].
        # La sonda sigue viendo la salida cruda: la física sigue obligada a ser
        # sensible; sólo su expresión en la materia puede atenuarse. Requiere
        # parametros > 0. theta_fijo también congela s. escala=False: byte-idéntico.
        self.escala = bool(escala)
        self.esc = np.ones(n0)
        # §36 (PERILLAS ESCRIBIBLES): la física puede mover su propia expresión en
        # vida: θ_eff = (θ + S1) mod 1 y s_eff = clip(s + S2, 0, 1), con S1, S2 los
        # registros lentos (lentos > 0) que la regla empuja despacio. La herencia
        # (θ, s) pone la línea de base; el comportamiento la desplaza según lo que la
        # física siente (p.ej. su energía, con percepcion) y recuerda. Requiere
        # parametros, escala y lentos. perillas=False: byte-idéntico.
        self.perillas = bool(perillas)
        self.quemada = np.zeros(n0, dtype=np.int64)   # tick hasta el cual el lugar sigue quemado
        self.e_costo = float(e_costo)
        self.lentos = float(lentos)
        self.S = np.zeros((n0, 2))
        self.luz_finita = float(luz_finita)
        self._ingreso = np.zeros(n0)
        self.energia_luz = energia_luz
        self.percepcion = percepcion
        self.energia = energia
        self.e0, self.e_mant, self.e_gan = float(e0), float(e_mant), float(e_gan)
        self.e_dif, self.e_parto = float(e_dif), float(e_parto)
        self.e = np.full(n0, float(e0))
        self.sol_eq_eps, self.sol_eq_window = float(sol_eq_eps), int(sol_eq_window)
        self.eq_sol_count = np.zeros(n0, dtype=np.int64)
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
        self._rng_orden = self.rng if orden_seed is None else np.random.default_rng(int(orden_seed))
        self.theta = np.zeros(n0)
        self.code = np.zeros((n0, K, F), dtype=np.int64)
        self.code[:, :, 0] = self.rng.integers(0, 10, size=(n0, K))
        self.code[:, :, 1:] = self.rng.integers(0, 16, size=(n0, K, F - 1))
        if self.parametros > 0.0:
            self.theta = self.rng.uniform(0.0, 1.0, size=n0)
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
            self.eq_sol_count[i] = 0
            self.e[i] = 0.0
            self.S[i] = 0.0
            self.quemada[i] = self._tick + self.refractario

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
        if self.energia and self.luz_finita > 0.0:
            vac = self._vacio()
            luz = self.luz_finita * (vac if self.sol is not None else 0.25)
            d = np.abs(self.v - vac)
            w = (np.minimum(d, 1.0 - d) if self.toroidal else d) + 0.05
            w = np.where(self.alive, w, 0.0)
            tot = w.sum()
            self._ingreso = luz * w / tot if tot > 0 else np.zeros(self.n)

        for i in self._rng_orden.permutation(np.flatnonzero(self.alive)):
            i = int(i)
            if not self.alive[i]:          # murió antes de su turno
                continue
            if i in doomed:
                self.alive[i] = False
                self.v[i] = 0.0
                self.code[i] = 0
                self.eq_count[i] = 0
                self.mem[i] = 0.0
                self.quemada[i] = self._tick + self.refractario
                deaths += 1
                continue
            ctx, vl, vr = self._ctx(i)
            mi = float(self.mem[i]) if self.memoria else 0.0
            stats: dict | None = {} if self.log_events else None
            if self.lentos > 0.0:
                xtra = ([float(self.e[i])] if (self.percepcion and self.energia) else []) \
                    + [float(self.S[i, 0]), float(self.S[i, 1])]
            else:
                xtra = float(self.e[i]) if (self.percepcion and self.energia) else None
            s_prev = list(xtra[-2:]) if self.lentos > 0.0 else None
            v_new, own_next, spawn, raw = execute(
                self.code[i], vl, float(self.v[i]), vr, ctx,
                wrap=self.toroidal, r3_init=mi, stats=stats, extra=xtra,
                total=self.escritura_total, frozen=self.congelado)
            if self.lentos > 0.0:
                for k in range(2):        # escritura lenta: S <- S + λ(w - S) sólo si la regla escribió
                    w = xtra[-2 + k]
                    if w != s_prev[k]:
                        self.S[i, k] += self.lentos * (w - self.S[i, k])
            if stats is not None:
                self.events[i - lg] = stats
            # persistencia: la física ciega a la materia muere (sonda, misma
            # memoria fija -> prueba de sensibilidad a la MATERIA sola)
            if self.shadow is None:
                v0 = self._vacio() if self.sol_sonda else 0.0
                h = (v0 + self._probe_hi) % 1.0 if (self.sol_sonda and self.toroidal)                     else self._probe_hi
                p1 = _output_only(self.code[i], v0, v0, v0, ctx,
                                  wrap=self.toroidal, r3_init=mi, extra=xtra)
                p2 = _output_only(self.code[i], h, h, h, ctx,
                                  wrap=self.toroidal, r3_init=mi, extra=xtra)
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
                self.quemada[i] = self._tick + self.refractario
                deaths += 1
                continue
            if self.parametros > 0.0 and self.toroidal:     # v17: desplazamiento heredable
                if self.escala:                                # v17b: y escala heredable
                    th_eff, s_eff = float(self.theta[i]), float(self.esc[i])
                    if self.perillas and self.lentos > 0.0:       # §36: la física mueve su expresión
                        th_eff = (th_eff + float(self.S[i, 0])) % 1.0
                        s_eff = min(1.0, max(0.0, s_eff + float(self.S[i, 1])))
                    v_new = (th_eff + s_eff * v_new) % 1.0
                else:
                    v_new = (v_new + float(self.theta[i])) % 1.0
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
                    self.quemada[i] = self._tick + self.refractario
                    continue
            # async: efectos inmediatos
            if self.sol is not None and self.sol_acople > 0.0:
                borde = ((i == 0 or not self.alive[i - 1])
                         or (i == self.n - 1 or not self.alive[i + 1]))
                if borde:
                    v_new = (1.0 - self.sol_acople) * v_new + self.sol_acople * self._vacio()
            if self.sol is not None and self.sol_eq_eps > 0.0:
                d = abs(v_new - self._vacio())
                d = min(d, 1.0 - d) if self.toroidal else d
                if d < self.sol_eq_eps:
                    self.eq_sol_count[i] += 1
                else:
                    self.eq_sol_count[i] = 0
                if self.eq_sol_count[i] > self.sol_eq_window:
                    self.vaciar(i - lg)       # disuelta en el entorno: es vacío
                    deaths += 1
                    continue
            if self.energia:
                e = self.e[i] - self.e_mant
                borde = ((i == 0 or not self.alive[i - 1])
                         or (i == self.n - 1 or not self.alive[i + 1]))
                if self.luz_finita > 0.0:
                    e += float(self._ingreso[i])
                elif borde or self.energia_luz:
                    d = abs(v_new - self._vacio())
                    e += self.e_gan * (min(d, 1.0 - d) if self.toroidal else d)
                if e <= 0.0:
                    self.vaciar(i - lg)       # sin energía: es vacío
                    deaths += 1
                    continue
                self.e[i] = e
            self.v[i] = v_new
            self.code[i] = own_next
            self.mem[i] = raw            # memoria: R3 crudo persistente
            if spawn is None:
                continue
            if self.energia and self.e_costo > 0.0:
                if self.e[i] <= self.e_costo:
                    continue                    # sin energía para parir: no pare
                self.e[i] -= self.e_costo       # el parto cuesta, aunque el vecino esté ocupado
            side, mpos, mop, locus = spawn
            child = own_next.copy()
            th = float(self.theta[i])
            sc = float(self.esc[i])
            if self.parametros > 0.0 and not self.theta_fijo:
                th = (th + self.parametros * (2.0 * ((abs(raw) * 131.0) % 1.0) - 1.0)) % 1.0
                if self.escala:
                    sc = min(1.0, max(0.0, sc + self.parametros * (2.0 * ((abs(raw) * 173.0) % 1.0) - 1.0)))
            escribe = self.tasa_germinal >= 1.0 or (abs(raw) * 97.0) % 1.0 < self.tasa_germinal
            if self.germinal and not self.congelado and escribe:   # v2: nace con UNA instrucción
                if self.escritura_total:    # v16: la instrucción ENTERA desde la materia
                    child[mpos] = mop
                else:
                    child[mpos, 0] = mop    # reescrita desde la materia (sólo el opcode)
            if self.recombina:              # v7: una instrucción del otro progenitor
                o = i + 1 if side == 0 else i - 1
                if 0 <= o < self.n and self.alive[o] and not np.array_equal(
                        self.code[o], self.code[i]):
                    child[locus] = self.code[o][locus]
            t = i - 1 if side == 0 else i + 1
            if t < 0:                       # escribe en el más-allá izquierdo
                if edge_left is None:
                    edge_left = (child, v_new, i - lg, th, sc)
            elif t >= self.n:               # más-allá derecho
                if edge_right is None:
                    edge_right = (child, v_new, i - lg, th, sc)
            elif not self.alive[t] and self.quemada[t] <= self._tick:   # vacío interior: colonización
                # (v15: si el lugar está quemado, el SPAWN fracasa como ante un vecino ocupado)
                self.code[t] = child
                self.v[t] = v_new
                self.alive[t] = True
                self.eq_count[t] = 0
                self.mem[t] = 0.0           # la cría nace sin recuerdos
                self.eq_sol_count[t] = 0
                self.S[t] = 0.0             # la cría nace sin reloj
                self.theta[t] = th
                self.esc[t] = sc
                if self.energia:            # la madre cede parte de su energía
                    self.e[t] = self.e_parto * self.e[i]
                    self.e[i] -= self.e[t]
                colonized += 1
                self.spawns.append((i - lg, t - lg))
            elif self.invasion is not None and (
                    self.invasion == "siempre" or self.eq_count[t] > self.eq_window):
                self.code[t] = child        # v6: invasión de tejido asentado
                self.v[t] = v_new
                self.eq_count[t] = 0
                self.mem[t] = 0.0
                self.S[t] = 0.0
                self.theta[t] = th
                self.esc[t] = sc
                if self.energia:
                    self.e[t] = self.e_parto * self.e[i]
                    self.e[i] -= self.e[t]
                invaded += 1
                self.spawns.append((i - lg, t - lg))

        # crecimiento del mundo (fin de tick; tope = la placa de Petri)
        grown = 0
        grew_left = False
        if edge_right is not None and self.n < self.max_n:
            c, val, madre, th, sc = edge_right
            self.spawns.append((madre, self.n - lg))
            e_hija = 0.0
            if self.energia:
                mi_ = madre + lg
                e_hija = self.e_parto * self.e[mi_]
                self.e[mi_] -= e_hija
            self.e = np.concatenate([self.e, [e_hija]])
            self._ingreso = np.concatenate([self._ingreso, [0.0]])
            self.S = np.concatenate([self.S, np.zeros((1, 2))])
            self.theta = np.concatenate([self.theta, [th]])
            self.esc = np.concatenate([self.esc, [sc]])
            self.v = np.concatenate([self.v, [val]])
            self.code = np.concatenate([self.code, c[None]])
            self.alive = np.concatenate([self.alive, [True]])
            self.eq_count = np.concatenate([self.eq_count, [0]])
            self.mem = np.concatenate([self.mem, [0.0]])
            self.eq_sol_count = np.concatenate([self.eq_sol_count, [0]])
            self.quemada = np.concatenate([self.quemada, [0]])
            grown += 1
        if edge_left is not None and self.n < self.max_n:
            c, val, madre, th, sc = edge_left
            self.spawns.append((madre, -(lg + 1)))
            e_hija = 0.0
            if self.energia:
                mi_ = madre + lg
                e_hija = self.e_parto * self.e[mi_]
                self.e[mi_] -= e_hija
            self.e = np.concatenate([[e_hija], self.e])
            self._ingreso = np.concatenate([[0.0], self._ingreso])
            self.S = np.concatenate([np.zeros((1, 2)), self.S])
            self.theta = np.concatenate([[th], self.theta])
            self.esc = np.concatenate([[sc], self.esc])
            self.v = np.concatenate([[val], self.v])
            self.code = np.concatenate([c[None], self.code])
            self.alive = np.concatenate([[True], self.alive])
            self.eq_count = np.concatenate([[0], self.eq_count])
            self.mem = np.concatenate([[0.0], self.mem])
            self.eq_sol_count = np.concatenate([[0], self.eq_sol_count])
            self.quemada = np.concatenate([[0], self.quemada])
            self.left_grown += 1
            grown += 1
            grew_left = True

        if self.energia and self.e_dif > 0.0:
            # intercambio simétrico entre pares de vecinas vivas (conservativo)
            a = self.alive
            par = a[:-1] & a[1:]
            flujo = np.zeros(self.n - 1)
            flujo[par] = self.e_dif * 0.5 * (self.e[:-1][par] - self.e[1:][par])
            self.e[:-1] -= flujo
            self.e[1:] += flujo

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

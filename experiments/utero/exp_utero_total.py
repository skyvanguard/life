"""
v16 — ESCRITURA TOTAL: ¿emerge regulación por orden cuando la variación puede
escribir el programa ENTERO? (docs/PLAN_INTELIGENCIA.md §15; ledger 2026-09-26)

MOTIVO. La cuarta jaula (exp_utero_alcance_operandos): ningún operador de
variación escribía operandos —MUTO y el germinal sólo el opcode, COPY traslada
filas existentes—, así que los tríos (a,b,c) de un mundo quedaban congelados
en su sopa inicial (6.06% de los 4096 posibles) y sólo 3/40 sopas contenían
siquiera las piezas del ahorrador. Dieciocho corridas buscaron emergencia en un
espacio con tres de cada cuatro campos fijos desde el tick 0. v16 abre el
espacio con `escritura_total=True`: MUTO y el germinal escriben la instrucción
entera desde los registros (op desde |R_b|; a, b, c desde |R_{b+1..b+3}| mod m,
escalados a 16). Sigue sin haber RNG nuestro: la materia escribe el programa
completo. Abre el espacio; no siembra ninguna respuesta. Todo lo demás es v14:
hambruna dura (A_BASE 0.08), parto costoso (e_costo 1), luz finita, registros
lentos, nada sembrado, sin tierra quemada (v15 mostró que no era el cuello).

CALIBRACIÓN (6 semillas × {apagado, encendido}, 12000 ticks, sol seed 0):
encendido es viable (5/6 vivas, N_A 29 vs 22, contacto conservado, muertes/t
0.028 vs 0.015) y ABIERTO: 16656 genomas nunca vistos por mundo (mediana) contra
198, y 52 tríos de operandos nuevos por mundo contra 0. La semilla 13 (la
"fértil" de v5) se extingue con el flag: la apertura también vuelve letal la
mutación. Decidido antes de correr: flag tal cual, sin ajustar nada más.

BRAZOS, LECTURAS Y VEREDICTO: idénticos a v14 corrida 2: clima, ciclo2,
permutado, sin sol, sombra; lectura primaria R2_A (mortalidad pareada en la
hambruna, clima < permutado en ≥ 75% de pares vivos, p signo < 0.05, razón ≤
0.5, con ciclo2 como control de tipos de transición); estructura de partos
A/B; secundarias A, A_m, L, L_m, A_n, A_nD, A_nB/A_nBD (control emparejado por
estación), A_e, A_eN (control), L_A con la vara §6b evaluada en clima y ciclo2.
VESTIGIO si R2_A cumple en clima y ciclo2, o si una lectura primaria cumple las
tres condiciones; SIN CONTACTO si las muertes no cambian al entrar en A; NADA
en otro caso. Si VESTIGIO: replicar con otro sembrado del sol antes de creerlo.
Si NADA: el espacio abierto tampoco basta en 30000 ticks; la pregunta pasa al
TIEMPO y al TAMAÑO (la evolución experimental real corre miles de generaciones
sobre poblaciones grandes) antes que a otra jaula.

    PYTHONPATH=src python experiments/utero/exp_utero_total.py
"""

from __future__ import annotations

import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.creciente import UteroCreciente  # noqa: E402
from zeta_life.utero.inteligencia import anticipacion, aprendizaje, correr_series  # noqa: E402
from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

N0, MAX_N = 16, 256
TICKS = 30000
SEEDS = list(range(40))
SOL_SEED = 0
KAPPA = 0.5
E_MANT, E_DIF, E_PARTO = 0.01, 0.25, 0.5
L0, E0, PERCEPCION = 3.0, 2.0, False
LENTOS = 0.02                               # registros lentos (tau = 50): detectores de estación posibles
A_BASE, E_COSTO = 0.08, 1.0                 # se fijan tras la calibración por viabilidad estacional
REGS = (("A", A_BASE, 0.02, 40),) + REGIMENES[1:]
FLAGS = dict(memoria=True, invasion="asentada", eq_window=100,
             energia=True, luz_finita=L0, e0=E0, e_mant=E_MANT, e_dif=E_DIF,
             e_parto=E_PARTO, percepcion=PERCEPCION, lentos=LENTOS, e_costo=E_COSTO,
             escritura_total=True)   # v16: la materia escribe la instruccion entera
PRECEDE_A = {"clima": ("C",), "ciclo2": ("B",), "permutado": None, "sin": ("C",), "sombra": ("C",)}
ALPHA, MIN_SEEDS, RATIO, CONTACTO = 0.05, 5, 2.0, 1.2
MATURE = (6000, 30000)
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_total"
ARMS = ("clima", "ciclo2", "permutado", "sin", "sombra")


def fabrica(seed: int, shadow, **flags) -> UteroCreciente:
    return UteroCreciente(n0=N0, seed=seed, max_n=MAX_N, germinal=True, toroidal=True,
                          log_events=True, shadow_deaths=shadow, **flags)


def job(seed: int) -> tuple:
    clima = Sol(seed=SOL_SEED, ticks=TICKS, regimenes=REGS)
    ciclo2 = Sol(seed=SOL_SEED, ticks=TICKS, orden="ciclico_inverso", regimenes=REGS)
    perm = Sol(seed=SOL_SEED, ticks=TICKS, orden="permutado", regimenes=REGS)
    series = {"clima": correr_series(seed, FLAGS, clima, TICKS, fabrica=fabrica),
              "ciclo2": correr_series(seed, FLAGS, ciclo2, TICKS, fabrica=fabrica),
              "permutado": correr_series(seed, FLAGS, perm, TICKS, fabrica=fabrica),
              "sin": correr_series(seed, FLAGS, None, TICKS, fabrica=fabrica)}
    series["sombra"] = correr_series(seed, FLAGS, clima, TICKS, fabrica=fabrica,
                                     shadow=list(series["clima"]["muertes"].astype(int)))
    cal = {"clima": clima, "ciclo2": ciclo2, "permutado": perm, "sin": clima, "sombra": clima}
    out = {}
    for arm, ser in series.items():
        for tag, serie in (("", ser["actividad"]), ("_m", ser["muertes"])):
            out[("A" + tag, arm)] = anticipacion(serie, cal[arm], rng_seed=seed)
            out[("L" + tag, arm)] = aprendizaje(serie, cal[arm], rng_seed=seed)
        out[("A_n", arm)] = anticipacion(-ser["nacimientos"], cal[arm], rng_seed=seed,
                                         regimenes=PRECEDE_A[arm])
        # corrida 2: A_nD = la misma caída de partos pero como residuo de la tendencia
        # lineal previa a la ventana (sin deriva): si A_n cumple y A_nD no, era saturación.
        out[("A_nD", arm)] = anticipacion(-ser["nacimientos"], cal[arm], rng_seed=seed,
                                          regimenes=PRECEDE_A[arm], detrend=True)
        # corrida 2: control EMPAREJADO por estación. A_n en ciclo2 mira las B largas
        # (PRECEDE_A), donde la población satura; los otros brazos miran C o todas. A_nB
        # es la misma lectura sobre B largas en TODOS los brazos: en clima/permutado/sin a
        # B no le sigue la hambruna, así que un A_nB alto allí es saturación, no anticipación.
        out[("A_nB", arm)] = anticipacion(-ser["nacimientos"], cal[arm], rng_seed=seed,
                                          regimenes=("B",))
        out[("A_nBD", arm)] = anticipacion(-ser["nacimientos"], cal[arm], rng_seed=seed,
                                           regimenes=("B",), detrend=True)
        em = np.nan_to_num(ser["e_media"], nan=0.0)
        # corrida 4: A_e = exceso de energía media en el instante esperado respecto de la
        # tendencia lineal ajustada ANTES de la ventana y extrapolada (sin deriva);
        # A_eN = el nivel crudo, sólo como control del artefacto.
        out[("A_e", arm)] = anticipacion(em, cal[arm], rng_seed=seed, regimenes=PRECEDE_A[arm],
                                         detrend=True)
        out[("A_eN", arm)] = anticipacion(em, cal[arm], rng_seed=seed, regimenes=PRECEDE_A[arm])
        # L_A: habituación ESPECÍFICA de la hambruna — Spearman(ocurrencia k, muertes al entrar en A)
        solA = type(cal[arm])(seed=cal[arm].seed, ticks=cal[arm].ticks, orden=cal[arm].orden)
        solA.estaciones = [e for e in cal[arm].estaciones if e[0] == "A"] + [cal[arm].estaciones[-1]]
        out[("L_A", arm)] = aprendizaje(ser["muertes"], solA, rng_seed=seed)
        out[("contacto", arm)] = contacto(ser["muertes"], cal[arm])
        out[("vivas", arm)] = float(np.median(ser["vivas"][MATURE[0]:]))
        out[("muertes", arm)] = float(ser["muertes"][MATURE[0]:].mean())
        mA, nA, nB = [], [], []
        for nombre, ini, fin in cal[arm].estaciones:
            if ini < MATURE[0]:
                continue
            if nombre == "A":
                mA.append(ser["muertes"][ini:fin].mean())
                nA.append(ser["nacimientos"][ini:fin].mean())
            elif nombre == "B":
                nB.append(ser["nacimientos"][ini:fin].mean())
        out[("muertes_A", arm)] = float(np.mean(mA)) if mA else float("nan")
        out[("nac_A_B", arm)] = float(np.mean(nA) / max(np.mean(nB), 1e-9)) if nA and nB else float("nan")
    return seed, out


def contacto(muertes: np.ndarray, sol: Sol) -> float:
    ratios = []
    for _, ini, _ in sol.estaciones[1:-1]:
        if ini - 100 >= 0 and ini + 100 <= len(muertes):
            pre, post = muertes[ini - 100:ini].mean(), muertes[ini:ini + 100].mean()
            if pre > 0:
                ratios.append(post / pre)
    return float(np.median(ratios)) if ratios else float("nan")


def binom_p(k: int, n: int, p0: float) -> float:
    return float(sum(math.comb(n, j) * p0 ** j * (1 - p0) ** (n - j) for j in range(k, n + 1)))


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("v16 ESCRITURA TOTAL -- v14 + MUTO/germinal escriben la instruccion entera (se rompe la clausura de operandos); lectura primaria R2_A")
    out("=" * 80)
    out(f"linea n0={N0} max {MAX_N}; flags {FLAGS}; {len(SEEDS)} semillas; {TICKS} ticks; sol seed {SOL_SEED}; workers={WORKERS}")
    out("veredicto pre-registrado (docstring; PLAN §6b)")
    out("")
    res: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, (seed, r) in enumerate(ex.map(job, SEEDS), 1):
            res[seed] = r
            if i % 5 == 0:
                print(f"  ... {i}/{len(SEEDS)} semillas", flush=True)

    out("-" * 80)
    out("CONTACTO y ESTADO por brazo (mediana sobre semillas)")
    cont = {}
    for arm in ARMS:
        c = np.array([res[s][("contacto", arm)] for s in SEEDS])
        cont[arm] = float(np.nanmedian(c))
        out(f"  {arm:<10} muertes post/pre {cont[arm]:.3f}  vivas {np.median([res[s][('vivas', arm)] for s in SEEDS]):.0f}  "
            f"muertes/tick {np.median([res[s][('muertes', arm)] for s in SEEDS]):.3f}  "
            f"semillas con contacto>=1.2: {int(np.nansum(c >= CONTACTO))}")
    hay_contacto = cont["clima"] >= CONTACTO or cont["clima"] <= 1.0 / CONTACTO

    # ---- R2_A: regulación por orden en la HAMBRUNA (mortalidad durante A, pareada, entre vivos) ----
    out("")
    out("-" * 80)
    out("R2_A. REGULACION POR ORDEN EN LA HAMBRUNA: muertes/tick durante A, pareadas, entre mundos vivos")
    out("  estructura de partos nacimientos_A / nacimientos_B (mediana entre vivos): "
        + "  ".join(f"{arm} {np.nanmedian([res[s][('nac_A_B', arm)] for s in SEEDS if res[s][('vivas', arm)] >= 10] or [np.nan]):.2f}"
                    for arm in ("clima", "ciclo2", "permutado")))
    r2 = {}
    for arm in ("clima", "ciclo2"):
        vivos = [s for s in SEEDS if res[s][("vivas", arm)] >= 10 and res[s][("vivas", "permutado")] >= 10
                 and not np.isnan(res[s][("muertes_A", arm)]) and not np.isnan(res[s][("muertes_A", "permutado")])]
        a = np.array([res[s][("muertes_A", arm)] for s in vivos])
        b = np.array([res[s][("muertes_A", "permutado")] for s in vivos])
        wins = int((a < b).sum()) if len(vivos) else 0
        razon = float(np.median(a / np.maximum(b, 1e-9))) if len(vivos) else float("nan")
        p_sign = binom_p(wins, max(len(vivos), 1), 0.5)
        r2[arm] = dict(wins=wins, n=len(vivos), razon=razon, p=p_sign,
                       ok=len(vivos) >= 8 and wins >= 0.75 * len(vivos) and p_sign < 0.05 and razon <= 0.5)
        out(f"  {arm:<7} < permutado en {wins}/{len(vivos)} pares con ambos vivos (p signo {p_sign:.3f}); "
            f"razon mediana {razon:.2f} -> {'CUMPLE' if r2[arm]['ok'] else 'no'}")
    if r2["clima"]["ok"] and r2["ciclo2"]["ok"]:
        out("  => ambos ordenes regulares mueren menos en la hambruna que el permutado: REGULACION POR ORDEN")
    elif r2["clima"]["ok"] and not r2["ciclo2"]["ok"]:
        out("  => solo A->B->C es 'suave': son los TIPOS de transicion, no el orden")
    else:
        out("  => sin regulacion por orden en la hambruna")

    def conteo(vara, arm):
        key = "estadistico" if vara.startswith("A") else "rho"
        signo = vara.startswith("A")
        return [s for s in SEEDS if not np.isnan(res[s][(vara, arm)]["p"])
                and res[s][(vara, arm)]["p"] < ALPHA and (res[s][(vara, arm)][key] > 0 or not signo)]

    lecturas = ("A", "A_m", "L", "L_m", "A_n", "A_nD", "A_nB", "A_nBD", "A_e", "A_eN", "L_A")
    PRIMARIAS = ("A", "A_m", "L", "L_m", "A_n", "A_nD", "A_e", "L_A")   # A_eN es control, no cuenta
    C = {v: {arm: conteo(v, arm) for arm in ARMS} for v in lecturas}
    out("")
    out("-" * 80)
    out("POSITIVAS POR LECTURA Y BRAZO (p<0.05; A con stat>0)")
    out(f"  {'lectura':<8} " + " ".join(f"{arm:>10}" for arm in ARMS)
        + "   p_binom(clima) c2 c3 | p_binom(ciclo2) c2 c3")
    cumplen = []
    for v in lecturas:
        fila = f"  {v:<8} " + " ".join(f"{len(C[v][arm]):>10}" for arm in ARMS)
        for brazo in ("clima", "ciclo2"):        # corrida 2: ambos brazos regulares se evalúan
            n_eval = sum(1 for s_ in SEEDS if not np.isnan(res[s_][(v, brazo)]["p"]))
            k = len(C[v][brazo])
            pb = binom_p(k, max(n_eval, 1), ALPHA)
            c2 = k >= MIN_SEEDS and pb < 0.05
            c3 = (k >= RATIO * max(len(C[v]["sin"]), len(C[v]["sombra"]), 1)
                  and k >= RATIO * max(len(C[v]["permutado"]), 1))
            if v in ("A_n", "A_nD"):
                # control emparejado: la misma lectura sobre B largas en los brazos donde a
                # B no le sigue la hambruna (clima, permutado, sin). Si allí es igual de
                # alta, es saturación demográfica dentro de B.
                vb = v.replace("A_n", "A_nB")
                sat = max(len(C[vb][a_]) for a_ in ("clima", "permutado", "sin"))
                c3 = c3 and k >= RATIO * max(sat, 1)
            if c2 and c3 and v in PRIMARIAS:
                cumplen.append(f"{v}@{brazo}")
            fila += f"   {pb:>13.3f} {str(c2)[0]:>2} {str(c3)[0]:>2}"
        out(fila)
    for v in lecturas:
        out(f"  {v}: " + "  ".join(f"{arm} {C[v][arm]}" for arm in ARMS))
    for v in ("L", "L_m", "L_A"):
        hab = [s_ for s_ in C[v]["clima"] if res[s_][(v, "clima")]["rho"] < 0]
        out(f"  habituacion en clima ({v}): {hab}")

    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if not hay_contacto:
        out(f"=> SIN CONTACTO: muertes post/pre en clima = {cont['clima']:.2f} dentro de [1/{CONTACTO}, {CONTACTO}]. No se lee como 'sin inteligencia'.")
    elif cumplen or (r2["clima"]["ok"] and r2["ciclo2"]["ok"]):
        que = list(cumplen) + (["R2 regularidad"] if (r2["clima"]["ok"] and r2["ciclo2"]["ok"]) else [])
        out(f"=> VESTIGIO en {que} (contacto {cont['clima']:.2f}). ANTES DE CREERLO: barrido de kappa y de la seed del sol.")
    else:
        out(f"=> NADA (con contacto {cont['clima']:.2f}): ninguna lectura cumple; R2 {'solo tipos de transicion' if r2['clima']['ok'] else 'no'}.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

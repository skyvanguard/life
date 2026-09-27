"""
§30 — TASA BAJA A POBLACIÓN GRANDE, Y ¿CARGA O REGULACIÓN?
(docs/PLAN_INTELIGENCIA.md §30; ledger 2026-09-27)

MOTIVO. §29 (N = 512): la criba entre programas fijos acumula el rasgo
anti-hambruna (banda 0.55 en el congelado) y la herencia de cambios lo
arrastra de vuelta (0.30–0.37): umbral de error sobre el rasgo. Y un dato
inesperado: mortalidad per cápita en la hambruna 0.14 (abierto) contra 0.96
(congelado), cerrado 0.29. Dos hipótesis: (H1) CARGA — las escrituras rompen
SPAWN, baja la fecundidad, sobra reserva para A; predice mortalidad ordenada
por tasa de mutación (más mutación → menos partos → menos muertes) y partos
per cápita menores en TODAS las estaciones; (H2) REGULACIÓN — el tejido con
herencia reduce los partos específicamente antes o durante la hambruna;
predice partos_A/partos_B menor que en el congelado y que la mortalidad baja
también con tasa baja.

DISEÑO. Como §29 (N = 512, L0 = 14, 120000 ticks, 12 semillas) con brazos
abierto p = 0.02, abierto p = 0.005 y congelado. Lectura primaria: el rasgo
w̄_A, misma regla que §27/§29 (ADAPTA si tardío/temprano y nivel superan al
congelado en ≥ 75% de los pares). Secundarias pre-registradas: partos per
cápita por estación (B y A, por 100 ticks), su cociente A/B, y mortalidad per
cápita en A, pareados contra el congelado. Lectura de H1/H2: CARGA si los
partos per cápita en B son menores que en el congelado en ≥ 75% de los pares
en ambos brazos Y la mortalidad en A es mayor con menos mutación (p0.005 >
p0.02 en ≥ 75%); REGULACIÓN si el cociente A/B es menor que en el congelado
en ≥ 75% de los pares sin que los partos en B sean menores; INDETERMINADO en
otro caso.

    PYTHONPATH=src python experiments/utero/exp_utero_tasa_grande.py
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
from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

N = 512
TICKS = 120000
SEEDS = list(range(12))
SOL_SEED = 0
L0 = 14.0               # = 1.75 x 8: misma luz por lugar que §27
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
BASE = dict(memoria=True, invasion="asentada", eq_window=100, energia=True, luz_finita=L0,
            e0=2.0, e_mant=0.01, e_dif=0.25, e_parto=0.5, percepcion=False, lentos=0.02, e_costo=1.0)
ARMS = {"abierto_p0.02": dict(escritura_total=True, tasa_germinal=0.02),
        "abierto_p0.005": dict(escritura_total=True, tasa_germinal=0.005),
        "cerrado": dict(),
        "congelado": dict(congelado=True)}
TRANSITORIO = 6000
MIN_HAMBRUNAS = 4
BANDA = 0.4
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_tasa_grande"


def correr(seed: int, arm: str) -> dict:
    sol = Sol(seed=SOL_SEED, ticks=TICKS, regimenes=REGS)
    u = UteroCreciente(n0=N, seed=seed, max_n=N, germinal=True, toroidal=True, sol=sol, **BASE, **ARMS[arm])
    w = np.full(TICKS, np.nan)
    banda = np.full(TICKS, np.nan)
    vivas = np.zeros(TICKS)
    muertes = np.zeros(TICKS)
    partos = np.zeros(TICKS)
    for t in range(TICKS):
        r = u.step()
        partos[t] = r.get("colonized", 0) + r.get("invaded", 0) + r.get("grown", 0)
        alive = u.alive
        n = int(alive.sum())
        vivas[t] = n
        muertes[t] = r["deaths"]
        if n:
            d = np.abs(u.v[alive] - float(sol(t)))
            d = np.minimum(d, 1.0 - d)
            w[t] = float(d.mean() + 0.05)
            banda[t] = float((d >= BANDA).mean())
    wA, pcA, bA, nA, nB = [], [], [], [], []
    for nombre, ini, fin in sol.estaciones:
        if ini < TRANSITORIO or fin > TICKS:
            continue
        vv = vivas[ini:fin].mean()
        if nombre == "B" and vv > 0:
            nB.append(float(partos[ini:fin].sum() / vv / (fin - ini) * 100))   # partos por 100 ticks per capita
        if nombre != "A":
            continue
        v = vv
        if v > 0:
            nA.append(float(partos[ini:fin].sum() / v / (fin - ini) * 100))
        if v <= 0 or np.all(np.isnan(w[ini:fin])):
            continue
        wA.append(float(np.nanmean(w[ini:fin])))
        bA.append(float(np.nanmean(banda[ini:fin])))
        pcA.append(float(muertes[ini:fin].sum() / v))

    def razon(x):
        h = len(x) // 2
        return float(np.mean(x[h:]) / np.mean(x[:h])) if (h >= MIN_HAMBRUNAS and np.mean(x[:h]) > 0) else float("nan")

    return dict(seed=seed, arm=arm, n_h=len(wA), w_nivel=float(np.mean(wA)) if wA else float("nan"),
                w_razon=razon(wA), pc_nivel=float(np.mean(pcA)) if pcA else float("nan"), pc_razon=razon(pcA),
                banda_nivel=float(np.mean(bA)) if bA else float("nan"),
                nac_A=float(np.mean(nA)) if nA else float("nan"), nac_B=float(np.mean(nB)) if nB else float("nan"),
                nac_AB=float(np.mean(nA) / np.mean(nB)) if (nA and nB and np.mean(nB) > 0) else float("nan"),
                vivas_med=float(np.median(vivas[TRANSITORIO:])), vivas_fin=float(vivas[-1]), genomas=len(u.seen))


def job(a):
    return correr(*a)


def signo_p(k: int, n: int) -> float:
    return float(sum(math.comb(n, j) * 0.5 ** n for j in range(k, n + 1))) if n > 0 else 1.0


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("TASA BAJA A N=512 -- rasgo premiado, y CARGA o REGULACION? partos per capita por estacion; peso de luz de la materia durante la hambruna, variacion abierta vs congelado; cerrado, luz escasa")
    out("=" * 80)
    out(f"ecologia {BASE}; N={N}; brazos {list(ARMS)}; {len(SEEDS)} semillas; {TICKS} ticks; sol seed {SOL_SEED}; workers={WORKERS}")
    out("veredicto pre-registrado (docstring)")
    out("")
    res: dict = {a: {} for a in ARMS}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for r in ex.map(job, [(s, a) for a in ARMS for s in SEEDS]):
            res[r["arm"]][r["seed"]] = r

    def med(arm, k):
        v = [res[arm][s][k] for s in SEEDS]
        v = [x for x in v if not (isinstance(x, float) and np.isnan(x))]
        return float(np.median(v)) if v else float("nan")

    out("-" * 80)
    out("ESTADO por brazo (medianas)")
    out(f"  {'brazo':<14} {'vivas med':>9} {'vivas fin':>9} {'hambr':>5} {'w_A nivel':>9} {'w_A t/t':>8} {'banda>=0.4':>10} {'pc_A':>6} {'pc_A t/t':>8} {'nac_B':>6} {'nac_A':>6} {'A/B':>5} {'genomas':>8}")
    for arm in ARMS:
        out(f"  {arm:<14} {med(arm, 'vivas_med'):>9.0f} {med(arm, 'vivas_fin'):>9.0f} {med(arm, 'n_h'):>5.0f} {med(arm, 'w_nivel'):>9.3f} "
            f"{med(arm, 'w_razon'):>8.2f} {med(arm, 'banda_nivel'):>10.2f} {med(arm, 'pc_nivel'):>6.2f} {med(arm, 'pc_razon'):>8.2f} {med(arm, 'nac_B'):>6.2f} {med(arm, 'nac_A'):>6.2f} {med(arm, 'nac_AB'):>5.2f} {med(arm, 'genomas'):>8.0f}")
    out("")
    out("-" * 80)
    out("PAREADO por semilla contra CONGELADO")
    veredictos = {}
    for arm in [a for a in ARMS if a != "congelado"]:
        pr = [(res[arm][s]["w_razon"], res["congelado"][s]["w_razon"]) for s in SEEDS
              if not np.isnan(res[arm][s]["w_razon"]) and not np.isnan(res["congelado"][s]["w_razon"])]
        pn = [(res[arm][s]["w_nivel"], res["congelado"][s]["w_nivel"]) for s in SEEDS
              if not np.isnan(res[arm][s]["w_nivel"]) and not np.isnan(res["congelado"][s]["w_nivel"])]
        kr = sum(1 for a, b in pr if a > b)
        kn = sum(1 for a, b in pn if a > b)
        ok = len(pr) >= 8 and kr / len(pr) >= 0.75 and signo_p(kr, len(pr)) < 0.05 and len(pn) >= 8 and kn / len(pn) >= 0.75
        veredictos[arm] = ok
        out(f"  {arm:<14} w_A tardio/temprano > congelado en {kr}/{len(pr)} (p signo {signo_p(kr, max(len(pr), 1)):.3f}); "
            f"nivel w_A > congelado en {kn}/{len(pn)}; medianas nivel {np.median([a for a, _ in pn]) if pn else float('nan'):.3f} vs "
            f"{np.median([b for _, b in pn]) if pn else float('nan'):.3f} -> {'ADAPTA' if ok else 'no'}")
        pm = [(res[arm][s]["pc_razon"], res["congelado"][s]["pc_razon"]) for s in SEEDS
              if not np.isnan(res[arm][s]["pc_razon"]) and not np.isnan(res["congelado"][s]["pc_razon"])]
        km = sum(1 for a, b in pm if a < b)
        out(f"  {'':<14} (secundaria) mortalidad per capita t/t < congelado en {km}/{len(pm)} (p signo {signo_p(km, max(len(pm), 1)):.3f})")
    out("")
    out("  CARGA o REGULACION (pareado contra congelado):")

    def pares(arm, k, menor=True):
        pr = [(res[arm][s_][k], res["congelado"][s_][k]) for s_ in SEEDS
              if not np.isnan(res[arm][s_][k]) and not np.isnan(res["congelado"][s_][k])]
        kk = sum(1 for a_, b_ in pr if (a_ < b_ if menor else a_ > b_))
        return kk, len(pr)

    h = {}
    for arm in [a_ for a_ in ARMS if a_ != "congelado"]:
        kb, nb = pares(arm, "nac_B")
        kab, nab = pares(arm, "nac_AB")
        km, nm = pares(arm, "pc_nivel")
        h[arm] = (kb, nb, kab, nab, km, nm)
        out(f"    {arm:<14} partos_B < congelado {kb}/{nb}; A/B < congelado {kab}/{nab}; mortalidad_A < congelado {km}/{nm}")
    pm = [(res["abierto_p0.005"][s_]["pc_nivel"], res["abierto_p0.02"][s_]["pc_nivel"]) for s_ in SEEDS
          if not np.isnan(res["abierto_p0.005"][s_]["pc_nivel"]) and not np.isnan(res["abierto_p0.02"][s_]["pc_nivel"])]
    kp = sum(1 for a_, b_ in pm if a_ > b_)
    out(f"    mortalidad_A p0.005 > p0.02 en {kp}/{len(pm)} (H1 carga predice >= 75%)")
    carga = all(v[0] / max(v[1], 1) >= 0.75 for v in h.values()) and len(pm) >= 8 and kp / len(pm) >= 0.75
    regul = any(v[2] / max(v[3], 1) >= 0.75 and v[0] / max(v[1], 1) < 0.75 for v in h.values())
    out(f"    => {'CARGA' if carga else ('REGULACION' if regul else 'INDETERMINADO')}")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if any(veredictos.values()):
        out("=> EVOLUCIONA en " + ", ".join(a for a, v in veredictos.items() if v) + ": el rasgo premiado sube con la herencia de cambios mas que en el congelado.")
    else:
        out("=> NO EVOLUCIONA: con gradiente real, seleccion fuerte y oferta suficiente, la variacion no sube el rasgo en 120000 ticks (camino).")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

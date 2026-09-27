"""
§31 — CONTROL DE DENSIDAD: ¿la menor mortalidad en la hambruna del tejido con
herencia (§30) es herencia o es densidad? (docs/PLAN_INTELIGENCIA.md §31;
ledger 2026-09-27)

MOTIVO. §30: con tasa germinal 0.02 y N = 512 el tejido muere en la hambruna
menos que el congelado en 12/12 mundos (0.15 contra 0.96 per cápita) y su
caída entre hambrunas también (11/12, p 0.003). La regla de carga no se
cumplió y la de regulación sí, justo en el umbral. Confusor no pre-registrado:
los brazos con herencia tienen menos vivas (138 contra 176); con luz finita,
menos densidad es más luz por celda y más reserva para la hambruna. La carga
mutacional puede bajar la mortalidad en A por esa vía sin regular nada.

DISEÑO (por semilla, 12 semillas, N = 512, L0 = 14, 120000 ticks, sol seed 0):
  ABIERTO         escritura total, tasa germinal 0.02 (el brazo de §30); se
                  registran sus muertes por tick.
  CONGELADO-SOMBRA congelado (sin herencia de cambios) con la DENSIDAD
                  IGUALADA POR TRAYECTORIA: antes de cada tick FUERA de las
                  estaciones A, si tiene más vivas que el brazo abierto de la
                  misma semilla en ese tick, se vacían al azar las que sobran
                  (`vaciar`; la sonda sigue encendida); DURANTE A no se impone
                  ninguna muerte (las de A salen sólo de la energía). Misma
                  densidad al entrar en cada hambruna, ninguna herencia.
                  (Primera versión, descartada en humo: copiar el conteo de
                  muertes con `shadow_deaths` no igualó la densidad —218
                  contra 137 vivas— y apagaba la sonda.)
  CONGELADO       el nulo de §30, para replicar 12/12.
LECTURA PRIMARIA: mortalidad per cápita en la hambruna (muertes en A /
vivas medias en A), nivel maduro, pareada ABIERTO contra CONGELADO-SOMBRA.
  HEREDABLE   si abierto < congelado-sombra en ≥ 75% de los pares (n ≥ 8), p
              signo < 0.05, y razón mediana ≤ 0.5 → la ventaja no es la
              densidad: primer candidato a vestigio (una población que, por
              herencia, muere menos en la hambruna). Paso siguiente: mecanismo
              (partos, energía al entrar en A, invasión) y réplica con otro sol.
  DENSIDAD    si abierto < congelado-sombra en ≤ 50% de los pares → la
              ventaja era la densidad que la carga produce.
  INTERMEDIO  en otro caso.
Secundarias: vivas medias por brazo (¿la sombra igualó la densidad?),
congelado-sombra contra congelado (¿la densidad sola baja la mortalidad?),
partos per cápita en B y A, caída tardío/temprano.

    PYTHONPATH=src python experiments/utero/exp_utero_densidad.py
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
L0 = 14.0
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
BASE = dict(memoria=True, invasion="asentada", eq_window=100, energia=True, luz_finita=L0,
            e0=2.0, e_mant=0.01, e_dif=0.25, e_parto=0.5, percepcion=False, lentos=0.02, e_costo=1.0)
TRANSITORIO = 6000
MIN_HAMBRUNAS = 4
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_densidad"


def correr(seed: int, sol: Sol, objetivo=None, enA=None, **flags) -> dict:
    """objetivo: serie de vivas a igualar (control de densidad). Antes de cada tick FUERA de A,
    si hay mas vivas que el objetivo se vacian al azar las que sobran (sonda encendida; nada
    impuesto durante A). None: mundo normal."""
    u = UteroCreciente(n0=N, seed=seed, max_n=N, germinal=True, toroidal=True, sol=sol, **BASE, **flags)
    rng = np.random.default_rng(90_000 + seed)
    vivas = np.zeros(TICKS)
    muertes = np.zeros(TICKS)
    partos = np.zeros(TICKS)
    for t in range(TICKS):
        if objetivo is not None and not enA[t]:
            exceso = int(u.alive.sum() - objetivo[t])
            if exceso > 0:
                for i in rng.choice(np.flatnonzero(u.alive), exceso, replace=False):
                    u.vaciar(int(i) - u.left_grown)
        r = u.step()
        vivas[t] = u.alive.sum()
        muertes[t] = r["deaths"]
        partos[t] = r.get("colonized", 0) + r.get("invaded", 0) + r.get("grown", 0)
    pcA, nA, nB = [], [], []
    for nombre, ini, fin in sol.estaciones:
        if ini < TRANSITORIO or fin > TICKS:
            continue
        v = vivas[ini:fin].mean()
        if v <= 0:
            continue
        if nombre == "A":
            pcA.append(float(muertes[ini:fin].sum() / v))
            nA.append(float(partos[ini:fin].sum() / v / (fin - ini) * 100))
        elif nombre == "B":
            nB.append(float(partos[ini:fin].sum() / v / (fin - ini) * 100))
    h = len(pcA) // 2
    razon = float(np.mean(pcA[h:]) / np.mean(pcA[:h])) if (h >= MIN_HAMBRUNAS and np.mean(pcA[:h]) > 0) else float("nan")
    return dict(vivas=vivas, pc_nivel=float(np.mean(pcA)) if pcA else float("nan"), pc_razon=razon,
                nac_A=float(np.mean(nA)) if nA else float("nan"), nac_B=float(np.mean(nB)) if nB else float("nan"),
                vivas_med=float(np.median(vivas[TRANSITORIO:])), vivas_fin=float(vivas[-1]))


def job(seed: int) -> tuple:
    sol = Sol(seed=SOL_SEED, ticks=TICKS, regimenes=REGS)
    enA = np.zeros(TICKS, dtype=bool)
    for nombre, ini, fin in sol.estaciones:
        if nombre == "A":
            enA[ini:min(fin, TICKS)] = True
    ab = correr(seed, sol, escritura_total=True, tasa_germinal=0.02)
    som = correr(seed, sol, objetivo=ab["vivas"], enA=enA, congelado=True)
    con = correr(seed, sol, congelado=True)
    for r in (ab, som, con):
        r.pop("vivas")
    return seed, {"abierto": ab, "congelado_sombra": som, "congelado": con}


def signo_p(k: int, n: int) -> float:
    return float(sum(math.comb(n, j) * 0.5 ** n for j in range(k, n + 1))) if n > 0 else 1.0


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("CONTROL DE DENSIDAD -- abierto p=0.02 vs congelado con la misma mortalidad de fondo (sombra fuera de A) vs congelado")
    out("=" * 80)
    out(f"ecologia {BASE}; N={N}; {len(SEEDS)} semillas; {TICKS} ticks; sol seed {SOL_SEED}; workers={WORKERS}")
    out("veredicto pre-registrado (docstring)")
    out("")
    res: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for seed, r in ex.map(job, SEEDS):
            res[seed] = r
    arms = ("abierto", "congelado_sombra", "congelado")

    def med(arm, k):
        v = [res[s][arm][k] for s in SEEDS]
        v = [x for x in v if not np.isnan(x)]
        return float(np.median(v)) if v else float("nan")

    out("-" * 80)
    out("ESTADO por brazo (medianas)")
    out(f"  {'brazo':<17} {'vivas med':>9} {'vivas fin':>9} {'pc_A':>6} {'pc_A t/t':>8} {'nac_B':>6} {'nac_A':>6}")
    for arm in arms:
        out(f"  {arm:<17} {med(arm, 'vivas_med'):>9.0f} {med(arm, 'vivas_fin'):>9.0f} {med(arm, 'pc_nivel'):>6.2f} "
            f"{med(arm, 'pc_razon'):>8.2f} {med(arm, 'nac_B'):>6.2f} {med(arm, 'nac_A'):>6.2f}")
    out("")
    out("-" * 80)
    out("PAREADO por semilla (mortalidad per capita en A, nivel)")

    def par(a, b, k="pc_nivel"):
        pr = [(res[s][a][k], res[s][b][k]) for s in SEEDS if not np.isnan(res[s][a][k]) and not np.isnan(res[s][b][k])]
        kk = sum(1 for x, y in pr if x < y)
        raz = float(np.median([x / y if y > 0 else np.nan for x, y in pr])) if pr else float("nan")
        return kk, len(pr), raz, pr

    k1, n1, r1, pr1 = par("abierto", "congelado_sombra")
    k2, n2, r2, _ = par("abierto", "congelado")
    k3, n3, r3, _ = par("congelado_sombra", "congelado")
    out(f"  abierto < congelado-sombra en {k1}/{n1} (p signo {signo_p(k1, n1):.3f}); razon mediana {r1:.2f}")
    out("    por semilla (abierto | sombra): " + " ".join(f"{x:.2f}|{y:.2f}" for x, y in pr1))
    out(f"  abierto < congelado        en {k2}/{n2} (p signo {signo_p(k2, n2):.3f}); razon mediana {r2:.2f}   (replica de §30)")
    out(f"  sombra  < congelado        en {k3}/{n3} (p signo {signo_p(k3, n3):.3f}); razon mediana {r3:.2f}   (la densidad sola)")
    kt, nt, _, _ = par("abierto", "congelado_sombra", "pc_razon")
    out(f"  caida tardio/temprano: abierto < sombra en {kt}/{nt}")
    out(f"  densidad igualada? vivas medias abierto {med('abierto', 'vivas_med'):.0f}, sombra {med('congelado_sombra', 'vivas_med'):.0f}, congelado {med('congelado', 'vivas_med'):.0f}")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if n1 >= 8 and k1 / n1 >= 0.75 and signo_p(k1, n1) < 0.05 and r1 <= 0.5:
        out("=> HEREDABLE: con la misma densidad de fondo y sin herencia, el congelado-sombra muere mas en la hambruna que el tejido con herencia. Candidato a vestigio: replicar con otro sol y buscar el mecanismo.")
    elif n1 >= 8 and k1 / n1 <= 0.5:
        out("=> DENSIDAD: la ventaja de §30 era la densidad que la carga produce.")
    else:
        out("=> INTERMEDIO.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

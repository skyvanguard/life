"""
§18 — ¿HAY FENOTIPO HEREDABLE? ¿La supervivencia a la hambruna es una
propiedad del genoma, o del lugar y el estado? (docs/PLAN_INTELIGENCIA.md §18;
ledger 2026-09-27)

MOTIVO. §17 mostró que el sustrato no evoluciona bajo esta ecología: la
mortalidad per cápita en la hambruna no baja más con herencia de cambios que
en un mundo congelado, aunque haya 23 variantes viables por 1000 ticks
(§16b). La selección requiere que el filtro discrimine entre GENOMAS. Aquí se
mide eso directamente, sin evolucionar nada: entre las celdas vivas al
empezar cada hambruna, ¿sobrevivir se predice por el genoma que portan?

DISEÑO. Ecología de §16/§17 (L0 = 9), sol seed 0 cíclico, 60000 ticks, 20
semillas, brazos abierto (v16) y cerrado (v14). En cada hambruna A_k madura
(inicio ≥ 6000) se toma la foto de las vivas: genoma (huella), energía,
materia, si linda con vacío. Se sigue cada una hasta el fin de A_k: sobrevive
o no (muerte o reemplazo).

ESTADÍSTICOS por hambruna (nulo: permutar los destinos entre las celdas de
esa hambruna, 500 permutaciones):
  GENOMA: suma ponderada de cuadrados entre genomas con ≥ 2 portadoras,
          Σ n_g (p_g − p)². p_gen = fracción de permutaciones con T ≥ T_obs.
  ENERGÍA / BORDE: |correlación punto-biserial| entre el destino y la energía
          inicial, y entre el destino y lindar con vacío; mismo nulo.
  Se descartan hambrunas con < 20 vivas o sin genoma repetido.
Por mundo: fracción de hambrunas con p < 0.05 para cada predictor (nominal
0.05). Repetibilidad: para genomas con ≥ 3 portadoras en dos hambrunas
consecutivas, Spearman entre su supervivencia en k y en k+1 (nulo: barajar).

VEREDICTO (escrito antes de correr):
  HEREDABLE   si en ≥ 15/20 mundos (por brazo) ≥ 25% de las hambrunas tienen
              p_gen < 0.05 (5× la tasa nominal). Entonces el filtro sí
              discrimina genomas y el "no evoluciona" de §17 es cuestión de
              intensidad de selección frente a la carga: lo siguiente es
              medir la ventaja selectiva y el tiempo de fijación.
  ESTADO      si el genoma no cumple pero energía o borde sí: sobrevivir a la
              hambruna es cuestión de dónde y con cuánto, no de qué programa.
              Entonces no hay fenotipo heredable sobre el que la hambruna
              discrimine y NINGUNA cantidad de tiempo produce adaptación: hay
              que cambiar qué mide el filtro o cómo el genoma fija el estado.
  NADA        si nada predice el destino (muerte al azar en la hambruna).

    PYTHONPATH=src python experiments/utero/exp_utero_heredabilidad.py
"""

from __future__ import annotations

import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.creciente import UteroCreciente  # noqa: E402
from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

N0, MAX_N = 16, 512
TICKS = 60000
SEEDS = list(range(20))
SOL_SEED = 0
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
BASE = dict(memoria=True, invasion="asentada", eq_window=100, energia=True, luz_finita=9.0,
            e0=2.0, e_mant=0.01, e_dif=0.25, e_parto=0.5, percepcion=False, lentos=0.02, e_costo=1.0)
ARMS = {"abierto": dict(escritura_total=True), "cerrado": dict()}
TRANSITORIO = 6000
MIN_VIVAS, N_PERM, ALPHA = 20, 500, 0.05
UMBRAL_MUNDO, MIN_MUNDOS = 0.25, 15
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_heredabilidad"


def T_genoma(gen: np.ndarray, fate: np.ndarray) -> float:
    p = fate.mean()
    t = 0.0
    for g in np.unique(gen):
        m = gen == g
        n = int(m.sum())
        if n >= 2:
            t += n * (fate[m].mean() - p) ** 2
    return float(t)


def corr_abs(x: np.ndarray, fate: np.ndarray) -> float:
    if x.std() == 0 or fate.std() == 0:
        return 0.0
    return float(abs(np.corrcoef(x, fate)[0, 1]))


def p_perm(stat, x, fate, rng) -> float:
    obs = stat(x, fate)
    if obs == 0.0:
        return 1.0
    cnt = 0
    for _ in range(N_PERM):
        if stat(x, rng.permutation(fate)) >= obs:
            cnt += 1
    return (cnt + 1) / (N_PERM + 1)


def spearman(x, y) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    if rx.std() == 0 or ry.std() == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def correr(seed: int, arm: str) -> dict:
    rng = np.random.default_rng(seed + 101)
    sol = Sol(seed=SOL_SEED, ticks=TICKS, regimenes=REGS)
    u = UteroCreciente(n0=N0, seed=seed, max_n=MAX_N, germinal=True, toroidal=True, sol=sol,
                       log_events=True, **BASE, **ARMS[arm])
    hambrunas = [(ini, fin) for nombre, ini, fin in sol.estaciones if nombre == "A" and ini >= TRANSITORIO and fin <= TICKS]
    idx_h = 0
    foto = None          # {coord: (huella, energia, borde)} de la hambruna en curso
    vivo = None          # {coord: True/False}
    res_h = []           # por hambruna: dict(p_gen, p_ene, p_bor, n, n_gen_rep, surv_por_genoma)
    for t in range(TICKS):
        u.step()
        cg = u.genomas()
        born = {c for _, c in u.spawns}
        if foto is not None:
            for coord in list(vivo):
                if vivo[coord] and (coord not in cg or coord in born):
                    vivo[coord] = False
            ini, fin = hambrunas[idx_h]
            if t >= fin - 1:
                coords = list(foto)
                gen = np.array([hash(foto[c][0]) for c in coords])
                ene = np.array([foto[c][1] for c in coords])
                bor = np.array([foto[c][2] for c in coords], dtype=float)
                fate = np.array([1.0 if vivo[c] else 0.0 for c in coords])
                _, counts = np.unique(gen, return_counts=True)
                rep = int((counts >= 2).sum())
                if len(coords) >= MIN_VIVAS and rep >= 1 and 0 < fate.mean() < 1:
                    surv = {foto[c][0]: [] for c in coords}
                    for c in coords:
                        surv[foto[c][0]].append(fate[coords.index(c)])
                    res_h.append(dict(
                        p_gen=p_perm(T_genoma, gen, fate, rng), p_ene=p_perm(corr_abs, ene, fate, rng),
                        p_bor=p_perm(corr_abs, bor, fate, rng), n=len(coords), n_gen_rep=rep,
                        mort=float(1 - fate.mean()),
                        surv={g: float(np.mean(v)) for g, v in surv.items() if len(v) >= 3}))
                foto, vivo = None, None
                idx_h += 1
        if idx_h < len(hambrunas) and foto is None and t == hambrunas[idx_h][0]:
            alive = np.flatnonzero(u.alive)
            foto, vivo = {}, {}
            for i in alive:
                coord = int(i) - u.left_grown
                borde = (i == 0 or not u.alive[i - 1]) or (i == u.n - 1 or not u.alive[i + 1])
                foto[coord] = (cg[coord], float(u.e[i]), bool(borde))
                vivo[coord] = True
    # repetibilidad entre hambrunas consecutivas
    pares = []
    for a, b in zip(res_h, res_h[1:]):
        for g, s in a["surv"].items():
            if g in b["surv"]:
                pares.append((s, b["surv"][g]))
    rep_rho, rep_p = float("nan"), float("nan")
    if len(pares) >= 8:
        x = np.array([p[0] for p in pares]); y = np.array([p[1] for p in pares])
        rep_rho = spearman(x, y)
        nul = [spearman(x, rng.permutation(y)) for _ in range(N_PERM)]
        rep_p = float((np.sum(np.array(nul) >= rep_rho) + 1) / (N_PERM + 1))
    return dict(seed=seed, arm=arm, hambrunas=res_h, rep_rho=rep_rho, rep_p=rep_p, n_pares=len(pares),
                vivas_fin=int(u.alive.sum()))


def job(a):
    return correr(*a)


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("HEREDABILIDAD -- la supervivencia a la hambruna se predice por el GENOMA, por el ESTADO (energia, borde), o por nada?")
    out("=" * 80)
    out(f"ecologia {BASE}; {len(SEEDS)} semillas; {TICKS} ticks; sol seed {SOL_SEED}; permutaciones {N_PERM}; workers={WORKERS}")
    out("veredicto pre-registrado (docstring)")
    out("")
    res: dict = {a: {} for a in ARMS}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for r in ex.map(job, [(s, a) for a in ARMS for s in SEEDS]):
            res[r["arm"]][r["seed"]] = r
    veredictos = {}
    for arm in ARMS:
        out("-" * 80)
        out(f"BRAZO {arm}")
        out(f"  {'seed':>4} {'hambr':>5} {'vivas/h':>7} {'gen rep':>7} {'mort':>5} {'f(p_gen<.05)':>12} {'f(p_ene<.05)':>12} {'f(p_bor<.05)':>12} {'repet rho':>9} {'p':>6} {'pares':>5}")
        fg, fe, fb = [], [], []
        for s in SEEDS:
            r = res[arm][s]
            H = r["hambrunas"]
            if not H:
                out(f"  {s:>4} {0:>5}   (sin hambrunas utilizables; vivas fin {r['vivas_fin']})")
                continue
            g = np.mean([h["p_gen"] < ALPHA for h in H]); e = np.mean([h["p_ene"] < ALPHA for h in H]); b = np.mean([h["p_bor"] < ALPHA for h in H])
            if len(H) >= 10:
                fg.append(g); fe.append(e); fb.append(b)
            out(f"  {s:>4} {len(H):>5} {np.median([h['n'] for h in H]):>7.0f} {np.median([h['n_gen_rep'] for h in H]):>7.0f} "
                f"{np.median([h['mort'] for h in H]):>5.2f} {g:>12.2f} {e:>12.2f} {b:>12.2f} {r['rep_rho']:>9.2f} {r['rep_p']:>6.3f} {r['n_pares']:>5}")
        n_ok_g = sum(1 for x in fg if x >= UMBRAL_MUNDO); n_ok_e = sum(1 for x in fe if x >= UMBRAL_MUNDO); n_ok_b = sum(1 for x in fb if x >= UMBRAL_MUNDO)
        out(f"  mundos con >= 10 hambrunas: {len(fg)}; con f >= {UMBRAL_MUNDO}: genoma {n_ok_g}, energia {n_ok_e}, borde {n_ok_b}; "
            f"medianas f: genoma {np.median(fg) if fg else float('nan'):.2f}, energia {np.median(fe) if fe else float('nan'):.2f}, borde {np.median(fb) if fb else float('nan'):.2f}")
        rep = [res[arm][s]["rep_p"] for s in SEEDS if not np.isnan(res[arm][s]["rep_p"])]
        out(f"  repetibilidad entre hambrunas consecutivas: p < 0.05 en {sum(1 for p in rep if p < ALPHA)}/{len(rep)} mundos con pares suficientes")
        if n_ok_g >= MIN_MUNDOS:
            veredictos[arm] = "HEREDABLE"
        elif n_ok_e >= MIN_MUNDOS or n_ok_b >= MIN_MUNDOS:
            veredictos[arm] = "ESTADO"
        else:
            veredictos[arm] = "NADA"
        out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    for arm, v in veredictos.items():
        out(f"=> {arm}: {v}")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

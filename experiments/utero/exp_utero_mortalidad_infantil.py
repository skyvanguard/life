"""
El Útero — mortalidad infantil: ¿de qué mueren las crías de las llanuras?

La anatomía 13 vs 35 dejó el mecanismo de la fertilidad a medio camino: las
crías de las llanuras de la 35 nacen y mueren (699 nacimientos, 6 genomas,
vida mediana 1 tick); las de la 13 viven. Un sondeo (no publicado) refutó la
explicación genética: el 85–91% de los mutantes de un opcode de cualquier
genoma pasan la sonda en el contexto de la madre — nueve de cada diez crías
POSIBLES nacen viables. Entonces la muerte no está en el genoma de la cría
sino en lo que pasa DESPUÉS del parto. Este experimento sigue a cada cría
desde su nacimiento y clasifica su muerte.

Definiciones (memoria ON, germinal+toroidal, sin invasión = v5; crías nacidas
en [8000, 9000) por colonización del vacío; seguimiento hasta 500 ticks):
  - "ciega al nacer": el probe (mem=0, contexto real al nacer) la declara
    ciega ANTES de ejecutar. Predicción, no causa.
  - "1a ejecución": muere en su primer tick sin haber reescrito su código.
  - "auto-mutilación": muere tras k ≥ 1 reescrituras propias — la cría rompe
    la idempotencia de la madre y su propia reescritura la lleva a una forma
    ciega.
  - "reemplazada": su coordenada muere y es recolonizada el mismo tick.
  - "sobrevive": llega a 500 ticks.
  Madre = bomba/llanura según reescritura en los últimos 200 ticks.

HIPÓTESIS — escritas ANTES de mirar (criterio ≥2× entre 35 y 13):
  H1 Las crías de llanura de la 35 mueren sobre todo por AUTO-MUTILACIÓN, no
     en la primera ejecución ni por ceguera al nacer.
  H2 La fracción "ciega al nacer" NO distingue 13 de 35 (< 2×): el sondeo lo
     predice.
  H3 En la 13 las crías de llanura sobreviven ≥ 2× más que en la 35 (H8 ya lo
     mostró tras la ablación; aquí sin ablar).
  H4 Las crías que se auto-mutilan lo hacen en pocas reescrituras (mediana
     ≤ 3): la lesión es inmediata, no una deriva larga.
  H5 Diversidad: crías distintas / nacimientos (llanura) 13 ≥ 2× 35.
Además se reporta la agregación sobre las 40 semillas (sólo las que tienen
nacimientos en la ventana) para ver si el patrón de la 35 es el típico.

    PYTHONPATH=src python experiments/utero/exp_utero_mortalidad_infantil.py
"""

from __future__ import annotations

import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zeta_life.utero.creciente import UteroCreciente  # noqa: E402
from zeta_life.utero.nivel2 import PROBE_EPS, _output_only  # noqa: E402

N0, MAX_N = 16, 256
WIN = (8000, 9000)
FOLLOW = 500
TICKS = WIN[1] + FOLLOW
ACTIVE_WIN = 200
SEEDS = list(range(40))
DETAIL = (13, 35, 21)
CAUSES = ("1a ejecucion", "auto-mutilacion", "reemplazada", "sobrevive")
WORKERS = max(1, min(20, (os.cpu_count() or 4) - 4))
RESULTS = Path(__file__).resolve().parents[2] / "results"
NAME = "utero_mortalidad_infantil"


def _blind_now(u: UteroCreciente, i: int) -> bool:
    ctx, vl, vr = u._ctx(i)
    h = u._probe_hi
    v = float(u.v[i])
    out = _output_only(u.code[i], vl, v, vr, ctx, wrap=True, r3_init=0.0)
    p1 = _output_only(u.code[i], 0.0, 0.0, 0.0, ctx, wrap=True, r3_init=0.0)
    p2 = _output_only(u.code[i], h, h, h, ctx, wrap=True, r3_init=0.0)
    return bool(abs(out - p1) < PROBE_EPS and abs(out - p2) < PROBE_EPS
                and abs(p1 - p2) < PROBE_EPS)


def correr(seed: int, flags: dict | None = None) -> dict:
    u = UteroCreciente(n0=N0, seed=seed, max_n=MAX_N, germinal=True, toroidal=True,
                       memoria=True, log_events=True, **(flags or {}))
    last_code: dict = {}
    last_change: dict = {}
    children: dict = {}          # coord -> registro de la cría viva en esa coord
    done: list[dict] = []
    for t in range(TICKS):
        u.step()
        cg = {int(i) - u.left_grown: u.code[i].tobytes() for i in np.flatnonzero(u.alive)}
        born = {c: m for m, c in u.spawns}
        # 1) seguimiento de crías ya registradas
        for coord in list(children):
            rec = children[coord]
            if coord not in cg or coord in born:
                rec["cause"] = "reemplazada" if coord in born else (
                    "1a ejecucion" if rec["rewrites"] == 0 else "auto-mutilacion")
                rec["life"] = t - rec["t0"]
                done.append(children.pop(coord))
                continue
            if cg[coord] != rec["genome"]:
                rec["rewrites"] += 1
                rec["genome"] = cg[coord]
            if t - rec["t0"] >= FOLLOW:
                rec["cause"] = "sobrevive"
                rec["life"] = FOLLOW
                done.append(children.pop(coord))
        # 2) nuevas crías en la ventana
        if WIN[0] <= t < WIN[1]:
            for coord, mother in born.items():
                if coord not in cg:
                    continue            # nació y murió en el mismo tick (no ejecutó)
                i = coord + u.left_grown
                mplain = (t - last_change.get(mother, -10**9)) > ACTIVE_WIN
                children[coord] = dict(t0=t, genome=cg[coord], birth=cg[coord],
                                       rewrites=0, mother_plain=mplain,
                                       blind0=_blind_now(u, i))
        # 3) cambios de código (para clasificar madres)
        for coord, g in cg.items():
            if coord in last_code and last_code[coord] != g:
                last_change[coord] = t
        last_code = cg
    for rec in children.values():        # las que quedaron a medio seguimiento
        rec["cause"] = "sobrevive" if TICKS - rec["t0"] >= FOLLOW else "censurada"
        rec["life"] = TICKS - rec["t0"]
        done.append(rec)
    return {"seed": seed, "children": [d for d in done if d["cause"] != "censurada"]}


def resumen(children: list[dict], plain: bool | None) -> dict:
    sel = [c for c in children if plain is None or c["mother_plain"] == plain]
    n = len(sel)
    if n == 0:
        return {"n": 0}
    causes = {k: sum(1 for c in sel if c["cause"] == k) / n for k in CAUSES}
    muts = [c["rewrites"] for c in sel if c["cause"] == "auto-mutilacion"]
    return {"n": n, "blind0": sum(1 for c in sel if c["blind0"]) / n, **causes,
            "k_med": float(np.median(muts)) if muts else float("nan"),
            "distinct": len({c["birth"] for c in sel}) / n,
            "life_med": float(np.median([c["life"] for c in sel]))}


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("EL UTERO -- mortalidad infantil: de que mueren las crias de las llanuras?")
    out("=" * 80)
    out(f"memoria ON, sin invasion (v5); crias nacidas en {WIN}, seguidas {FOLLOW} ticks; "
        f"40 semillas; workers={WORKERS}")
    out("hipotesis H1..H5 y criterios en el docstring, escritos antes de correr")
    out("")
    res: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for r in ex.map(correr, SEEDS):
            res[r["seed"]] = r["children"]

    hdr = (f"  {'seed':>4} {'madre':<8} {'crias':>5} {'ciega0':>7} {'1a ejec':>8} "
           f"{'auto-mut':>9} {'k med':>6} {'reempl':>7} {'sobrev':>7} {'vida med':>8} {'distintas':>9}")

    def fila(tag, madre, s):
        if s["n"] == 0:
            return f"  {tag:>4} {madre:<8} {0:>5}"
        return (f"  {tag:>4} {madre:<8} {s['n']:>5} {100*s['blind0']:>6.0f}% {100*s['1a ejecucion']:>7.0f}% "
                f"{100*s['auto-mutilacion']:>8.0f}% {s['k_med']:>6.1f} {100*s['reemplazada']:>6.0f}% "
                f"{100*s['sobrevive']:>6.0f}% {s['life_med']:>8.0f} {100*s['distinct']:>8.0f}%")

    out("-" * 80)
    out("DETALLE 13 / 35 / 21 (madre = llanura o bomba)")
    out(hdr)
    S = {}
    for seed in DETAIL:
        for madre, plain in (("llanura", True), ("bomba", False)):
            S[(seed, madre)] = resumen(res[seed], plain)
            out(fila(seed, madre, S[(seed, madre)]))
    out("")
    out("AGREGADO 40 semillas (solo crias de LLANURA; semillas con >=10 nacimientos)")
    out(hdr.replace("seed", "   n"))
    agg = []
    per_seed = {}
    for seed in SEEDS:
        s = resumen(res[seed], True)
        if s["n"] >= 10:
            per_seed[seed] = s
            agg += [c for c in res[seed] if c["mother_plain"]]
    tot = resumen(agg, True)
    out(fila(len(per_seed), "llanura", tot))
    out(f"  semillas con >=10 crias de llanura en la ventana: {sorted(per_seed)}")
    surv = sorted(per_seed.items(), key=lambda kv: -kv[1]["sobrevive"])
    out("  sobrevivencia de crias de llanura por semilla (top 8): "
        + ", ".join(f"s{k}={100*v['sobrevive']:.0f}%" for k, v in surv[:8]))
    out("  auto-mutilacion por semilla (top 8): "
        + ", ".join(f"s{k}={100*v['auto-mutilacion']:.0f}%"
                    for k, v in sorted(per_seed.items(), key=lambda kv: -kv[1]['auto-mutilacion'])[:8]))

    # ---- hipótesis ----
    out("")
    out("=" * 80)
    out("HIPOTESIS (criterios pre-registrados)")
    a, b = S[(13, "llanura")], S[(35, "llanura")]

    def ok(x):
        return "SI" if x else "no"

    if a["n"] and b["n"]:
        h1 = b["auto-mutilacion"] >= max(b["1a ejecucion"], b["blind0"]) and b["auto-mutilacion"] > 0.5
        out(f"  H1 35-llanura muere por auto-mutilacion (>{50}% y mas que 1a ejec/ciega0): "
            f"auto-mut {100*b['auto-mutilacion']:.0f}%, 1a ejec {100*b['1a ejecucion']:.0f}%, "
            f"ciega0 {100*b['blind0']:.0f}% -> {ok(h1)}")
        r2 = max(a["blind0"], b["blind0"]) / max(min(a["blind0"], b["blind0"]), 1e-9)
        out(f"  H2 ciega-al-nacer NO distingue (<2x): 13 {100*a['blind0']:.0f}% vs 35 {100*b['blind0']:.0f}% "
            f"(ratio {r2:.1f}) -> {ok(r2 < 2 or max(a['blind0'], b['blind0']) < 0.05)}")
        r3 = a["sobrevive"] / max(b["sobrevive"], 1e-9)
        out(f"  H3 sobreviven 13 >= 2x 35: {100*a['sobrevive']:.0f}% vs {100*b['sobrevive']:.0f}% "
            f"(ratio {r3:.1f}) -> {ok(r3 >= 2)}")
        out(f"  H4 k mediana de la auto-mutilacion <= 3: 13 {a['k_med']:.1f}, 35 {b['k_med']:.1f} "
            f"-> {ok(np.nanmax([a['k_med'], b['k_med']]) <= 3)}")
        r5 = a["distinct"] / max(b["distinct"], 1e-9)
        out(f"  H5 diversidad de crias 13 >= 2x 35: {100*a['distinct']:.0f}% vs {100*b['distinct']:.0f}% "
            f"(ratio {r5:.1f}) -> {ok(r5 >= 2)}")
    else:
        out("  sin crias de llanura suficientes en 13 o 35 para evaluar H1-H5")

    # ---- figura ----
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    ax = axes[0]
    labels, mat = [], []
    for seed in DETAIL:
        for madre in ("llanura", "bomba"):
            s = S[(seed, madre)]
            if s["n"]:
                labels.append(f"{seed} {madre}\n(n={s['n']})")
                mat.append([s[k] for k in CAUSES])
    mat = np.array(mat) if mat else np.zeros((0, 4))
    bottom = np.zeros(len(labels))
    for j, k in enumerate(CAUSES):
        ax.bar(labels, mat[:, j], bottom=bottom, label=k)
        bottom += mat[:, j]
    ax.set_ylabel("fracción de crías")
    ax.set_title("destino de las crías por madre")
    ax.legend(fontsize=7)
    ax.tick_params(axis="x", labelsize=7)
    ax = axes[1]
    xs = [v["auto-mutilacion"] for v in per_seed.values()]
    ys = [v["sobrevive"] for v in per_seed.values()]
    ax.scatter(xs, ys, s=18)
    for k, v in per_seed.items():
        if k in DETAIL:
            ax.annotate(str(k), (v["auto-mutilacion"], v["sobrevive"]), fontsize=8, color="tab:red")
    ax.set_xlabel("crías de llanura que se auto-mutilan")
    ax.set_ylabel("crías de llanura que sobreviven 500 ticks")
    ax.set_title(f"{len(per_seed)} semillas con ≥10 crías de llanura")
    fig.suptitle("El Útero — mortalidad infantil")
    fig.tight_layout()
    RESULTS.mkdir(exist_ok=True)
    fig.savefig(RESULTS / f"{NAME}.png", dpi=110)
    out("")
    out(f"figura: results/{NAME}.png")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

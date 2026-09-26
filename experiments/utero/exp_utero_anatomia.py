"""
El Útero — anatomía comparada: ¿qué tiene la seed 13 que la 35 no?

La réplica en 40 semillas (exp_utero_memoria_semillas.py) dejó dos motores
maduros con memoria: la 13 se auto-repara tras la ablación de la bomba y la
35 —con un motor MAYOR— muere para siempre (vaciar 66/198 celdas → cola 0, el
hueco nunca se recoloniza). Este experimento disecciona ambas en el instante
de la ablación (t=8000, memoria ON, germinal+toroidal) y en los 4000 ticks
siguientes. La seed 0 (motor seco) va de referencia. n=2: lo que salga es
HIPÓTESIS para el próximo experimento, no conclusión.

HIPÓTESIS — escritas ANTES de mirar (cada una con su medida):
  H1 geometría. La 13 tiene una bomba LOCALIZADA con llanuras asentadas a los
     lados (sustrato, lección de v4); la 35 tiene la turbulencia difusa.
     Medida: nº de segmentos activos, fracción activa, llanura mayor.
  H2 reservorio lento. La 13 tiene reescritores LENTOS (última reescritura en
     200..2000 ticks) que la ablación (ventana 200) no toca y que pueden
     re-nuclear; la 35 es de un solo tempo (todo lo que reescribe es rápido).
     Medida: fracción de vivas con última reescritura en (200, 2000].
  H3 capacidad de los sobrevivientes. Los que quedan vivos en la 13 portan
     SPAWN (recolonizar) y MUTO/COPY (reescribir); los de la 35 son inertes.
     Medida: fracción de sobrevivientes con cada op en su código.
  H4 recolonización. En la 13 el hueco se recoloniza (SPAWN) y la turbulencia
     renace en su borde; en la 35 nadie coloniza. Medida: colonizaciones en
     los primeros 1000 ticks, vivas en +1/+500/+4000, y dónde ocurren las
     primeras 100 reescrituras post-ablación (borde del hueco / dentro / lejos).
  H5 especificidad y dosis. Si la 35 sobrevive a una ablación ALEATORIA del
     mismo tamaño pero no a la de la bomba, lo que la mata es perder la bomba;
     si muere a ambas, es fragilidad global. Ventanas 50/100/200/400 miden si
     hay una dosis que la 13 no aguante o que la 35 sí aguante.
  H6 potencial de los sobrevivientes (la explicación de v5). El borde del hueco
     en la 13 guarda potencial interno |mem| grande; en la 35 no.
     Medida: mediana de |mem| y fracción |mem|>1 en las celdas del borde.
CRITERIO para decir que una medida "distingue": difiere ≥2× entre 13 y 35 (y
en la dirección predicha). Todo lo que distinga es PREDICCIÓN a testear.

POST-HOC (añadido tras la primera corrida, marcado como tal): H1–H3 y H6 no
distinguieron; H4 mostró que en la 35 el hueco se coloniza 6× más y las vivas
no suben, y que NINGUNA llanura de la 35 reescribe tras la ablación aunque
todas portan MUTO/COPY. Una prueba aparte refutó que fuera la memoria (la
física de las llanuras pasa la sonda también con mem=0). Se añaden entonces:
  H7 plasticidad EFECTIVA de las llanuras: ejecutar cada llanura con su
     contexto real y con un vecino vaciado (lo que ve el borde del hueco):
     ¿cambia su código? Predicción: la 13 sí, la 35 no (ops latentes, inertes).
  H8 destino de las crías nacidas en los 1000 ticks post-ablación: cuántas,
     cuántos genomas DISTINTOS al nacer (¿misma cría, parto tras parto? — la
     jaula de v2), y su vida (mediana, fracción que llega a 100 ticks).

    PYTHONPATH=src python experiments/utero/exp_utero_anatomia.py
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

from zeta_life.utero.ablacion import ACTIVE_WIN, medir_cola  # noqa: E402
from zeta_life.utero.creciente import UteroCreciente  # noqa: E402
from zeta_life.utero.nivel2 import COPY, MUTO, SPAWN, execute  # noqa: E402

N0, MAX_N = 16, 256
T_ABL, POST = 8000, 4000
TOTAL = T_ABL + POST
REC_FROM = 6000                  # desde cuándo se guardan las series por celda
OFFSET, W = 256, 512             # coordenada -> columna del kimógrafo
SLOW_LO, SLOW_HI = ACTIVE_WIN, 2000
SEEDS_MAIN = (13, 35)
SEED_REF = 0
WINS = (50, 100, 200, 400)
RANDOM_REPS = (0, 1, 2)
FIRST_N = 100
WORKERS = max(1, min(20, (os.cpu_count() or 4) - 4))
RESULTS = Path(__file__).resolve().parents[2] / "results"
NAME = "utero_anatomia"


def _vaciar(u: UteroCreciente, idx: int) -> None:
    u.alive[idx] = False
    u.v[idx] = 0.0
    u.code[idx] = 0
    u.eq_count[idx] = 0
    u.mem[idx] = 0.0


def _ablar(u: UteroCreciente, spec: tuple, last_change: dict, t: int) -> list:
    """spec = ('pump', win) | ('random', n, k). Devuelve las coords vaciadas."""
    if spec[0] == "pump":
        coords = [c for c, tc in last_change.items() if t - tc <= spec[1]]
    else:
        alive = [int(i) - u.left_grown for i in np.flatnonzero(u.alive)]
        rng = np.random.default_rng(1000 + spec[2])
        coords = list(rng.choice(alive, size=min(spec[1], len(alive)),
                                 replace=False))
    done = []
    for c in coords:
        i = int(c) + u.left_grown
        if 0 <= i < u.n and u.alive[i]:
            _vaciar(u, i)
            done.append(int(c))
    return done


def _snapshot(u: UteroCreciente, last_change: dict, t: int) -> dict:
    idx = np.flatnonzero(u.alive)
    coords = idx - u.left_grown
    return {"coords": coords, "code": u.code[idx].copy(), "mem": u.mem[idx].copy(),
            "last": np.array([t - last_change.get(int(c), -10**9) for c in coords])}


def _plasticidad(u: UteroCreciente, last_change: dict, t: int) -> dict:
    """H7/H8 (post-hoc): plasticidad EFECTIVA y descendencia de las llanuras.

    Para cada llanura (viva, sin reescritura en ACTIVE_WIN): ¿su código cambia
    al ejecutarse con su contexto real? ¿y con un vecino vaciado (lo que ve una
    celda del borde del hueco)? ¿qué cría pariría ahora mismo?"""
    now = void = spawning = 0
    children: list[bytes] = []
    n = 0
    for i in np.flatnonzero(u.alive):
        c = int(i) - u.left_grown
        if t - last_change.get(c, -10**9) <= ACTIVE_WIN:
            continue
        n += 1
        ctx, vl, vr = u._ctx(i)
        mi = float(u.mem[i])
        _, own, spawn, _ = execute(u.code[i], vl, float(u.v[i]), vr, ctx,
                                   wrap=True, r3_init=mi)
        now += int(not np.array_equal(own, u.code[i]))
        changed = False
        for ctx_v, vl_v, vr_v in (((None, ctx[1], ctx[2]), 0.0, vr),
                                  ((ctx[0], ctx[1], None), vl, 0.0)):
            _, own_v, _, _ = execute(u.code[i], vl_v, float(u.v[i]), vr_v, ctx_v,
                                     wrap=True, r3_init=mi)
            changed |= not np.array_equal(own_v, u.code[i])
        void += int(changed)
        if spawn is not None:
            spawning += 1
            _, mpos, mop = spawn
            child = own.copy()
            child[mpos, 0] = mop
            children.append(child.tobytes())
    return {"n_plains": n, "frac_change_now": now / max(n, 1),
            "frac_change_void": void / max(n, 1), "frac_spawning": spawning / max(n, 1),
            "distinct_children": len(set(children)), "n_children": len(children)}


def correr(seed: int, spec: tuple | None) -> dict:
    """Corrida instrumentada: kimógrafos (cambio de código, vivas, novedad),
    series por tick, snapshot en t_abl y la ablación `spec` (None = sin)."""
    u = UteroCreciente(n0=N0, seed=seed, max_n=MAX_N, germinal=True,
                       toroidal=True, memoria=True)
    seen: set = set(u.seen)
    last_code: dict = {}
    last_change: dict = {}
    nrec = TOTAL - REC_FROM
    kymo_chg = np.zeros((nrec, W), dtype=bool)
    kymo_alive = np.zeros((nrec, W), dtype=bool)
    kymo_new = np.zeros((nrec, W), dtype=bool)
    novedad = np.zeros(TOTAL, dtype=np.int64)
    vivas = np.zeros(TOTAL, dtype=np.int64)
    colonized = np.zeros(TOTAL, dtype=np.int64)
    snap, ablated, plast = None, [], None
    prev_alive: set = set()
    born_at: dict = {}
    birth_genomes: list[bytes] = []
    lifetimes: list[int] = []
    for t in range(TOTAL):
        m = u.step()
        colonized[t] = m["colonized"]
        cg = {int(i) - u.left_grown: u.code[i].tobytes() for i in np.flatnonzero(u.alive)}
        new = 0
        r = t - REC_FROM
        # H8: nacimientos en (T_ABL, T_ABL+1000] y su vida (muertes hasta el final)
        if t > T_ABL:
            cur_alive = set(cg)
            for c in prev_alive - cur_alive:
                if c in born_at:
                    lifetimes.append(t - born_at.pop(c))
            if t <= T_ABL + 1000:
                for c in cur_alive - prev_alive:
                    born_at[c] = t
                    birth_genomes.append(cg[c])
        prev_alive = set(cg)
        for coord, g in cg.items():
            col = coord + OFFSET
            if r >= 0:
                kymo_alive[r, col] = True
            if g not in seen:
                seen.add(g)
                new += 1
                if r >= 0:
                    kymo_new[r, col] = True
            if coord in last_code and last_code[coord] != g:
                last_change[coord] = t
                if r >= 0:
                    kymo_chg[r, col] = True
        last_code = cg
        novedad[t] = new
        if t == T_ABL:
            snap = _snapshot(u, last_change, t)
            plast = _plasticidad(u, last_change, t)
            if spec is not None:
                ablated = _ablar(u, spec, last_change, t)
                last_code = {int(i) - u.left_grown: u.code[i].tobytes()
                             for i in np.flatnonzero(u.alive)}
                prev_alive = set(last_code)
        vivas[t] = int(u.alive.sum())
    censored = len(born_at)      # crías todavía vivas al final
    return {"seed": seed, "spec": spec, "kymo_chg": kymo_chg, "kymo_alive": kymo_alive,
            "kymo_new": kymo_new, "novedad": novedad, "vivas": vivas,
            "colonized": colonized, "snap": snap, "ablated": np.array(ablated, dtype=int),
            "plast": plast, "births": len(birth_genomes),
            "birth_distinct": len(set(birth_genomes)),
            "lifetimes": np.array(lifetimes + [POST] * censored), "censored": censored}


def job(args: tuple) -> dict:
    return correr(*args)


# ------------------------------------------------------------------ análisis
def _segments(mask: np.ndarray) -> list[int]:
    """Largos de los tramos contiguos True."""
    out, run = [], 0
    for m in mask:
        if m:
            run += 1
        elif run:
            out.append(run)
            run = 0
    if run:
        out.append(run)
    return out


def anatomia(res: dict) -> dict:
    """H1, H2, H3, H6 sobre el snapshot en t_abl (antes de ablar)."""
    s = res["snap"]
    coords, code, mem, last = s["coords"], s["code"], s["mem"], s["last"]
    lo, hi = coords.min(), coords.max()
    alive_line = np.zeros(hi - lo + 1, dtype=bool)
    active_line = np.zeros_like(alive_line)
    alive_line[coords - lo] = True
    active = last <= ACTIVE_WIN
    active_line[coords[active] - lo] = True
    plains = _segments(alive_line & ~active_line)
    slow = (last > SLOW_LO) & (last <= SLOW_HI)
    surv = ~active
    ops = code[:, :, 0]

    def frac_with(op: int, sel: np.ndarray) -> float:
        return float((ops[sel] == op).any(axis=1).mean()) if sel.any() else float("nan")

    ablated_set = set(coords[active].tolist())
    border = np.array([(not a) and ((c - 1 in ablated_set) or (c + 1 in ablated_set))
                       for c, a in zip(coords, active)])
    return {
        "n_alive": int(len(coords)), "n_active": int(active.sum()),
        "frac_active": float(active.mean()),
        "n_segments": len(_segments(active_line)),
        "largest_segment": max(_segments(active_line) or [0]),
        "largest_plain": max(plains or [0]),
        "touches_border": bool(active_line[0] or active_line[-1]),
        "frac_slow": float(slow.mean()),
        "surv_spawn": frac_with(SPAWN, surv), "surv_rewrite": float(
            ((ops[surv] == MUTO) | (ops[surv] == COPY)).any(axis=1).mean()) if surv.any() else float("nan"),
        "pump_spawn": frac_with(SPAWN, active), "pump_rewrite": float(
            ((ops[active] == MUTO) | (ops[active] == COPY)).any(axis=1).mean()) if active.any() else float("nan"),
        "surv_genomes": len({code[i].tobytes() for i in np.flatnonzero(surv)}),
        "n_border": int(border.sum()),
        "border_mem_med": float(np.median(np.abs(mem[border]))) if border.any() else float("nan"),
        "border_mem_gt1": float((np.abs(mem[border]) > 1).mean()) if border.any() else float("nan"),
        "all_mem_med": float(np.median(np.abs(mem))),
    }


def recolonizacion(res: dict) -> dict:
    """H4 sobre la corrida con ablación de bomba (win 200)."""
    abl = set(res["ablated"].tolist())
    t0 = T_ABL - REC_FROM
    chg = res["kymo_chg"][t0 + 1:]
    ts, cols = np.nonzero(chg)
    where = {"borde": 0, "hueco": 0, "lejos": 0}
    for c in (cols[:FIRST_N] - OFFSET):
        if c in abl:
            where["hueco"] += 1
        elif (c - 1 in abl) or (c + 1 in abl):
            where["borde"] += 1
        else:
            where["lejos"] += 1
    v = res["vivas"]
    return {"n_abl": len(abl), "colon_1000": int(res["colonized"][T_ABL + 1:T_ABL + 1001].sum()),
            "vivas_pre": int(v[T_ABL - 1]), "vivas_1": int(v[T_ABL + 1]),
            "vivas_500": int(v[T_ABL + 500]), "vivas_fin": int(v[-1]),
            "first_n": len(cols[:FIRST_N]), "where": where,
            "t_first": int(ts[0]) + 1 if len(ts) else -1}


def dosis(runs: dict, seed: int) -> list[tuple]:
    base = runs[(seed, None)]["novedad"]
    _, _, tail_base = medir_cola(base, T_ABL)
    rows = []
    for spec in [("pump", w) for w in WINS] + [("random", None, k) for k in RANDOM_REPS]:
        key = (seed, spec) if spec[0] == "pump" else (seed, ("random", runs["n_rand"][seed], spec[2]))
        r = runs[key]
        pre, pulse, tail = medir_cola(r["novedad"], T_ABL)
        rows.append((key[1], len(r["ablated"]), pre, pulse, tail, tail / max(tail_base, 1.0)))
    return rows


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 78)
    out("EL UTERO -- anatomia comparada: que tiene la seed 13 que la 35 no?")
    out("=" * 78)
    out(f"memoria ON, germinal+toroidal, ablacion en t={T_ABL}, post={POST}, workers={WORKERS}")
    out("hipotesis H1..H6 y criterio (>=2x) escritos en el docstring ANTES de correr")
    out("")

    # el tamaño de la ablación aleatoria = tamaño de la ablación de bomba (win 200)
    first = [(s, ("pump", ACTIVE_WIN)) for s in (*SEEDS_MAIN, SEED_REF)]
    first += [(s, None) for s in (*SEEDS_MAIN, SEED_REF)]
    runs: dict = {"n_rand": {}}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for r in ex.map(job, first):
            runs[(r["seed"], r["spec"])] = r
        for s in SEEDS_MAIN:
            runs["n_rand"][s] = len(runs[(s, ("pump", ACTIVE_WIN))]["ablated"])
        second = [(s, ("pump", w)) for s in SEEDS_MAIN for w in WINS if w != ACTIVE_WIN]
        second += [(s, ("random", runs["n_rand"][s], k)) for s in SEEDS_MAIN for k in RANDOM_REPS]
        for r in ex.map(job, second):
            runs[(r["seed"], r["spec"])] = r

    # ---- H1 H2 H3 H6: anatomía en el instante de la ablación ----
    an = {s: anatomia(runs[(s, None)]) for s in (*SEEDS_MAIN, SEED_REF)}
    out("-" * 78)
    out(f"ANATOMIA EN t={T_ABL} (antes de ablar)          seed 13     seed 35   ref seed 0")
    labels = [("vivas", "n_alive", "d"), ("activas (<=200)", "n_active", "d"),
              ("H1 fraccion activa", "frac_active", ".2f"),
              ("H1 segmentos activos", "n_segments", "d"),
              ("H1 segmento activo mayor", "largest_segment", "d"),
              ("H1 llanura mayor (viva, inactiva)", "largest_plain", "d"),
              ("H1 bomba toca el borde del mundo", "touches_border", ""),
              ("H2 frac. lentas (200<ultima<=2000)", "frac_slow", ".2f"),
              ("H3 sobreviv. con SPAWN", "surv_spawn", ".2f"),
              ("H3 sobreviv. con MUTO/COPY", "surv_rewrite", ".2f"),
              ("   bomba con SPAWN", "pump_spawn", ".2f"),
              ("   bomba con MUTO/COPY", "pump_rewrite", ".2f"),
              ("H3 genomas distintos entre sobreviv.", "surv_genomes", "d"),
              ("H6 celdas de borde del hueco", "n_border", "d"),
              ("H6 |mem| mediana en el borde", "border_mem_med", ".3f"),
              ("H6 frac |mem|>1 en el borde", "border_mem_gt1", ".2f"),
              ("   |mem| mediana global", "all_mem_med", ".3f")]
    for lab, key, fmt in labels:
        vals = [an[s][key] for s in (*SEEDS_MAIN, SEED_REF)]
        cells = [f"{v:>11{fmt}}" if fmt else f"{str(v):>11}" for v in vals]
        out(f"  {lab:<38}" + " ".join(cells))

    # ---- H4: recolonización tras la ablación de bomba ----
    out("")
    out("-" * 78)
    out("H4 RECOLONIZACION tras ablar la bomba (win 200)")
    rec = {s: recolonizacion(runs[(s, ("pump", ACTIVE_WIN))]) for s in (*SEEDS_MAIN, SEED_REF)}
    out(f"  {'seed':>4} {'abl':>4} {'vivas pre':>9} {'+1':>5} {'+500':>5} {'fin':>5} "
        f"{'colon<=1000':>11} {'1a reescr.':>10} {'primeras 100: borde/hueco/lejos':>32}")
    for s in (*SEEDS_MAIN, SEED_REF):
        r = rec[s]
        w = r["where"]
        out(f"  {s:>4} {r['n_abl']:>4} {r['vivas_pre']:>9} {r['vivas_1']:>5} {r['vivas_500']:>5} "
            f"{r['vivas_fin']:>5} {r['colon_1000']:>11} {r['t_first']:>10} "
            f"{w['borde']:>10}/{w['hueco']:>5}/{w['lejos']:>5}  (n={r['first_n']})")

    # ---- H5: dosis y especificidad ----
    out("")
    out("-" * 78)
    out("H5 DOSIS Y ESPECIFICIDAD (R = cola ablada / cola sin ablar; R>=0.5 = se reparo)")
    for s in SEEDS_MAIN:
        out(f"  seed {s}:  {'ablacion':<22} {'abl':>4} {'pre':>6} {'pulso':>6} {'cola':>6} {'R':>6}")
        for spec, n_abl, pre, pulse, tail, R in dosis(runs, s):
            name = f"bomba win={spec[1]}" if spec[0] == "pump" else f"aleatoria n={spec[1]} k={spec[2]}"
            out(f"           {name:<22} {n_abl:>4} {pre:>6.0f} {pulse:>6} {tail:>6.0f} {R:>6.2f}")

    # ---- H7 / H8 (post-hoc) ----
    out("")
    out("-" * 78)
    out("H7 [POST-HOC] PLASTICIDAD EFECTIVA DE LAS LLANURAS en t=8000 (todas portan MUTO/COPY)")
    out(f"  {'seed':>4} {'llanuras':>8} {'cambia ctx real':>15} {'cambia vecino vacio':>19} "
        f"{'paren':>6} {'crias distintas/parideras':>25}")
    pl = {s: runs[(s, None)]["plast"] for s in (*SEEDS_MAIN, SEED_REF)}
    for s in (*SEEDS_MAIN, SEED_REF):
        p = pl[s]
        out(f"  {s:>4} {p['n_plains']:>8} {p['frac_change_now']:>15.2f} "
            f"{p['frac_change_void']:>19.2f} {p['frac_spawning']:>6.2f} "
            f"{p['distinct_children']:>12}/{p['n_children']:<12}")
    out("")
    out("H8 [POST-HOC] DESTINO DE LAS CRIAS nacidas en los 1000 ticks tras la ablacion")
    out("   (control = misma ventana SIN ablar: el churn natural)")
    out(f"  {'seed':>4} {'ablacion':<9} {'nacim.':>7} {'genomas':>8} {'vida med':>9} "
        f"{'>=10':>6} {'>=100':>6} {'vivas al fin':>12}")
    h8 = {}
    for s in (*SEEDS_MAIN, SEED_REF):
        for spec, lab in ((("pump", ACTIVE_WIN), "bomba"), (None, "sin")):
            r = runs[(s, spec)]
            lt = r["lifetimes"]
            row = dict(births=r["births"], distinct=r["birth_distinct"],
                       med=float(np.median(lt)) if len(lt) else float("nan"),
                       ge10=float((lt >= 10).mean()) if len(lt) else float("nan"),
                       ge100=float((lt >= 100).mean()) if len(lt) else float("nan"),
                       cens=r["censored"])
            h8[(s, lab)] = row
            out(f"  {s:>4} {lab:<9} {row['births']:>7} {row['distinct']:>8} {row['med']:>9.0f} "
                f"{row['ge10']:>6.2f} {row['ge100']:>6.2f} {row['cens']:>12}")

    # ---- qué distingue (criterio >=2x en la dirección predicha) ----
    out("")
    out("=" * 78)
    out("QUE DISTINGUE (>=2x entre 13 y 35, direccion predicha; n=2 => PREDICCIONES)")
    a13, a35 = an[13], an[35]

    def ratio(k: str, invert: bool = False) -> float:
        x, y = a13[k], a35[k]
        if invert:
            x, y = y, x
        return x / y if y else (float("inf") if x else 1.0)

    checks = [("H1 llanura mayor 13 > 35", ratio("largest_plain")),
              ("H1 fraccion activa 35 > 13", ratio("frac_active", invert=True)),
              ("H2 frac. lentas 13 > 35", ratio("frac_slow")),
              ("H3 sobreviv. con SPAWN 13 > 35", ratio("surv_spawn")),
              ("H3 sobreviv. con MUTO/COPY 13 > 35", ratio("surv_rewrite")),
              ("H6 |mem| borde 13 > 35", ratio("border_mem_med"))]
    r13, r35 = rec[13], rec[35]
    checks.append(("H4 colonizaciones<=1000 13 > 35",
                   r13["colon_1000"] / max(r35["colon_1000"], 1)))
    p13, p35 = pl[13], pl[35]
    b13, b35 = h8[(13, "bomba")], h8[(35, "bomba")]
    checks += [("H7 llanuras que cambian con vecino vacio 13 > 35",
                p13["frac_change_void"] / max(p35["frac_change_void"], 1e-9)),
               ("H8 diversidad de crias (distintas/nacim.) 13 > 35",
                (p13["distinct_children"] / max(p13["n_children"], 1))
                / max(p35["distinct_children"] / max(p35["n_children"], 1), 1e-9)),
               ("H8 crias que llegan a 100 ticks 13 > 35",
                b13["ge100"] / max(b35["ge100"], 1e-9))]
    for lab, rt in checks:
        out(f"  {'SI ' if rt >= 2 else 'no '} {lab:<50} ratio={rt:.2f}")
    d35 = {spec: R for spec, *_, R in dosis(runs, 35)}
    rand_ok = [R >= 0.5 for spec, R in d35.items() if spec[0] == "random"]
    pump_ok = d35[("pump", ACTIVE_WIN)] >= 0.5
    if all(rand_ok) and not pump_ok:
        out("  SI  H5 la 35 sobrevive a la ablacion ALEATORIA y muere a la de BOMBA:")
        out("      lo que la mata es perder la bomba, no perder celdas.")
    elif not any(rand_ok):
        out("  --  H5 la 35 muere tambien a la ablacion aleatoria: fragilidad GLOBAL,")
        out("      no especifica de la bomba.")
    else:
        out(f"  ?   H5 mixto: aleatoria {sum(rand_ok)}/{len(rand_ok)} sobreviven, bomba {pump_ok}")

    # ---- figura: kimógrafos 13 vs 35 alrededor de la ablación ----
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), gridspec_kw={"width_ratios": [3, 1]})
    for row, s in enumerate(SEEDS_MAIN):
        r = runs[(s, ("pump", ACTIVE_WIN))]
        t0, t1 = T_ABL - 1000 - REC_FROM, TOTAL - REC_FROM
        alive = r["kymo_alive"][t0:t1]
        cols = np.flatnonzero(alive.any(axis=0))
        c0, c1 = cols.min(), cols.max() + 1
        img = np.zeros(alive[:, c0:c1].shape + (3,))
        img[alive[:, c0:c1]] = (0.82, 0.82, 0.82)
        img[r["kymo_chg"][t0:t1, c0:c1]] = (0.1, 0.1, 0.1)
        img[r["kymo_new"][t0:t1, c0:c1]] = (0.85, 0.1, 0.1)
        ax = axes[row, 0]
        ax.imshow(img.transpose(1, 0, 2), aspect="auto", interpolation="nearest",
                  extent=[T_ABL - 1000, TOTAL, c1 - OFFSET, c0 - OFFSET])
        ax.axvline(T_ABL, color="tab:blue", ls=":", lw=1.5)
        ax.set_title(f"seed {s} — gris=viva, negro=reescribe, rojo=genoma nuevo; azul=ablación")
        ax.set_ylabel("coordenada")
        ax2 = axes[row, 1]
        ts = np.arange(T_ABL - 1000, TOTAL)
        ax2.plot(ts, r["vivas"][T_ABL - 1000:], color="k", label="vivas")
        ax2.plot(ts, np.convolve(r["colonized"][T_ABL - 1000:], np.ones(50), "same"),
                 color="tab:green", label="colonizaciones/50 ticks")
        ax2.axvline(T_ABL, color="tab:blue", ls=":")
        ax2.legend(fontsize=7)
        ax2.set_title("H4 recolonización")
    axes[1, 0].set_xlabel("tick")
    axes[1, 1].set_xlabel("tick")
    fig.suptitle("El Útero — anatomía comparada 13 vs 35 alrededor de la ablación de la bomba")
    fig.tight_layout()
    RESULTS.mkdir(exist_ok=True)
    fig.savefig(RESULTS / f"{NAME}.png", dpi=110)
    out("")
    out(f"figura: results/{NAME}.png")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

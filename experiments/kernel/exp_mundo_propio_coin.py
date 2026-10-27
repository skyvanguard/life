"""
§K6 -- a ROBUST repertoire of the world: does a COIN-style world model (one expert
per inferred context, a new expert for what no known one explains, each sleeping on
its own life) keep the known regimes through a never-seen one?
(docs/MUNDO_PROPIO.md; DRAFT -- the pre-registration is written after the
calibration and before any run on the test seeds)

WHY. §K3 gave the kernel a repertoire (seeing its own error, with 4x sleep, the
world model infers which regime it is in: REPERTORIO 12/12 in part 2) that did not
replicate by the letter (8/12). Post hoc, the reason: the single NOVEL visit
overwrites the known regimes (probe ratio to the exact average 0.47/0.36 at the end
of cycle 6 -> 1.06/1.07 at the end of the NOVEL visit) and sleep needs ~2 cycles to
rebuild them, so the cycle 7-8 reading falls mid-recovery. COIN (Heald, Lengyel &
Wolpert 2021) avoids that interference by creating a new memory for a new context.

THE CHANGE. coin = error_x4 (the §K3 kernel: wm_error_input + 4 x sleep) with
ConsciousKernel(wm_contexts=6): src/zeta_life/kernel/contextual_world_model.py
(tests/test_contextual_world_model.py). The world, the calendar, the test ticks,
the probe sequences, the readouts and the §K1 rule are §K3's. The error_x4 lives
(§K3) and kernel / secuencia / congelado / reactivo lives (§K2) are READ from disk.
Declared: the coin kernel allocates 6 experts at birth, so its initial weights and
its later random draws differ from error_x4's on the same seed (paired by seed, not
byte-shared).

THE PROBE with contexts: every expert in use runs its own recurrence over each probe
sequence; per sequence, step j is predicted by the expert with the lowest mean error
over steps < j (the active one at step 0) -- the regime inferred from the first
ticks, as the single GRU does with its latent. With one expert it is §K3's probe.
Reported also: the ORACLE probe (per sequence the best expert after the burn-in),
whether a right expert exists even when the selection misses it.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_coin.py humo
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_coin.py calibracion
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("mundo_propio_contexto", HERE / "exp_mundo_propio_contexto.py")
cx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cx)
ms, mp = cx.ms, cx.mp

RESULTS = ROOT / "results"
DATA = ROOT / "data" / "mundo_propio_coin"
SEEDS = mp.SEEDS
SEEDS_CAL = cx.SEEDS_CAL
N_OK = mp.N_OK
D = mp.D
CONTEXTOS = 6
BRAZOS = {"coin": {**cx.BRAZOS["error_x4"], "wm_contexts": CONTEXTOS},
          "error_x4": cx.BRAZOS["error_x4"]}
EVENTO = {"switch": 1, "spawn": 2}


def errores_sonda(wm, obs, a) -> np.ndarray:
    """Per step and per sequence (L, M) error of one world model on a probe: the §K3
    recurrence (with the error input, zero at the start). Read-only."""
    import torch
    b = wm.posterior_blend
    errs = []
    with torch.no_grad():
        z = wm.encoder(obs[:, 0])
        err = torch.zeros_like(obs[:, 0]) if wm.error_input else None
        for j in range(a.shape[1]):
            prior = wm.transition(wm._transition_input(a[:, j], None, err), z)
            pred = wm.predictor(prior)
            errs.append(torch.linalg.vector_norm(pred - obs[:, j + 1], dim=-1))
            if err is not None:
                err = obs[:, j + 1] - pred
            z = b * prior + (1.0 - b) * wm.encoder(obs[:, j + 1])
    return torch.stack(errs).numpy()


def sonda_ctx(wm, obs, a) -> tuple[float, float, float]:
    """(error after the burn-in, during it, oracle after it) with context inference over
    the experts in use; a plain WorldModel is one expert (= §K3's probe)."""
    expertos = list(wm.experts[: wm.in_use]) if hasattr(wm, "experts") else [wm]
    activo = wm.active if hasattr(wm, "experts") else 0
    E = np.stack([errores_sonda(x, obs, a) for x in expertos])  # (C, L, M)
    C, L, M = E.shape
    sel = np.empty((L, M))
    acum = np.zeros((C, M))
    for j in range(L):
        elige = np.full(M, activo) if j == 0 else np.argmin(acum, axis=0)
        sel[j] = E[elige, j, np.arange(M)]
        acum += E[:, j]
    q = ms.QUEMA
    return float(sel[q:].mean()), float(sel[:q].mean()), float(E[:, q:].mean(axis=1).min(axis=0).mean())


def vivir(args: tuple[str, int]) -> dict:
    """One life: the loop of exp_mundo_propio_contexto.vivir (acting, test ticks) with the
    arm's kernel, plus the active context per tick and the context events."""
    import torch

    from zeta_life.kernel import ConsciousKernel
    brazo, seed = args
    t0 = time.time()
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    vis = mp.calendario(seed)
    tipo, a_test, a_babble = mp.pruebas(seed, vis)
    n = len(vis) * D
    pref = torch.tensor(mp.C)
    k = ConsciousKernel(obs_dim=4, action_mode="efe", preference=pref, efe_n_samples=48,
                        efe_obs_norm="l1", **BRAZOS[brazo])
    probes = ms.sondas()
    s = torch.full((4,), 0.25)
    dist, psi, fe = np.empty(n), np.empty(n), np.empty(n)
    ctx = np.zeros(n, dtype=np.int8)
    sonda, sonda0, oraculo = (np.empty((len(vis), 4)) for _ in range(3))
    for t in range(n):
        fase, reg, _ = vis[t // D]
        r = k.step(s)
        dist[t] = float(torch.linalg.vector_norm(s - pref))
        psi[t], fe[t] = r.psi, r.free_energy
        ctx[t] = getattr(k.world_model, "active", 0)
        if fase == "babble":
            a = torch.tensor(a_babble[t], dtype=torch.float32)
            k.last_action = a
        elif tipo[t]:
            a = torch.tensor(a_test[t], dtype=torch.float32)
            if tipo[t] == 1:
                k.last_action = a
        else:
            a = r.action.detach()
        s = ((1 - mp.R) * s + mp.R * torch.roll(a, reg)).clamp(min=1e-6)
        s = s / s.sum()
        if t % D == D - 1:
            v = t // D
            for kk in range(4):
                sonda[v, kk], sonda0[v, kk], oraculo[v, kk] = sonda_ctx(k.world_model, *probes[kk])
    ev = np.array([(EVENTO[e], t, c) for e, t, c in getattr(k.world_model, "events", [])],
                  dtype=int).reshape(-1, 3)
    vida = {"dist": dist, "psi": psi, "fe": fe, "tipo": tipo, "sonda": sonda, "sonda0": sonda0,
            "oraculo": oraculo, "ctx": ctx, "eventos": ev}
    DATA.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(DATA / f"{brazo}_{seed}.npz", **vida)
    return {"brazo": brazo, "seed": seed, "min": (time.time() - t0) / 60, **vida}


def correr(arms: tuple, seeds: tuple) -> dict:
    with ProcessPoolExecutor(max_workers=cx.WORKERS) as pool:
        vidas = list(pool.map(vivir, itertools.product(arms, seeds)))
    return {(x["brazo"], x["seed"]): x for x in vidas}


def visita(seed: int, ciclo: int) -> list[int]:
    return [v for v, (_, _, c) in enumerate(mp.calendario(seed)) if c == ciclo]


def cociente_nuevo(vida: dict, seed: int) -> float:
    """Known-regime probe at the end of the NOVEL visit / the exact average (§K3: 1.06)."""
    conocidos = [k for k in range(4) if k != seed % 4]
    return float(vida["sonda"][visita(seed, 0)[0], conocidos].mean() / ms.ref_promedio(seed))


def pureza(vida: dict, seed: int) -> dict:
    """Context bookkeeping: experts in use, the majority expert of each regime over its
    acting ticks after the first 50 of each visit and its share, and whether the NOVEL
    regime's majority expert is none of the known regimes'."""
    vis = mp.calendario(seed)
    por_reg: dict[int, list[int]] = {}
    for v, (fase, reg, _) in enumerate(vis):
        if fase == "act":
            por_reg.setdefault(reg, []).extend(vida["ctx"][v * D + 50: (v + 1) * D].tolist())
    mayor = {r: int(np.bincount(c).argmax()) for r, c in por_reg.items()}
    share = {r: float(np.mean(np.array(c) == mayor[r])) for r, c in por_reg.items()}
    nuevo = seed % 4
    return {"en_uso": int(vida["ctx"].max()) + 1, "mayor": mayor, "share": share,
            "nuevo_propio": mayor[nuevo] not in [mayor[r] for r in mayor if r != nuevo]}


def main_humo() -> None:
    """Short check: with one expert the context probe equals §K3's; a coin kernel runs a
    few visits and spawns."""
    import torch

    from zeta_life.kernel import ConsciousKernel
    torch.set_num_threads(1)
    torch.manual_seed(0)
    k = ConsciousKernel(obs_dim=4, action_mode="efe", preference=torch.tensor(mp.C), efe_n_samples=48,
                        efe_obs_norm="l1", **cx.BRAZOS["error_x4"])
    probes = ms.sondas()
    s = torch.full((4,), 0.25)
    for _ in range(150):
        s = ms.mover(s, k.step(s).action.detach(), 1)
    for kk in range(4):
        a, b = cx.error_sonda(k.world_model, *probes[kk]), sonda_ctx(k.world_model, *probes[kk])[:2]
        print(f"regime {kk}: §K3 probe {a[0]:.6f}/{a[1]:.6f}  context probe {b[0]:.6f}/{b[1]:.6f}  "
              f"max diff {max(abs(a[0] - b[0]), abs(a[1] - b[1])):.2e}")


def main_calibracion() -> None:
    """Seeds 100-102 (never test seeds), the acting §K3 life, coin and error_x4: does the
    mechanism keep the known regimes through the NOVEL visit? Nothing tuned on the test."""
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    t0 = time.time()
    arms = ("coin", "error_x4")
    V = correr(arms, SEEDS_CAL)
    out("§K6 CALIBRATION (seeds 100-102, acting §K3 life; not test seeds)")
    out(f"arms {arms}; run {(time.time() - t0) / 60:.1f} min "
        f"(median {np.median([x['min'] for x in V.values()]):.1f} min/life)")
    out("known-regime probe / exact average, end of visit (median over the cycle's visits), per seed")
    for a in arms:
        for s in SEEDS_CAL:
            ref = ms.ref_promedio(s)
            fila = [f"{ms.conocidos_medio(V[(a, s)], s, (c,)) / ref:.2f}" for c in (1, 2, 3, 4, 5, 6, 0, 7, 8)]
            out(f"  {a:>8} {s} | " + " ".join(fila) + "   (cycles 1-6, NOVEL, 7, 8)")
    out("")
    pv = {key: mp.por_visita(x, mp.calendario(key[1])) for key, x in V.items()}
    for a in arms:
        for s in SEEDS_CAL:
            x = V[(a, s)]
            kn = [p for p in pv[(a, s)] if p["ciclo"] in (7, 8)]
            nv = [p for p in pv[(a, s)] if p["ciclo"] == 0][0]
            orc = x["oraculo"][visita(s, 0)[0], [k for k in range(4) if k != s % 4]].mean() / ms.ref_promedio(s)
            out(f"  {a:>8} {s} | NOVEL-end ratio {cociente_nuevo(x, s):.2f} (oracle {orc:.2f}) | "
                f"known 7-8 early/late {np.mean([p['early'] for p in kn]):.3f}/"
                f"{np.mean([p['late'] for p in kn]):.3f} | NOVEL early/late {nv['early']:.3f}/{nv['late']:.3f} | "
                f"stuck {sum(p['late'] > 0.3 for p in pv[(a, s)] if p['fase'] == 'act')}")
            if a == "coin":
                pz = pureza(x, s)
                out(f"           contexts {pz['en_uso']}, majority expert per regime {pz['mayor']}, "
                    f"share {({r: round(v, 2) for r, v in pz['share'].items()})}, NOVEL own expert "
                    f"{pz['nuevo_propio']}; events {len(x['eventos'])} "
                    f"(spawns {int((x['eventos'][:, 0] == 2).sum()) if len(x['eventos']) else 0})")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "mundo_propio_coin_calibracion_run.txt").write_text("\n".join(lines), encoding="utf-8")
    (RESULTS / "mundo_propio_coin_calibracion_visitas.json").write_text(
        json.dumps({f"{a}_{s}": v for (a, s), v in pv.items()}), encoding="utf-8")


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    if modo == "humo":
        main_humo()
    elif modo == "calibracion":
        main_calibracion()
    else:
        raise SystemExit("draft: only humo / calibracion until the pre-registration is written")

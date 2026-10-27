"""
§K7 -- the HOUSES: does a kernel with a repertoire (one world-model expert per
inferred context, §K6) still have an identity, is it still rigid, and does its
identity become WHICH EXPERT IT GOES BACK TO when it comes home?
(docs/MUNDO_PROPIO.md; written 2026-10-27, before the calibration below)

WHY. §K4: twins raised in different worlds stay different after a shared exile
(IDENTIDAD, por el sueño, 24/24); the identity lives in the world model and its
price is rigidity (the kernel that keeps its childhood enters a never-lived world
worse, 12/12). §K5: a plural upbringing (home + school) shrinks the price without
losing the identity, and the declared identity module (self_embedding) carries the
life but not the childhood. §K6: a COIN-style repertoire keeps the known regimes
through a never-seen one (24/24). Here the two lines meet: the §K4/§K5 twins with
the §K6 world model.

DESIGN. The §K4 life (33 blocks of 300 ticks: 3 babbling + 15 childhood + 15 exile;
assays T1/Tm/T2 before blocks 18/23/33, where clones visit both twins' homes) and the
§K5 upbringings ("una" = home only; "dos" = home and the school N alternating,
ending at home), with one new arm: coin = error_x4 + wm_contexts=6 (§K6's arm).
error_x4 and kernel are READ from disk: "una" from §K4 (data/mundo_propio_gemelos),
"dos" from §K5 (data/mundo_propio_crianza). New per life: the active expert per tick
(`ctx`) and per assay tick (`ens_ctx`), the context events, and the probe with
context inference (§K6's sonda_ctx: per sequence, the expert with the lowest error
so far; `oraculo` = the best expert). The loop is exp_mundo_propio_gemelos.vivir's;
it is re-run on error_x4 (first pair, twin A, "una") and must reproduce the stored
§K4 life exactly (max diff 0). clonar() was generalized for this experiment: it
detaches the prior latent of every expert, not only the active one's (the inactive
ones also hold a graph between steps); for a single world model it is unchanged.
Declared: coin allocates 6 experts at birth, so its weights and later draws differ
from error_x4's on the same pair; the twins still share theirs (torch.manual_seed
(pair)).

THE EXPERTS. Home expert h = the mode of `ctx` over the last 5 childhood blocks at
home; exile expert e = the mode over the last 5 exile blocks; in an assay, the
SETTLED expert = the mode of `ens_ctx` over ticks 100-299 (after the re-entry
window). ELIGE(pair) at an assay = for both twins e != h (the exile got its own
memory) and the settled expert at home == h (it went back to its own memory).

RULE (sign tests over 12 pairs; 10/12 = one-sided p 0.019), on coin under "una":
  SE DIFERENCIA (positive control) H(T1) > 0. If it fails: NO SE DIFERENCIA.
  PERSISTE      (primary) H(T2) > 0 (the §K4 readout).
  ELIGE         (primary) ELIGE(pair) at T2.
  VERDICT  PERSISTE and ELIGE -> IDENTIDAD EN EL REPERTORIO (the identity is which
           expert it goes back to); PERSISTE only -> IDENTIDAD, SIN ELEGIR; ELIGE
           only -> ELIGE SIN PERSISTIR; neither -> IDENTIDAD FRAGIL.
  Secondary:
  PAREADO   H(T2) coin > error_x4 (§K4's lives): the repertoire keeps it better.
  RIGIDEZ   the §K4 criterion on coin: T1 cost in the sibling's home (mean of the
            twins) coin > kernel.
  ACHICA    T1 cost coin < error_x4.
  EXILIO    (added after the calibration, before the test) the first exile block's
            e_early (mean of the twins) coin < error_x4.
  Under "dos", the same readouts against §K5's lives: CONSERVA (H(T2) > 0), ELIGE,
  RIGIDEZ, ACHICA, EXILIO.
  Reported: H at Tm; ELIGE at T1 and Tm; the switch latency at home at T2 (first
  tick on h); NO CONFUNDE (the settled expert in the sibling's home at T2 != h);
  contexts in use; the probe by role; stuck blocks; the first exile block; RECONOCE
  (§K4's free-energy cross at T2); the twins' self_embedding distance.

PREDICTIONS (written before the calibration). SE DIFERENCIA 12/12. PERSISTE and
PAREADO pass: the exile gets its own expert, so the childhood expert is restored and
never overwritten; H(T2) stays below H(T1) because at T2 the clone must first switch
back (the switch waits for the running error, ~10-30 of the 100 re-entry ticks).
ELIGE passes. RIGIDEZ still passes and ACHICA fails: in the childhood coin has one
expert (an error_x4), and in a never-lived world its new expert starts as a copy of
that one; §K6 entered the NOVEL regime no faster (13/24). Under "dos": CONSERVA and
ELIGE pass; coin's T1 cost like error_x4's.

CALIBRATION (`calibracion`, pairs 100-102, never test pairs; "dos" has no stored
error_x4 / kernel lives there; results/mundo_propio_casas_calibracion_run.txt; 31.2
min). Nothing was tuned. Verification max diff 0. "una": H(T1) +1.47, H(T2) +1.09
(3/3; error_x4 +0.74), ELIGE 3/3 at every assay (2 contexts per twin: home and
exile, e != h 6/6; latency back to h at home 10 ticks at T2); T1 cost in the
sibling's home 0.77 vs error_x4 0.91 and kernel 0.44 (ACHICA 3/3, RIGIDEZ 3/3: the
written ACHICA prediction already looks wrong and stays as written); the first
exile block 0.26 vs error_x4 0.72, stuck 0 vs 2. "dos": 3 contexts (home, school,
exile; one twin 4), ELIGE 3/3, but H(T2) only +0.10 (3/3) with latency 42 ticks.
The coin probe keeps the home at 0.005-0.015 through the exile.
PREDICTIONS added after the calibration, before the test pairs: PERSISTE, ELIGE and
PAREADO pass; RIGIDEZ passes; ACHICA uncertain (the written prediction stands);
EXILIO passes -- hypothesis: each expert sleeps on its own buffer, so replaying the
childhood no longer drags the exile's learning back toward home; under "dos",
CONSERVA at risk (small H(T2)), ELIGE passes.

REPLICATION, pre-registered with the test: pairs 12-23 (the replication lives of §K4
and §K5 are read), the same rule, launched right after the test unless a bug is found
(any change recorded). REPLICADO if the verdict repeats.

RESULT (pairs 0-11, results/mundo_propio_casas_run.txt, 137.2 min; verification max
diff 0). Pre-registered verdict ("una"): IDENTIDAD EN EL REPERTORIO -- SE DIFERENCIA
12/12 (H(T1) +0.96), PERSISTE 12/12 (H(T2) +0.69), ELIGE 11/12 (the exile got its own
expert in 24/24 twins; back to h at home in 23/24, latency 11 ticks; the failing pair
opened a second childhood expert and settled on the first). Secondary: PAREADO 6/12
(FAILED, predicted to pass), ACHICA 10/12 (passed; the written prediction said it
fails: T1 cost 0.51 vs error_x4 0.71), RIGIDEZ 7/12 (FAILED, predicted to pass: 0.51
vs kernel 0.46), EXILIO 11/12 (0.50 vs 0.68; stuck 2 vs 12). "dos": SE DIFERENCIA
12/12, CONSERVA 12/12 (+0.46), ELIGE 12/12, PAREADO 8/12, ACHICA 7/12, RIGIDEZ 5/12,
EXILIO 10/12. Post hoc: coin differentiates less at T1 (10/12 below error_x4) and
keeps more through the exile (retention 0.76 vs 0.43, 8/12); in the sibling's home
at T1 its clone opens a new expert (settles on h in 2/24 twins). The repertoire does
not keep more identity than error_x4, but it nearly stops paying §K4's price.

REPLICATION RESULT (pairs 12-23, results/mundo_propio_casas_replica_run.txt; run in two
legs: the first was killed for low system memory after 28/48 lives, the second loaded
them with `reanudar` and ran the other 20 in 42.2 min; verification max diff 0).
REPLICADO: IDENTIDAD EN EL REPERTORIO again -- SE DIFERENCIA 12/12, PERSISTE 12/12
(H(T2) +0.98), ELIGE 11/12. Secondary: PAREADO 9/12, ACHICA 9/12, RIGIDEZ 8/12 (none
passes by the letter), EXILIO 11/12 (stuck 1 vs 16). "dos": CONSERVA 10/12, ELIGE
12/12, ACHICA 10/12, RIGIDEZ 3/12, EXILIO 10/12. Pooled 24: PERSISTE 24/24, ELIGE
22/24, PAREADO 15/24, ACHICA 19/24 (p 0.003), RIGIDEZ 15/24, EXILIO 22/24; under
"dos" coin < kernel T1 cost 16/24 (p 0.08). The identity survives the repertoire and
becomes WHICH EXPERT IT GOES BACK TO; it is not larger than error_x4's, and §K4's
price nearly vanishes (the never-lived goes to a new expert). Open: a coin arm without
sleep (attribution), a relative threshold (the two ELIGE misses have a third expert).

48 new lives + 1 verification life per run; 3 CPU processes, one torch thread each
(the declared kernel exception); ~7 min per coin life.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_casas.py humo
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_casas.py calibracion
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_casas.py
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_casas.py replica   # pairs 12-23
    # `reanudar` after any mode loads the lives already on disk instead of re-running them
    # (added 2026-10-27, when the replication was killed for low system memory; a stored
    # life is the loop's own deterministic output, so the report is unchanged):
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_casas.py replica reanudar
"""

from __future__ import annotations

import importlib.util
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _cargar_modulo(nombre: str, archivo: str):
    spec = importlib.util.spec_from_file_location(nombre, HERE / archivo)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


cr = _cargar_modulo("mundo_propio_crianza", "exp_mundo_propio_crianza.py")
co = _cargar_modulo("mundo_propio_coin", "exp_mundo_propio_coin.py")
g = cr.g
mp, ms = g.mp, g.ms

RESULTS = ROOT / "results"
DATA = ROOT / "data" / "mundo_propio_casas"
D = g.D
N_OK = g.N_OK
PAIRS = g.PAIRS
GEMELOS = g.GEMELOS
CRIANZAS = ("una", "dos")
LEIDOS = ("error_x4", "kernel")
ULTIMOS = 5


def salida(args: tuple, vida: dict, t0: float) -> dict:
    brazo, par, gemelo, escala, crianza = args[:5]
    return {"brazo": brazo, "par": par, "gemelo": gemelo, "crianza": crianza,
            "T": [T for T, _ in escala["ensayos"]], "bloque": [b for _, b in escala["ensayos"]],
            "vida_bloques": escala["vida"], "min": (time.time() - t0) / 60, **vida}


def vivir(args: tuple) -> dict:
    """One twin's life: exp_mundo_propio_gemelos.vivir's loop with the arm's kernel, plus the
    active expert per tick and per assay tick, the context events and the context probe.
    With `reanudar`, a life already on disk is loaded instead of re-run."""
    import torch

    from zeta_life.kernel import ConsciousKernel
    brazo, par, gemelo, escala, crianza, archivo, reanudar = args
    t0 = time.time()
    if reanudar and (DATA / f"{archivo}.npz").exists():
        return salida(args, dict(np.load(DATA / f"{archivo}.npz")), t0)
    torch.set_num_threads(1)
    nb, nn, ne = escala["vida"]
    n_bloques = nb + nn + ne
    papel = g.papeles(par)
    tipo, a_test, a_babble = g.pruebas(par, n_bloques, nb)
    torch.manual_seed(par)
    k = ConsciousKernel(obs_dim=4, action_mode="efe", preference=torch.tensor(mp.C),
                        efe_n_samples=48, efe_obs_norm="l1", **co.BRAZOS[brazo])
    contextos = hasattr(k.world_model, "experts")
    probes = ms.sondas()
    pref = torch.tensor(mp.C)
    n = n_bloques * D
    s = torch.full((4,), 0.25)
    dist, psi, fe = np.empty(n), np.empty(n), np.empty(n)
    ctx = np.zeros(n, dtype=np.int8)
    sonda, oraculo = np.full((n_bloques, 4), np.nan), np.full((n_bloques, 4), np.nan)
    nombres = [T for T, _ in escala["ensayos"]]
    cuando = {b: i for i, (_, b) in enumerate(escala["ensayos"])}
    ens = np.empty((3, len(nombres), 2, D))
    ens_ctx = np.zeros((len(nombres), 2, D), dtype=np.int8)
    yo = np.empty((len(nombres), k.self_model.embed_dim))
    for t in range(n + 1):
        if t % D == 0 and t // D in cuando:
            i = cuando[t // D]
            for w, rol in enumerate(GEMELOS):
                x = g.ensayo(k, s, papel[rol], 900_000 + 100 * par + 10 * i + papel[rol])
                ens[:, i, w] = x["dist"], x["fe"], x["psi"]
                ens_ctx[i, w] = x["ctx"]
            yo[i] = k.self_model.self_embedding.detach().numpy()
        if t == n:
            break
        v = t // D
        reg = g.regimen(papel, gemelo, v, nb, nn, crianza)
        r = k.step(s)
        dist[t] = float(torch.linalg.vector_norm(s - pref))
        psi[t], fe[t] = r.psi, r.free_energy
        ctx[t] = getattr(k.world_model, "active", 0)
        if v < nb:
            a = torch.tensor(a_babble[t], dtype=torch.float32)
            k.last_action = a
        elif tipo[t]:
            a = torch.tensor(a_test[t], dtype=torch.float32)
            if tipo[t] == 1:
                k.last_action = a
        else:
            a = r.action.detach()
        s = ms.mover(s, a, reg)
        if t % D == D - 1:
            for kk in range(4):
                if contextos:
                    sonda[v, kk], _, oraculo[v, kk] = co.sonda_ctx(k.world_model, *probes[kk])
                else:
                    sonda[v, kk] = g.cx.error_sonda(k.world_model, *probes[kk])[0]
    ev = np.array([(co.EVENTO[e], t, c) for e, t, c in getattr(k.world_model, "events", [])],
                  dtype=int).reshape(-1, 3)
    vida = {"dist": dist, "psi": psi, "fe": fe, "tipo": tipo, "sonda": sonda, "oraculo": oraculo,
            "ctx": ctx, "ens_dist": ens[0], "ens_fe": ens[1], "ens_psi": ens[2], "ens_ctx": ens_ctx,
            "yo": yo, "eventos": ev}
    DATA.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(DATA / f"{archivo}.npz", **vida)
    return salida(args, vida, t0)


def tareas(pares: tuple, escala: dict, reanudar: bool = False) -> list[tuple]:
    h = cr.humo(escala)
    t = [("error_x4", pares[0], "A", escala, "una", f"verif_error_x4_{pares[0]}_A{h}", reanudar)]
    return t + [("coin", p, gm, escala, crianza, f"{crianza}_coin_{p}_{gm}{h}", reanudar)
                for crianza in CRIANZAS for p in pares for gm in GEMELOS]


def correr(pares: tuple, escala: dict, reanudar: bool = False) -> tuple[dict, dict]:
    with ProcessPoolExecutor(max_workers=g.WORKERS) as pool:
        vidas = list(pool.map(vivir, tareas(pares, escala, reanudar)))
    V = {crianza: {} for crianza in CRIANZAS}
    for x in vidas[1:]:
        V[x["crianza"]][(x["brazo"], x["par"], x["gemelo"])] = x
    return V, vidas[0]


def cargar(brazo: str, par: int, gemelo: str, crianza: str, escala: dict) -> dict | None:
    """A stored life of §K4 ("una") or §K5 ("dos"), in the shape vivir() returns; None if absent."""
    h = cr.humo(escala)
    ruta = (g.DATA / f"{brazo}_{par}_{gemelo}{h}.npz" if crianza == "una"
            else cr.DATA / f"dos_{brazo}_{par}_{gemelo}{h}.npz")
    if not ruta.exists():
        return None
    x = dict(np.load(ruta))
    x.update(brazo=brazo, par=par, gemelo=gemelo, crianza=crianza,
             T=[t for t, _ in escala["ensayos"]], bloque=[b for _, b in escala["ensayos"]],
             vida_bloques=escala["vida"])
    return x


def leidos(V: dict, pares: tuple, escala: dict) -> list[str]:
    """Add the stored error_x4 / kernel lives to V; return the arms present for every pair."""
    brazos = ["coin"]
    for crianza in CRIANZAS:
        for a in LEIDOS:
            xs = {(a, p, gm): cargar(a, p, gm, crianza, escala) for p in pares for gm in GEMELOS}
            if all(x is not None for x in xs.values()):
                V[crianza].update(xs)
                if a not in brazos:
                    brazos.append(a)
    return brazos


def moda(a: np.ndarray) -> int:
    return int(np.bincount(np.asarray(a, dtype=int)).argmax())


def casa_exilio(x: dict, par: int) -> tuple[int, int]:
    """(home expert h, exile expert e): the mode of ctx over the last ULTIMOS childhood
    blocks at home and over the last ULTIMOS exile blocks."""
    nb, nn, ne = x["vida_bloques"]
    papel = g.papeles(par)
    casa = [v for v in range(nb, nb + nn)
            if g.regimen(papel, x["gemelo"], v, nb, nn, x["crianza"]) == papel[x["gemelo"]]]
    bloques = lambda vs: np.concatenate([x["ctx"][v * D:(v + 1) * D] for v in vs])  # noqa: E731
    total = nb + nn + ne
    return moda(bloques(casa[-ULTIMOS:])), moda(bloques(range(total - min(ULTIMOS, ne), total)))


def asentado(x: dict, j: int, w: int) -> int:
    """The settled expert of assay j in world w (mode over the ticks after the re-entry window)."""
    return moda(x["ens_ctx"][j, w, mp.EARLY:])


def elige(V: dict, par: int, j: int) -> bool:
    """Both twins: the exile got its own expert and, back home, the clone settles on h."""
    for i, gm in enumerate(GEMELOS):
        x = V[("coin", par, gm)]
        h, e = casa_exilio(x, par)
        if e == h or asentado(x, j, i) != h:
            return False
    return True


def confunde(V: dict, par: int, j: int) -> bool:
    """Some twin settles on its home expert in its sibling's home."""
    return any(asentado(V[("coin", par, gm)], j, 1 - i) == casa_exilio(V[("coin", par, gm)], par)[0]
               for i, gm in enumerate(GEMELOS))


def latencia(x: dict, par: int, j: int, i: int) -> int:
    """First tick of the home assay j on the home expert (D if never)."""
    h, _ = casa_exilio(x, par)
    idx = np.flatnonzero(x["ens_ctx"][j, i] == h)
    return int(idx[0]) if idx.size else D


def veredicto(sd: int, persiste: int, elige_n: int) -> str:
    """The pre-registered §K7 rule."""
    if sd < N_OK:
        return "NO SE DIFERENCIA"
    if persiste >= N_OK and elige_n >= N_OK:
        return "IDENTIDAD EN EL REPERTORIO"
    if persiste >= N_OK:
        return "IDENTIDAD, SIN ELEGIR"
    if elige_n >= N_OK:
        return "ELIGE SIN PERSISTIR"
    return "IDENTIDAD FRAGIL"


def informe(V: dict, brazos: list, pares: tuple, escala: dict, nombre: str, titulo: str,
            minutos: float, verif: float) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    n = len(pares)
    T = [t for t, _ in escala["ensayos"]]
    j2 = len(T) - 1
    cuenta = lambda xs: sum(bool(v) for v in xs)  # noqa: E731
    out("=" * 80)
    out(titulo)
    out("=" * 80)
    out(f"pairs {pares[0]}-{pares[-1]}; coin = error_x4 + wm_contexts={co.CONTEXTOS}, run under 'una' and "
        f"'dos'; read: {[a for a in brazos if a != 'coin']} (§K4 'una', §K5 'dos' where stored); "
        f"run {minutos:.1f} min")
    out(f"verification: the loop re-run on error_x4 pair {pares[0]} twin A ('una') vs the stored §K4 life, "
        f"max diff {verif}")
    H = {}
    for crianza in CRIANZAS:
        W = V[crianza]
        presentes = [a for a in brazos if all((a, p, gm) in W for p in pares for gm in GEMELOS)]
        out("")
        out(f"=== crianza '{crianza}' (arms {presentes})")
        out("H_early (cross) medians and H>0 per assay")
        for a in presentes:
            cel = []
            for t in T:
                h = [g.cruce(g.leer(W, a, p, t, "early")) for p in pares]
                H[(crianza, a, t)] = h
                cel.append(f"{t} {np.median(h):+.3f} ({cuenta(v > 0 for v in h)}/{n})")
            out(f"  {a:>8} | " + " | ".join(cel))
        out("T1 cost in the sibling's home (median) | first exile block e_early | stuck blocks (twins)")
        for a in presentes:
            b, tw = cr.atascos(W, a, pares)
            out(f"  {a:>8} | {np.median([cr.costo(W, a, p) for p in pares]):.3f} | "
                f"{np.median([cr.exilio(W, a, p) for p in pares]):.3f} | stuck {b} ({tw}/{2 * n})")
        out("coin experts: contexts in use per twin | home expert h, exile expert e per twin")
        usos = [1 + int((W[("coin", p, gm)]["eventos"][:, 0] == co.EVENTO["spawn"]).sum())
                for p in pares for gm in GEMELOS]
        he = [casa_exilio(W[("coin", p, gm)], p) for p in pares for gm in GEMELOS]
        out(f"  in use {usos}")
        out(f"  (h, e) {he}; e != h in {cuenta(e != h for h, e in he)}/{2 * n} twins")
        for j, t in enumerate(T):
            if escala["ensayos"][j][1] == 0:
                continue
            casa = [asentado(W[("coin", p, gm)], j, i) == casa_exilio(W[("coin", p, gm)], p)[0]
                    for p in pares for i, gm in enumerate(GEMELOS)]
            lat = [latencia(W[("coin", p, gm)], p, j, i) for p in pares for i, gm in enumerate(GEMELOS)]
            out(f"  {t:>3}: settled at home on h {cuenta(casa)}/{2 * n} twins; ELIGE pairs "
                f"{cuenta(elige(W, p, j) for p in pares)}/{n}; NO CONFUNDE pairs "
                f"{cuenta(not confunde(W, p, j) for p in pares)}/{n}; latency to h at home median "
                f"{np.median(lat):.0f} ticks")
        out("coin probe (median over twins and pairs): home | sibling | X | N (the school under 'dos') "
            "| oracle at home")
        for j, t in enumerate(T):
            if escala["ensayos"][j][1] == 0:
                continue
            cel = []
            for campo, roles in (("sonda", ("home", "sibling", "X", "N")), ("oraculo", ("home",))):
                for rol in roles:
                    vals = []
                    for p in pares:
                        pa = g.papeles(p)
                        for gm, otro in (("A", "B"), ("B", "A")):
                            x = W[("coin", p, gm)]
                            r = {"home": gm, "sibling": otro, "X": "X", "N": "N"}[rol]
                            vals.append(x[campo][x["bloque"][j] - 1, pa[r]])
                    cel.append(f"{np.median(vals):.3f}")
            out(f"  {t:>3} | " + " | ".join(cel))
        yo = {a: [float(np.linalg.norm(W[(a, p, 'A')]['yo'][j2] - W[(a, p, 'B')]['yo'][j2])) for p in pares]
              for a in presentes}
        out("  (reported) twins' self_embedding distance at the last assay, median: "
            + ", ".join(f"{a} {np.median(v):.2f}" for a, v in yo.items()))
        rec = [g.cruce(g.leer(W, "coin", p, T[j2], "fe")) for p in pares]
        out(f"  (reported) RECONOCE coin (free-energy cross at {T[j2]} > 0): {cuenta(v > 0 for v in rec)}/{n}")
    out("")
    out("-" * 80)
    lectura = {}
    for crianza in CRIANZAS:
        W = V[crianza]
        c = {a: [cr.costo(W, a, p) for p in pares] for a in brazos
             if all((a, p, gm) in W for p in pares for gm in GEMELOS)}
        lectura[(crianza, "sd")] = cuenta(v > 0 for v in H[(crianza, "coin", "T1")])
        lectura[(crianza, "persiste")] = cuenta(v > 0 for v in H[(crianza, "coin", T[j2])])
        lectura[(crianza, "elige")] = cuenta(elige(W, p, j2) for p in pares)
        nombre_p = "PERSISTE" if crianza == "una" else "CONSERVA"
        out(f"[{crianza}] SE DIFERENCIA H(T1) > 0: {lectura[(crianza, 'sd')]}/{n} | "
            f"{nombre_p} H({T[j2]}) > 0: {lectura[(crianza, 'persiste')]}/{n} | "
            f"ELIGE at {T[j2]}: {lectura[(crianza, 'elige')]}/{n}")
        if "error_x4" in c:
            out(f"[{crianza}] PAREADO H({T[j2]}) coin > error_x4: "
                f"{cuenta(x > y for x, y in zip(H[(crianza, 'coin', T[j2])], H[(crianza, 'error_x4', T[j2])]))}/{n}"
                f" | ACHICA T1 cost coin < error_x4: {cuenta(x < y for x, y in zip(c['coin'], c['error_x4']))}/{n}")
        if "kernel" in c:
            out(f"[{crianza}] RIGIDEZ T1 cost coin > kernel: "
                f"{cuenta(x > y for x, y in zip(c['coin'], c['kernel']))}/{n}")
        if "error_x4" in c:
            ex = {a: [cr.exilio(W, a, p) for p in pares] for a in ("coin", "error_x4")}
            out(f"[{crianza}] EXILIO first exile block e_early coin < error_x4: "
                f"{cuenta(x < y for x, y in zip(ex['coin'], ex['error_x4']))}/{n}")
    if n == len(PAIRS):
        out(f"VERDICT (pre-registered rule, 'una'): "
            f"{veredicto(lectura[('una', 'sd')], lectura[('una', 'persiste')], lectura[('una', 'elige')])}")
    else:
        out("(n < 12: no verdict)")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{nombre}_run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(pares: tuple, escala: dict, nombre: str, titulo: str, reanudar: bool = False) -> None:
    t0 = time.time()
    V, x0 = correr(pares, escala, reanudar)
    ref = cargar("error_x4", pares[0], "A", "una", escala)
    verif = cr.diferencia(x0, ref) if ref is not None else float("nan")
    brazos = leidos(V, pares, escala)
    if escala == g.HUMO:
        for crianza in CRIANZAS:
            h0 = g.cruce(g.leer(V[crianza], "coin", pares[0], "T0", "early"))
            print(f"newborn coin twins ('{crianza}'): H(T0) = {h0} (must be 0 exactly)")
    informe(V, brazos, pares, escala, nombre, titulo, (time.time() - t0) / 60, verif)


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    reanudar = "reanudar" in argumentos
    modo = next((a for a in argumentos if a != "reanudar"), "")
    if modo == "humo":
        main((0,), g.HUMO, "mundo_propio_casas_humo", "§K7 SMOKE TEST (pair 0, short life)", reanudar)
    elif modo == "calibracion":
        main(g.PAIRS_CAL, g.ESCALA, "mundo_propio_casas_calibracion",
             "§K7 CALIBRATION (pairs 100-102) -- the houses: identity with a repertoire", reanudar)
    elif modo == "replica":
        main(tuple(range(12, 24)), g.ESCALA, "mundo_propio_casas_replica",
             "§K7 REPLICATION (pairs 12-23) -- the houses: identity with a repertoire", reanudar)
    else:
        main(PAIRS, g.ESCALA, "mundo_propio_casas", "§K7 -- the houses: identity with a repertoire",
             reanudar)

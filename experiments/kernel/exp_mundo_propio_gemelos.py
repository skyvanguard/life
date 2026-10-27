"""
§K4 -- IDENTITY: twins raised in different worlds. Does a life write an
individual, does the individual survive a long SHARED life, and does the kernel's
own signal recognize its own world? (docs/MUNDO_PROPIO.md; pre-registered
2026-10-26, after the calibration below and before any run on the test pairs)

WHY. The north (docs/NORTE.md) asks for a system that is born empty, learns in
life AND sustains an identity. §K1-§K3 answered the first two in the kernel's own
world; identity was declared next ("twins raised in different worlds"). Here
identity is PSYCHOLOGICAL CONTINUITY: an individual difference written by one's
own past, which survives a shared present and which the kernel's own signal can
read. It does not measure a sense of self. New over §K1-§K3: (1) twins -- born
identical, so any difference is the life's; (2) a long adversary -- an exile as
long as the childhood (§K3's novel visit was 300 ticks); (3) the declared
identity module (the self-model's self_embedding) is checked for whether it
carries the identity.

DESIGN. Twins = the same weights and the same draws at birth (torch.manual_seed
(pair)); they share babbling, test ticks and test actions (the §K1 protocol);
only their home regime differs. Worlds = the 4 §K1 regimes; per pair four roles:
A's home, B's home, the shared exile X, and N (never lived); over 12 pairs each
regime plays each role 3 times (papeles()). Life = 33 blocks of 300 ticks:
3 babbling at home, 15 acting at home (childhood; the ticks of §K1's cycles 2-6),
15 acting in X (exile; both twins, same regime, same tests). 9900 ticks fit the
sleep buffer (capacity 10000); declared hand: a longer life would start
forgetting the childhood by construction. Declared asymmetry: the twins babble
only at home (infancy), the exile is acting only.
ASSAYS before blocks 18 (end of childhood, T1), 23 (1500 exile ticks, Tm) and 33
(end of exile, T2): a CLONE of each twin lives one 300-tick visit in A's home and
another in B's home, acting, no test ticks, from the current state; clones are
discarded (the original's life is unchanged: verified, max diff 0); both twins
get the same draws in each assay (paired). CROSS H = (A in B's home + B in A's
home) - (A at home + B at home) on the re-entry cost e_early (mean ||s - C|| over
ticks 0-99, §K1's RECUERDA readout): world and twin main effects cancel; H > 0 =
each does better in its own world than its sibling. Smoke test (`humo`): clones
of the newborn twins give identical readings (H = 0 exactly), and a clone
continued with its original's draws reproduces it (max diff 0).

ARMS. error_x4 (the §K3 kernel: 4 x sleep dose + wm_error_input) and kernel (the
§K1 kernel, no sleep): the attribution control.

RULE (sign tests over 12 pairs; 10/12 = one-sided p 0.019):
  SE DIFERENCIA  (positive control) H(T1) > 0 on error_x4. If it fails: NO SE
                 DIFERENCIA, nothing else is read.
  PERSISTE       (primary) H(T2) > 0 on error_x4.
  RECONOCE       (secondary) the cross of the kernel's OWN free energy over ticks
                 1-20 of the visit (the ticks that perceive the new world), at T2,
                 > 0 on error_x4: its own surprise says "this is my home".
  ATTRIBUTION    PERSISTE on kernel, and paired H(T2) error_x4 > kernel.
  VERDICT  no SE DIFERENCIA -> NO SE DIFERENCIA; SE DIFERENCIA and PERSISTE ->
           IDENTIDAD, "por el sueño" if kernel does not persist and the paired
           contrast passes, "también sin el sueño" if kernel persists, "sin
           atribuir" otherwise; SE DIFERENCIA without PERSISTE -> IDENTIDAD FRAGIL.
  Reported, not verdicts: H at Tm (time course), the probe and Psi crosses, the
  twins' self_embedding distance at each assay, control at home and in exile,
  stuck blocks, and DESVENTAJA (below).
PREDICTIONS written before the calibration: SE DIFERENCIA 12/12 in both arms
(near-trivial: at T1 the home assay does not switch regime, the other does);
kernel: PERSISTE fails (§K1 had no savings); error_x4: PERSISTE passes with H(T2)
well below H(T1) (sleep replays the whole life: at the end of the exile half of
what it replays is the childhood); RECONOCE follows PERSISTE; self_embedding: the
twins' distance shrinks a lot in the exile (an EMA, tau ~100 ticks, of what the
kernel does): the declared identity module does not carry the identity.

CALIBRATION (`calibracion`, pairs 100-102, never test pairs; all three share the
role pattern B - A = 2, X - A = 3; results/mundo_propio_gemelos_calibracion_run.txt).
Nothing was tuned. SE DIFERENCIA 3/3 in both arms. error_x4: H(T1) +1.75, H(T2)
+0.74 (3/3), RECONOCE 3/3; its world model keeps the home (probe 0.014 vs 0.18 on
the sibling's home) and the exile regime never shows in the probe (0.18, as the
never-lived N): the probe uses random actions and the exile has no babbling.
kernel: H(T2) -0.51 (1/3 > 0) -- after the exile the kernel without sleep
re-enters its OWN home more slowly than its sibling's (A->A 0.88/0.43/0.36 vs
A->B 0.32/0.22/0.31), unexplained; its probe forgets the home (0.26, as the
sibling's). Psi saturates after T1 (its crosses are 0). self_embedding: the
twins' distance does not shrink (error_x4 2.06 -> 2.40, kernel 2.05 -> 2.97); the
prediction above already looks wrong and stays as written.
PREDICTIONS added after the calibration, before the test pairs: PERSISTE and
RECONOCE pass on error_x4; kernel PERSISTE fails; reported, with its own
criterion: DESVENTAJA = H(T2) < 0 on kernel in >= 10/12 (the home disadvantage
seen in calibration, 2/3); predicted to pass.

REPLICATION (pre-registered 2026-10-26 after the test landed -- IDENTIDAD (por el
sueño): PERSISTE 12/12, kernel 9/12, paired 11/12 -- and before running): pairs
12-23 (each regime still plays each role 3 times), both arms, the same rule.
REPLICADO if the verdict is IDENTIDAD again; the attribution is read by the same
rule and reported pooled over the 24 pairs. Secondary, from a post hoc reading of
the test (11/12 there; the first exile block 21/24 twins): RIGIDEZ = the T1 cost
in the sibling's home (mean of the twins) of error_x4 > that of kernel, >= 10/12:
the kernel that keeps its childhood enters a never-lived world worse. Reported
again: RECONOCE (8/12 in the test), DESVENTAJA (3/12 in the test, the
calibration's prediction failed), self_embedding, stuck blocks.
PREDICTIONS: PERSISTE replicates (12/12, minimum H +0.26 in the test); kernel
PERSISTE is a coin at the threshold (9/12), so the attribution "por el sueño" is
at risk; RECONOCE fails again; RIGIDEZ passes.

3 CPU processes, one torch thread each (declared exception to the GPU rule: the
kernel is tiny); ~4 min per life, 48 lives, ~65 min.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_gemelos.py humo
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_gemelos.py calibracion
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_gemelos.py
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_gemelos.py replica   # pairs 12-23
"""

from __future__ import annotations

import copy
import importlib.util
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
DATA = ROOT / "data" / "mundo_propio_gemelos"
D = mp.D
PAIRS = tuple(range(12))
PAIRS_CAL = (100, 101, 102)
N_OK = mp.N_OK
WORKERS = 3
ARMS = ("error_x4", "kernel")
GEMELOS = ("A", "B")
OFFSETS = ((1, 2), (2, 3), (3, 1))
ENTRADA = slice(1, 21)
ESCALA = {"vida": (3, 15, 15), "ensayos": (("T1", 18), ("Tm", 23), ("T2", 33))}
HUMO = {"vida": (1, 2, 2), "ensayos": (("T0", 0), ("T1", 3), ("Tm", 4), ("T2", 5))}


def papeles(par: int) -> dict:
    """Regime of each role: A and B the twins' homes, X the shared exile, N never lived.
    Over every 12 consecutive pairs each regime plays each role 3 times."""
    a = par % 4
    db, dx = OFFSETS[(par // 4) % 3]
    b, x = (a + db) % 4, (a + dx) % 4
    return {"A": a, "B": b, "X": x, "N": ({0, 1, 2, 3} - {a, b, x}).pop()}


def pruebas(par: int, n_bloques: int, babble: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The §K1 test-tick protocol per tick (0 none, 1 EFERENCIA, 2 EXO), the test actions and
    the babbling actions; shared by both twins and both arms of a pair."""
    rng = np.random.default_rng(8000 + par)
    n = n_bloques * D
    tipo = np.zeros(n, dtype=int)
    ultimo = -mp.GAP
    for v in range(babble, n_bloques):
        for t in range(v * D + mp.LATE0, (v + 1) * D - 1):
            if t - ultimo >= mp.GAP and rng.random() < 2 * mp.P_TEST:
                tipo[t] = 1 + int(rng.random() < 0.5)
                ultimo = t
    return tipo, rng.dirichlet(np.full(4, 0.5), size=n), rng.dirichlet(np.ones(4), size=n)


def clonar(k):
    """Deep copy of a kernel between steps. The only non-leaf tensor it holds there is the
    world model's prior latent, which is only ever read detached; the original keeps its own."""
    wm = k.world_model
    p = wm._prior_latent
    wm._prior_latent = None if p is None else p.detach()
    try:
        return copy.deepcopy(k)
    finally:
        wm._prior_latent = p


def ensayo(k, s, mundo: int, semilla: int) -> dict:
    """A CLONE of the kernel lives one visit (D ticks, acting, no test ticks) in regime
    `mundo` from the current state. The original and the global RNG are untouched."""
    import torch
    estado = torch.get_rng_state()
    c, s = clonar(k), s.clone()
    torch.manual_seed(semilla)
    pref = torch.tensor(mp.C)
    dist, fe, psi = np.empty(D), np.empty(D), np.empty(D)
    for t in range(D):
        r = c.step(s)
        dist[t] = float(torch.linalg.vector_norm(s - pref))
        fe[t], psi[t] = r.free_energy, r.psi
        s = ms.mover(s, r.action.detach(), mundo)
    torch.set_rng_state(estado)
    return {"dist": dist, "fe": fe, "psi": psi}


def vivir(args: tuple) -> dict:
    """One twin's life: babble and childhood at home, then the shared exile; before the
    step of each assay block, clones visit both twins' homes."""
    import torch
    brazo, par, gemelo, escala = args
    t0 = time.time()
    torch.set_num_threads(1)
    nb, nn, ne = escala["vida"]
    n_bloques = nb + nn + ne
    papel = papeles(par)
    tipo, a_test, a_babble = pruebas(par, n_bloques, nb)
    torch.manual_seed(par)
    k = cx.nuevo_kernel(brazo, False)
    probes = ms.sondas()
    pref = torch.tensor(mp.C)
    n = n_bloques * D
    s = torch.full((4,), 0.25)
    dist, psi, fe = np.empty(n), np.empty(n), np.empty(n)
    sonda = np.full((n_bloques, 4), np.nan)
    nombres = [T for T, _ in escala["ensayos"]]
    cuando = {b: i for i, (_, b) in enumerate(escala["ensayos"])}
    ens = np.empty((3, len(nombres), 2, D))
    yo = np.empty((len(nombres), k.self_model.embed_dim))
    for t in range(n + 1):
        if t % D == 0 and t // D in cuando:
            i = cuando[t // D]
            for w, rol in enumerate(GEMELOS):
                x = ensayo(k, s, papel[rol], 900_000 + 100 * par + 10 * i + papel[rol])
                ens[:, i, w] = x["dist"], x["fe"], x["psi"]
            yo[i] = k.self_model.self_embedding.detach().numpy()
        if t == n:
            break
        v = t // D
        reg = papel[gemelo] if v < nb + nn else papel["X"]
        r = k.step(s)
        dist[t] = float(torch.linalg.vector_norm(s - pref))
        psi[t], fe[t] = r.psi, r.free_energy
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
                sonda[v, kk] = cx.error_sonda(k.world_model, *probes[kk])[0]
    vida = {"dist": dist, "psi": psi, "fe": fe, "tipo": tipo, "sonda": sonda,
            "ens_dist": ens[0], "ens_fe": ens[1], "ens_psi": ens[2], "yo": yo}
    DATA.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(DATA / f"{brazo}_{par}_{gemelo}{'_humo' if escala == HUMO else ''}.npz", **vida)
    return {"brazo": brazo, "par": par, "gemelo": gemelo, "T": nombres,
            "bloque": [b for _, b in escala["ensayos"]], "vida_bloques": escala["vida"],
            "min": (time.time() - t0) / 60, **vida}


def correr(arms: tuple, pares: tuple, escala: dict) -> dict:
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        vidas = list(pool.map(vivir, [(a, p, g, escala) for a in arms for p in pares for g in GEMELOS]))
    return {(x["brazo"], x["par"], x["gemelo"]): x for x in vidas}


def leer(V: dict, brazo: str, par: int, T: str, campo: str) -> np.ndarray:
    """2 x 2 [twin, world of twin] of an assay reading."""
    m = np.empty((2, 2))
    for i, g in enumerate(GEMELOS):
        x = V[(brazo, par, g)]
        j = x["T"].index(T)
        for w in range(2):
            if campo == "early":
                m[i, w] = x["ens_dist"][j, w, :mp.EARLY].mean()
            elif campo == "late":
                m[i, w] = x["ens_dist"][j, w, mp.LATE0:].mean()
            elif campo == "fe":
                m[i, w] = x["ens_fe"][j, w, ENTRADA].mean()
            elif campo == "psi":
                m[i, w] = (x["ens_psi"][j, w, ENTRADA] < mp.HI).mean()
            elif campo == "sonda":
                b = x["bloque"][j]
                m[i, w] = x["sonda"][b - 1, papeles(par)[GEMELOS[w]]] if b > 0 else np.nan
    return m


def afuera(V: dict, brazo: str, par: int, T: str) -> float:
    """Mean over the twins of the re-entry cost in the sibling's home."""
    m = leer(V, brazo, par, T, "early")
    return float((m[0, 1] + m[1, 0]) / 2)


def cruce(m: np.ndarray) -> float:
    """Crossed home advantage (A abroad + B abroad) - (A home + B home): the world and twin
    main effects cancel; > 0 = each twin does better in its own world than its sibling."""
    return float(m[0, 1] + m[1, 0] - m[0, 0] - m[1, 1])


def por_bloque(x: dict, par: int) -> list[dict]:
    """e_early / e_late per block of life (the §K1 readout)."""
    nb, nn, _ = x["vida_bloques"]
    papel = papeles(par)
    n_bloques = len(x["dist"]) // D
    vis = [("babble" if v < nb else "act", papel[x["gemelo"]] if v < nb + nn else papel["X"], v)
           for v in range(n_bloques)]
    return mp.por_visita(x, vis)


def informe(V: dict, pares: tuple, arms: tuple, nombre: str, titulo: str, minutos: float) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    x0 = V[(arms[0], pares[0], "A")]
    nb, nn, ne = x0["vida_bloques"]
    T = x0["T"]
    out("=" * 80)
    out(titulo)
    out("=" * 80)
    out(f"pairs {pares[0]}-{pares[-1]} x {arms} x twins A/B; life = {nb} babble + {nn} childhood at home "
        f"+ {ne} exile blocks of {D}; assays {list(zip(T, x0['bloque']))}; run {minutos:.1f} min "
        f"(median {np.median([x['min'] for x in V.values()]):.1f} min/life)")
    out("")
    out("life: median e_late (last 5 childhood blocks | last 5 exile blocks); stuck act blocks (late > 0.3)")
    for a in arms:
        pb = {(p, g): por_bloque(V[(a, p, g)], p) for p in pares for g in GEMELOS}
        casa = [np.mean([b["late"] for b in pb[key][max(nb, nb + nn - 5): nb + nn]]) for key in pb]
        fuera = [np.mean([b["late"] for b in pb[key][-5:]]) for key in pb]
        stuck = sum(b["late"] > 0.3 for key in pb for b in pb[key] if b["fase"] == "act")
        out(f"{a:>10} | {np.median(casa):.3f} | {np.median(fuera):.3f} | stuck {stuck}")
    out("")
    out("ASSAYS (clones visit each twin's home; medians over pairs)")
    out(f"{'arm':>10} {'T':>3} | early home  abroad  H_early | fe home abroad H_fe | Psi<.85 H | "
        f"probe H | H>0")
    res = {}
    for a in arms:
        for t in T:
            m = {c: [leer(V, a, p, t, c) for p in pares] for c in ("early", "fe", "psi", "sonda")}
            h = {c: [cruce(x) for x in m[c]] for c in m}
            res[(a, t)] = h
            casa = np.median([(x[0, 0] + x[1, 1]) / 2 for x in m["early"]])
            fuera = np.median([(x[0, 1] + x[1, 0]) / 2 for x in m["early"]])
            fc = np.median([(x[0, 0] + x[1, 1]) / 2 for x in m["fe"]])
            ff = np.median([(x[0, 1] + x[1, 0]) / 2 for x in m["fe"]])
            out(f"{a:>10} {t:>3} | {casa:>10.3f} {fuera:>7.3f} {np.median(h['early']):>+8.3f} | "
                f"{fc:>7.3f} {ff:>6.3f} {np.median(h['fe']):>+5.3f} | {np.median(h['psi']):>+9.3f} | "
                f"{np.median(h['sonda']):>+7.3f} | {sum(v > 0 for v in h['early'])}/{len(pares)}")
    out("")
    out("H_early per pair:")
    for a in arms:
        for t in T:
            out(f"  {a:>10} {t:>3}: " + str([round(v, 3) for v in res[(a, t)]["early"]]))
    out("")
    out("self_embedding: ||A - B|| at each assay (median over pairs)")
    for a in arms:
        dd = {t: [float(np.linalg.vector_norm(V[(a, p, 'A')]['yo'][j] - V[(a, p, 'B')]['yo'][j]))
                  for p in pares] for j, t in enumerate(T)}
        out(f"{a:>10} | " + " | ".join(f"{t} {np.median(dd[t]):.3f}" for t in T))
    out("")
    out("probe after the burn-in on each role's regime (median over twins and pairs), at each assay")
    for a in arms:
        for j, t in enumerate(T):
            cel = []
            for etiqueta in ("home", "sibling", "X", "N"):
                vals = []
                for p in pares:
                    pa = papeles(p)
                    for g, otro in (("A", "B"), ("B", "A")):
                        x = V[(a, p, g)]
                        rol = {"home": g, "sibling": otro, "X": "X", "N": "N"}[etiqueta]
                        b = x["bloque"][j]
                        vals.append(x["sonda"][b - 1, pa[rol]] if b > 0 else np.nan)
                cel.append(f"{etiqueta} {np.nanmedian(vals):.3f}")
            out(f"{a:>10} {t:>3} | " + " | ".join(cel))
    out("")
    out("H_fe per pair (error_x4, T2): " + str([round(v, 2) for v in res[("error_x4", T[-1])]["fe"]]))
    out("-" * 80)
    n = len(pares)
    t1, t2 = ("T1", "T2") if "T1" in T else (T[0], T[-1])
    dif = positivos(res[("error_x4", t1)]["early"])
    per = positivos(res[("error_x4", t2)]["early"])
    rec = positivos(res[("error_x4", t2)]["fe"])
    per_k = positivos(res[("kernel", t2)]["early"])
    par = sum(x > y for x, y in zip(res[("error_x4", t2)]["early"], res[("kernel", t2)]["early"]))
    desv = sum(v < 0 for v in res[("kernel", t2)]["early"])
    out(f"SE DIFERENCIA (positive control)  H(T1) > 0, error_x4: {dif}/{n}   "
        f"(kernel {positivos(res[('kernel', t1)]['early'])}/{n})")
    out(f"PERSISTE (primary)                H(T2) > 0, error_x4: {per}/{n}")
    out(f"RECONOCE (secondary)              H_fe(T2) > 0, error_x4: {rec}/{n}")
    out(f"ATTRIBUTION  PERSISTE on kernel: {per_k}/{n}; paired H(T2) error_x4 > kernel: {par}/{n}")
    out(f"(reported) DESVENTAJA  H(T2) < 0 on kernel: {desv}/{n}")
    rig = sum(afuera(V, "error_x4", p, t1) > afuera(V, "kernel", p, t1) for p in pares)
    out(f"RIGIDEZ (secondary in the replication)  T1 cost in the sibling's home, error_x4 > kernel: "
        f"{rig}/{n} (medians {np.median([afuera(V, 'error_x4', p, t1) for p in pares]):.3f} vs "
        f"{np.median([afuera(V, 'kernel', p, t1) for p in pares]):.3f})")
    if n == len(PAIRS):
        out("")
        out(f"VERDICT (pre-registered rule): {veredicto(dif, per, per_k, par)}")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{nombre}_run.txt").write_text("\n".join(lines), encoding="utf-8")
    (RESULTS / f"{nombre}_cruces.json").write_text(
        json.dumps({f"{a}_{t}": h for (a, t), h in res.items()}), encoding="utf-8")


def positivos(v: list[float]) -> int:
    return sum(x > 0 for x in v)


def veredicto(dif: int, per: int, per_k: int, par: int) -> str:
    """The pre-registered §K4 rule."""
    if dif < N_OK:
        return "NO SE DIFERENCIA"
    if per < N_OK:
        return "IDENTIDAD FRAGIL"
    if per_k >= N_OK:
        return "IDENTIDAD (también sin el sueño)"
    if par >= N_OK:
        return "IDENTIDAD (por el sueño)"
    return "IDENTIDAD (sin atribuir)"


def fiel() -> float:
    """A clone continued with the same RNG and world as its original gives the same life."""
    import torch
    torch.set_num_threads(1)
    torch.manual_seed(0)
    k = cx.nuevo_kernel("error_x4", False)
    s = torch.full((4,), 0.25)
    for _ in range(120):
        s = ms.mover(s, k.step(s).action.detach(), 1)
    c, sc = clonar(k), s.clone()
    out = []
    for kern, st in ((k, s), (c, sc)):
        torch.manual_seed(7)
        fe = []
        for _ in range(80):
            r = kern.step(st)
            fe.append(r.free_energy)
            st = ms.mover(st, r.action.detach(), 2)
        out.append(np.array(fe))
    return float(np.abs(out[0] - out[1]).max())


def main_humo() -> None:
    t0 = time.time()
    print(f"clone fidelity, max |fe original - fe clone| over 80 ticks: {fiel()}")
    V = correr(ARMS, (0,), HUMO)
    for a in ARMS:
        for c in ("early", "fe", "psi", "sonda"):
            m = leer(V, a, 0, "T0", c)
            print(f"{a:>10} T0 {c:>6}: twins identical at birth -> |A - B| max "
                  f"{np.abs(m[0] - m[1]).max():.2e}, H {cruce(m):+.2e}")
    informe(V, (0,), ARMS, "mundo_propio_gemelos_humo", "§K4 SMOKE TEST (pair 0, short life)",
            (time.time() - t0) / 60)


def main(pares: tuple, nombre: str, titulo: str) -> None:
    t0 = time.time()
    V = correr(ARMS, pares, ESCALA)
    informe(V, pares, ARMS, nombre, titulo, (time.time() - t0) / 60)


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    if modo == "humo":
        main_humo()
    elif modo == "calibracion":
        main(PAIRS_CAL, "mundo_propio_gemelos_calibracion",
             "§K4 CALIBRATION (pairs 100-102; not test pairs)")
    elif modo == "replica":
        main(tuple(range(12, 24)), "mundo_propio_gemelos_replica",
             "§K4 REPLICATION (pairs 12-23) -- IDENTITY: twins raised in different worlds")
    else:
        main(PAIRS, "mundo_propio_gemelos", "§K4 -- IDENTITY: twins raised in different worlds")

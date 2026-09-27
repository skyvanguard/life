"""
§38 — VALIDACIÓN DEL MOTOR EN GPU: ¿el útero por lotes (orden en damero)
reproduce dos resultados establecidos en CPU (orden asincrónico)?
(docs/PLAN_INTELIGENCIA.md §38; ledger 2026-09-27)

`utero/gpu.py` tiene el VM exactamente igual al de CPU (test), pero el orden
de actualización es otro (damero en dos medios pasos, conflictos de parto al
azar). Es otra encarnación del sustrato; antes de usarla para preguntas
nuevas debe reproducir lo que ya se sabe.

V1 — EL GRADIENTE (§26, CPU: ANTISOL gana en 17/20). Ecología cerrada N = 64,
     congelada, L0 = 1.75, 30000 ticks, 20 semillas; 4 ANTISOL + 4 ESPEJO
     sembrados en las mismas posiciones que en CPU. ANTISOL "gana" si su
     fracción final ≥ 0.25 y ≥ 2× la de ESPEJO.
     ACEPTA V1 si ANTISOL gana en ≥ 15/20 (el veredicto GRADIENTE de §26).
V2 — LA PRIMERA EVOLUCIÓN (§34–§35, CPU: theta_s_solo ADAPTA 10/12 y 10/12,
     w̄_A 0.43 contra 0.38, s̄ 0.71–0.75). N = 512, L0 = 14, 120000 ticks, 12
     semillas, sol seed 0; brazos theta_s_solo (programas congelados, θ y s
     heredables) y nulo (todo fijo). Regla de §27.
     ACEPTA V2 si theta_s_solo ADAPTA (w̄_A tardío/temprano y nivel > nulo en
     ≥ 75% de los pares, p signo < 0.05).
VEREDICTO: MOTOR VALIDADO si V1 y V2 se aceptan. Si alguno falla, el motor
en GPU no se usa para preguntas nuevas hasta entender la diferencia (el
damero cambia la dinámica) y se dice así.

    PYTHONPATH=src python experiments/utero/exp_utero_gpu_validacion.py
"""

from __future__ import annotations

import importlib.util
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.gpu import UteroGPU  # noqa: E402
from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
TRANSITORIO = 6000
MIN_HAMBRUNAS = 4
RESULTS = HERE.parents[1] / "results"
CKPT = HERE.parents[1] / "data" / "ckpt"          # gitignorado; puntos de control reanudables
NAME = "utero_gpu_validacion"
V1 = dict(n=64, ticks=30000, seeds=list(range(20)), l0=1.75, sembradas=4)
V2 = dict(n=512, ticks=120000, seeds=list(range(12)), l0=14.0, eps=0.05)


def _programas():
    spec = importlib.util.spec_from_file_location("g", HERE / "exp_utero_gradiente.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ANTISOL, mod.ESPEJO


def signo_p(k: int, n: int) -> float:
    return float(sum(math.comb(n, j) * 0.5 ** n for j in range(k, n + 1))) if n > 0 else 1.0


def por_hambruna(ser: dict, sol: Sol, ticks: int, clave: str) -> np.ndarray:
    """(H, B): media de la serie en cada hambruna madura."""
    out = []
    for nombre, ini, fin in sol.estaciones:
        if nombre == "A" and ini >= TRANSITORIO and fin <= ticks:
            out.append(np.nanmean(ser[clave][ini:fin], axis=0))
    return np.array(out)


def razon(x: np.ndarray) -> np.ndarray:
    h = x.shape[0] // 2
    if h < MIN_HAMBRUNAS:
        return np.full(x.shape[1], np.nan)
    return np.nanmean(x[h:], axis=0) / np.nanmean(x[:h], axis=0)


def validar_v1(out) -> bool:
    antisol, espejo = _programas()
    c = V1
    cache = CKPT / f"{NAME}_v1.npz"
    if cache.exists():                       # V1 ya medida (la corrida se cortó en V2): no se repite
        z = np.load(cache)
        if list(z["seeds"]) == c["seeds"]:
            return _informar_v1(out, c, z["fa"], z["fe"], z["vivas"], float(z["segundos"]), " [de cache]")
    sol = Sol(seed=0, ticks=c["ticks"], regimenes=REGS)
    g = UteroGPU(c["seeds"], c["n"], np.tile(sol.serie, (len(c["seeds"]), 1)), luz_finita=c["l0"], congelado=True)
    ta = torch.as_tensor(antisol, device=g.device)
    te = torch.as_tensor(espejo, device=g.device)
    for i, s in enumerate(c["seeds"]):
        pos = np.random.default_rng(5000 + s).permutation(c["n"])
        for j in pos[:c["sembradas"]]:
            g.code[i, j] = ta
        for j in pos[c["sembradas"]:2 * c["sembradas"]]:
            g.code[i, j] = te
    t0 = time.time()
    for _ in range(c["ticks"]):
        g.step()
    n = g.alive.sum(dim=1).clamp_min(1).double()
    fa = (((g.code == ta).all(dim=-1).all(dim=-1)) & g.alive).sum(dim=1).double() / n
    fe = (((g.code == te).all(dim=-1).all(dim=-1)) & g.alive).sum(dim=1).double() / n
    fa, fe, vivas = fa.cpu().numpy(), fe.cpu().numpy(), g.alive.sum(dim=1).cpu().numpy()
    CKPT.mkdir(parents=True, exist_ok=True)
    np.savez(CKPT / f"{NAME}_v1.npz", seeds=np.array(c["seeds"]), vivas=vivas, fa=fa, fe=fe, segundos=time.time() - t0)
    return _informar_v1(out, c, fa, fe, vivas, time.time() - t0, "")


def _informar_v1(out, c, fa, fe, vivas, seg, nota) -> bool:
    gana = [(a >= 0.25 and a >= 2 * max(e, 1e-9)) for a, e in zip(fa, fe)]
    out(f"V1 gradiente (N={c['n']}, congelado, L0={c['l0']}, {c['ticks']} ticks, {len(c['seeds'])} semillas) -- {seg:.0f} s{nota}")
    out(f"  {'seed':>4} {'vivas':>6} {'antisol':>8} {'espejo':>7} {'gana':>5}")
    for i, s in enumerate(c["seeds"]):
        out(f"  {s:>4} {vivas[i]:>6} {fa[i]:>8.2f} {fe[i]:>7.2f} {'si' if gana[i] else 'no':>5}")
    out(f"  ANTISOL gana en {sum(gana)}/{len(gana)} (CPU §26: 17/20); medianas antisol {np.median(fa):.2f}, espejo {np.median(fe):.2f}")
    ok = sum(gana) >= 15
    out(f"  => V1 {'ACEPTADA' if ok else 'RECHAZADA'}")
    return ok


def validar_v2(out) -> bool:
    c = V2
    ns = len(c["seeds"])
    sol = Sol(seed=0, ticks=c["ticks"], regimenes=REGS)
    seeds = c["seeds"] * 2                                   # [theta_s_solo..., nulo...]
    fijo = [False] * ns + [True] * ns
    g = UteroGPU(seeds, c["n"], np.tile(sol.serie, (2 * ns, 1)), luz_finita=c["l0"], congelado=True,
                 parametros=c["eps"], escala=True, theta_fijo=fijo)
    t0 = time.time()
    CKPT.mkdir(parents=True, exist_ok=True)
    ser = g.correr(c["ticks"], checkpoint=str(CKPT / f"{NAME}_v2.pt"), cada=5000)
    wA = por_hambruna(ser, sol, c["ticks"], "w")
    sA = por_hambruna(ser, sol, c["ticks"], "s")
    bA = por_hambruna(ser, sol, c["ticks"], "banda")
    nivel, raz = np.nanmean(wA, axis=0), razon(wA)
    vivo, nulo = slice(0, ns), slice(ns, 2 * ns)
    out(f"V2 primera evolucion (N={c['n']}, L0={c['l0']}, {c['ticks']} ticks, {ns} semillas x 2 brazos) -- {time.time() - t0:.0f} s")
    out(f"  {'brazo':<13} {'vivas med':>9} {'w_A nivel':>9} {'w_A t/t':>8} {'banda':>6} {'s_A':>5}")
    for nombre, sl in (("theta_s_solo", vivo), ("nulo", nulo)):
        out(f"  {nombre:<13} {np.median(np.nanmedian(ser['vivas'][TRANSITORIO:, sl], axis=0)):>9.0f} {np.nanmedian(nivel[sl]):>9.3f} "
            f"{np.nanmedian(raz[sl]):>8.2f} {np.nanmedian(np.nanmean(bA, axis=0)[sl]):>6.2f} {np.nanmedian(np.nanmean(sA, axis=0)[sl]):>5.2f}")
    pr = [(a, b) for a, b in zip(raz[vivo], raz[nulo]) if not (np.isnan(a) or np.isnan(b))]
    pn = [(a, b) for a, b in zip(nivel[vivo], nivel[nulo]) if not (np.isnan(a) or np.isnan(b))]
    kr, kn = sum(1 for a, b in pr if a > b), sum(1 for a, b in pn if a > b)
    ok = len(pr) >= 8 and kr / len(pr) >= 0.75 and signo_p(kr, len(pr)) < 0.05 and len(pn) >= 8 and kn / len(pn) >= 0.75
    out(f"  w_A tardio/temprano > nulo en {kr}/{len(pr)} (p signo {signo_p(kr, len(pr)):.3f}); nivel > nulo en {kn}/{len(pn)} "
        f"(CPU §34: 10/12 y 10/12; §35: 10/12 y 10/12)")
    out(f"  => V2 {'ACEPTADA (ADAPTA)' if ok else 'RECHAZADA'}")
    return ok


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("VALIDACION DEL MOTOR EN GPU (orden en damero) contra dos resultados establecidos en CPU")
    out("=" * 80)
    out(f"dispositivo: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'}; veredicto pre-registrado (docstring)")
    out("")
    ok1 = validar_v1(out)
    out("")
    ok2 = validar_v2(out)
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    out("=> MOTOR VALIDADO: reproduce el gradiente y la primera evolucion." if (ok1 and ok2)
        else f"=> MOTOR NO VALIDADO (V1 {'ok' if ok1 else 'falla'}, V2 {'ok' if ok2 else 'falla'}): no se usa para preguntas nuevas hasta entender la diferencia.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

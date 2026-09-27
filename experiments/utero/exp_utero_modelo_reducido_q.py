"""
§40 — MODELO REDUCIDO CON UNA PERILLA DE HISTORIA DE VIDA: propensión al
parto condicionada al nivel de ingreso. (docs/PLAN_INTELIGENCIA.md §40; ledger
2026-09-27)

QUÉ ES Y QUÉ NO. NO es el útero: es el modelo reducido de §39b (ecología del
útero cerrado, perillas heredables, salida de la física reemplazada por su
estadística) con una perilla más. Un positivo aquí es una PREDICCIÓN.

MOTIVO. §39b: con θ, s, g la población no codifica el orden (local < foráneo
12/24 y 15/24). La tendencia de la energía da la misma señal en la estación
templada venga después hambruna o abundancia; lo que el orden cambia es qué
conviene HACER allí. Perilla: tres propensiones heredables al parto, q_bajo,
q_medio, q_alto ∈ [0, 1], elegidas por el ingreso propio del tick relativo
al mantenimiento (bajo: < 1×; medio: 1–3.5×; alto: ≥ 3.5×; con ~125 vivas
corresponden a hambruna A, templada C y abundancia B). Nacen en 1 (como el
modelo de §39b) y se heredan con ±ε. La probabilidad de intentar un parto es
P_PARTO · q[nivel].

PREDICCIONES (escritas antes de correr):
  P1  bajo clima (a C le sigue A) la selección baja q_medio más que bajo
      ciclo2 (a C le sigue B): q_medio(clima) < q_medio(ciclo2) en ≥ 75% de
      las semillas pareadas, p signo < 0.05.
  P2  trasplante recíproco con perillas fijas y otro calendario (sol seed 1),
      criterio LOCAL CONTRA FORÁNEO sobre la mortalidad per cápita en la
      hambruna: local < foráneo en ≥ 75% de los pares, p signo < 0.05, razón
      mediana ≤ 0.8, en AMBOS destinos.
  PREDICE VESTIGIO si P2 cumple en ambos destinos (y P1 da el mecanismo);
  ASIMÉTRICO si P2 en un destino; NADA si en ninguno. Secundaria: vivas
  medias en el ensayo, local contra foráneo (la aptitud incluye los partos).

    PYTHONPATH=src python experiments/utero/exp_utero_modelo_reducido_q.py
"""

from __future__ import annotations

import importlib.util
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.sol import Sol  # noqa: E402

_spec = importlib.util.spec_from_file_location("base", HERE / "exp_utero_modelo_reducido.py")
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)

N, W = B.N, B.W
T_EVOL, T_ENSAYO = B.T_EVOL, B.T_ENSAYO
UMBRALES = (1.0, 3.5)                  # ingreso / mantenimiento: bajo | medio | alto
RESULTS = HERE.parents[1] / "results"
NAME = "utero_modelo_reducido_q"


class ModeloQ(B.Modelo):
    def __init__(self, w: int, rng: np.random.Generator):
        super().__init__(w, rng)
        self.q = np.ones((w, N, 3))
        self.cuenta = np.zeros((3, 3))          # [estación A,B,C][nivel]: sanidad de los niveles

    def copia(self, veces: int) -> ModeloQ:
        m = ModeloQ.__new__(ModeloQ)
        m.rng = self.rng
        for k in ("alive", "theta", "s", "g", "e", "el", "v", "q"):
            setattr(m, k, np.concatenate([getattr(self, k)] * veces, axis=0).copy())
        m.cuenta = np.zeros((3, 3))
        return m

    def paso(self, vac: np.ndarray, fijo: bool, est: np.ndarray | None = None) -> tuple:
        al = self.alive
        d = np.abs(self.v - vac)
        w = np.where(al, np.minimum(d, 1.0 - d) + 0.05, 0.0)
        tot = w.sum(axis=1, keepdims=True)
        ing = np.where(tot > 0, B.L0 * vac * w / np.maximum(tot, 1e-300), 0.0)
        nivel = (ing / B.E_MANT >= UMBRALES[0]).astype(int) + (ing / B.E_MANT >= UMBRALES[1]).astype(int)
        if getattr(self, "forzado", None) is not None:      # oráculo (§41): el nivel es la estación verdadera
            nivel = np.broadcast_to(np.asarray(self.forzado)[:, None], al.shape).copy()
        if est is not None:
            for k in range(3):
                m_k = al & (est[:, None] == k)
                if m_k.any():
                    self.cuenta[k] += np.bincount(nivel[m_k], minlength=3)
        th = self.theta + self.g * np.tanh((self.el - self.e) / B.E0)
        y = self.rng.random(al.shape)
        self.v = np.where(al, (th + self.s * y) % 1.0, self.v)
        e = self.e - B.E_MANT + ing
        muere = al & (e <= 0.0)
        al = al & ~muere
        self.e = np.where(al, e, 0.0)
        self.el = np.where(al, self.el + (self.e - self.el) / B.TAU, self.el)
        qn = np.take_along_axis(self.q, nivel[..., None], axis=2)[..., 0]
        intenta = al & (self.rng.random(al.shape) < B.P_PARTO * qn) & (self.e > B.E_COSTO)
        self.e = np.where(intenta, self.e - B.E_COSTO, self.e)
        lado = self.rng.random(al.shape) < 0.5
        for der in (True, False):
            madre = intenta & (lado == der)
            llega = np.zeros_like(al)
            if der:
                llega[:, 1:] = madre[:, :-1]
            else:
                llega[:, :-1] = madre[:, 1:]
            llega &= ~al
            if not llega.any():
                continue
            src = np.roll(np.arange(N), 1 if der else -1)
            eh = B.E_PARTO * self.e[:, src]

            def pert(eps, forma=al.shape):
                return 0.0 if fijo else eps * (2.0 * self.rng.random(forma) - 1.0)

            self.theta = np.where(llega, (self.theta[:, src] + pert(B.EPS)) % 1.0, self.theta)
            self.s = np.where(llega, np.clip(self.s[:, src] + pert(B.EPS), 0.0, 1.0), self.s)
            self.g = np.where(llega, np.clip(self.g[:, src] + pert(B.EPS_G), -2.0, 2.0), self.g)
            self.q = np.where(llega[..., None], np.clip(self.q[:, src] + pert(B.EPS, (*al.shape, 3)), 0.0, 1.0), self.q)
            self.v = np.where(llega, self.v[:, src], self.v)
            self.e = np.where(llega, eh, self.e)
            self.el = np.where(llega, eh, self.el)
            dona = np.zeros_like(al)
            if der:
                dona[:, :-1] = llega[:, 1:]
            else:
                dona[:, 1:] = llega[:, :-1]
            self.e = np.where(dona, self.e - B.E_PARTO * self.e, self.e)
            al = al | llega
        par = al[:, :-1] & al[:, 1:]
        flujo = np.where(par, B.E_DIF * 0.5 * (self.e[:, :-1] - self.e[:, 1:]), 0.0)
        self.e[:, :-1] -= flujo
        self.e[:, 1:] += flujo
        self.alive = al
        return muere.sum(axis=1), al.sum(axis=1)


def estaciones_por_tick(sol: Sol, ticks: int) -> np.ndarray:
    e = np.zeros(ticks, dtype=int)
    for nombre, ini, fin in sol.estaciones:
        e[ini:min(fin, ticks)] = "ABC".index(nombre)
    return e


def correr(m: ModeloQ, soles: np.ndarray, ticks: int, fijo: bool, est: np.ndarray | None = None) -> tuple:
    muertes = np.zeros((ticks, soles.shape[0]), dtype=np.float32)
    vivas = np.zeros_like(muertes)
    for t in range(ticks):
        mu, vi = m.paso(soles[:, t:t + 1], fijo, None if est is None else est[:, t])
        muertes[t], vivas[t] = mu, vi
    return muertes, vivas


def main() -> None:
    lines: list[str] = []

    def out(x: str = "") -> None:
        print(x, flush=True)
        lines.append(x)

    out("=" * 80)
    out("MODELO REDUCIDO + PERILLA DE HISTORIA DE VIDA (no es el utero): propension al parto por nivel de ingreso")
    out("=" * 80)
    out(f"N={N}; {W} mundos por origen; evolucion {T_EVOL}, ensayo {T_ENSAYO}; umbrales de ingreso/mantenimiento {UMBRALES}")
    out("predicciones pre-registradas (docstring)")
    out("")
    rng = np.random.default_rng(2027)
    sol1 = {o: Sol(seed=B.SOL_EVOL, ticks=T_EVOL, orden=r, regimenes=B.REGS) for o, r in B.ORIGENES.items()}
    soles1 = np.concatenate([np.tile(sol1[o].serie, (W, 1)) for o in B.ORIGENES])
    est1 = np.concatenate([np.tile(estaciones_por_tick(sol1[o], T_EVOL), (W, 1)) for o in B.ORIGENES])
    m = ModeloQ(W * len(B.ORIGENES), rng)
    t0 = time.time()
    correr(m, soles1, T_EVOL, fijo=False, est=est1)
    out(f"fase 1 (evolucion): {(time.time() - t0) / 60:.1f} min")
    c = m.cuenta / np.maximum(m.cuenta.sum(axis=1, keepdims=True), 1)
    out("  sanidad de los niveles (fraccion de celda-ticks por estacion en cada nivel de ingreso):")
    for k, nom in enumerate("ABC"):
        out(f"    estacion {nom}: bajo {c[k, 0]:.2f}  medio {c[k, 1]:.2f}  alto {c[k, 2]:.2f}")
    qm = {}
    out(f"  {'origen':<10} {'vivas':>6} {'q_bajo':>7} {'q_medio':>8} {'q_alto':>7} {'s media':>8} {'g media':>8}")
    for i, o in enumerate(B.ORIGENES):
        sl = slice(i * W, (i + 1) * W)
        al = m.alive[sl]
        den = np.maximum(al.sum(axis=1), 1)
        qm[o] = (m.q[sl] * al[..., None]).sum(axis=1) / den[:, None]            # (W, 3) por mundo
        out(f"  {o:<10} {np.median(al.sum(axis=1)):>6.0f} {np.median(qm[o][:, 0]):>7.2f} {np.median(qm[o][:, 1]):>8.2f} "
            f"{np.median(qm[o][:, 2]):>7.2f} {m.s[sl][al].mean():>8.2f} {m.g[sl][al].mean():>8.3f}")
    k1 = int((qm["clima"][:, 1] < qm["ciclo2"][:, 1]).sum())
    p1 = B.signo_p(k1, W)
    ok1 = k1 / W >= 0.75 and p1 < 0.05
    out(f"  P1: q_medio(clima) < q_medio(ciclo2) en {k1}/{W} (p signo {p1:.3f}) -> {'si' if ok1 else 'no'}")
    out("")
    sol2 = {d: Sol(seed=B.SOL_ENSAYO, ticks=T_ENSAYO, orden=r, regimenes=B.REGS) for d, r in B.DESTINOS.items()}
    nb = W * len(B.ORIGENES)
    soles2 = np.concatenate([np.tile(sol2[d].serie, (nb, 1)) for d in B.DESTINOS])
    h = m.copia(len(B.DESTINOS))
    t0 = time.time()
    mu, vi = correr(h, soles2, T_ENSAYO, fijo=True)
    out(f"fase 2 (ensayo, perillas fijas): {(time.time() - t0) / 60:.1f} min")
    pc, viv = {}, {}
    for j, d in enumerate(B.DESTINOS):
        for i, o in enumerate(B.ORIGENES):
            sl = slice(j * nb + i * W, j * nb + (i + 1) * W)
            pc[(o, d)] = B.pc_hambruna(mu, vi, sol2[d], T_ENSAYO, sl, B.TRANS_ENSAYO)
            viv[(o, d)] = vi[B.TRANS_ENSAYO:, sl].mean(axis=0)
    out("  mortalidad per capita en la hambruna | vivas medias (medianas), origen -> destino:")
    out(f"  {'origen':<10} " + " ".join(f"{'-> ' + d:>22}" for d in B.DESTINOS))
    for o in B.ORIGENES:
        out(f"  {o:<10} " + " ".join(f"{np.nanmedian(pc[(o, d)]):>12.3f} | {np.median(viv[(o, d)]):>7.0f}" for d in B.DESTINOS))
    out("")
    out("-" * 80)
    out("P2. LOCAL CONTRA FORANEO (dentro de cada destino, pareado por semilla)")
    local = {}
    for d, foraneo in (("clima", "ciclo2"), ("ciclo2", "clima")):
        pr = [(x, y) for x, y in zip(pc[(d, d)], pc[(foraneo, d)]) if not (np.isnan(x) or np.isnan(y))]
        k = sum(1 for x, y in pr if x < y)
        raz = float(np.median([x / y if y > 0 else np.nan for x, y in pr])) if pr else float("nan")
        local[d] = len(pr) >= 8 and k / len(pr) >= 0.75 and B.signo_p(k, len(pr)) < 0.05 and raz <= 0.8
        kv = int((viv[(d, d)] > viv[(foraneo, d)]).sum())
        out(f"  destino {d:<7}: mortalidad local < foraneo en {k}/{len(pr)} (p signo {B.signo_p(k, len(pr)):.3f}); razon mediana {raz:.2f} "
            f"-> {'si' if local[d] else 'no'};  vivas local > foraneo en {kv}/{W} (p signo {B.signo_p(kv, W):.3f})")
    out("")
    out("=" * 80)
    out("PREDICCION (regla escrita antes de correr)")
    if local["clima"] and local["ciclo2"]:
        out(f"=> PREDICE VESTIGIO: ventaja local en ambos destinos (P1 {'cumple' if ok1 else 'no cumple'}). Justifica implementar la perilla en el motor de GPU y correrla en el sustrato real.")
    elif local["clima"] or local["ciclo2"]:
        out(f"=> PREDICE ASIMETRICO: ventaja local en un solo destino (P1 {'cumple' if ok1 else 'no cumple'}).")
    else:
        out(f"=> PREDICE NADA: sin ventaja local en ningun destino (P1 {'cumple' if ok1 else 'no cumple'}).")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

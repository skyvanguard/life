"""
§39b — MODELO REDUCIDO DE PERILLAS: el trasplante recíproco, predicho en un
modelo sin programas. (docs/PLAN_INTELIGENCIA.md §39; ledger 2026-09-27)

QUÉ ES Y QUÉ NO. NO es el útero. En los brazos donde el útero evoluciona
(§34–§35) los programas están CONGELADOS y su salida es pseudoaleatoria
(§28): lo que evoluciona son las perillas heredables de expresión (θ, s, g).
Este modelo conserva esa parte y reemplaza la física por su estadística: la
salida de cada celda es y ~ U(0,1) independiente en cada tick. Todo lo demás
es la ecología del útero cerrado: materia visible (θ + g·tanh((ē − e)/e0) +
s·y) mod 1; luz finita L0·sol repartida por peso |v − sol| + 0.05;
mantenimiento; muerte por energía ≤ 0; parto costoso hacia un lugar vacío
vecino, la hija hereda la mitad de la energía y las perillas con ±ε;
difusión de energía entre vecinas. Manos del modelo: y iid (sin dinámica de
programa, sin sonda, sin invasión), intento de parto con probabilidad fija
por tick. Numpy, un núcleo, sin GPU. Sirve para PREDECIR qué dará §39 en el
sustrato real; un positivo aquí es una predicción, no un vestigio.

DISEÑO. El de §39: N = 256 lugares (L0 = 7: la misma luz por lugar), 24
mundos por origen. Fase 1: evolución 120000 ticks (sol seed 0) bajo clima,
ciclo2 y permutado. Fase 2: cada población se copia y se ensaya 40000 ticks
bajo clima y bajo ciclo2 con OTRO calendario (sol seed 1) y las perillas
FIJAS. Lectura y regla idénticas a §39: mortalidad per cápita en la
hambruna del ensayo; VENTAJA DE CASA si en casa < fuera en ≥ 75% de los
pares (n ≥ 8), p signo < 0.05, razón mediana ≤ 0.8.
  PREDICE VESTIGIO  si ambos orígenes tienen ventaja de casa.
  PREDICE ENTORNO   si gana el mismo calendario sea cual sea el origen.
  PREDICE NADA      en otro caso.
CORRIDA 1 (regla original): NADA por la letra; clima es más benigno que
ciclo2 para cualquier origen (control permutado 22/24): "en casa contra
fuera" confunde adaptación con calidad del entorno. CORRIDA 2: se agrega el
criterio LOCAL CONTRA FORÁNEO (Kawecki y Ebert 2004), que es el diagnóstico;
para este modelo es una lectura POST HOC (se declara); para §39 en el
sustrato real queda pre-registrada como primaria. PREDICE VESTIGIO si hay
ventaja local en ambos destinos; ASIMÉTRICO si en uno; NADA si en ninguno.

    PYTHONPATH=src python experiments/utero/exp_utero_modelo_reducido.py
"""

from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

N = 256
W = 24
T_EVOL, T_ENSAYO = 120000, 40000
SOL_EVOL, SOL_ENSAYO = 0, 1
L0, E0, E_MANT, E_DIF, E_PARTO, E_COSTO = 7.0, 2.0, 0.01, 0.25, 0.5, 1.0
EPS, EPS_G, TAU, P_PARTO = 0.05, 0.05, 200.0, 0.02
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
ORIGENES = {"clima": "ciclico", "ciclo2": "ciclico_inverso", "permutado": "permutado"}
DESTINOS = {"clima": "ciclico", "ciclo2": "ciclico_inverso"}
TRANS_ENSAYO = 4000
RESULTS = HERE.parents[1] / "results"
NAME = "utero_modelo_reducido"


class Modelo:
    def __init__(self, w: int, rng: np.random.Generator):
        self.rng = rng
        self.alive = np.ones((w, N), dtype=bool)
        self.theta = rng.uniform(0, 1, (w, N))
        self.s = np.ones((w, N))
        self.g = np.zeros((w, N))
        self.e = np.full((w, N), E0)
        self.el = np.full((w, N), E0)
        self.v = rng.uniform(0, 1, (w, N))

    def copia(self, veces: int) -> Modelo:
        m = Modelo.__new__(Modelo)
        m.rng = self.rng
        for k in ("alive", "theta", "s", "g", "e", "el", "v"):
            setattr(m, k, np.concatenate([getattr(self, k)] * veces, axis=0).copy())
        return m

    def paso(self, vac: np.ndarray, fijo: bool) -> tuple:
        """vac: (W, 1). Devuelve (muertes, vivas) por mundo."""
        al = self.alive
        d = np.abs(self.v - vac)
        w = np.where(al, np.minimum(d, 1.0 - d) + 0.05, 0.0)
        tot = w.sum(axis=1, keepdims=True)
        ing = np.where(tot > 0, L0 * vac * w / np.maximum(tot, 1e-300), 0.0)
        th = self.theta + self.g * np.tanh((self.el - self.e) / E0)      # expresión ANTES de la energía del tick
        y = self.rng.random(al.shape)
        self.v = np.where(al, (th + self.s * y) % 1.0, self.v)
        e = self.e - E_MANT + ing
        muere = al & (e <= 0.0)
        al = al & ~muere
        self.e = np.where(al, e, 0.0)
        self.el = np.where(al, self.el + (self.e - self.el) / TAU, self.el)
        # partos: intento con probabilidad fija, hacia un lado al azar, si el lugar está vacío
        intenta = al & (self.rng.random(al.shape) < P_PARTO) & (self.e > E_COSTO)
        self.e = np.where(intenta, self.e - E_COSTO, self.e)             # el parto cuesta aunque fracase
        lado = self.rng.random(al.shape) < 0.5                           # True = derecha
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
            src = np.roll(np.arange(N), 1 if der else -1)                # índice de la madre de cada lugar
            em = self.e[:, src]
            eh = E_PARTO * em
            pert = (lambda eps: 0.0) if fijo else (lambda eps: eps * (2.0 * self.rng.random(al.shape) - 1.0))
            self.theta = np.where(llega, (self.theta[:, src] + pert(EPS)) % 1.0, self.theta)
            self.s = np.where(llega, np.clip(self.s[:, src] + pert(EPS), 0.0, 1.0), self.s)
            self.g = np.where(llega, np.clip(self.g[:, src] + pert(EPS_G), -2.0, 2.0), self.g)
            self.v = np.where(llega, self.v[:, src], self.v)
            self.e = np.where(llega, eh, self.e)
            self.el = np.where(llega, eh, self.el)
            dona = np.zeros_like(al)
            if der:
                dona[:, :-1] = llega[:, 1:]
            else:
                dona[:, 1:] = llega[:, :-1]
            self.e = np.where(dona, self.e - E_PARTO * self.e, self.e)
            al = al | llega
        par = al[:, :-1] & al[:, 1:]
        flujo = np.where(par, E_DIF * 0.5 * (self.e[:, :-1] - self.e[:, 1:]), 0.0)
        self.e[:, :-1] -= flujo
        self.e[:, 1:] += flujo
        self.alive = al
        return muere.sum(axis=1), al.sum(axis=1)


def correr(m: Modelo, soles: np.ndarray, ticks: int, fijo: bool) -> tuple:
    muertes = np.zeros((ticks, soles.shape[0]), dtype=np.float32)
    vivas = np.zeros_like(muertes)
    for t in range(ticks):
        mu, vi = m.paso(soles[:, t:t + 1], fijo)
        muertes[t], vivas[t] = mu, vi
    return muertes, vivas


def pc_hambruna(muertes, vivas, sol: Sol, ticks: int, cols: slice, desde: int) -> np.ndarray:
    pc = []
    for nombre, ini, fin in sol.estaciones:
        if nombre == "A" and ini >= desde and fin <= ticks:
            v = vivas[ini:fin, cols].mean(axis=0)
            pc.append(muertes[ini:fin, cols].sum(axis=0) / np.where(v > 0, v, np.nan))
    return np.nanmean(np.array(pc), axis=0)


def signo_p(k: int, n: int) -> float:
    return float(sum(math.comb(n, j) * 0.5 ** n for j in range(k, n + 1))) if n > 0 else 1.0


def main() -> None:
    lines: list[str] = []

    def out(x: str = "") -> None:
        print(x, flush=True)
        lines.append(x)

    out("=" * 80)
    out("MODELO REDUCIDO DE PERILLAS (no es el utero): trasplante reciproco predicho sin programas")
    out("=" * 80)
    out(f"N={N}; L0={L0}; {W} mundos por origen; evolucion {T_EVOL} (sol {SOL_EVOL}), ensayo {T_ENSAYO} (sol {SOL_ENSAYO}); eps={EPS}; eps_g={EPS_G}; p_parto={P_PARTO}")
    out("regla pre-registrada (docstring): la de §39")
    out("")
    rng = np.random.default_rng(2026)
    sol1 = {o: Sol(seed=SOL_EVOL, ticks=T_EVOL, orden=r, regimenes=REGS) for o, r in ORIGENES.items()}
    soles1 = np.concatenate([np.tile(sol1[o].serie, (W, 1)) for o in ORIGENES])
    m = Modelo(W * len(ORIGENES), rng)
    t0 = time.time()
    correr(m, soles1, T_EVOL, fijo=False)
    out(f"fase 1 (evolucion): {(time.time() - t0) / 60:.1f} min")
    out(f"  {'origen':<10} {'vivas':>6} {'g media':>8} {'g>0':>5} {'s media':>8} {'theta (media circular)':>23} {'R_theta':>8}")
    for i, o in enumerate(ORIGENES):
        sl = slice(i * W, (i + 1) * W)
        al = m.alive[sl]
        ang = 2 * math.pi * m.theta[sl][al]
        c, s_ = np.cos(ang).mean(), np.sin(ang).mean()
        out(f"  {o:<10} {np.median(al.sum(axis=1)):>6.0f} {m.g[sl][al].mean():>8.3f} {(m.g[sl][al] > 0).mean():>5.2f} "
            f"{m.s[sl][al].mean():>8.2f} {(math.atan2(s_, c) / (2 * math.pi)) % 1.0:>23.2f} {math.hypot(c, s_):>8.2f}")
    out("")
    sol2 = {d: Sol(seed=SOL_ENSAYO, ticks=T_ENSAYO, orden=r, regimenes=REGS) for d, r in DESTINOS.items()}
    nb = W * len(ORIGENES)
    soles2 = np.concatenate([np.tile(sol2[d].serie, (nb, 1)) for d in DESTINOS])
    h = m.copia(len(DESTINOS))
    t0 = time.time()
    mu, vi = correr(h, soles2, T_ENSAYO, fijo=True)
    out(f"fase 2 (ensayo, perillas fijas): {(time.time() - t0) / 60:.1f} min")
    pc = {}
    for j, d in enumerate(DESTINOS):
        for i, o in enumerate(ORIGENES):
            sl = slice(j * nb + i * W, j * nb + (i + 1) * W)
            pc[(o, d)] = pc_hambruna(mu, vi, sol2[d], T_ENSAYO, sl, TRANS_ENSAYO)
    out("  mortalidad per capita en la hambruna (mediana), origen -> destino:")
    out(f"  {'origen':<10} " + " ".join(f"{'-> ' + d:>12}" for d in DESTINOS))
    for o in ORIGENES:
        out(f"  {o:<10} " + " ".join(f"{np.nanmedian(pc[(o, d)]):>12.3f}" for d in DESTINOS))
    out("")
    out("-" * 80)
    out("VENTAJA DE CASA (pareado por mundo)")
    casa = {}
    for o, propio, ajeno in (("clima", "clima", "ciclo2"), ("ciclo2", "ciclo2", "clima")):
        pr = [(x, y) for x, y in zip(pc[(o, propio)], pc[(o, ajeno)]) if not (np.isnan(x) or np.isnan(y))]
        k = sum(1 for x, y in pr if x < y)
        raz = float(np.median([x / y if y > 0 else np.nan for x, y in pr])) if pr else float("nan")
        casa[o] = len(pr) >= 8 and k / len(pr) >= 0.75 and signo_p(k, len(pr)) < 0.05 and raz <= 0.8
        out(f"  origen {o:<7}: en casa < fuera en {k}/{len(pr)} (p signo {signo_p(k, len(pr)):.3f}); razon mediana {raz:.2f} -> {'si' if casa[o] else 'no'}")
    prp = [(x, y) for x, y in zip(pc[("permutado", "clima")], pc[("permutado", "ciclo2")]) if not (np.isnan(x) or np.isnan(y))]
    out(f"  control (origen permutado, sin casa): clima < ciclo2 en {sum(1 for x, y in prp if x < y)}/{len(prp)} (el efecto del ENTORNO solo)")
    out("")
    out("-" * 80)
    out("LOCAL CONTRA FORANEO (dentro de cada destino, pareado por semilla; criterio de Kawecki y Ebert 2004)")
    local = {}
    for d, foraneo in (("clima", "ciclo2"), ("ciclo2", "clima")):
        pr = [(x, y) for x, y in zip(pc[(d, d)], pc[(foraneo, d)]) if not (np.isnan(x) or np.isnan(y))]
        k = sum(1 for x, y in pr if x < y)
        raz = float(np.median([x / y if y > 0 else np.nan for x, y in pr])) if pr else float("nan")
        local[d] = len(pr) >= 8 and k / len(pr) >= 0.75 and signo_p(k, len(pr)) < 0.05 and raz <= 0.8
        prp2 = [(x, y) for x, y in zip(pc[(d, d)], pc[("permutado", d)]) if not (np.isnan(x) or np.isnan(y))]
        kp2 = sum(1 for x, y in prp2 if x < y)
        out(f"  destino {d:<7}: local < foraneo ({foraneo}) en {k}/{len(pr)} (p signo {signo_p(k, len(pr)):.3f}); razon mediana {raz:.2f} "
            f"-> {'si' if local[d] else 'no'};  local < origen permutado en {kp2}/{len(prp2)}")
    out("")
    out("=" * 80)
    out("PREDICCION (regla escrita antes de correr; criterio primario: local contra foraneo en AMBOS destinos)")
    if local["clima"] and local["ciclo2"]:
        out("=> PREDICE VESTIGIO: en el modelo, en cada destino la poblacion local supera a la foranea. Justifica correr §39 en el sustrato real.")
    elif local["clima"] != local["ciclo2"]:
        out("=> PREDICE ASIMETRICO: ventaja local en un solo destino.")
    else:
        out("=> PREDICE NADA: ninguna poblacion tiene ventaja local en el modelo.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

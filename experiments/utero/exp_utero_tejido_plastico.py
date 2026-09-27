"""
§45 — TEJIDO PLÁSTICO (prototipo): ¿aprende en vida, y generaliza, un tejido
cuya regla es continua y cambia según el propio bienestar de cada celda?
(docs/PLAN_INTELIGENCIA.md §44–§45; ledger 2026-09-27)

QUÉ ES Y QUÉ NO. Es un prototipo fuera del útero (numpy, un núcleo), con la
misma ecología cerrada: una línea de N lugares, el vacío lleva la materia del
sol, luz finita L0·sol repartida por distancia de la materia al sol,
mantenimiento, muerte por energía, parto costoso hacia un lugar vacío. Lo que
cambia es la física de la celda: en lugar de un programa discreto de 16
instrucciones, una regla CONTINUA (una red mínima de pesos W), para tener
localidad (§44–§45: un cambio chico de la regla produce un cambio chico de lo
que hace).

LA CELDA. Lee x = [cos, sen de la materia izquierda, propia y derecha (en un
hueco, el sol), dos variables internas h, 1]. Produce:
  u = tanh(W0·x) + σ·ξ   motor: mueve su materia, v ← (v + κ·u) mod 1;
  h ← 0.9·h + 0.1·tanh(W1..2·x)   memoria;
  pare si tanh(W3·x) > 0 y su energía supera el costo del parto.
La cría copia W de la madre con ruido chico (herencia: la evolución actúa en
TODOS los brazos por igual).

EL APRENDIZAJE EN VIDA (sólo la fila del motor). Perturbación de nodo
(Williams 1992; Fiete y Seung 2006): la celda explora con ruido ξ en su acción
y lleva una traza de elegibilidad El ← λ·El + ξ·x. Su señal es su propio
ingreso de este tick frente a su propio promedio reciente, m = (r − r̄)/r̄.
Actualiza W0 ← W0 + η·m·El. Sin maestro, sin datos, sin objetivo externo.

BRAZOS (misma exploración σ en todos; misma herencia):
  plastico         m propio.
  invertido        −m (control adversarial).
  barajado         m de otra celda del mismo mundo al azar (misma cantidad de
                   cambio, sin crédito).
  sin_plasticidad  η = 0 (sólo evolución).

CALIBRACIÓN (declarada; sobre OTRA condición): con el sol constante en 0.3,
se elige η, σ tales que el brazo plástico supere al sin_plasticidad en
cosecha. Es el control positivo de la regla de aprendizaje. RESULTADO de la
calibración (results/utero_tejido_plastico_calibracion_run.txt; 16 mundos por
brazo, 20000 ticks): la regla funciona en los SEIS puntos (η ∈ {0.01, 0.05,
0.2} × σ ∈ {0.1, 0.3}): plástico 0.48–0.53 contra sin_plasticidad 0.32–0.33 y
barajado 0.30–0.32 (el máximo posible es 0.55: materia en el punto opuesto al
sol); el invertido aprende lo contrario (0.08–0.29). Se fija η = 0.05, σ = 0.3
(centro del rango, 0.524), antes de correr la prueba con estaciones.

PRUEBA (estaciones, sol seed 0 cíclico; 16 mundos por brazo; N = 256; L0 = 7;
60000 ticks; lecturas en la segunda mitad; pareado por mundo):
  COSECHA  peso de luz medio de las vivas (distancia de la materia al sol
           + 0.05; 0.30 es el valor de una materia al azar).
  DENSIDAD vivas medias (confusor de §30–§31).
  GENERALIZACIÓN G: por cada estación nueva, (cosecha en sus primeros 50
           ticks − 0.30) / (cosecha media de toda la estación − 0.30), sólo
           donde el denominador es > 0.02; mediana por mundo. G ≈ 1: llega a
           la estación nueva sabiendo qué hacer; G ≈ 0: la re-aprende.
VEREDICTO (escrito antes de correr la prueba):
  APRENDE EN VIDA  si plastico supera a invertido, barajado y
                   sin_plasticidad en cosecha en ≥ 75% de los pares (p signo
                   < 0.05) con vivas ≥ 0.9 × las del control.
  ... Y GENERALIZA si además G ≥ 0.8 en ≥ 75% de los mundos plásticos donde
                   está definido.
  NADA             en otro caso.

    PYTHONPATH=src python experiments/utero/exp_utero_tejido_plastico.py            # prueba
    PYTHONPATH=src python experiments/utero/exp_utero_tejido_plastico.py calibrar   # calibración
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
W = 16
TICKS = 60000
SOL_SEED = 0
L0, E0, E_MANT, E_DIF, E_PARTO, E_COSTO = 7.0, 2.0, 0.01, 0.25, 0.5, 1.0
KAPPA, LAMBDA, TAU_R, EPS_W = 0.1, 0.8, 20.0, 0.02
ETA, SIGMA = 0.05, 0.3                  # CALIBRADOS (ver docstring); se fijan antes de la prueba
N_IN, N_OUT = 9, 4
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
ARMS = ("plastico", "invertido", "barajado", "sin_plasticidad")
TEMPRANO = 50
RESULTS = HERE.parents[1] / "results"
NAME = "utero_tejido_plastico"


def circ(m: np.ndarray) -> tuple:
    a = 2.0 * math.pi * m
    return np.cos(a), np.sin(a)


class Tejido:
    def __init__(self, modos: np.ndarray, rng: np.random.Generator, eta: float, sigma: float):
        b = len(modos)
        self.rng, self.eta, self.sigma = rng, eta, sigma
        self.modo = modos                                   # 0 plastico, 1 invertido, 2 barajado, 3 sin
        self.alive = np.ones((b, N), dtype=bool)
        self.v = rng.uniform(0, 1, (b, N))
        self.h = np.zeros((b, N, 2))
        self.Wt = rng.normal(0.0, 0.5, (b, N, N_OUT, N_IN))
        self.el = np.zeros((b, N, N_IN))
        self.e = np.full((b, N), E0)
        self.rbar = np.full((b, N), 0.02)

    def _x(self, vac: np.ndarray) -> np.ndarray:
        al = self.alive
        vl = np.where(np.roll(al, 1, axis=1), np.roll(self.v, 1, axis=1), vac)
        vr = np.where(np.roll(al, -1, axis=1), np.roll(self.v, -1, axis=1), vac)
        vl[:, 0] = vac[:, 0]
        vr[:, -1] = vac[:, 0]
        cl, sl = circ(vl)
        cv, sv = circ(self.v)
        cr, sr = circ(vr)
        return np.stack([cl, sl, cv, sv, cr, sr, self.h[..., 0], self.h[..., 1], np.ones_like(cv)], axis=-1)

    def paso(self, vac: np.ndarray) -> tuple:
        al = self.alive
        x = self._x(vac)                                                    # (B, N, 9)
        a = np.tanh(np.einsum("bnoi,bni->bno", self.Wt, x))                 # (B, N, 4)
        xi = self.rng.normal(0.0, 1.0, al.shape)
        u = a[..., 0] + self.sigma * xi
        self.v = np.where(al, (self.v + KAPPA * u) % 1.0, self.v)
        self.h = np.where(al[..., None], 0.9 * self.h + 0.1 * a[..., 1:3], self.h)
        self.el = np.where(al[..., None], LAMBDA * self.el + xi[..., None] * x, self.el)
        d = np.abs(self.v - vac)
        dd = np.minimum(d, 1.0 - d)
        w = np.where(al, dd + 0.05, 0.0)
        tot = w.sum(axis=1, keepdims=True)
        ing = np.where(tot > 0, L0 * vac * w / np.maximum(tot, 1e-300), 0.0)
        # aprendizaje en vida: señal propia, relativa a su propio promedio
        m = np.where(al, (ing - self.rbar) / np.maximum(self.rbar, 1e-4), 0.0)
        self.rbar = np.where(al, self.rbar + (ing - self.rbar) / TAU_R, self.rbar)
        m = np.clip(m, -5.0, 5.0)
        mb = m.copy()
        for i in np.flatnonzero(self.modo == 2):                            # barajado: la señal de otra celda
            idx = np.flatnonzero(al[i])
            if len(idx) > 1:
                mb[i, idx] = m[i, self.rng.permutation(idx)]
        signo = np.where(self.modo == 1, -1.0, 1.0)[:, None]
        mu = np.where((self.modo == 2)[:, None], mb, m) * signo
        eta = np.where(self.modo == 3, 0.0, self.eta)[:, None]
        dW0 = (eta * mu)[..., None] * self.el
        self.Wt[..., 0, :] = np.clip(self.Wt[..., 0, :] + np.where(al[..., None], dW0, 0.0), -5.0, 5.0)
        # energía
        e = self.e - E_MANT + ing
        muere = al & (e <= 0.0)
        al = al & ~muere
        self.e = np.where(al, e, 0.0)
        # partos
        intenta = al & (a[..., 3] > 0.0) & (self.e > E_COSTO)
        self.e = np.where(intenta, self.e - E_COSTO, self.e)
        lado = self.rng.random(al.shape) < 0.5
        partos = np.zeros(al.shape[0])
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
            eh = E_PARTO * self.e[:, src]
            nuevoW = self.Wt[:, src] + EPS_W * self.rng.normal(0.0, 1.0, self.Wt.shape)
            self.Wt = np.where(llega[..., None, None], nuevoW, self.Wt)
            self.v = np.where(llega, self.v[:, src], self.v)
            self.h = np.where(llega[..., None], 0.0, self.h)
            self.el = np.where(llega[..., None], 0.0, self.el)
            self.rbar = np.where(llega, self.rbar[:, src], self.rbar)
            self.e = np.where(llega, eh, self.e)
            dona = np.zeros_like(al)
            if der:
                dona[:, :-1] = llega[:, 1:]
            else:
                dona[:, 1:] = llega[:, :-1]
            self.e = np.where(dona, self.e - E_PARTO * self.e, self.e)
            al = al | llega
            partos += llega.sum(axis=1)
        par = al[:, :-1] & al[:, 1:]
        flujo = np.where(par, E_DIF * 0.5 * (self.e[:, :-1] - self.e[:, 1:]), 0.0)
        self.e[:, :-1] -= flujo
        self.e[:, 1:] += flujo
        self.alive = al
        n = al.sum(axis=1)
        wm = np.where(n > 0, np.where(al, dd, 0).sum(axis=1) / np.maximum(n, 1), np.nan) + 0.05
        return muere.sum(axis=1), n, wm, partos


def signo_p(k: int, n: int) -> float:
    return float(sum(math.comb(n, j) * 0.5 ** n for j in range(k, n + 1))) if n > 0 else 1.0


def correr(soles: np.ndarray, ticks: int, eta: float, sigma: float, semilla: int) -> tuple:
    modos = np.repeat(np.arange(len(ARMS)), W)
    t = Tejido(modos, np.random.default_rng(semilla), eta, sigma)
    w_ser = np.zeros((ticks, len(modos)), dtype=np.float32)
    viv = np.zeros((ticks, len(modos)), dtype=np.float32)
    for k in range(ticks):
        _, n, wm, _ = t.paso(soles[:, k:k + 1])
        w_ser[k], viv[k] = wm, n
    return w_ser, viv


def calibrar() -> None:
    ticks = 20000
    soles = np.full((len(ARMS) * W, ticks), 0.3)
    print("CALIBRACION con sol constante 0.3: cosecha media (segunda mitad) por brazo")
    for eta in (0.01, 0.05, 0.2):
        for sigma in (0.1, 0.3):
            w_ser, viv = correr(soles, ticks, eta, sigma, 7)
            m = np.nanmean(w_ser[ticks // 2:], axis=0).reshape(len(ARMS), W)
            vv = viv[ticks // 2:].mean(axis=0).reshape(len(ARMS), W)
            print(f"  eta={eta:<5} sigma={sigma:<4} " + "  ".join(f"{a} {np.median(m[i]):.3f}/{np.median(vv[i]):.0f}" for i, a in enumerate(ARMS)), flush=True)


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    sol = Sol(seed=SOL_SEED, ticks=TICKS, regimenes=REGS)
    soles = np.tile(sol.serie, (len(ARMS) * W, 1))
    out("=" * 80)
    out("TEJIDO PLASTICO (prototipo fuera del utero): regla continua que cambia en vida segun el propio ingreso de cada celda")
    out("=" * 80)
    out(f"N={N}; {W} mundos por brazo; brazos {list(ARMS)}; eta={ETA}; sigma={SIGMA}; kappa={KAPPA}; {TICKS} ticks; sol seed {SOL_SEED}; "
        f"veredicto pre-registrado (docstring)")
    out("")
    t0 = time.time()
    w_ser, viv = correr(soles, TICKS, ETA, SIGMA, 2032)
    out(f"corrida: {(time.time() - t0) / 60:.1f} min")
    mitad = TICKS // 2
    res = {}
    for i, a in enumerate(ARMS):
        sl = slice(i * W, (i + 1) * W)
        G = []
        for j in range(sl.start, sl.stop):
            gs = []
            for nombre, ini, fin in sol.estaciones:
                if ini < mitad or fin > TICKS or fin - ini < 2 * TEMPRANO:
                    continue
                den = float(np.nanmean(w_ser[ini:fin, j])) - 0.30
                if den > 0.02:
                    gs.append((float(np.nanmean(w_ser[ini:ini + TEMPRANO, j])) - 0.30) / den)
            G.append(float(np.median(gs)) if gs else np.nan)
        res[a] = dict(w=np.nanmean(w_ser[mitad:, sl], axis=0), vivas=viv[mitad:, sl].mean(axis=0),
                      w1=np.nanmean(w_ser[:mitad, sl], axis=0), G=np.array(G))
    out("-" * 80)
    out("ESTADO por brazo (medianas)")
    out(f"  {'brazo':<16} {'vivas':>6} {'cosecha 1a mitad':>16} {'cosecha 2a mitad':>16} {'G (generaliza)':>15} {'mundos con G':>12}")
    for a, r in res.items():
        out(f"  {a:<16} {np.median(r['vivas']):>6.0f} {np.nanmedian(r['w1']):>16.3f} {np.nanmedian(r['w']):>16.3f} "
            f"{np.nanmedian(r['G']) if np.any(~np.isnan(r['G'])) else float('nan'):>15.2f} {int(np.sum(~np.isnan(r['G']))):>12}")
    out("")
    out("-" * 80)
    out("PLASTICO contra cada control (cosecha, pareado por mundo)")
    supera = {}
    for c in ARMS[1:]:
        u, x = res["plastico"], res[c]
        k = int(np.sum(u["w"] > x["w"]))
        dens = float(np.median(u["vivas"]) / max(np.median(x["vivas"]), 1e-9))
        supera[c] = k / W >= 0.75 and signo_p(k, W) < 0.05 and dens >= 0.9
        out(f"  vs {c:<16} cosecha mayor en {k}/{W} (p {signo_p(k, W):.3f}); vivas {dens:.2f} -> {'SUPERA' if supera[c] else 'no'}")
    g = res["plastico"]["G"]
    g = g[~np.isnan(g)]
    kg = int(np.sum(g >= 0.8))
    generaliza = len(g) >= 4 and kg / len(g) >= 0.75
    out(f"  generalizacion: G >= 0.8 en {kg}/{len(g)} mundos plasticos donde esta definido -> {'si' if generaliza else 'no'}")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if all(supera.values()) and generaliza:
        out("=> APRENDE EN VIDA Y GENERALIZA: llega a cada estacion nueva sabiendo que hacer. Replicar con otro sol antes de creerlo.")
    elif all(supera.values()):
        out("=> APRENDE EN VIDA (sin generalizar): mejora con su propia experiencia, pero re-aprende cada estacion.")
    else:
        out("=> NADA: la regla plastica no supera a sus controles.")
    (RESULTS / f"{NAME}_run.txt").write_text(chr(10).join(lines), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "calibrar":
        calibrar()
    else:
        main()

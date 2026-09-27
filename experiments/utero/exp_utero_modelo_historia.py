"""
§42 — MODELO REDUCIDO: propensión al parto como función heredable de la
HISTORIA de energía propia. (docs/PLAN_INTELIGENCIA.md §41–§42; ledger 2026-09-27)

QUÉ ES Y QUÉ NO. NO es el útero: es el modelo reducido de §39b. Un positivo
aquí es una PREDICCIÓN para el sustrato real, no un vestigio.

MOTIVO. §41: el entorno contiene un óptimo que depende del orden —contenerse
siempre y parir sólo en la estación que sigue a la hambruna—, y esa señal se
lee de la historia propia (energía que sube desde un mínimo). Las perillas
de §36–§40 no podían expresarla. Aquí la propensión al parto es
    q = clip(q0 + k·tanh((e − ē)/e0) + c·tanh(ē/e0 − 1), 0, 1)
con ē la media lenta de la energía propia (τ = 200) y q0, k, c heredables
(±ε al nacer). Nacen en q0 = 1, k = 0, c = 0: el comportamiento actual del
útero (parir siempre que se pueda). k > 0: parir cuando la energía sube
respecto de su historia; c < 0: parir cuando la historia de energía es baja
(hambruna reciente). La selección decide.

DISEÑO. N = 256, L0 = 7, 120000 ticks, 24 semillas, sol seed 0. Seis brazos:
{clima, ciclo2, permutado} × {heredable, nulo}. El nulo tiene las mismas
perillas fijas en su valor inicial (pare siempre): sin herencia de cambios.
θ, s, g también heredables en el brazo heredable (como en §39b) y fijas en
el nulo. Lecturas sobre la segunda mitad de la corrida.
PREDICCIONES (escritas antes de correr), pareadas por semilla contra el nulo
del mismo calendario:
  REGULA (calendario) si la mortalidad per cápita en la hambruna del brazo
      heredable es menor que la del nulo en ≥ 75% de los pares (n ≥ 8), p
      signo < 0.05, razón mediana ≤ 0.8, Y SIN PAGAR CON DENSIDAD: la
      mediana de vivas del heredable es ≥ 0.9 × la del nulo (el confusor de
      §30–§31).
  POR EL ORDEN si REGULA bajo clima y ciclo2 y además la razón
      heredable/nulo es menor (mejor) bajo cada orden regular que bajo el
      permutado en ≥ 75% de los pares (p signo < 0.05).
  PREDICE VESTIGIO si POR EL ORDEN; PREDICE REGULACIÓN SIN ORDEN si REGULA
  en los tres calendarios por igual; PREDICE NADA en otro caso.
SECUNDARIAS: q0, k, c medios por brazo; fracción de los partos que cae en la
estación que sigue a la hambruna (B bajo clima, C bajo ciclo2).

    PYTHONPATH=src python experiments/utero/exp_utero_modelo_historia.py
"""

from __future__ import annotations

import importlib.util
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
TICKS = 120000
CALENDARIOS = {"clima": "ciclico", "ciclo2": "ciclico_inverso", "permutado": "permutado"}
SIGUE_A_HAMBRUNA = {"clima": 1, "ciclo2": 2}           # índice de estación (A, B, C) que sigue a A
RESULTS = HERE.parents[1] / "results"
NAME = "utero_modelo_historia"


class ModeloH(B.Modelo):
    def __init__(self, w: int, rng: np.random.Generator, fijo: np.ndarray):
        super().__init__(w, rng)
        self.q0 = np.ones((w, N))
        self.k = np.zeros((w, N))
        self.c = np.zeros((w, N))
        self.fijo = fijo[:, None]                        # (W, 1): mundos sin herencia de cambios

    def paso(self, vac: np.ndarray) -> tuple:
        al = self.alive
        d = np.abs(self.v - vac)
        w = np.where(al, np.minimum(d, 1.0 - d) + 0.05, 0.0)
        tot = w.sum(axis=1, keepdims=True)
        ing = np.where(tot > 0, B.L0 * vac * w / np.maximum(tot, 1e-300), 0.0)
        th = self.theta + self.g * np.tanh((self.el - self.e) / B.E0)
        self.v = np.where(al, (th + self.s * self.rng.random(al.shape)) % 1.0, self.v)
        e = self.e - B.E_MANT + ing
        muere = al & (e <= 0.0)
        al = al & ~muere
        self.e = np.where(al, e, 0.0)
        q = np.clip(self.q0 + self.k * np.tanh((self.e - self.el) / B.E0) + self.c * np.tanh(self.el / B.E0 - 1.0), 0.0, 1.0)
        self.el = np.where(al, self.el + (self.e - self.el) / B.TAU, self.el)
        intenta = al & (self.rng.random(al.shape) < B.P_PARTO * q) & (self.e > B.E_COSTO)
        self.e = np.where(intenta, self.e - B.E_COSTO, self.e)
        lado = self.rng.random(al.shape) < 0.5
        partos = np.zeros(al.shape[0])
        varia = ~self.fijo
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

            def pert(eps):
                return np.where(varia, eps * (2.0 * self.rng.random(al.shape) - 1.0), 0.0)

            self.theta = np.where(llega, (self.theta[:, src] + pert(B.EPS)) % 1.0, self.theta)
            self.s = np.where(llega, np.clip(self.s[:, src] + pert(B.EPS), 0.0, 1.0), self.s)
            self.g = np.where(llega, np.clip(self.g[:, src] + pert(B.EPS_G), -2.0, 2.0), self.g)
            self.q0 = np.where(llega, np.clip(self.q0[:, src] + pert(B.EPS), 0.0, 1.0), self.q0)
            self.k = np.where(llega, np.clip(self.k[:, src] + pert(B.EPS), -2.0, 2.0), self.k)
            self.c = np.where(llega, np.clip(self.c[:, src] + pert(B.EPS), -2.0, 2.0), self.c)
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
            partos += llega.sum(axis=1)
        par = al[:, :-1] & al[:, 1:]
        flujo = np.where(par, B.E_DIF * 0.5 * (self.e[:, :-1] - self.e[:, 1:]), 0.0)
        self.e[:, :-1] -= flujo
        self.e[:, 1:] += flujo
        self.alive = al
        return muere.sum(axis=1), al.sum(axis=1), partos


def main() -> None:
    lines: list[str] = []

    def out(x: str = "") -> None:
        print(x, flush=True)
        lines.append(x)

    out("=" * 80)
    out("MODELO REDUCIDO (no es el utero): propension al parto como funcion heredable de la historia de energia propia")
    out("=" * 80)
    out(f"N={N}; {W} semillas; {TICKS} ticks; brazos {{clima, ciclo2, permutado}} x {{heredable, nulo}}; predicciones pre-registradas (docstring)")
    out("")
    soles, est, fijo, etiquetas = [], [], [], []
    sol = {}
    for c, orden in CALENDARIOS.items():
        sol[c] = Sol(seed=B.SOL_EVOL, ticks=TICKS, orden=orden, regimenes=B.REGS)
        e = np.zeros(TICKS, dtype=int)
        for nombre, ini, fin in sol[c].estaciones:
            e[ini:min(fin, TICKS)] = "ABC".index(nombre)
        for brazo in ("heredable", "nulo"):
            soles.append(np.tile(sol[c].serie, (W, 1)))
            est.append(np.tile(e, (W, 1)))
            fijo += [brazo == "nulo"] * W
            etiquetas.append((c, brazo))
    soles, est = np.concatenate(soles), np.concatenate(est)
    nb = soles.shape[0]
    # la misma sopa por semilla en los seis brazos
    m = ModeloH(nb, np.random.default_rng(2030), np.array(fijo))
    for k in ("theta", "v"):
        base = getattr(m, k)[:W].copy()
        setattr(m, k, np.tile(base, (len(etiquetas), 1)))
    mitad = TICKS // 2
    muA = np.zeros(nb)
    vivA_t = np.zeros(nb)
    vivas_s = np.zeros(nb)
    partos_est = np.zeros((nb, 3))
    t0 = time.time()
    for t in range(TICKS):
        mu, vi, pa = m.paso(soles[:, t:t + 1])
        if t >= mitad:
            enA = est[:, t] == 0
            muA += np.where(enA, mu, 0)
            vivA_t += np.where(enA, vi, 0)
            vivas_s += vi
            partos_est[np.arange(nb), est[:, t]] += pa
    out(f"corrida: {(time.time() - t0) / 60:.1f} min")
    nA = np.array([(est[i, mitad:] == 0).sum() for i in range(nb)])
    n_h = {}
    for c in CALENDARIOS:
        n_h[c] = sum(1 for nombre, ini, fin in sol[c].estaciones if nombre == "A" and ini >= mitad and fin <= TICKS)
    res = {}
    for j, (c, brazo) in enumerate(etiquetas):
        sl = slice(j * W, (j + 1) * W)
        viv_media_A = vivA_t[sl] / np.maximum(nA[sl], 1)
        al = m.alive[sl]
        den = np.maximum(al.sum(axis=1), 1)
        pe = partos_est[sl]
        res[(c, brazo)] = dict(
            pc=muA[sl] / np.where(viv_media_A > 0, viv_media_A, np.nan) / max(n_h[c], 1),
            vivas=vivas_s[sl] / (TICKS - mitad),
            q0=(m.q0[sl] * al).sum(axis=1) / den, k=(m.k[sl] * al).sum(axis=1) / den, c=(m.c[sl] * al).sum(axis=1) / den,
            frac_est=pe / np.maximum(pe.sum(axis=1, keepdims=True), 1))
    out(f"  {'calendario':<10} {'brazo':<10} {'vivas':>6} {'pc_A':>6} {'q0':>5} {'k':>6} {'c':>6} {'partos A/B/C':>16}")
    for (c, brazo), r in res.items():
        f = np.median(r["frac_est"], axis=0)
        out(f"  {c:<10} {brazo:<10} {np.median(r['vivas']):>6.0f} {np.nanmedian(r['pc']):>6.3f} {np.median(r['q0']):>5.2f} "
            f"{np.median(r['k']):>6.2f} {np.median(r['c']):>6.2f} {f[0]:>5.2f}/{f[1]:.2f}/{f[2]:.2f}")
    out("")
    out("-" * 80)
    out("REGULA? heredable contra nulo del mismo calendario (pareado por semilla)")
    regula, razon = {}, {}
    for c in CALENDARIOS:
        h, n = res[(c, "heredable")], res[(c, "nulo")]
        pr = [(x, y) for x, y in zip(h["pc"], n["pc"]) if not (np.isnan(x) or np.isnan(y)) and y > 0]
        kk = sum(1 for x, y in pr if x < y)
        razon[c] = np.array([x / y if (not np.isnan(x) and not np.isnan(y) and y > 0) else np.nan for x, y in zip(h["pc"], n["pc"])])
        rz = float(np.nanmedian(razon[c]))
        dens = float(np.median(h["vivas"]) / max(np.median(n["vivas"]), 1e-9))
        regula[c] = len(pr) >= 8 and kk / len(pr) >= 0.75 and B.signo_p(kk, len(pr)) < 0.05 and rz <= 0.8 and dens >= 0.9
        kpos = int((h["k"] > 0).sum())
        out(f"  {c:<10} mortalidad heredable < nulo en {kk}/{len(pr)} (p signo {B.signo_p(kk, len(pr)):.3f}); razon mediana {rz:.2f}; "
            f"vivas heredable/nulo {dens:.2f}; k > 0 en {kpos}/{W} -> {'REGULA' if regula[c] else 'no'}")
    out("")
    orden_ok = {}
    for c in ("clima", "ciclo2"):
        pr = [(x, y) for x, y in zip(razon[c], razon["permutado"]) if not (np.isnan(x) or np.isnan(y))]
        kk = sum(1 for x, y in pr if x < y)
        orden_ok[c] = len(pr) >= 8 and kk / len(pr) >= 0.75 and B.signo_p(kk, len(pr)) < 0.05
        out(f"  la mejora bajo {c} es mayor que bajo el permutado en {kk}/{len(pr)} (p signo {B.signo_p(kk, len(pr)):.3f})")
    for c, idx in SIGUE_A_HAMBRUNA.items():
        fh = res[(c, "heredable")]["frac_est"][:, idx]
        fn = res[(c, "nulo")]["frac_est"][:, idx]
        kk = int((fh > fn).sum())
        out(f"  {c}: fraccion de partos en la estacion que sigue a la hambruna ({'ABC'[idx]}): heredable {np.median(fh):.2f} vs nulo {np.median(fn):.2f}; mayor en {kk}/{W}")
    out("")
    out("=" * 80)
    out("PREDICCION (regla escrita antes de correr)")
    if regula["clima"] and regula["ciclo2"] and orden_ok["clima"] and orden_ok["ciclo2"]:
        out("=> PREDICE VESTIGIO: la regla de historia heredable regula bajo los dos ordenes regulares y mas que bajo el permutado.")
    elif all(regula.values()):
        out("=> PREDICE REGULACION SIN ORDEN: regula en los tres calendarios por igual (la regla de historia no necesita regularidad).")
    elif regula["clima"] and regula["ciclo2"]:
        out("=> PREDICE REGULACION bajo los dos ordenes regulares, sin superar al permutado con la regla exigida.")
    else:
        out("=> PREDICE NADA: la perilla de historia no baja la mortalidad en la hambruna sin pagar con densidad.")
    (RESULTS / f"{NAME}_run.txt").write_text(chr(10).join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

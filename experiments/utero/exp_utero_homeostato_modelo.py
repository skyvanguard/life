"""
§44 — EL HOMEOSTATO: ¿aprende en vida una celda que reconfigura su EXPRESIÓN
cuando su reserva de energía sale de rango? Modelo reducido.
(docs/PLAN_INTELIGENCIA.md §44; ledger 2026-09-27)

POR QUÉ. §43 (ultraestabilidad sobre la regla, GPU, provisional): NADA. La
cosecha de luz quedó en 0.303–0.309 en los cuatro brazos, el valor de una
materia al azar. Es la quinta jaula otra vez (§28, §32): el mapa
programa→materia no tiene localidad, la salida de cualquier programa legal
es pseudoaleatoria, así que ninguna regla cosecha mejor que otra y reescribir
la regla "cuando va mal" no tiene nada mejor que encontrar. Lo que sí es
gradual y controlable es la EXPRESIÓN de la física en la materia (θ, s;
§34–§35). El homeostato de Ashby hecho literal: una celda que, cuando su
variable esencial (su reserva de energía) sale de rango, da un paso al azar
en su expresión, y cuando vuelve a rango se queda quieta.

QUÉ ES Y QUÉ NO. NO es el útero: es el modelo reducido (§39b: la ecología del
útero cerrado con la salida de la física reemplazada por su estadística,
y ~ U(0,1) iid). Un positivo aquí es una PREDICCIÓN. Y NO hay evolución de
las perillas: las crías nacen INGENUAS (θ al azar, s = 1). Todo lo que la
población tenga de bueno lo aprendió cada celda en su vida.

BRAZOS (24 mundos cada uno; N = 256, L0 = 7; 120000 ticks; sol seed 0,
orden cíclico). Paso δ = 0.02 en θ y en s, por tick, desde el generador del
modelo:
  homeo_4    paso sólo si e < 4 (PRIMARIO; 4 ≈ percentil 10 de la energía
             en la abundancia, calibrado en el modelo sin homeostato).
  homeo_2    idem con e < 2 (secundario, sensibilidad del umbral).
  homeo_8    idem con e < 8 (secundario).
  deriva     paso siempre (misma exploración, sin consecuencias).
  invertido  paso sólo si e ≥ 4 (control adversarial).
  fijo       nunca da pasos.
LECTURAS (segunda mitad de la corrida, pareadas por mundo):
  P1a COSECHA   peso de luz medio de las vivas.
  P1b HAMBRUNA  mortalidad per cápita en la hambruna (muertes / vivas
                medias en A), sin pagar con densidad (vivas ≥ 0.9 × control).
  P2  AHORRO    ¿aprende a adaptarse más rápido cada vez que vuelve una
                estación? Para cada tipo de estación, Spearman entre el
                número de ocurrencia k y la cosecha media en los primeros
                100 ticks de la ocurrencia; promedio sobre A, B, C.
  SEC CURVA     cosecha de las celdas con edad > 2000 menos la de las celdas
                con edad < 100 (aprender con la experiencia; el brazo fijo
                da el sesgo de supervivencia).
"homeo_4 supera a X": P1a mayor y P1b menor en ≥ 75% de los pares (n ≥ 8),
p signo < 0.05 en ambas, vivas ≥ 0.9 × las de X.
PREDICCIONES / VEREDICTO (escrito antes de correr):
  APRENDE CON MEMORIA   si homeo_4 supera a deriva, a invertido y a fijo, Y
                        su P2 es mayor que el de fijo en ≥ 75% de los pares
                        (p signo < 0.05): adaptarse cada vez más rápido a lo
                        que vuelve.
  APRENDE SIN MEMORIA   si supera a los tres pero P2 no: un homeostato puro,
                        que reacciona pero no recuerda (lo que Ashby
                        predice).
  NADA                  si no supera a los tres.

    PYTHONPATH=src python experiments/utero/exp_utero_homeostato_modelo.py
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
TICKS = 120000
DELTA = 0.02
ARMS = {"homeo_4": ("bajo", 4.0), "homeo_2": ("bajo", 2.0), "homeo_8": ("bajo", 8.0),
        "deriva": ("siempre", 0.0), "invertido": ("alto", 4.0), "fijo": ("nunca", 0.0)}
PRIMARIO = "homeo_4"
CONTROLES = ("deriva", "invertido", "fijo")
TEMPRANO = 100
RESULTS = HERE.parents[1] / "results"
NAME = "utero_homeostato_modelo"


class Homeostato:
    """Modelo reducido con crías ingenuas y un homeostato de Ashby sobre la expresión (θ, s)."""

    def __init__(self, modos: np.ndarray, umbrales: np.ndarray, rng: np.random.Generator):
        w = len(modos)
        self.rng = rng
        self.modos = modos[:, None]                   # (W, 1): 0 bajo, 1 siempre, 2 alto, 3 nunca
        self.umbral = umbrales[:, None]
        self.alive = np.ones((w, N), dtype=bool)
        self.theta = rng.uniform(0, 1, (w, N))
        self.s = np.ones((w, N))
        self.e = np.full((w, N), B.E0)
        self.v = rng.uniform(0, 1, (w, N))
        self.edad = np.zeros((w, N))

    def paso(self, vac: np.ndarray) -> tuple:
        al = self.alive
        d = np.abs(self.v - vac)
        dd = np.minimum(d, 1.0 - d)
        w = np.where(al, dd + 0.05, 0.0)
        tot = w.sum(axis=1, keepdims=True)
        ing = np.where(tot > 0, B.L0 * vac * w / np.maximum(tot, 1e-300), 0.0)
        y = self.rng.random(al.shape)
        self.v = np.where(al, (self.theta + self.s * y) % 1.0, self.v)
        e = self.e - B.E_MANT + ing
        muere = al & (e <= 0.0)
        al = al & ~muere
        self.e = np.where(al, e, 0.0)
        self.edad = np.where(al, self.edad + 1, 0.0)
        # homeostato: paso al azar en la expresión según la variable esencial
        fuera = self.e < self.umbral
        da_paso = al & np.where(self.modos == 0, fuera, np.where(self.modos == 1, True,
                                                                 np.where(self.modos == 2, ~fuera, False)))
        self.theta = np.where(da_paso, (self.theta + DELTA * (2 * self.rng.random(al.shape) - 1)) % 1.0, self.theta)
        self.s = np.where(da_paso, np.clip(self.s + DELTA * (2 * self.rng.random(al.shape) - 1), 0.0, 1.0), self.s)
        # partos: crías INGENUAS (θ al azar, s = 1, edad 0)
        intenta = al & (self.rng.random(al.shape) < B.P_PARTO) & (self.e > B.E_COSTO)
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
            self.theta = np.where(llega, self.rng.uniform(0, 1, al.shape), self.theta)
            self.s = np.where(llega, 1.0, self.s)
            self.edad = np.where(llega, 0.0, self.edad)
            self.v = np.where(llega, self.v[:, src], self.v)
            self.e = np.where(llega, eh, self.e)
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
        # lecturas del tick: peso medio, y peso de las celdas jóvenes y viejas
        n = al.sum(axis=1)
        wm = np.where(n > 0, np.where(al, dd, 0).sum(axis=1) / np.maximum(n, 1), np.nan) + 0.05
        joven = al & (self.edad < 100)
        viejo = al & (self.edad > 2000)
        wj = np.where(joven.sum(axis=1) > 0, np.where(joven, dd, 0).sum(axis=1) / np.maximum(joven.sum(axis=1), 1), np.nan)
        wv = np.where(viejo.sum(axis=1) > 0, np.where(viejo, dd, 0).sum(axis=1) / np.maximum(viejo.sum(axis=1), 1), np.nan)
        return muere.sum(axis=1), n, wm, wj, wv


def spearman(x, y) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    if rx.std() == 0 or ry.std() == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def signo_p(k: int, n: int) -> float:
    return float(sum(math.comb(n, j) * 0.5 ** n for j in range(k, n + 1))) if n > 0 else 1.0


def main() -> None:
    lines: list[str] = []

    def out(x: str = "") -> None:
        print(x, flush=True)
        lines.append(x)

    modo_id = {"bajo": 0, "siempre": 1, "alto": 2, "nunca": 3}
    modos = np.concatenate([np.full(W, modo_id[m]) for m, _ in ARMS.values()])
    umbr = np.concatenate([np.full(W, u) for _, u in ARMS.values()])
    nb = len(modos)
    sol = Sol(seed=B.SOL_EVOL, ticks=TICKS, regimenes=B.REGS)
    out("=" * 80)
    out("HOMEOSTATO (modelo reducido, no es el utero): paso al azar en la expresion cuando la reserva de energia sale de rango; crias ingenuas")
    out("=" * 80)
    out(f"N={N}; {W} mundos por brazo; brazos {list(ARMS)}; delta={DELTA}; {TICKS} ticks; sol seed {B.SOL_EVOL}; veredicto pre-registrado (docstring)")
    out("")
    h = Homeostato(modos, umbr, np.random.default_rng(2031))
    soles = np.tile(sol.serie, (nb, 1))
    mitad = TICKS // 2
    muA, vivA, nA_t = np.zeros(nb), np.zeros(nb), 0
    w_ser = np.zeros((TICKS, nb), dtype=np.float32)
    viv_s = np.zeros(nb)
    wj_s, wv_s, nj, nv = np.zeros(nb), np.zeros(nb), np.zeros(nb), np.zeros(nb)
    enA = np.zeros(TICKS, dtype=bool)
    for nombre, ini, fin in sol.estaciones:
        if nombre == "A":
            enA[ini:min(fin, TICKS)] = True
    t0 = time.time()
    for t in range(TICKS):
        mu, n, wm, wj, wv = h.paso(soles[:, t:t + 1])
        w_ser[t] = wm
        if t >= mitad:
            viv_s += n
            if enA[t]:
                muA += mu
                vivA += n
                nA_t += 1
            ok = ~np.isnan(wj)
            wj_s[ok] += wj[ok]
            nj[ok] += 1
            ok = ~np.isnan(wv)
            wv_s[ok] += wv[ok]
            nv[ok] += 1
    out(f"corrida: {(time.time() - t0) / 60:.1f} min")
    n_hA = sum(1 for nombre, ini, fin in sol.estaciones if nombre == "A" and ini >= mitad and fin <= TICKS)
    # P2: ahorro por recurrencia
    rho = np.zeros(nb)
    for i in range(nb):
        rs = []
        for tipo in "ABC":
            occ = [(ini, fin) for nombre, ini, fin in sol.estaciones if nombre == tipo and ini >= 6000 and fin <= TICKS]
            if len(occ) >= 4:
                x = [float(np.nanmean(w_ser[ini:ini + TEMPRANO, i])) for ini, _ in occ]
                rs.append(spearman(np.arange(len(x)), np.array(x)))
        rho[i] = float(np.mean(rs)) if rs else np.nan
    res = {}
    for j, a in enumerate(ARMS):
        sl = slice(j * W, (j + 1) * W)
        viv_media_A = vivA[sl] / max(nA_t, 1)
        res[a] = dict(w=np.nanmean(w_ser[mitad:, sl], axis=0), pcA=muA[sl] / np.where(viv_media_A > 0, viv_media_A, np.nan) / max(n_hA, 1),
                      vivas=viv_s[sl] / (TICKS - mitad), rho=rho[sl],
                      curva=np.where((nj[sl] > 0) & (nv[sl] > 0), wv_s[sl] / np.maximum(nv[sl], 1) - wj_s[sl] / np.maximum(nj[sl], 1), np.nan),
                      s=np.array([h.s[i][h.alive[i]].mean() if h.alive[i].any() else np.nan for i in range(sl.start, sl.stop)]))
    out("-" * 80)
    out("ESTADO por brazo (medianas; segunda mitad)")
    out(f"  {'brazo':<10} {'vivas':>6} {'cosecha w':>10} {'mort A':>7} {'ahorro rho':>10} {'curva viejo-joven':>18} {'s final':>8}")
    for a, r in res.items():
        f = lambda k: float(np.nanmedian(r[k]))   # noqa: E731
        out(f"  {a:<10} {f('vivas'):>6.0f} {f('w'):>10.3f} {f('pcA'):>7.3f} {f('rho'):>10.2f} {f('curva'):>18.3f} {f('s'):>8.2f}")
    out("")
    out("-" * 80)
    out(f"{PRIMARIO} contra cada control (pareado por mundo)")
    supera = {}
    for c in CONTROLES:
        u, x = res[PRIMARIO], res[c]
        idx = [i for i in range(W) if not (np.isnan(u["w"][i]) or np.isnan(x["w"][i]) or np.isnan(u["pcA"][i]) or np.isnan(x["pcA"][i]))]
        n = len(idx)
        kw = sum(1 for i in idx if u["w"][i] > x["w"][i])
        km = sum(1 for i in idx if u["pcA"][i] < x["pcA"][i])
        dens = float(np.nanmedian(u["vivas"]) / max(np.nanmedian(x["vivas"]), 1e-9))
        supera[c] = n >= 8 and kw / n >= 0.75 and signo_p(kw, n) < 0.05 and km / n >= 0.75 and signo_p(km, n) < 0.05 and dens >= 0.9
        out(f"  vs {c:<10} cosecha mayor en {kw}/{n} (p {signo_p(kw, n):.3f}); mortalidad en A menor en {km}/{n} (p {signo_p(km, n):.3f}); "
            f"vivas {dens:.2f} -> {'SUPERA' if supera[c] else 'no'}")
    idx = [i for i in range(W) if not (np.isnan(res[PRIMARIO]["rho"][i]) or np.isnan(res["fijo"]["rho"][i]))]
    k2 = sum(1 for i in idx if res[PRIMARIO]["rho"][i] > res["fijo"]["rho"][i])
    p2 = len(idx) >= 8 and k2 / len(idx) >= 0.75 and signo_p(k2, len(idx)) < 0.05
    out(f"  P2 ahorro: rho {PRIMARIO} > fijo en {k2}/{len(idx)} (p {signo_p(k2, len(idx)):.3f}) -> {'si' if p2 else 'no'}")
    for a in ("homeo_2", "homeo_8"):
        kw = sum(1 for i in range(W) if res[a]["w"][i] > res["fijo"]["w"][i])
        out(f"  (secundario) {a}: cosecha mayor que fijo en {kw}/{W}")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if all(supera.values()) and p2:
        out("=> PREDICE APRENDIZAJE CON MEMORIA: el homeostato cosecha mas, muere menos en la hambruna y se adapta cada vez mas rapido a lo que vuelve.")
    elif all(supera.values()):
        out("=> PREDICE APRENDIZAJE SIN MEMORIA: el homeostato aprende en vida (reacciona) pero no se adapta mas rapido a lo que vuelve.")
    else:
        out("=> PREDICE NADA: el homeostato no supera a sus tres controles.")
    (RESULTS / f"{NAME}_run.txt").write_text(chr(10).join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

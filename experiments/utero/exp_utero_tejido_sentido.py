"""
§49 — TEJIDO PLÁSTICO CON SENTIDO DEL PROPIO INGRESO: ¿generaliza la celda
cuando su regla puede leer en qué estación está? (pre-registrado 2026-10-26,
tras §45/§45b; docs/NORTE.md, decisión de Fran: "vamos con lo que propones")

DE DÓNDE VIENE. §45 (dos soles) y §45b (estaciones 10×) dieron APRENDE EN
VIDA, SIN GENERALIZAR: la regla continua aprende en vida de su propio ingreso,
lo aprendido es mortal y la dirección rinde sobre el azar gated, pero llega a
cada estación nueva posicionada para la anterior y la re-aprende (G < 0). El
diagnóstico (ledger §45b): la celda no tiene dónde guardar nada que sobreviva
al cambio de estación ni nada que le diga en qué estación está. Sus entradas
son la materia (propia y vecina) y una memoria h de ~10 ticks; sólo W0 (el
motor) es plástico, y lo único que puede aprender es UN atractor fijo en el
círculo, que mueve cada vez que el sol cambia.

LA PIEZA MÍNIMA. Dos entradas nuevas a la regla, y nada más:
  r_f = clip(r̄ / R_ESCALA, 0, 2) − 1      el propio ingreso reciente (τ = 20)
  r_l = clip(r̄_lento / R_ESCALA, 0, 2) − 1  el propio ingreso lento (τ = 500,
                                             del orden de una estación)
El ingreso de una celda depende del nivel del sol (A ≈ 0.1, B ≈ 0.55–0.95,
C ≈ 0.4–0.6): es una SEÑAL DE ESTACIÓN que la celda ya tiene y no leía
(cf. v10 `percepcion` en el útero discreto). Con ella, W0 puede aprender —por
la misma perturbación de nodo, sin maestro— una política CONDICIONADA:
"cuando mi ingreso es así, mi atractor está allá". Esa política vive en W0 y
no se borra al cambiar la estación: es la memoria que sobrevive. Si la celda
vive varias estaciones (aprendizaje por recurrencia, vara L del plan), al
empezar una estación nueva r_f cambia en ~20 ticks y el atractor debería
cambiar con él, sin re-aprender: eso es lo que mide G. Nada más cambia: misma
ecología, misma herencia genotípica, mismo η y σ, misma regla de aprendizaje.

BRAZOS (16 mundos cada uno; misma herencia genotípica):
  plastico         m propio, con los dos sentidos.
  invertido        −m, con sentidos (control adversarial).
  barajado         m de otra celda, con sentidos (misma cantidad de cambio).
  sin_plasticidad  η = 0, con sentidos (¿la evolución de genotipos usa los
                   sentidos sola?).
  ciego            m propio, SIN sentidos (= la celda del §45: las dos entradas
                   valen 0 siempre). Es el control que separa "generaliza por
                   los sentidos" de cualquier otra cosa.

PRUEBA: estaciones (sol seed 0; réplica sol seed 1 lanzada a la vez, misma
regla); N = 256; L0 = 7; 60000 ticks; lecturas en la segunda mitad; pareado
por mundo. Mismas medidas que §45: COSECHA, REGRET, DENSIDAD, G.
VEREDICTO (escrito antes de correr):
  GENERALIZA   si plastico supera a invertido, barajado y sin_plasticidad en
               cosecha en ≥ 75% de los pares (p signo < 0.05) con vivas ≥ 0.9×,
               Y G ≥ 0.8 en ≥ 75% de los mundos plásticos donde está definido.
  INTERMEDIO   si cumple lo primero y G del plastico > G del ciego en ≥ 75% de
               los pares (p < 0.05) pero no llega a 0.8: los sentidos ayudan a
               llegar sabiendo algo, no todo.
  NADA         en otro caso (incluye: los sentidos no mueven G; o la evolución
               sola, sin plasticidad, ya los usa igual).
Se cree sólo si el veredicto coincide en los dos soles.
LECTURAS SECUNDARIAS: cosecha por estación por brazo; cosecha del plastico en
los primeros 50 ticks de cada estación vs la del ciego (¿llega mejor?);
cosecha de sin_plasticidad con sentidos vs §45 (¿la evolución los usa?).

    PYTHONPATH=src python experiments/utero/exp_utero_tejido_sentido.py            # sol seed 0
    PYTHONPATH=src python experiments/utero/exp_utero_tejido_sentido.py replica 1  # sol seed 1
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

_spec = importlib.util.spec_from_file_location("tejido_plastico", HERE / "exp_utero_tejido_plastico.py")
tp = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(tp)

N, W, TICKS = tp.N, tp.W, tp.TICKS
ETA, SIGMA = tp.ETA, tp.SIGMA
ORACULO, AZAR, TEMPRANO = tp.ORACULO, tp.AZAR, tp.TEMPRANO
N_IN = tp.N_IN + 2
R_ESCALA, TAU_LENTO = 0.03, 500.0
ARMS = ("plastico", "invertido", "barajado", "sin_plasticidad", "ciego")
MODO_DE = {"plastico": 0, "invertido": 1, "barajado": 2, "sin_plasticidad": 3, "ciego": 0}
CONTROLES = ("invertido", "barajado", "sin_plasticidad")
RESULTS = tp.RESULTS
DATA = tp.DATA
NAME = "utero_tejido_sentido"


class TejidoSentido(tp.Tejido):
    """La celda del §45 con dos entradas más: su propio ingreso, rápido y lento."""

    def __init__(self, modos: np.ndarray, ciego: np.ndarray, rng: np.random.Generator, eta: float, sigma: float):
        super().__init__(modos, rng, eta, sigma, lesion_desde=None)
        b = len(modos)
        self.ciego = ciego
        self.Wt = rng.normal(0.0, 0.5, (b, N, tp.N_OUT, N_IN))
        self.Wn = self.Wt.copy()
        self.el = np.zeros((b, N, N_IN))
        self.rlento = np.full((b, N), 0.02)

    def _x(self, vac: np.ndarray) -> np.ndarray:
        x9 = super()._x(vac)
        rf = np.clip(self.rbar / R_ESCALA, 0.0, 2.0) - 1.0
        rl = np.clip(self.rlento / R_ESCALA, 0.0, 2.0) - 1.0
        sentido = np.where(self.ciego[:, None, None], 0.0, np.stack([rf, rl], axis=-1))
        return np.concatenate([x9, sentido], axis=-1)

    def paso(self, vac: np.ndarray) -> tuple:
        antes = self.alive.copy()
        res = super().paso(vac)
        nacen = self.alive & ~antes
        self.rlento = np.where(nacen, self.rbar, self.rlento + (self.rbar - self.rlento) / TAU_LENTO)
        return res


def correr(soles: np.ndarray, ticks: int, semilla: int) -> tuple:
    modos = np.repeat(np.array([MODO_DE[a] for a in ARMS]), W)
    ciego = np.repeat(np.array([a == "ciego" for a in ARMS]), W)
    t = TejidoSentido(modos, ciego, np.random.default_rng(semilla), ETA, SIGMA)
    w_ser = np.zeros((ticks, len(modos)), dtype=np.float32)
    viv = np.zeros((ticks, len(modos)), dtype=np.float32)
    for k in range(ticks):
        _, n, wm, _ = t.paso(soles[:, k:k + 1])
        w_ser[k], viv[k] = wm, n
    return w_ser, viv


def main(sol_seed: int = 0) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    sufijo = "" if sol_seed == 0 else f"_sol{sol_seed}"
    sol = Sol(seed=sol_seed, ticks=TICKS, regimenes=tp.REGS)
    soles = np.tile(sol.serie, (len(ARMS) * W, 1))
    out("=" * 80)
    out("§49 TEJIDO PLASTICO CON SENTIDO DEL PROPIO INGRESO: ¿generaliza cuando la regla puede leer en que estacion esta?")
    out("=" * 80)
    out(f"N={N}; {W} mundos por brazo; brazos {list(ARMS)}; eta={ETA}; sigma={SIGMA}; R_ESCALA={R_ESCALA}; tau_lento={TAU_LENTO}; "
        f"{TICKS} ticks; sol seed {sol_seed}; veredicto pre-registrado (docstring)")
    out("")
    t0 = time.time()
    w_ser, viv = correr(soles, TICKS, 4049 + sol_seed)
    out(f"corrida: {(time.time() - t0) / 60:.1f} min")
    DATA.mkdir(exist_ok=True)
    np.savez_compressed(DATA / f"{NAME}{sufijo}_series.npz", w_ser=w_ser, viv=viv, arms=np.array(ARMS),
                        estaciones=np.array([(n, i, f) for n, i, f in sol.estaciones], dtype=object))
    mitad = TICKS // 2
    res = {}
    for i, a in enumerate(ARMS):
        sl = slice(i * W, (i + 1) * W)
        G, tempr = [], []
        for j in range(sl.start, sl.stop):
            gs, ts = [], []
            for nombre, ini, fin in sol.estaciones:
                if ini < mitad or fin > TICKS or fin - ini < 2 * TEMPRANO:
                    continue
                den = float(np.nanmean(w_ser[ini:fin, j])) - AZAR
                ts.append(float(np.nanmean(w_ser[ini:ini + TEMPRANO, j])))
                if den > 0.02:
                    gs.append((ts[-1] - AZAR) / den)
            G.append(float(np.median(gs)) if gs else np.nan)
            tempr.append(float(np.mean(ts)) if ts else np.nan)
        res[a] = dict(w=np.nanmean(w_ser[mitad:, sl], axis=0), vivas=viv[mitad:, sl].mean(axis=0),
                      w1=np.nanmean(w_ser[:mitad, sl], axis=0), G=np.array(G), temprano=np.array(tempr))
    out("-" * 80)
    out("ESTADO por brazo (medianas)")
    out(f"  {'brazo':<16} {'vivas':>6} {'cosecha 1a mitad':>16} {'cosecha 2a mitad':>16} {'regret':>7} {'G (generaliza)':>15} {'mundos con G':>12} {'cosecha 0-50':>12}")
    for a, r in res.items():
        w2 = float(np.nanmedian(r["w"]))
        out(f"  {a:<16} {np.median(r['vivas']):>6.0f} {np.nanmedian(r['w1']):>16.3f} {w2:>16.3f} {(ORACULO - w2) / (ORACULO - AZAR):>7.2f} "
            f"{np.nanmedian(r['G']) if np.any(~np.isnan(r['G'])) else float('nan'):>15.2f} {int(np.sum(~np.isnan(r['G']))):>12} "
            f"{np.nanmedian(r['temprano']):>12.3f}")
    out("")
    out("-" * 80)
    out("POR ESTACION (cosecha media por tipo de estacion, 2a mitad)")
    for i, a in enumerate(ARMS):
        sl = slice(i * W, (i + 1) * W)
        por = {nm: float(np.mean([np.nanmean(w_ser[ini:fin, sl]) for n_, ini, fin in sol.estaciones if n_ == nm and ini >= mitad] or [np.nan]))
               for nm in "ABC"}
        out(f"  {a:<16} " + "  ".join(f"{nm} {por[nm]:.3f}" for nm in "ABC"))
    out("")
    out("-" * 80)
    out("PRIMARIO: PLASTICO (con sentidos) contra cada control (cosecha 2a mitad, pareado por mundo)")
    supera = {}
    for c in CONTROLES:
        u, x = res["plastico"], res[c]
        k = int(np.sum(u["w"] > x["w"]))
        dens = float(np.median(u["vivas"]) / max(np.median(x["vivas"]), 1e-9))
        supera[c] = k / W >= 0.75 and tp.signo_p(k, W) < 0.05 and dens >= 0.9
        out(f"  vs {c:<16} cosecha mayor en {k}/{W} (p {tp.signo_p(k, W):.3f}); vivas {dens:.2f} -> {'SUPERA' if supera[c] else 'no'}")
    g = res["plastico"]["G"]
    gdef = ~np.isnan(g)
    kg = int(np.sum(g[gdef] >= 0.8))
    generaliza = int(gdef.sum()) >= 4 and kg / max(int(gdef.sum()), 1) >= 0.75
    out(f"  generalizacion: G >= 0.8 en {kg}/{int(gdef.sum())} mundos plasticos donde esta definido -> {'si' if generaliza else 'no'}")
    gc = res["ciego"]["G"]
    ambos = gdef & ~np.isnan(gc)
    kgc = int(np.sum(g[ambos] > gc[ambos]))
    nn = int(ambos.sum())
    sube = nn >= 4 and kgc / nn >= 0.75 and tp.signo_p(kgc, nn) < 0.05
    out(f"  G plastico > G ciego en {kgc}/{nn} pares (p {tp.signo_p(kgc, nn):.3f}) -> {'SI' if sube else 'no'}; "
        f"G mediana plastico {np.nanmedian(g):.2f} vs ciego {np.nanmedian(gc):.2f}")
    out("")
    out("-" * 80)
    out("SECUNDARIAS")
    u, x = res["plastico"]["temprano"], res["ciego"]["temprano"]
    k = int(np.sum(u > x))
    out(f"  LLEGA MEJOR   cosecha en los primeros 50 ticks de cada estacion, plastico > ciego: {k}/{W} (p {tp.signo_p(k, W):.3f}); "
        f"medianas {np.nanmedian(u):.3f} vs {np.nanmedian(x):.3f}")
    k = int(np.sum(res["plastico"]["w"] > res["ciego"]["w"]))
    out(f"  COSECHA       plastico > ciego (2a mitad): {k}/{W} (p {tp.signo_p(k, W):.3f}); medianas {np.nanmedian(res['plastico']['w']):.3f} vs {np.nanmedian(res['ciego']['w']):.3f}")
    out(f"  EVOLUCION     sin_plasticidad con sentidos, cosecha 2a mitad {np.nanmedian(res['sin_plasticidad']['w']):.3f} (§45 sin sentidos: 0.293 / 0.291)")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if all(supera.values()) and generaliza:
        out("=> GENERALIZA: con el sentido de su propio ingreso, la celda llega a cada estacion nueva sabiendo que hacer. Vale solo si coincide en los dos soles.")
    elif all(supera.values()) and sube:
        out("=> INTERMEDIO: los sentidos ayudan a llegar sabiendo algo (G sube sobre el ciego), no todo.")
    else:
        out("=> NADA: los sentidos no mueven la generalizacion (o la evolucion sola ya los usa igual).")
    (RESULTS / f"{NAME}{sufijo}_run.txt").write_text(chr(10).join(lines), encoding="utf-8")
    tp.figura(sol, w_ser, ARMS, RESULTS / f"{NAME}{sufijo}.png")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "replica":
        main(int(sys.argv[2]))
    else:
        main()

"""Tests de las varas de inteligencia sobre series sintéticas y una corrida corta."""

import numpy as np

from zeta_life.utero.inteligencia import (
    ACTIVIDAD_W,
    W_ANT,
    anticipacion,
    aprendizaje,
    correr_series,
    regulacion,
)
from zeta_life.utero.sol import Sol

SOL = Sol(seed=0, ticks=20000)


def _ruido(seed=0, escala=0.05):
    return np.random.default_rng(seed).normal(0, escala, SOL.ticks)


def _esperados():
    """Los instantes 'esperados' que la vara de anticipación va a examinar."""
    est = SOL.estaciones[:-1]
    out = []
    for k, (_, ini, fin) in enumerate(est):
        if k < 5:
            continue
        med = np.median([f - i for _, i, f in est[:k]])
        esp = ini + int(med)
        if fin - esp >= 2 * W_ANT:
            out.append(esp)
    return out


def test_anticipacion_detects_an_injected_expectation_bump():
    act = _ruido()
    for esp in _esperados():
        act[esp - W_ANT:esp + W_ANT] += 0.2          # actividad ANTES del cambio real
    r = anticipacion(act, SOL, n_perm=300)
    assert r["n"] >= 3 and r["estadistico"] > 0 and r["p"] < 0.01


def test_anticipacion_is_null_on_noise_and_on_reflex():
    r = anticipacion(_ruido(1), SOL, n_perm=300)
    assert r["p"] > 0.05
    reflejo = 0.1 + 0.5 * SOL.serie + _ruido(2, 0.01)   # x_t = f(s_t): sin memoria
    r2 = anticipacion(reflejo, SOL, n_perm=300)
    assert r2["p"] > 0.05


def test_aprendizaje_detects_habituation():
    act = _ruido(3)
    counts = {}
    for nombre, ini, fin in SOL.estaciones[1:-1]:
        k = counts.get(nombre, 0)
        act[ini:ini + ACTIVIDAD_W] += 0.5 / (1 + k)      # respuesta que decae con la repetición
        counts[nombre] = k + 1
    r = aprendizaje(act, SOL, n_perm=500)
    assert r["rho"] < -0.5 and r["p"] < 0.01


def test_aprendizaje_is_null_without_trend():
    # sin tendencia, la fracción de falsos positivos al 5% debe quedar cerca del 5%
    falsos = 0
    for seed in range(12):
        act = _ruido(100 + seed)
        for nombre, ini, fin in SOL.estaciones[1:-1]:
            act[ini:ini + ACTIVIDAD_W] += 0.3            # misma respuesta siempre
        falsos += aprendizaje(act, SOL, n_perm=300)["p"] < 0.05
    assert falsos <= 3


def test_series_and_regulacion_on_a_short_run():
    sol = Sol(seed=1, ticks=300)
    con = correr_series(seed=3, flags=dict(memoria=True), sol=sol, ticks=300, max_n=64)
    sin = correr_series(seed=3, flags=dict(memoria=True), sol=None, ticks=300, max_n=64)
    for k in ("vivas", "actividad", "v_int", "v_borde", "novedad"):
        assert con[k].shape == (300,)
    assert (con["actividad"] >= 0).all()
    r = regulacion(con, sin, sol, (100, 300))
    assert set(r) == {"vivas_sol", "vivas_sin", "novedad_sol", "novedad_sin",
                      "amortiguacion", "acople_borde"}


def test_anticipacion_detrend_ignores_pure_drift_but_catches_a_bump():
    # deriva: la serie se acumula dentro de cada estación (como la energía media)
    drift = _ruido(7, 0.01)
    for _, ini, fin in SOL.estaciones:
        drift[ini:fin] += np.linspace(0, 1.0, fin - ini)
    r_dt = anticipacion(drift, SOL, n_perm=300, detrend=True)    # el residuo no dispara con deriva
    assert r_dt["p"] > 0.05 and abs(r_dt["estadistico"]) < 0.05
    bump = drift.copy()
    for esp in _esperados():
        bump[esp - W_ANT:esp + W_ANT] += 0.3
    r_b = anticipacion(bump, SOL, n_perm=300, detrend=True)
    assert r_b["estadistico"] > 0 and r_b["p"] < 0.01

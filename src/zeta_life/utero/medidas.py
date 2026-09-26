"""
La corrida MEDIDA de El Útero: una corrida con la vara honesta completa.

Reúne en una sola función lo que los experimentos de 2026-09 fueron
acumulando: novedad cruda (genomas nunca vistos por tick), novedad con filtro
de persistencia de linaje (MODES), ecología (Shannon de genomas persistentes
por tramo), cuota del genoma dominante, muertes/invasiones/vivas por tick y
la causa de cada acuñación (parto/invasión vs reescritura). Sirve para
cualquier combinación de flags de `UteroCreciente` y para su corrida sombra.
"""

from __future__ import annotations

import math
from collections import Counter

import numpy as np

from zeta_life.utero.creciente import MAX_N, N0, UteroCreciente
from zeta_life.utero.linaje import RastreadorLinaje


def correr_medido(seed: int, flags: dict, ticks: int, tranche: int = 500,
                  t_filtro: int = 500, shadow: list | None = None,
                  n0: int = N0, max_n: int = MAX_N) -> dict:
    """Correr `ticks` con `flags` (p.ej. memoria=True, invasion="asentada") y
    devolver las series de la vara honesta. `shadow` = muertes por tick de una
    corrida real → corrida sombra (muertes al azar, sin sonda)."""
    u = UteroCreciente(n0=n0, seed=seed, max_n=max_n, germinal=True, toroidal=True,
                       log_events=True, shadow_deaths=shadow, **flags)
    tr = RastreadorLinaje(t_filtro)
    seen: set = set(u.seen)
    nt = (ticks + tranche - 1) // tranche
    raw = np.zeros(ticks, dtype=np.int64)
    deaths = np.zeros(ticks, dtype=np.int64)
    invaded = np.zeros(ticks, dtype=np.int64)
    vivas = np.zeros(ticks, dtype=np.int64)
    presence = [Counter() for _ in range(nt)]
    causa = np.zeros((nt, 2), dtype=np.int64)          # [parto/invasión, reescritura]
    for t in range(ticks):
        m = u.step()
        deaths[t], invaded[t], vivas[t] = m["deaths"], m["invaded"], int(u.alive.sum())
        born = {c for _, c in u.spawns}
        cg = {int(i) - u.left_grown: u.code[i].tobytes() for i in np.flatnonzero(u.alive)}
        k = t // tranche
        for coord, g in cg.items():
            if g not in seen:
                seen.add(g)
                raw[t] += 1
                causa[k, 0 if coord in born else 1] += 1
        presence[k].update(cg.values())
        tr.tick(t, cg, u.spawns)
    filt = tr.novedad_filtrada(tranche, ticks)
    ok = tr.resueltos()
    eco, share = np.zeros(nt), np.zeros(nt)
    for k, c in enumerate(presence):
        kept = {g: n for g, n in c.items() if ok.get(g, False)}
        tot = sum(kept.values())
        if tot:
            eco[k] = -sum(n / tot * math.log2(n / tot) for n in kept.values())
        share[k] = (max(c.values()) / sum(c.values())) if c else 0.0
    return {"raw": raw, "filt": filt, "deaths": deaths, "invaded": invaded, "vivas": vivas,
            "eco": eco, "share": share, "causa": causa}


def por_tramo(x: np.ndarray, tranche: int = 500) -> np.ndarray:
    return np.asarray(x)[: (len(x) // tranche) * tranche].reshape(-1, tranche).sum(axis=1)


def media_ventana(xt: np.ndarray, ventana: tuple, tranche: int = 500) -> float:
    """Media por tramo de una serie POR TRAMO dentro de una ventana en ticks."""
    a, b = ventana[0] // tranche, ventana[1] // tranche
    return float(np.asarray(xt)[a:b].mean())

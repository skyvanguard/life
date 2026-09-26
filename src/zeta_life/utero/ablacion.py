"""
Protocolo de ablación de la zona-bomba (extraído de v5 para replicarlo).

Es EXACTAMENTE el `tail_ablation` de `experiments/utero/exp_utero_memoria.py`
(v5, 2026-07-09), puesto en un módulo con tests para poder correrlo en N
semillas sin copiar el código. Lo que mide:

  - novedad por tick: genomas NUNCA VISTOS acuñados en ese tick (registro
    externo, coordenada-estable — la vara anti-ilusión de toda la línea).
  - la ablación: en `ablate_at`, se vuelven VACÍO todas las celdas cuyo código
    cambió en los últimos `win` ticks (la "zona-bomba", la turbulencia que
    acuña). Sin reescritura de código no hay novedad, así que matar la zona que
    reescribe es matar el motor — y ver si algo lo vuelve a encender.
  - la medida honesta es la COLA (novedad/tramo en +1000..+3000), NO el pulso
    de recolonización de los primeros 500 ticks, que sólo rellena el hueco.

Manos declaradas: `win` (qué cuenta como "activa"), las ventanas de medida.
"""

from __future__ import annotations

import numpy as np

from zeta_life.utero.creciente import MAX_N, N0, UteroCreciente

TRANCHE = 500          # tramo de la novedad (genomas nuevos por 500 ticks)
PRE_TICKS = 1000       # ventana previa: t_abl-1000 .. t_abl
TAIL_FROM = 1000       # la cola empieza 1000 ticks después de ablar...
TAIL_TO = 3000         # ...y termina 3000 después (2000 ticks = 4 tramos)
ACTIVE_WIN = 200       # "activa" = código reescrito en los últimos 200 ticks


def _genomas_por_coord(u: UteroCreciente) -> dict:
    return {i - u.left_grown: u.code[i].tobytes() for i in np.flatnonzero(u.alive)}


def _ablar(u: UteroCreciente, last_change: dict, t: int, win: int) -> int:
    """Vaciar toda celda cuyo código cambió en los últimos `win` ticks."""
    n_abl = 0
    for coord, tc in list(last_change.items()):
        if t - tc > win:
            continue
        i = coord + u.left_grown
        if 0 <= i < u.n and u.alive[i]:
            u.alive[i] = False
            u.v[i] = 0.0
            u.code[i] = 0
            u.eq_count[i] = 0
            u.mem[i] = 0.0
            n_abl += 1
    return n_abl


def correr(seed: int, memoria: bool, ticks: int, ablate_at: int | None,
           n0: int = N0, max_n: int = MAX_N, germinal: bool = True,
           toroidal: bool = True, win: int = ACTIVE_WIN) -> dict:
    """Correr `ticks` y (opcionalmente) ablar la zona-bomba en `ablate_at`.

    Devuelve {"novedad": genomas nuevos por tick, "vivas": celdas vivas por
    tick, "ablated": cuántas celdas mató la ablación (0 si no hubo)}.
    `ablate_at=None` = línea base sin ablación, mismas medidas.
    """
    u = UteroCreciente(n0=n0, seed=seed, max_n=max_n, germinal=germinal,
                       toroidal=toroidal, memoria=memoria)
    seen: set = set(u.seen)       # los genomas iniciales ya cuentan como vistos
    last_code: dict = {}
    last_change: dict = {}
    novedad = np.zeros(ticks, dtype=np.int64)
    vivas = np.zeros(ticks, dtype=np.int64)
    ablated = 0
    for t in range(ticks):
        u.step()
        cg = _genomas_por_coord(u)
        new = 0
        for coord, g in cg.items():
            if g not in seen:
                seen.add(g)
                new += 1
            if coord in last_code and last_code[coord] != g:
                last_change[coord] = t
        last_code = cg
        novedad[t] = new
        if ablate_at is not None and t == ablate_at:
            ablated = _ablar(u, last_change, t, win)
            last_code = _genomas_por_coord(u)
        vivas[t] = int(u.alive.sum())
    return {"novedad": novedad, "vivas": vivas, "ablated": ablated}


def medir_cola(novedad: np.ndarray, t_abl: int) -> tuple[float, int, float]:
    """(pre, pulso, cola), en genomas nuevos por tramo de 500 ticks.

    pre   = media por tramo en los 1000 ticks previos a t_abl
    pulso = suma de los 500 ticks siguientes (recolonización; NO es la medida)
    cola  = media por tramo en t_abl+1000 .. t_abl+3000 (la medida honesta)
    """
    npt = np.asarray(novedad)
    pre = float(npt[t_abl - PRE_TICKS:t_abl].sum()) / (PRE_TICKS / TRANCHE)
    pulse = int(npt[t_abl:t_abl + TRANCHE].sum())
    tail = float(npt[t_abl + TAIL_FROM:t_abl + TAIL_TO].sum()) / (
        (TAIL_TO - TAIL_FROM) / TRANCHE)
    return pre, pulse, tail

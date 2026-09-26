"""
Filtro de persistencia de linaje (MODES, Dolson et al. 2019) para El Útero.

Nuestra vara "genomas nunca vistos por tramo" cuenta ACUÑACIÓN: cada evento de
escritura que produce un genoma inédito. MODES advierte que eso se infla por
deriva (un bit distinto en una instrucción muerta cuenta como novedad). Su
remedio: contar un componente sólo si, `t_filtro` ticks después de aparecer,
sigue teniendo DESCENDENCIA viva.

Descendencia aquí = continuidad de la celda (una celda que se reescribe sigue
siendo la misma línea) + SPAWN (la cría hereda la línea de la madre). COPY es
transferencia horizontal de una instrucción, no descendencia: no cuenta.

Uso: por tick, `tick(t, vivas={coord: genoma_bytes}, spawns=[(madre, cría)])`;
al final, `resueltos()` → {genoma: persistió}, y `novedad_filtrada(tramo,
ticks)` → genomas acuñados por tramo que pasaron el filtro. Los últimos
`t_filtro` ticks quedan sin resolver por construcción (no se cuentan).
"""

from __future__ import annotations

import numpy as np


class RastreadorLinaje:
    def __init__(self, t_filtro: int):
        self.t_filtro = int(t_filtro)
        self.first_seen: dict[bytes, int] = {}
        self.pending: dict[bytes, int] = {}          # genoma -> tick de acuñación
        self.resolved: dict[bytes, bool] = {}
        self.carriers: dict[int, set[bytes]] = {}    # coord -> genomas pendientes que porta

    def tick(self, t: int, vivas: dict, spawns: list) -> None:
        # 1) las crías heredan la línea de la madre
        for madre, cria in spawns:
            self.carriers[cria] = set(self.carriers.get(madre, ()))
        # 2) acuñaciones: la celda que las produce porta la línea
        for coord, g in vivas.items():
            if coord not in self.carriers:
                self.carriers[coord] = set()
            if g not in self.first_seen:
                self.first_seen[g] = t
                self.pending[g] = t
                self.carriers[coord].add(g)
        # 3) las muertas dejan de portar
        for coord in [c for c in self.carriers if c not in vivas]:
            del self.carriers[coord]
        # 4) resolver lo que ya cumplió el plazo
        due = [g for g, t0 in self.pending.items() if t - t0 >= self.t_filtro]
        if not due:
            return
        for g in due:
            self.resolved[g] = any(g in s for s in self.carriers.values())
            del self.pending[g]
        due_set = set(due)
        for s in self.carriers.values():
            s -= due_set

    def resueltos(self) -> dict[bytes, bool]:
        return dict(self.resolved)

    def novedad_filtrada(self, tramo: int, ticks: int) -> np.ndarray:
        """Genomas acuñados en cada tramo cuyo linaje persistió `t_filtro`."""
        n = (ticks + tramo - 1) // tramo
        out = np.zeros(n, dtype=np.int64)
        for g, ok in self.resolved.items():
            if ok:
                out[self.first_seen[g] // tramo] += 1
        return out

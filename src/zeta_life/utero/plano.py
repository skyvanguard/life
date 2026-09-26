"""
El Útero PLANO — v8: el mismo sustrato, en dos dimensiones.

Por qué cambiar de perspectiva (docs/EL_UTERO.md, ledger 2026-09-26): en la
línea 1-D, tres mecanismos distintos (memoria, invasión, recombinación) dan
el mismo techo, 3/40 semillas con novedad sostenida, y la última jaula
nombrada es el BARRIDO DEL CLON VIABLE: liberada la fertilidad, un genoma con
ruta de copia confiable ocupa todo el tejido. La literatura no resuelve eso
con filtros de persistencia sino con ESTRUCTURA ESPACIAL (frentes, enclaves,
coexistencia), conservación de recursos o parasitismo. En una línea con dos
vecinos la estructura espacial es mínima. Aquí cada celda tiene cuatro.

Lo que se conserva (los tres principios y todas las lecciones):
  - reglas-como-estado: cada celda lleva su programa (K×F), que actúa sobre la
    materia y sobre sí mismo (MUTO/COPY) y coloniza el vacío (SPAWN);
  - persistencia como único filtro: la física ciega a la materia muere (sonda:
    todos los vecinos en 0 vs todos en h, misma memoria);
  - materia toroidal (v3), memoria (v5), invasión de tejido asentado (v6) y
    recombinación al nacer (v7) como flags; variación germinal (v2) siempre;
  - actualización asincrónica en orden aleatorio sembrado; sin ruido de código.
Lo que cambia: vecindario de von Neumann (N, E, S, O); registros
[vN, vE, vS, vO, v, R] (seis; los campos a,b,c indexan mod 6); READ/COPY leen
de (N, E, S, O, yo) con a mod 5; SPAWN hacia (a + |R[b]|·4) mod 4 — la dirección
del parto la modula la materia, como el opcode germinal (si fuera fija por
genoma, el crecimiento avanza en rayos y la placa no se coloniza). El espacio es una placa
H×W con bordes (la pared de la placa de Petri); nace un bloque vivo en el
centro y el resto es vacío colonizable — "el espacio se abre donde la física
lo abre", como en v1, pero el crecimiento ES la colonización del vacío.

Interfaz común con `UteroCreciente` para la vara honesta (`medidas`,
`linaje`, `ablacion`): `step()` → dict con deaths/invaded/colonized/
new_genomes; `spawns`, `events`, `seen`; `genomas()` → {coord: bytes};
`vaciar(coord)`. Las coordenadas son tuplas (fila, columna).
"""

from __future__ import annotations

import math

import numpy as np

from zeta_life.utero.nivel2 import (
    ADD,
    CONST,
    COPY,
    MUL,
    MUTO,
    N_OPS,
    PROBE_EPS,
    READ,
    SPAWN,
    SUB,
    THR,
    F,
    K,
    _clip,
)

NREG = 6                       # vN, vE, vS, vO, v, R (R = potencial interno / memoria)
NCTX = 5                       # N, E, S, O, yo
DIRS = ((-1, 0), (0, 1), (1, 0), (0, -1))     # N, E, S, O
PROBE_HI = 0.6180339887498949  # separación irracional en el toro (v3)


def execute_plano(code: np.ndarray, vs: tuple, v: float, ctx: tuple,
                  r_init: float = 0.0, stats: dict | None = None) -> tuple:
    """Ejecutar una regla plana. vs = (vN, vE, vS, vO) (0.0 si vacío), ctx =
    (codeN, codeE, codeS, codeO, code_self) con None donde no hay vecino.
    Devuelve (v', own_next, spawn, r_raw); spawn = None | (dir, pos, opcode,
    locus). Total por construcción. Materia siempre toroidal (v' = R mod 1)."""
    if stats is not None:
        stats.update(copy_writes=0, muto_writes=0, copy_distinct=False)
    r = [vs[0], vs[1], vs[2], vs[3], v, r_init]
    own_next = code.copy()
    spawn = None
    for k in range(K):
        op, a, b, c = int(code[k, 0]), int(code[k, 1]), int(code[k, 2]), int(code[k, 3])
        if op == ADD:
            r[c % NREG] = _clip(r[a % NREG] + r[b % NREG])
        elif op == SUB:
            r[c % NREG] = _clip(r[a % NREG] - r[b % NREG])
        elif op == MUL:
            r[c % NREG] = _clip(r[a % NREG] * r[b % NREG])
        elif op == THR:
            r[c % NREG] = 1.0 if r[a % NREG] > r[b % NREG] else 0.0
        elif op == CONST:
            r[c % NREG] = (a - 8) / 4.0
        elif op == READ:
            src = ctx[a % NCTX]
            r[c % NREG] = float(src[b % K, 0]) / N_OPS if src is not None else 0.0
        elif op == MUTO:
            new_op = int(abs(r[b % NREG]) * N_OPS) % N_OPS
            if stats is not None and own_next[a % K, 0] != new_op:
                stats["muto_writes"] += 1
            own_next[a % K, 0] = new_op
        elif op == COPY:
            src = ctx[a % NCTX]
            if src is not None:
                if stats is not None and not np.array_equal(own_next[c % K], src[b % K]):
                    stats["copy_writes"] += 1
                    if not np.array_equal(src, code):
                        stats["copy_distinct"] = True
                own_next[c % K] = src[b % K]
        elif op == SPAWN:
            # la DIRECCIÓN del parto la decide la física con la materia: base a%4
            # girada por |R[b]| (misma función que el opcode germinal). Con
            # dirección fija por genoma el crecimiento 2-D avanza en rayos y la
            # placa no se coloniza (sondeo 2026-09-26: 160–320 vivas de 1024).
            spawn = ((a + int(abs(r[b % NREG]) * 4)) % 4, c % K,
                     int(abs(r[b % NREG]) * N_OPS) % N_OPS, b % K)
    raw = r[5]
    return raw % 1.0, own_next, spawn, raw


def _salida(code, vs, v, ctx, r_init):
    return execute_plano(code, vs, v, ctx, r_init=r_init)[0]


class UteroPlano:
    """Placa H×W con bordes; bloque vivo inicial en el centro; vacío colonizable."""

    def __init__(self, h: int = 32, w: int = 32, seed: int = 0, bloque: int = 4,
                 memoria: bool = False, invasion: str | None = None,
                 recombina: bool = False, eq_eps: float = 1e-9, eq_window: int = 100,
                 log_events: bool = False, shadow_deaths=None):
        if invasion not in (None, "asentada", "siempre"):
            raise ValueError("invasion debe ser None, 'asentada' o 'siempre'")
        self.h, self.w = h, w
        self.memoria, self.invasion, self.recombina = memoria, invasion, recombina
        self.eq_eps, self.eq_window = eq_eps, eq_window
        self.log_events = log_events
        self.shadow = None if shadow_deaths is None else list(shadow_deaths)
        self._shadow_rng = np.random.default_rng(seed + 7919)
        self._tick = 0
        self.rng = np.random.default_rng(seed)
        self.v = np.zeros((h, w))
        self.mem = np.zeros((h, w))
        self.eq_count = np.zeros((h, w), dtype=np.int64)
        self.code = np.zeros((h, w, K, F), dtype=np.int64)
        self.alive = np.zeros((h, w), dtype=bool)
        r0, c0 = (h - bloque) // 2, (w - bloque) // 2
        sl = (slice(r0, r0 + bloque), slice(c0, c0 + bloque))
        self.alive[sl] = True
        self.v[sl] = self.rng.uniform(0.0, 1.0, size=(bloque, bloque))
        self.code[sl][..., 0] = self.rng.integers(0, N_OPS, size=(bloque, bloque, K))
        self.code[sl][..., 1:] = self.rng.integers(0, 16, size=(bloque, bloque, K, F - 1))
        self.seen: set = set()
        self.events: dict = {}
        self.spawns: list = []
        self._register_genomes()

    # ---- interfaz común ----
    @property
    def n(self) -> int:
        return self.h * self.w

    def genomas(self) -> dict:
        return {(int(r), int(c)): self.code[r, c].tobytes()
                for r, c in zip(*np.nonzero(self.alive))}

    def vaciar(self, coord: tuple) -> None:
        r, c = coord
        self.alive[r, c] = False
        self.v[r, c] = 0.0
        self.code[r, c] = 0
        self.eq_count[r, c] = 0
        self.mem[r, c] = 0.0

    def _register_genomes(self) -> int:
        new = 0
        for g in self.genomas().values():
            if g not in self.seen:
                self.seen.add(g)
                new += 1
        return new

    def _ctx(self, r: int, c: int) -> tuple:
        codes, vs = [], []
        for dr, dc in DIRS:
            rr, cc = r + dr, c + dc
            if 0 <= rr < self.h and 0 <= cc < self.w and self.alive[rr, cc]:
                codes.append(self.code[rr, cc])
                vs.append(float(self.v[rr, cc]))
            else:
                codes.append(None)
                vs.append(0.0)
        codes.append(self.code[r, c])
        return tuple(codes), tuple(vs)

    def _blind(self, code, vs, v, ctx, mi) -> bool:
        out = _salida(code, vs, v, ctx, mi)
        p1 = _salida(code, (0.0,) * 4, 0.0, ctx, mi)
        p2 = _salida(code, (PROBE_HI,) * 4, PROBE_HI, ctx, mi)
        return bool(abs(out - p1) < PROBE_EPS and abs(out - p2) < PROBE_EPS
                    and abs(p1 - p2) < PROBE_EPS)

    def step(self) -> dict:
        prev_v, prev_code, prev_alive = self.v.copy(), self.code.copy(), self.alive.copy()
        colonized = deaths = invaded = 0
        self.events, self.spawns = {}, []
        doomed: set = set()
        if self.shadow is not None:
            d = self.shadow[self._tick] if self._tick < len(self.shadow) else 0
            idx = np.flatnonzero(self.alive.ravel())
            if d > 0 and len(idx) > 0:
                doomed = set(int(k) for k in self._shadow_rng.choice(
                    idx, size=min(int(d), len(idx)), replace=False))
        self._tick += 1
        for flat in self.rng.permutation(np.flatnonzero(self.alive.ravel())):
            r, c = divmod(int(flat), self.w)
            if not self.alive[r, c]:
                continue
            if int(flat) in doomed:
                self.vaciar((r, c))
                deaths += 1
                continue
            ctx, vs = self._ctx(r, c)
            mi = float(self.mem[r, c]) if self.memoria else 0.0
            stats: dict | None = {} if self.log_events else None
            v_new, own_next, spawn, raw = execute_plano(self.code[r, c], vs, float(self.v[r, c]),
                                                        ctx, r_init=mi, stats=stats)
            if stats is not None:
                self.events[(r, c)] = stats
            blind = False if self.shadow is not None else self._blind(self.code[r, c], vs,
                                                                       float(self.v[r, c]), ctx, mi)
            if not math.isfinite(v_new) or blind:
                self.vaciar((r, c))
                deaths += 1
                continue
            if self.invasion is not None:
                if abs(v_new - float(self.v[r, c])) < self.eq_eps:
                    self.eq_count[r, c] += 1
                else:
                    self.eq_count[r, c] = 0
            self.v[r, c] = v_new
            self.code[r, c] = own_next
            self.mem[r, c] = raw
            if spawn is None:
                continue
            side, mpos, mop, locus = spawn
            child = own_next.copy()
            child[mpos, 0] = mop                      # germinal (v2), siempre
            if self.recombina:                        # v7: el otro progenitor
                orr, occ = r - DIRS[side][0], c - DIRS[side][1]
                if (0 <= orr < self.h and 0 <= occ < self.w and self.alive[orr, occ]
                        and not np.array_equal(self.code[orr, occ], self.code[r, c])):
                    child[locus] = self.code[orr, occ][locus]
            tr, tc = r + DIRS[side][0], c + DIRS[side][1]
            if not (0 <= tr < self.h and 0 <= tc < self.w):
                continue                              # la pared de la placa
            if not self.alive[tr, tc]:
                self.code[tr, tc] = child
                self.v[tr, tc] = v_new
                self.alive[tr, tc] = True
                self.eq_count[tr, tc] = 0
                self.mem[tr, tc] = 0.0
                colonized += 1
                self.spawns.append(((r, c), (tr, tc)))
            elif self.invasion is not None and (
                    self.invasion == "siempre" or self.eq_count[tr, tc] > self.eq_window):
                self.code[tr, tc] = child
                self.v[tr, tc] = v_new
                self.eq_count[tr, tc] = 0
                self.mem[tr, tc] = 0.0
                invaded += 1
                self.spawns.append(((r, c), (tr, tc)))
        both = prev_alive & self.alive
        code_change = float((self.code[both] != prev_code[both]).any(axis=(1, 2)).mean()) if both.any() else 0.0
        value_change = float(np.abs(self.v[both] - prev_v[both]).mean()) if both.any() else 0.0
        new_genomes = self._register_genomes()
        n_alive = int(self.alive.sum())
        return {"alive_frac": float(self.alive.mean()), "n_world": self.n,
                "code_change": code_change, "value_change": value_change,
                "colonized": colonized, "grown": 0, "deaths": deaths, "invaded": invaded,
                "new_genomes": new_genomes,
                "diversity": len(set(self.genomas().values())) if n_alive else 0}

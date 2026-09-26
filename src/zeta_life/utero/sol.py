"""
El sol: un entorno con estructura aprendible para El Útero (docs/PLAN_INTELIGENCIA.md).

No es una mano que dirige: es clima. La materia del MÁS ALLÁ (los vecinos
fuera del mundo, que en v1..v8 valen 0) sigue `s(t)` en [0,1). El tejido no
puede leer código del sol (no hay) ni saber cuándo cambia: sólo siente la
materia de su borde.

Estructura, determinista y sembrada aparte (el observador la conoce, el tejido no):
- ESTACIONES en orden fijo y cíclico A → B → C → A…: la regularidad aprendible.
  (`orden="permutado"`: sucesor al azar sin repetir el régimen actual — el
  control que quita la regularidad de orden y deja todo lo demás igual.)
- DURACIONES tomadas de un mapa logístico (r=3.9) escalado a [dur_min, dur_max]:
  típicas pero impredecibles desde la señal. En una estación LARGA el instante
  típico de cambio pasa sin que el sol cambie: ahí se mide la anticipación.
- DÍA dentro de cada estación: s(t) = base + amp·(0.5+0.5·sin(2πt/T)) mod 1.

Manos declaradas: la forma de s(t), los tres regímenes, el rango de duraciones.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

# (nombre, base, amplitud, periodo del día)
REGIMENES = (("A", 0.15, 0.05, 40), ("B", 0.55, 0.40, 120), ("C", 0.40, 0.20, 20))


@dataclass
class Sol:
    seed: int = 0
    ticks: int = 20000
    dur_min: int = 300
    dur_max: int = 900
    regimenes: tuple = REGIMENES
    orden: str = "ciclico"          # "ciclico" (A→B→C, aprendible) | "permutado" (control)
    estaciones: list = field(default_factory=list, init=False)   # (nombre, inicio, fin)
    _s: np.ndarray = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        x = 0.1 + 0.8 * ((self.seed * 0.6180339887498949) % 1.0)   # semilla del mapa logístico
        rng = np.random.default_rng(10_000 + self.seed)             # sólo para orden="permutado"
        t, k = 0, 0
        prev = None
        while t < self.ticks:
            x = 3.9 * x * (1.0 - x)                                 # mapa logístico, caótico
            dur = int(self.dur_min + x * (self.dur_max - self.dur_min))
            if self.orden == "ciclico":
                nombre = self.regimenes[k % len(self.regimenes)][0]
            else:                                                   # permutado: sin sucesor fijo
                opciones = [r[0] for r in self.regimenes if r[0] != prev]
                nombre = str(rng.choice(opciones))
            prev = nombre
            self.estaciones.append((nombre, t, min(t + dur, self.ticks)))
            t += dur
            k += 1
        s = np.zeros(self.ticks)
        for nombre, ini, fin in self.estaciones:
            _, base, amp, periodo = next(r for r in self.regimenes if r[0] == nombre)
            tt = np.arange(ini, fin)
            s[ini:fin] = (base + amp * (0.5 + 0.5 * np.sin(2 * math.pi * (tt - ini) / periodo))) % 1.0
        self._s = s

    def __call__(self, t: int) -> float:
        """Materia del más allá en el tick t (constante = último valor si t excede)."""
        return float(self._s[min(int(t), self.ticks - 1)])

    @property
    def serie(self) -> np.ndarray:
        return self._s

    def regimen(self, t: int) -> str:
        for nombre, ini, fin in self.estaciones:
            if ini <= t < fin:
                return nombre
        return self.estaciones[-1][0]

    def duracion_tipica(self) -> float:
        """Mediana de las duraciones de todas las estaciones completas."""
        return float(np.median([fin - ini for _, ini, fin in self.estaciones[:-1]]))

    def largas(self, factor: float = 1.25) -> list:
        """Estaciones cuya duración supera factor × la típica (para la anticipación)."""
        tip = self.duracion_tipica()
        return [(n, i, f) for n, i, f in self.estaciones[:-1] if f - i > factor * tip]

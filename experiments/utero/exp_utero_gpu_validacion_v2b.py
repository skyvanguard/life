"""
§38b — VALIDACIÓN DEL MOTOR EN GPU, réplica de V2 con 24 semillas nuevas.
(docs/PLAN_INTELIGENCIA.md §38; ledger 2026-09-27)

V2 (§38) en GPU dio, contra la primera evolución de CPU (§34–§35): nivel de
w̄_A > nulo en 11/12 (CPU 10/12 y 10/12), medianas 0.442 contra 0.380 (CPU
0.434/0.385 y 0.423/0.363), escala media 0.76 (CPU 0.71/0.75), banda
anti-hambruna 0.59 contra 0.37 (CPU 0.54/0.34 y 0.56/0.35); pero la tendencia
tardía/temprana superó al nulo en 9/12 (p signo 0.073), un par por debajo de
la regla (p < 0.05). Por la letra: MOTOR NO VALIDADO.

Decisión declarada ANTES de correr esta réplica: la magnitud del efecto
coincide con CPU en todas las lecturas; lo que falló es la significación con
n = 12. Réplica independiente con 24 semillas NUEVAS (12–35), mismo diseño y
MISMA regla (tendencia y nivel > nulo en ≥ 75% de los pares, p signo < 0.05
en la tendencia). Si cumple: motor validado, con la nota de que la primera
réplica de 12 falló por un par. Si no cumple: el motor sigue sin validar y
las preguntas nuevas se hacen en CPU hasta entender la diferencia.

    PYTHONPATH=src python experiments/utero/exp_utero_gpu_validacion_v2b.py
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("val", HERE / "exp_utero_gpu_validacion.py")
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)
V.V2["seeds"] = list(range(12, 36))
V.NAME = "utero_gpu_validacion_v2b"


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("VALIDACION DEL MOTOR EN GPU -- replica de V2 con 24 semillas nuevas (12-35), misma regla")
    out("=" * 80)
    out(f"dispositivo: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'}; regla pre-registrada (docstring)")
    out("")
    ok = V.validar_v2(out)
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    out("=> MOTOR VALIDADO: la replica de 24 semillas reproduce la primera evolucion con la regla de §27." if ok
        else "=> MOTOR NO VALIDADO: tampoco con 24 semillas nuevas.")
    (V.RESULTS / f"{V.NAME}_run.txt").write_text(chr(10).join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

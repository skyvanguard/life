# Zeta Life

**Emergent coherent integration in adaptive multi-agent systems**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-643%20passed-brightgreen.svg)](tests/)

---

## Overview

Zeta Life is a computational framework for studying **phase transitions in adaptive integration systems**. It models how independent processing units (kernels) can transition from fragmented computation to coherent, unified integration -- and how populations of such units exhibit emergent collective behavior.

The core equation predicts when integration emerges:

$$\Psi = B^3 + \Phi \qquad \text{(integration index, supercritical regime)}$$

$$\Phi_c = \frac{F_i}{\alpha - C} \qquad \text{(critical threshold for phase transition)}$$

$$B = \frac{\Phi - \Phi_c}{\Phi_c} \qquad \text{(binding factor)}$$

The cubic term $B^3$ creates a **sharp phase transition**: below the critical threshold $\Phi_c$, integration is zero. Above it, the system amplifies nonlinearly -- a mathematical signature of emergent coherence.

### Three programs, in the order they were built

| # | Program | Question | Status |
|---|---------|----------|--------|
| 1 | **The Conscious Kernel** (`kernel/`) | Can one adaptive unit integrate its own experience? | Mature substrate — architecture below |
| 2 | **The North** (`introspection/`) | Can $\Psi$ live in a real LLM's own activations, and can the model *learn to perceive it*? | **Closed 2026-07-02 as an honest negative** |
| 3 | **El Útero** (`utero/`) | What if the physics itself is mutable, and only what sustains itself persists? | **Live frontier** |

The north asked the harder question — *adaptation, not scale* — and answered it
honestly in the negative: a model trained to name a non-textual injected state
memorizes the exact vectors rather than reading the concept direction, at 0.6B and
at 8B alike. That closure is what moved the work down a level, to a substrate with
no pretrained anything in it at all.

---

## El Útero — the live frontier

> Full design, the three principles, and the honest results ledger:
> [`docs/EL_UTERO.md`](docs/EL_UTERO.md) (written in Spanish, like this line's code
> comments).

The smallest universe where something could emerge without anyone dictating what it
will be. Conway-style — minimal local rules, undictated emergence — with one twist:

**the rules are part of the mutable state.**

Three non-negotiable principles:

1. **Rules-as-state.** No untouchable law outside the world. The law lives inside,
   mutable — like a genome, which is at once the instruction that builds *and* the
   matter that can mutate.
2. **Closed loop (physics ↔ physics).** A cell's rule acts on the world *and on
   itself*: `(v', r') = APPLY(r_i, {v, r}_{i-1, i, i+1})`. Local, self-referential,
   with no outer level.
3. **Persistence as the only filter.** No goal, no reward, no judge. A cell becomes
   VOID if its next rule is degenerate. *Alive is what manages to keep being.*

```python
from zeta_life.utero import UteroCreciente, run_history_creciente

# v1..v5 are boolean flags on one class, not separate implementations.
# All-False == v1, byte-identical to the committed v1 results.
utero = UteroCreciente(n0=16, seed=13, toroidal=True, memoria=True)   # v3 + v5
```

| Flag | Version | Hypothesis about where the "cage" moved |
|------|---------|------------------------------------------|
| *(none)* | v1 | Async update + a space that opens from the inside (the world grows only where a physics `SPAWN`s past the border) |
| `germinal=True` | v2 | Offspring vary from the matter present at birth — variation from the world's state, not from an RNG of ours |
| `toroidal=True` | v3 | Matter on a circle (`v' = R3 mod 1`) so expansive maps become expressible |
| `muerte_equilibrio=True` | v4 | Still matter = dead standing |
| `memoria=True` | v5 | Each cell retains its raw internal potential and re-injects it next tick — 2nd-order dynamics |

**The yardstick (anti-illusion).** With random update ordering, "it didn't cycle"
proves nothing. The honest measure is **never-before-seen genomes minted per
segment**, because new code can only come from write events (`MUTO`/`COPY`), never
from the ordering RNG. Every experiment declares its "visible hands" (seeded order,
the `max_n` wall, probe thresholds) in its docstring.

**Honest ledger** — more refutations than wins, and that is the point:

| Version | Result |
|---------|--------|
| **Nivel 1** — rewrite a law's *content* | 20/20 seeds beat at 500 ticks (0 thermal deaths, real death + re-colonization). At 5000 ticks: **slow-motion crystallization** — only 3/20 sustain macroscopic change |
| **Nivel 2** — rewrite the law's *form* | Richer attractors (real ecology: 75% extinction → 70% recovery via `SPAWN`), **but the anti-cycle control unmasks it**: 20/20 in short limit cycles. Determinism + fixed space + synchrony ⇒ recurrence |
| **v1** creciente | The space **does** open (13/20 worlds grow 16→256, growth done by the physics itself) — **but novelty dries up**: ~12 new genomes in the first segment, zero after. Cage moved to frozen code |
| **v2** germinal | Doubles early novelty (23.6 vs 12.1) and **still dries up**. Sharp diagnosis: births continue (3465 late ones) minting **zero** new genomes — same context → same offspring. Cage moved to frozen *matter* |
| **v3** toroidal | **First sustained structural novelty** — seed 13 still minting new genomes at t=12000. Survived a noise-vs-function ablation control: verdict **function** (novelty propagates and persists), though the pump does not regenerate |
| **v4** equilibrium-death | **Hypothesis REFUTED** — killing still matter produces a desert, not self-repair. 15/20 thermal deaths; the ablated pump does not come back |
| **v5** memoria | **First self-repair**: with recurrent hidden state the post-ablation tail sustains where without it it collapses to ~0. Caveats kept: not universal (early ablation, OFF even wins), n=1 seed, the regime is still 1/20 |

---

## Architecture — the Conscious Kernel

### Adaptive Kernel (Active Inference)

Each `ConsciousKernel` implements a full Active Inference cycle:

```
PERCEIVE -> PREDICT -> COMPARE -> UPDATE -> MEMORIZE -> ACT -> REFLECT -> DREAM
```

| Component | Role |
|-----------|------|
| WorldModel | GRU-based predictive model of the environment |
| SelfModel | Recursive self-modeling (Strange Loop) |
| PredictionErrorEngine | Multi-channel precision-weighted error signals |
| PrecisionController | Learned precision hyper-model (attention) |
| FastMemory / SlowMemory | Complementary Learning Systems (episodic + semantic) |
| DreamEngine | Zeta-driven offline consolidation |
| PersistenceLayer | Identity save/load across sessions |

The integration index $\Psi$ is derived from internal signals:
- $\Phi$ (integrated information) from inverse free energy + memory depth
- $F_i$ (binding force) from learned precisions + self-reflection convergence
- $C$ (coherence cost) from recent prediction errors

```python
import torch
from zeta_life.kernel import ConsciousKernel

kernel = ConsciousKernel(obs_dim=4, latent_dim=32, alpha=1.0)
result = kernel.step(torch.randn(4))
print(result.psi)          # integration index [0, 1]
print(result.free_energy)  # prediction error magnitude
```

Or run the full demo (learning loop + identity save/load):

```bash
make quickstart            # = PYTHONPATH=src python demos/quickstart.py
```

### Multi-Kernel Organism (Darwinian Brain)

Multiple kernels compete for a shared `GlobalWorkspace` via proposal strength. Energy-managed spawning, merging, and death create a Darwinian selection process at the kernel level.

```python
import torch
from zeta_life.kernel import ConsciousOrganism

organism = ConsciousOrganism(obs_dim=4, initial_kernels=5)
result = organism.step(torch.randn(4))
print(result.psi)         # organism-level integration
print(result.population)  # surviving kernel count
```

### Hierarchical Integration (Cells -> Clusters -> Organism) — archived

> **Archived (2026-06-08).** A parallel Cells→Clusters→Organism consciousness
> formalism that the live kernel never used. Removed from the working tree in the
> refocus; preserved on the `legacy/pre-refocus-snapshot` branch.

### Zeta Function as Temporal Binding (optional — tested, not load-bearing)

The Riemann zeta zeros give an *optional* temporal basis:

$$K_\sigma(t) = 2 \sum_n \exp\!\bigl(-\sigma\,|\gamma_n|\bigr)\,\cos(\gamma_n\, t)$$

where $\gamma_n$ are the imaginary parts of zeta zeros (14.134, 21.022, 25.011, ...). They drive the DreamEngine's consolidation rhythm and are available as an optional `OscillatorBank` time code for the world model.

**Honest result (this project's own experiments).** The *specific* zeta spectrum is **not** load-bearing. In the kernel, an equispaced **Fourier lattice matches or beats zeta** at temporal prediction — even on a zeta-structured signal — and zeta's GUE level-repulsion is functionally flat (`results/zeta_vs_baselines_run.txt`, `results/spacing_statistics_run.txt`). In the consciousness dynamics, ZETA == UNIFORM (p=1.0). Zeta genuinely wins only in the spatial cellular automata. **Recommendation:** fixed temporal basis → `OscillatorBank.fourier`/`log_spaced`; adaptive → `learned`. Zeta is kept as a documented, tested design choice — not the thesis.

---

## The North: making Ψ internal (introspection research) — closed

> **Status: closed 2026-07-02 as an honest negative.** Kept here for the record and
> the tooling. Do not cite the F3 row below as a positive result.

The kernel's $\Psi$ is an **external** index — a thermometer pointed *at* an agent.
This program asked the harder question: can $\Psi$ become a property of an agent's
**own activations**, and can the agent learn to **perceive** it? The bet was
*adaptation, not scale* — a model that adapts until it can observe itself, rather
than scaling to a giant.

**Substrate.** A live LLM (Yvyra, Qwen3-8B) runs in `transformers`/8-bit. The
`bridge/` couples its real experience to the kernel; `introspection/` computes
candidate integration metrics over its hidden states and tests introspection with
the methods of Anthropic (Lindsey, concept injection) and Binder (privileged
access). Honest, control-driven results so far:

| Experiment | Result |
|------------|--------|
| **Phase A/B** (expose Ψ to the agent, sham control) | Inconclusive — Ψ saturates (~89% high); the design works, the signal didn't vary enough (`docs/PHASE_B_DESIGN.md`) |
| **Spontaneous introspection** (concept injection, untrained) | **Negative** — 0/30; a control killed the apparent positive (steering, not introspection). Replicates the scale limit Anthropic sees |
| **Trained P(IK) self-report** (LoRA) | **Honest negative** — a strong blind M2 (Claude, 0.82) and the model's own softmax confidence (0.81) both beat the self-report (0.76). It verbalizes confidence, no robust *privileged* access |
| **Trained injected-concept detection** (F3; LoRA, constant prompt → non-textual by construction) | **Negative.** The 10-concept run looked like a win (accuracy 1.000 vs chance 0.091, 0 false positives), but the generalization control killed it: at 45 concepts, in-distribution 0.909–0.953 yet **held-out vectors at chance** (0.022 / 0.033, chance 0.022) on **both** Qwen3-0.6B and 8B. Both models memorize the exact injected vectors; neither reads the concept *direction*. Scale does not help |

**Net verdict: negative.** The F3 row is the discipline working as intended — an
apparent 1.000 accuracy that died to a control built after the fact. Every result
here was reported only after its adversarial control, which is what separates
"verbalizing confidence" from "privileged introspection." See
`docs/{ANTHROPIC_NORTH,RESEARCH_PHASE_B,TARGET_SELECTION,TRAINED_INTROSPECTION,LORA_PLAN}.md`
and `results/f3_inject_{06b,8b}_scale_run.txt`.

```python
from zeta_life.introspection import psi_act_all   # 4 integration metrics over hidden states
# harness.py / concept_injection.py need the GPU stack (transformers); see experiments/introspection/
```

---

## Installation

```bash
git clone https://github.com/skyvanguard/zeta-life.git
cd zeta-life
pip install -e .

# With all extras (mpmath for exact zeta zeros, jupyter)
pip install -e ".[full]"

# Dev toolchain (pytest, ruff, black, mypy) -- same as `make install`
pip install -e ".[dev,full]"

# Only for the RL benchmark experiments (CartPole, Pendulum, MuJoCo Reacher)
pip install -e ".[rl]"
```

### Dependencies

- Python 3.9+
- PyTorch 2.0+
- NumPy, SciPy, Matplotlib

The introspection experiments additionally need a GPU stack (`transformers`, `peft`,
`bitsandbytes`, `datasets`, `scikit-learn`) that the base install does not provide.

---

## Quick Start

```python
import torch
from zeta_life.kernel import ConsciousKernel

# Create a kernel and run it for 100 steps
kernel = ConsciousKernel(obs_dim=4, latent_dim=32)
for i in range(100):
    stimulus = torch.randn(4)
    result = kernel.step(stimulus)

print(f"Psi: {result.psi:.4f}")
print(f"Free energy: {result.free_energy:.4f}")
print(f"Dreamed: {result.dreamed}")
```

### Run Experiments

Experiments are self-pathing; each writes `results/<name>_run.txt` (+ a `.png`).

```bash
# El Utero -- the live line (docs/EL_UTERO.md)
python experiments/utero/exp_primer_latido.py         # Nivel 1: rewrite a rule's CONTENT
python experiments/utero/exp_nivel2_latido.py         # Nivel 2: rewrite the rule's FORM
python experiments/utero/exp_utero_creciente.py       # v1: async + self-opening space
python experiments/utero/exp_utero_germinal.py        # v2: germinal variation
python experiments/utero/exp_utero_toroidal.py        # v3: toroidal matter (sustained novelty)
python experiments/utero/exp_utero_ruido_vs_funcion.py  # control: noise vs function (seed 13)
python experiments/utero/exp_utero_motor.py           # v4: equilibrium-death (REFUTED)
python experiments/utero/exp_utero_memoria.py         # v5: memory (first self-repair)

# Psi validation on real datasets
python experiments/datasets/exp_real_data_psi.py

# Kernel validation (compositionality, grounding, emergence)
python experiments/kernel/exp_conscious_kernel_validation.py

# Multi-kernel organism dynamics
python experiments/kernel/exp_organism_emergence.py

# Science pipeline (toy -> instrument; see docs/SCIENCE_PLAN.md)
python experiments/kernel/exp_psi_vs_free_energy.py   # validate Psi (Albantakis method)
python experiments/kernel/exp_epistemic_depth.py      # precision hyper-model (epistemic depth)
python experiments/kernel/exp_yvyra_experiment.py     # Yvyra pipeline (modes + blind re-scorer)

# Introspection / the north (needs the GPU stack: transformers + bitsandbytes)
python experiments/introspection/exp_pik_probe.py          # is "I know" in the activations?
python experiments/introspection/exp_pik_train.py          # train P(IK) self-report (LoRA)
python experiments/introspection/exp_f3_inject_train.py    # trained injected-concept detection
```

### Run Tests

```bash
PYTHONPATH=src pytest tests/ -q                    # 643 tests, ~105s (or `pip install -e .` first)
PYTHONPATH=src pytest tests/test_utero_memoria.py -q   # a single file
make lint                                          # ruff + mypy
make format                                        # black + ruff --fix
```

---

## Project Structure

```
zeta-life/
|-- src/zeta_life/
|   |-- utero/           # LIVE FRONTIER - self-rewriting substrate (nivel1, nivel2, creciente)
|   |-- kernel/          # Active Inference kernel + Darwinian organism (21 files)
|   |-- bridge/          # Yvyra coupling - feed a live agent's experience to the kernel
|   |-- introspection/   # the north (closed) - Psi over an LLM's activations
|   |-- instrumentation/ # TickLogger - paired per-tick logging (science pipeline)
|   |-- integration/     # formal_equations.py - the integration index Psi
|   |-- datasets/        # Real-world dataset adapters (for Psi validation)
|   |-- core/            # zeta_constants, vertex, tetrahedral geometry
|   +-- utils/           # Shared utilities
|
|-- experiments/
|   |-- utero/           # 8 experiments - the live line (Nivel 1/2, v1..v5, controls)
|   |-- kernel/          # 31 kernel experiments
|   |-- introspection/   # the north - probe, P(IK) LoRA, injected-concept detection
|   +-- datasets/        # Psi on real data
|
|-- demos/               # quickstart.py - the 60-line kernel demo
|-- deploy/zeta/         # yvyra_kernel.py - tick-driven entry point for Yvyra
|
|-- tests/               # 41 test files (643 tests)
+-- docs/                # Documentation, papers, plans (start at EL_UTERO.md;
                         #   also ANTHROPIC_NORTH, TRAINED_INTROSPECTION, SCIENCE_PLAN)

(Legacy subsystems -- psyche, hierarchical/IPUESA integration, organism,
evolution -- were archived on 2026-06-08 to the legacy/pre-refocus-snapshot branch.)
```

---

## Formal Equations

| Equation | Formula | Meaning |
|----------|---------|---------|
| Critical threshold | $\Phi_c = \frac{F_i}{\alpha - C}$ | Minimum integration for phase transition |
| Binding factor | $B = \frac{\Phi - \Phi_c}{\Phi_c}$ | Distance above threshold (normalized) |
| Integration index | $\Psi = B^3 + \Phi$ | Nonlinear amplification of coherence |
| Critical mass | $M_c = \frac{F_i}{\alpha - C}$ | Minimum units for integration to emerge |
| Corruption threshold | $1 - \frac{F_i}{\alpha \cdot M \cdot \alpha_s}$ | Maximum damage ratio before collapse |

These are implemented as pure functions in `integration/formal_equations.py` and consumed by the kernel's `_compute_psi()`.

---

## Theoretical Foundations

- **Active Inference / Free Energy Principle** (Friston) -- the kernel minimizes prediction error
- **Complementary Learning Systems** (McClelland et al.) -- fast episodic + slow semantic memory
- **Darwinian Brain** -- multi-kernel competition via Global Workspace
- **Integrated Information Theory** (Tononi) -- Phi as integration measure
- **LLM introspection** (Lindsey/Anthropic concept injection; Binder privileged access) -- the basis of the introspection program (see "The North")
- **Self-modifying cellular automata** -- Conway-style minimal locality, but with the rules as mutable state and persistence as the only filter (see "El Útero")
- **Riemann zeta zeros** -- optional temporal basis (tested; not load-bearing except in spatial CA -- see "Zeta Function as Temporal Binding")

---

## Citation

```bibtex
@software{zeta_life_2026,
  author = {Francisco Ruiz},
  title = {Zeta Life: Emergent Coherent Integration in Adaptive Multi-Agent Systems},
  year = {2026},
  url = {https://github.com/skyvanguard/zeta-life}
}
```

---

## License

MIT License -- See [LICENSE](LICENSE) for details.

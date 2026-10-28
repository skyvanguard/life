# Zeta Life

**Can a system be born empty, learn from its own experience in life, and sustain an
identity -- without pretraining?**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-810%20passed-brightgreen.svg)](tests/)

---

## Overview

Zeta Life is a research repository built around **one invariant question**
([`docs/NORTE.md`](docs/NORTE.md)): can a system be born empty, learn from its own
experience while it lives, and keep an identity, with no pretraining? Every program
here is one incarnation of that question. When an incarnation hits a wall, the work
moves down a level and the wall is written down.

The discipline is the same in every program: the yardstick is written before looking,
every verdict is a pre-registered rule (sign tests over 12 seeds or pairs, then a
replication on 12 others), the adversarial control is built before a result is
believed, and refutations go into the ledger with the same weight as positives.

### The programs, in the order they were built

| Program | Question | Answer | Status |
|---------|----------|--------|--------|
| **Zeta / IPUESA / psyche** (2025-12 to 2026-03) | Do the Riemann zeta zeros give structure to an adaptive AI? | No: zeta == uniform outside the spatial cellular automata | archived |
| **The Conscious Kernel** (`kernel/`, 2026-03 to 2026-06) | Can one active-inference unit integrate its experience with a persistent identity? | Yes as a harness: learns in life, solves CartPole / Pendulum / Reacher with $\Psi$ live; $\Psi$ is a heuristic, not a consciousness measure | mature substrate |
| **The North** (`introspection/`, 2026-06 to 2026-07) | Can $\Psi$ live in a real LLM's own activations, and can the model learn to read it? | No: trained introspection is a lookup, not a general read (0.6B and 8B alike) | closed, honest negative |
| **El Útero** (`utero/`, 2026-07 to 2026-10-26) | What emerges from a physics that rewrites itself, with nothing pretrained in it? | Rare sustained novelty behind five named cages; a measured, replicated Darwinian adaptation; learning in life that does not generalize | closed |
| **The kernel coupled to Yvyra** (Phase A/B, 2026-06 to 2026-10-26) | Does an LLM's introspection anchor to the kernel's $\Psi$? | Inconclusive; $\Psi$ turned out to be a relative-surprise detector | closed as a vehicle: the kernel *is* the agent |
| **The kernel in its own world** (2026-10-26 on, [`docs/MUNDO_PROPIO.md`](docs/MUNDO_PROPIO.md)) | Does it learn in life, remember, tell what it did from what happened to it, and keep an identity? | §K1–§K13, below | **live frontier** |

---

## The kernel in its own world — the live frontier

> Design, every pre-registration and the honest ledger:
> [`docs/MUNDO_PROPIO.md`](docs/MUNDO_PROPIO.md) (written in Spanish).

The kernel is the agent: no LLM, no pretraining. It lives in a small world where **its
own actions cause its experience** -- an action moves a state on the simplex, and a
hidden regime decides how (four remappings: three recur, one is never seen until late).
It is born empty, plans by expected free energy toward a preferred state, and learns
its world model awake and in sleep.

The experiments change one variable at a time:

- **§K1–§K3, memory.** Does it learn, remember, and distinguish what it did from what
  happened to it?
- **§K4–§K5, identity.** Identical newborn twins are raised in different worlds, then
  share a long exile in a world neither has lived. Do they stay different? The readout
  H > 0 means each twin does better in its own childhood world than its sibling does.
- **§K6–§K13, a repertoire.** A COIN-style set of context experts in the world model,
  and what holds the identity inside it: the sleep, the separation, the snapshot, the
  wake, a wake rate per expert, and the return home.

| § | Mechanism | Pre-registered verdict (pairs 0–11) | Replication (pairs 12–23) |
|---|-----------|-------------------------------------|---------------------------|
| §K1 | the plain kernel: online world model only | NO CONTROLA by the letter (9/12); learns the never-seen regime 12/12, does not remember 6/12 | — |
| §K2 | `wm_sleep_replay`: sleep replays lived sequences (BPTT) | APRENDE Y RECUERDA (12/12, 12/12, 11/12), by averaging the lived regimes, not by context | REPLICADO |
| §K3 | + `wm_error_input`, 4× sleep | REPERTORIO; DISTINGUE 12/12 | repertoire NOT replicated (8/12); DISTINGUE replicated |
| §K4 | twins raised in different worlds | IDENTIDAD (por el sueño): PERSISTE 12/12 after an exile as long as the childhood | REPLICADO (24/24); its price, rigidity before the never-lived, 12/12 |
| §K5 | raised between home and a school | MENOS RÍGIDO, CON IDENTIDAD; the `self_embedding` carries the life, not the childhood | REPLICADO |
| §K6 | `wm_contexts=6`: COIN-style context experts | REPERTORIO ROBUSTO 12/12: known regimes survive a never-seen one | REPLICADO (24/24) |
| §K7 | the repertoire + the twins | IDENTIDAD EN EL REPERTORIO: the identity is which expert it returns to (PERSISTE 12/12, ELIGE 11/12); §K4's price nearly vanishes | REPLICADO (24/24, 22/24) |
| §K8 | 2×2, sleep × experts | POR EL SUEÑO: without sleep the home expert stays frozen but coarse | REPLICADO; later traced to a lagged snapshot (§K10) |
| §K9 | sleep only in the childhood | INDETERMINADO: the first exile steps damage the precise expert before the snapshot | NOT replicated (HACE FALTA SEGUIR DURMIENDO) |
| §K10 | `snapshot_lag=50`: a snapshot in time | BASTA LA NIÑEZ: a precise frozen expert holds the identity; never sleeping, separation alone holds it too (19/24) | REPLICADO |
| §K11 | `wake_lr_scale=0.1`: a slower wake | PRECISA PERO LENTA: the slow wake keeps what sleep consolidates (home oracle 0.009 vs 0.042 awake) but enters never-lived worlds late (first exile block 0.970 vs 0.497) | REPLICADO (24/24 pooled on every readout); the price falls in the first two exile blocks |
| §K12 | `wake_lr_scale_learning=1.0`: slow wake only while an expert explains its stream | VIGILIA QUE NO BORRA: keeps like the slow wake (0.009) and enters never-lived worlds faster than the full-rate kernel (first exile block 0.367 vs 0.497); 0 stuck blocks | REPLICADO (24/24 pooled; 1 stuck block in 48 twins); the return home after the exile costs a bit more (VUELVE 7/24) |
| §K13 | `slow_return=True`: an expert made active again by a switch learns slowly until it explains its stream (at most `persist` ticks) | VUELVE A CASA: the return home costs less than under §K12 (12/12; home T2 0.117 vs 0.168) and than the full-rate kernel (11/12), keeping all of §K12 | REPLICADO (pooled 24/24 and 22/24); after the switch the home expert costs what an intact one does (0.056 vs 0.114); the price is 9 of 96 twin-assays abroad |

**What it adds up to, so far.** The kernel learns in life from its own stream. With a
sleep that replays what it lived, it remembers. With a repertoire of experts it keeps
the known through the new. Twins raised apart stay different after a long shared
exile, and the identity lives in the world model -- in *which expert it goes back to*
-- not in the `self_embedding`. What holds it is a precise expert kept frozen at the
right time. Online learning between two sleeps erodes what sleep consolidated; a
slower wake prevents that, at the price of entering the never-lived late. That is the
stability–plasticity dilemma, measured inside the kernel -- and a wake rate per expert
resolves it: each expert learns slowly while it explains its stream and at the full
rate while it is newborn or failing. What it learns fast while failing is safe, because
the §K6 snapshot restores the home expert when the new one is born. The last cost was
the return home: the home expert came back intact, but its running error carried the
exile, so it relearned at the full rate and damaged itself until the next sleep. Letting
a returning expert learn slowly until it explains its stream again removes that. The
same kernel now keeps what sleep consolidates, enters the never-lived faster than the
full-rate kernel, and returns home better than it.

```python
import torch
from zeta_life.kernel import ConsciousKernel

# The §K7 "coin" kernel, with §K12's per-expert wake and §K13's slow return.
kernel = ConsciousKernel(
    obs_dim=4, action_mode="efe", preference=torch.tensor([0.7, 0.1, 0.1, 0.1]),
    efe_n_samples=48, efe_obs_norm="l1",
    wm_sleep_replay=200, wm_sleep_seq_len=16, wm_sleep_batch=8,  # §K2, 4x dose (§K3)
    wm_error_input=True,                                          # §K3
    wm_contexts=6,                                                # §K6
    wm_context_kwargs={"wake_lr_scale": 0.1,                      # §K11 (snapshot_lag: §K10)
                       "wake_lr_scale_learning": 1.0,             # §K12
                       "slow_return": True},                      # §K13
)
```

Every one of these mechanisms is off by default, and off is byte-identical to the
plain kernel (tested).

---

## El Útero — closed 2026-10-26

> Design, the three principles and the honest ledger: [`docs/EL_UTERO.md`](docs/EL_UTERO.md);
> paper draft: [`docs/papers/utero-paper.md`](docs/papers/utero-paper.md) (both in Spanish).

The smallest universe where something could emerge without anyone dictating what it
will be: Conway-style minimal local rules, with one twist -- **the rules are part of
the mutable state.**

1. **Rules-as-state.** No untouchable law outside the world. The law lives inside,
   mutable -- like a genome, at once the instruction that builds *and* the matter that
   can mutate.
2. **Closed loop (physics ↔ physics).** A cell's rule acts on the world *and on itself*,
   locally, with no outer level.
3. **Persistence as the only filter.** No goal, no reward, no judge. *Alive is what
   manages to keep being.*

| Arc | Result |
|-----|--------|
| **Novelty** (Nivel 1/2, v1–v8) | The first sustained structural novelty (v3, toroidal matter) and the first self-repair (v5, memory) -- but rare (4–6% of 1-D worlds, intrinsic to 1-D) and bounded by named cages: frozen code, frozen matter, sterile plains, operands no variation operator could write (the fourth cage), a program→matter map with no locality (the fifth) |
| **Intelligence under a sun** (`docs/PLAN_INTELIGENCIA.md`) | Nineteen pre-registered emergence runs, zero vestiges of regulation, anticipation or learning; a hand-designed famine anticipator is viable but not selected |
| **Evolution** (§17–§35) | Without a local knob the substrate does not evolve: heritable variation is load. With heritable expression knobs, the first measured Darwinian adaptation (§34), replicated with another sun and other soups (§35). Evolution, not intelligence |
| **Learning in life** (§43–§49) | A plastic tissue learns in life from its own income (§45, two suns) but does not generalize: its cells live two seasons and never see the same one twice (§49). Closed by the `docs/NORTE.md` rule; the frontier went back to the kernel |

```python
from zeta_life.utero import UteroCreciente

# The versions are flags on one class; all off == v1, byte-identical to the committed results.
utero = UteroCreciente(n0=16, seed=13, toroidal=True, memoria=True)   # v3 + v5
```

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
| ContextualWorldModel | COIN-style repertoire of world-model experts: hard context inference, spawn on the unexplained, per-expert sleep, snapshots (`snapshot_lag`), a slower wake (`wake_lr_scale`), a wake rate per expert (`wake_lr_scale_learning`), a slow return (`slow_return`) -- §K6–§K13 |
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
git clone https://github.com/skyvanguard/life.git
cd life
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

Experiments are self-pathing; each writes `results/<name>_run.txt` (some also a `.png`).
The full list, with every verdict, is in [`CLAUDE.md`](CLAUDE.md).

```bash
# The kernel in its own world -- the live line (docs/MUNDO_PROPIO.md; 3 CPU processes)
python experiments/kernel/exp_mundo_propio.py               # §K1: learns in life, does not remember
python experiments/kernel/exp_mundo_propio_sueno.py         # §K2: sleep replay of lived sequences
python experiments/kernel/exp_mundo_propio_contexto.py      # §K3: error input + 4x sleep (DISTINGUE)
python experiments/kernel/exp_mundo_propio_gemelos.py       # §K4: twins raised in different worlds
python experiments/kernel/exp_mundo_propio_crianza.py       # §K5: home + school upbringing
python experiments/kernel/exp_mundo_propio_coin.py          # §K6: COIN-style context experts
python experiments/kernel/exp_mundo_propio_casas.py         # §K7: identity in the repertoire
python experiments/kernel/exp_mundo_propio_separacion.py    # §K8: sleep or separation (2x2)
python experiments/kernel/exp_mundo_propio_ninez.py         # §K9: sleep only in the childhood
python experiments/kernel/exp_mundo_propio_foto.py          # §K10: the snapshot in time
python experiments/kernel/exp_mundo_propio_vigilia.py       # §K11: the wake that does not erase
python experiments/kernel/exp_mundo_propio_madurez.py       # §K12: a wake rate per expert
python experiments/kernel/exp_mundo_propio_regreso.py       # §K13: the return home
# most take `humo` (smoke), `calibracion`, `replica` and `reanudar` (resume from disk)

python experiments/kernel/exp_psi_quiebres.py               # Psi as a relative-surprise detector

# El Utero -- closed (docs/EL_UTERO.md)
python experiments/utero/exp_utero_toroidal.py              # v3: first sustained novelty
python experiments/utero/exp_utero_memoria.py               # v5: first self-repair
python experiments/utero/exp_utero_escala.py                # §34: first Darwinian adaptation
python experiments/utero/exp_utero_tejido_plastico.py       # §45: learns in life, does not generalize

# Kernel validation and the science pipeline (docs/SCIENCE_PLAN.md)
python experiments/kernel/exp_conscious_kernel_validation.py
python experiments/kernel/exp_psi_vs_free_energy.py         # validate Psi (Albantakis method)
python experiments/kernel/exp_epistemic_depth.py            # precision hyper-model (epistemic depth)

# Introspection / the north (needs the GPU stack: transformers + bitsandbytes)
python experiments/introspection/exp_pik_probe.py           # is "I know" in the activations?
python experiments/introspection/exp_f3_inject_train.py     # trained injected-concept detection
```

### Run Tests

```bash
PYTHONPATH=src pytest tests/ -q                         # 810 tests (or `pip install -e .` first)
PYTHONPATH=src pytest tests/test_contextual_world_model.py -q   # a single file
make lint                                               # ruff + mypy
make format                                             # black + ruff --fix
```

---

## Project Structure

```
zeta-life/
|-- src/zeta_life/
|   |-- kernel/          # Active Inference kernel (21 modules): world model, contextual
|   |                    #   world model (§K6-§K13), self model, CLS memory, dream, organism
|   |-- utero/           # El Utero (closed) - self-rewriting substrate, 1-D/2-D, sun, GPU engine
|   |-- bridge/          # Yvyra coupling (closed as a vehicle)
|   |-- introspection/   # the north (closed) - Psi over an LLM's activations
|   |-- instrumentation/ # TickLogger - paired per-tick logging (science pipeline)
|   |-- integration/     # formal_equations.py - the integration index Psi
|   |-- datasets/        # real-world dataset adapters (for Psi validation)
|   |-- core/            # zeta_constants, vertex, tetrahedral geometry
|   +-- utils/           # shared utilities
|
|-- experiments/
|   |-- kernel/          # 52 experiments - the kernel's own world (§K1-§K13) and earlier
|   |-- utero/           # 71 experiments - the útero line, closed
|   |-- introspection/   # the north - probe, P(IK) LoRA, injected-concept detection
|   +-- datasets/        # Psi on real data
|
|-- demos/               # quickstart.py - the 60-line kernel demo
|-- deploy/zeta/         # yvyra_kernel.py - tick-driven entry point for Yvyra
|-- tests/               # 65 test files (810 tests)
+-- docs/                # start at NORTE.md, then MUNDO_PROPIO.md (the live ledger)

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

These are implemented as pure functions in `integration/formal_equations.py` and consumed by the kernel's `_compute_psi()`. $\Psi$ is a bespoke, hand-tuned heuristic, not a measure of consciousness: measured alone, it behaves as a **relative-surprise detector** -- it sees rare large breaks in a predictable stream, not frequent ones (`experiments/kernel/exp_psi_quiebres.py`).

---

## Theoretical Foundations

- **Active Inference / Free Energy Principle** (Friston) -- the kernel minimizes prediction error
- **Complementary Learning Systems** (McClelland et al.) -- fast episodic + slow semantic memory
- **Contextual inference / COIN** (Heald, Lengyel & Wolpert, 2021) -- a repertoire of context-specific models, the basis of `ContextualWorldModel`
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
  url = {https://github.com/skyvanguard/life}
}
```

---

## License

MIT License -- See [LICENSE](LICENSE) for details.

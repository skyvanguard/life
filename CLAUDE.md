# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Status note (2026-06-08):** This file was rewritten to match the repository's
> actual current state. The project's center of gravity has moved to the
> **active-inference Conscious Kernel** (`src/zeta_life/kernel/`). Several earlier
> subsystems (psyche, hierarchical/IPUESA integration, evolution, organism) were
> **archived on 2026-06-08** to the `legacy/pre-refocus-snapshot` branch and
> removed from the working tree. See "Core vs Archived" below.
>
> **Update (2026-06-13):** "the north" — making Ψ a property of a real LLM's
> **own activations** and testing whether the model can learn to **introspect**
> it (`src/zeta_life/introspection/`). See "The North" below.
>
> **Update (2026-07, current):** the north **closed as an honest negative**
> (trained injected-concept detection is a *lookup*, not a general read — held-out
> vectors at chance on both 0.6B and 8B). The live frontier moved to **El Útero**
> (`src/zeta_life/utero/`, `docs/EL_UTERO.md`): a minimal self-rewriting substrate
> — Conway-style, but the rules are part of the mutable state. All commits since
> 2026-07-09 are this line. The kernel and the introspection code remain in the
> tree as prior programs; they are not where new work is happening.

## What this project actually is

Three research programs, in the order they were built. Only the third is live:

1. **The Conscious Kernel** (`kernel/`) — the substrate; an active-inference unit
   (below). Mature, tested, not the frontier.
2. **The North** (`introspection/`) — Ψ over a real LLM's own activations.
   **Closed 2026-07-02 as an honest negative.**
3. **El Útero** (`utero/`) — **the live frontier**: the smallest universe where a
   physics rewrites itself and only what sustains itself persists. See below.

### Program 1 — the Conscious Kernel

An **active-inference "Conscious Kernel"** for AI: a single adaptive unit that
runs a perception→prediction→action→reflection→dream loop with a learned world
model, a recursive self-model, precision-weighted prediction errors,
complementary (fast/slow) memory, expected-free-energy action selection, and
persistent identity — plus a Darwinian multi-kernel organism built on top.

The project grew out of earlier work integrating the **Riemann zeta zeros** with
artificial-life systems. That heritage survives in the name and in the
`K_σ(t)` kernel, but **zeta is no longer the thesis**: see "Where zeta actually
matters" below. The real, current research program is emergent coherent
integration via active inference.

**Theoretical foundation (zeta kernel):**
`K_σ(t) = 2 · Σ exp(-σ|γ|) · cos(γt)`, where γ are the imaginary parts of the
non-trivial zeta zeros (14.134725, 21.022040, 25.010858, …). Used in the dream
consolidation rhythm and in the cellular automata; optional in the kernel.

## Repository structure (verified)

```
zeta-life/
├── src/zeta_life/
│   ├── utero/           # LIVE FRONTIER — self-rewriting substrate (3 modules)
│   ├── kernel/          # active-inference Conscious Kernel (21 files)
│   ├── bridge/          # Yvyra coupling — feed a live agent's experience to the kernel
│   ├── introspection/   # the north (closed) — Psi over an LLM's activations
│   ├── integration/     # formal_equations.py — the integration index Psi
│   ├── instrumentation/ # TickLogger — paired per-tick logging (science pipeline)
│   ├── datasets/        # real/synthetic signal loaders for Psi validation
│   ├── core/            # zeta_constants, vertex, tetrahedral geometry
│   └── utils/           # statistics helpers
├── experiments/
│   ├── utero/           # 8 experiments — the live line (Nivel 1/2, v1..v5, controls)
│   ├── kernel/          # 31 kernel experiments
│   ├── introspection/   # the north — probe, P(IK) LoRA, injected-concept detection
│   └── datasets/        # 1 experiment (Psi on real data)
├── deploy/zeta/         # yvyra_kernel.py — the tick-driven entry point for Yvyra
├── tests/               # 41 test files (643 tests, ~105s)
├── results/             # experiment outputs (PNG + run .txt)
├── data/                # GITIGNORED — LoRA adapters, datasets, captured activations (regenerable)
├── docs/                # reports, papers, plans, theory (see SCIENCE_PLAN.md)
└── demos/               # quickstart.py — the 60-line kernel demo
```

## Commands

```bash
# === INSTALL ===
pip install -e .                 # makes `zeta_life` importable
pip install -e ".[dev,full]"     # + pytest/ruff/black/mypy (same as `make install`)
pip install -e ".[rl]"           # gymnasium + mujoco, only for the RL benchmark experiments
# (mpmath optional, for exact zeta zeros; otherwise hardcoded values are used)

# === TESTS ===
# Tests import `zeta_life...`; either install (above) or set PYTHONPATH:
PYTHONPATH=src python -m pytest tests/ -q          # full suite (643 tests, ~105s)
PYTHONPATH=src python -m pytest tests/test_conscious_kernel.py -q   # single file
PYTHONPATH=src python -m pytest tests/test_utero_memoria.py -q -k regenera   # single test
# `make test` / `make test-cov` wrap these (pyproject forces -v --tb=short).

# === LINT / FORMAT ===
ruff check src/ tests/                              # `make lint` also runs mypy
mypy src/zeta_life --ignore-missing-imports
black src/ tests/ experiments/ && ruff check --fix src/ tests/   # `make format`
# line-length 100; E501/F401/F841 intentionally ignored (see pyproject).

# === EXPERIMENTS (self-pathing; run directly) ===
# El Útero — THE LIVE LINE (docs/EL_UTERO.md; each writes results/<name>_run.txt + .png):
PYTHONPATH=src python experiments/utero/exp_primer_latido.py    # Nivel 1: rewrite a rule's CONTENT
PYTHONPATH=src python experiments/utero/exp_nivel2_latido.py    # Nivel 2: rewrite the rule's FORM
PYTHONPATH=src python experiments/utero/exp_utero_creciente.py  # v1: async + self-opening space
PYTHONPATH=src python experiments/utero/exp_utero_germinal.py   # v2: germinal variation
PYTHONPATH=src python experiments/utero/exp_utero_toroidal.py   # v3: toroidal matter (sustained novelty)
PYTHONPATH=src python experiments/utero/exp_utero_ruido_vs_funcion.py  # control: noise vs function (seed 13)
PYTHONPATH=src python experiments/utero/exp_utero_motor.py      # v4: equilibrium-death (REFUTED)
PYTHONPATH=src python experiments/utero/exp_utero_memoria.py    # v5: memory (first self-repair)

# Kernel:
PYTHONPATH=src python experiments/kernel/exp_conscious_kernel_validation.py
PYTHONPATH=src python experiments/kernel/exp_agency.py
PYTHONPATH=src python experiments/kernel/exp_zeta_vs_baselines.py    # zeta vs fourier/random/learned/rnn
PYTHONPATH=src python experiments/kernel/exp_spacing_statistics.py --kernel  # GUE vs Poisson vs lattice
PYTHONPATH=src python experiments/kernel/exp_grounding.py
PYTHONPATH=src python experiments/kernel/exp_organism_vs_individual.py
# Science pipeline (docs/SCIENCE_PLAN.md):
PYTHONPATH=src python experiments/kernel/exp_psi_vs_free_energy.py   # Phase 1: validate Psi (Albantakis method)
PYTHONPATH=src python experiments/kernel/exp_epistemic_depth.py      # Phase 2: hyper-model / 2nd-order error
PYTHONPATH=src python experiments/kernel/exp_yvyra_experiment.py     # Phases 3-5: Yvyra pipeline (simulated)
# Datasets:
PYTHONPATH=src python experiments/datasets/exp_real_data_psi.py
```

### Introspection ("the north") — SEPARATE GPU venv
These load a real LLM (Qwen3-8B) via `transformers` + 4/8-bit `bitsandbytes`, which
the base install does NOT provide. Use a dedicated venv with the GPU stack (torch
CUDA, transformers, peft, bitsandbytes, datasets, scikit-learn):
```bash
# e.g. C:/Users/skyva/.venvs/ztf/Scripts/python  (torch cu128 for Blackwell sm_120)
PYTHONPATH=src <gpu-python> experiments/introspection/exp_pik_probe.py         # is "I know" decodable from activations?
PYTHONPATH=src <gpu-python> experiments/introspection/exp_pik_train.py         # train P(IK) self-report (LoRA)
PYTHONPATH=src <gpu-python> experiments/introspection/exp_pik_binder.py        # Binder: self-report vs external text predictor
PYTHONPATH=src <gpu-python> experiments/introspection/exp_f3_inject_train.py   # trained injected-concept detection
```
The pure-numeric metric tests DO run on the base install:
`PYTHONPATH=src python -m pytest tests/test_psi_act.py -q`.
Note: after a WSL reset the host IPv6 can break HF downloads — force IPv4 (the
scripts monkeypatch `socket.getaddrinfo`) or pre-download datasets with `curl -4`.

### Dependencies
`numpy`, `torch`, `matplotlib`, `scipy` (required). `mpmath` optional.
Introspection extras (GPU venv only): `transformers`, `peft`, `bitsandbytes`,
`datasets`, `scikit-learn`, `accelerate`.

## Architecture — El Útero (`src/zeta_life/utero/`) — THE LIVE LINE

A minimal self-rewriting substrate. Conway-style (minimal local rules → undictated
emergence) with one twist: **the rules are part of the mutable state**. Full design
+ the honest results ledger: `docs/EL_UTERO.md` (written in Spanish, like the code
comments here — this line's prose is Spanish by design).

**Three non-negotiable principles** (everything else is one concrete incarnation):
1. **Rules-as-state** — no untouchable law outside. The law lives inside, mutable.
2. **Closed loop (physics ↔ physics)** — a cell's rule acts on the world *and on
   itself*: `(v', r') = APPLY(r_i, {v,r}_{i-1,i,i+1})`. Local, no outer level.
3. **Persistence as the only filter** — no goal, no reward, no judge. A cell becomes
   VOID if its next rule is degenerate (out of range, non-terminating, or blind to
   matter under the probe). *Alive = what manages to keep being.*

| Module | Role |
|--------|------|
| `nivel1.py` | `Utero1D` — rewrite a fixed law's **content** (parameters). Safe seed. |
| `nivel2.py` | The **rule-as-program** VM: 10 ops incl. `MUTO`/`COPY` (self-rewrite) and `SPAWN` (colonization). `execute()`, `K`, `F`, `PROBE_EPS` are the primitives every later version reuses. |
| `creciente.py` | `UteroCreciente` — the current substrate: a **line with borders** (not a ring), asynchronous seeded-random update, world grows only where a physics `SPAWN`s past the edge. |

**Critical: v1→v5 are boolean flags on `UteroCreciente`, not separate classes.**
All defaults `False` = v1, byte-identical to the committed v1 results. Each flag is
one hypothesis about where the "cage" moved:

| Flag | Version | Hypothesis |
|------|---------|------------|
| *(none)* | v1 | async + growing space |
| `germinal=True` | v2 | offspring vary from the matter at birth (no RNG of ours) |
| `toroidal=True` | v3 | matter on a circle (`v' = R3 mod 1`) — expansive maps become expressible. Also switches the death probe to irrational separation (0 / 0.618…), since 0 and 1 are the same point on the torus |
| `muerte_equilibrio=True` (+`eq_eps`,`eq_window`) | v4 | still matter = dead standing |
| `memoria=True` | v5 | each cell retains its raw `R3` (internal potential, pre-wrap) and re-injects it next tick — 2nd-order dynamics |

**The novelty yardstick (anti-illusion):** with random ordering, "it didn't cycle"
proves nothing. The honest measure is **never-before-seen genomes minted per
segment** (`self.seen`), because new code can only come from write events
(`MUTO`/`COPY`), never from the ordering RNG. Every experiment declares its
"visible hands" (seeded order, `max_n` wall, probe thresholds) in its docstring.

**Working discipline (same as the north):** define the yardstick *before* looking,
and build the adversarial control before believing a result. This line's ledger has
more refutations than wins — v2 dried up, v4 was **refuted** (desert, not
self-repair), the v3 win survived a noise-vs-function ablation, v5's self-repair is
n=1 seed. Keep it that way.

## Architecture — the Conscious Kernel (`src/zeta_life/kernel/`)

The active-inference cycle, one `ConsciousKernel.step(stimulus)` per tick:

```
PERCEIVE → PREDICT → COMPARE → UPDATE → MEMORIZE → ACT → REFLECT → DREAM
```

| File | Role |
|------|------|
| `conscious_kernel.py` | Orchestrator; the step loop, Psi computation, EFE agency |
| `world_model.py` | Learned latent dynamics (encoder + GRUCell transition + predictor); `imagine()` for counterfactual rollouts |
| `self_model.py` | Recursive self-model / identity embedding (Strange-Loop-flavored EMA + trained self-prediction) |
| `prediction_error.py` | Multi-channel precision-weighted errors; **precision learning** toward inverse error variance |
| `complementary_memory.py` | `FastMemory` (episodic deque, surprise-gated) + `SlowMemory` (slow-lr semantic net) — CLS |
| `dream_engine.py` | Zeta-rhythm sleep consolidation (fast→slow transfer, identity replay) |
| `temporal_features.py` | `OscillatorBank` — optional time code fed to the world model (see below) |
| `global_workspace.py`, `energy_pool.py`, `spawn_controller.py`, `organism_state.py`, `conscious_organism.py` | Darwinian multi-kernel organism (winner-take-all GW, energy, spawn/merge/death) |
| `persistence.py` | Save/load identity across sessions |
| `policy.py`, `replay.py`, `dynamics_ensemble.py` | Dreamer amortized actor/critic, transition replay, independent dynamics ensemble (curiosity) used by `action_mode="dreamer"` |
| `rssm.py`, `dreamerv3_agent.py` | **Reference** DreamerV2/V3-style RSSM agent (NOT the kernel) — recurrent state-space model trained on sequences + learned reward; **solves CartPole** where the kernel's 1-step model plateaus (`exp_dreamerv3.py`, §3.10). `action_type="discrete"` (categorical, REINFORCE) or `"continuous"` (tanh-Gaussian, value gradients — solves Pendulum §3.13, learns MuJoCo Reacher §3.14 / `exp_mujoco.py`) |
| `rssm_kernel.py` | **Integration (composition)** — `RSSMConsciousKernel`: the kernel's faculties (identity, CLS memory, dream, **Ψ**) layered on the RSSM world model + controller; reaches CartPole's ceiling with Ψ live (`exp_rssm_kernel.py`, §3.11) |
| `conscious_kernel.py` (`world_model_type="rssm"`) | **In-situ fusion** — the canonical kernel runs its full `step()`/`_compute_psi` on the RSSM (via `_step_rssm`/`learn_rssm`); reaches CartPole's ceiling, Ψ live; GRU path byte-identical (`exp_kernel_rssm.py`, §3.12) |

**Consciousness index Ψ** (in `integration/formal_equations.py`, imported by the
kernel): `Ψ = B³ + Φ` (cubic) or a bounded **Hill** variant (default), with a
critical threshold `Φ_c = F_i/(α − C)`. Note: Ψ is a bespoke, hand-tuned
heuristic (not IIT/FEP); treat it as a monotone integration signal, not a proven
consciousness measure.

**`OscillatorBank` temporal bases** (`temporal_features.py`):
```python
OscillatorBank.fourier(M)      # equispaced lattice — RECOMMENDED fixed basis
OscillatorBank.log_spaced(M)   # multi-scale (Transformer-style)
OscillatorBank.learned(M)      # trainable frequencies (adaptive)
OscillatorBank.zeta(M)         # the zeta zeros (kept for the comparison studies)
# spacing-statistic banks for the decisive test:
OscillatorBank.by_spacing("gue"|"poisson"|"uniform"|"zeta", M)
```
Default for `ConsciousKernel` is `temporal_features=None` (byte-identical to the
pre-temporal kernel).

## Where zeta actually matters (tested, honest)

This session's experiments (and the project's own prior results) settled it:

- **Cellular automata (spatial):** zeta genuinely wins (+134% survival vs Moore,
  beats UNIFORM, p<0.001). This is the one place the specific spectrum earns its
  keep.
- **Kernel / temporal prediction:** zeta's apparent edge is **basis-matching**,
  not specialness. A `fourier` (equispaced) lattice matches or beats zeta even on
  a zeta-structured signal (`results/zeta_vs_baselines_run.txt`).
- **Spacing statistics:** zeta's GUE level repulsion is real but **≤ a rigid
  lattice** on covering radius and conditioning, and **functionally flat** inside
  the kernel (`results/spacing_statistics_run.txt`).
- **Consciousness/psyche (legacy):** ZETA == UNIFORM (p=1.0). Structure matters,
  the specific zeta frequencies do not.

**Recommendation in code:** fixed basis → `fourier`/`log_spaced`; adaptive →
`learned`. Zeta is an optional, documented-and-falsified design choice.

## The North — Ψ-internal & trained introspection (`src/zeta_life/introspection/`)

**Status: closed as a negative (2026-07-02); kept for the record and the tooling.**
The program: stop treating Ψ as an **external** index pointed *at* an
agent, and make it a property of a real LLM's **own activations** — then test
whether the model can learn to **introspect** it. Thesis: *adaptation, not scale*
(a small model that learns to observe itself, per Fran's original vision).

**Substrate.** A live LLM (Yvyra = Qwen3-8B) runs in `transformers`/8-bit; the
`bridge/` couples its real experience to the kernel (Phase A/B), and
`introspection/` computes/tests internal signals with the methods of Anthropic
(Lindsey, concept injection) and Binder (privileged access).

| File | Role |
|------|------|
| `introspection/psi_act.py` | 4 candidate integration metrics over hidden states (participation ratio, phi-proxy, inter-layer coherence, trajectory predictability). Pure-numeric, tested. |
| `introspection/harness.py` | Loads Qwen in transformers/8-bit; generates a reflection, captures hidden states, elicits a self-report. Needs the GPU stack; NOT imported by the package `__init__`. |
| `introspection/concept_injection.py` | Difference-of-means concept vectors + residual-stream injection hook + detection/bias-control trials (Lindsey's method). |

**Honest results ledger (each reported only after an adversarial control):**
- **Phase A/B** (expose Ψ to the agent, sham control): **inconclusive** — Ψ
  saturates (~89% high); the design works, the signal didn't vary enough
  (`docs/PHASE_B_DESIGN.md`).
- **Spontaneous introspection** (concept injection, untrained): **NEGATIVE** —
  0/30; the introspection-vs-steering control killed the apparent "Ocean." hit.
  Replicates the scale limit Anthropic sees (`results/concept_injection_sweep_run.txt`).
- **Trained P(IK) self-report** (LoRA on MMLU correctness): **honest negative** —
  the "+0.18 vs a weak logreg M2" was an artifact; a strong blind M2 (Claude, 0.82)
  and the model's own softmax confidence (0.81) both beat the self-report (0.76).
  Verbalizes confidence, no robust *privileged* access (`results/{pik_binder,m2_claude}_run.txt`).
- **Trained injected-concept detection** (F3; LoRA, **constant prompt → non-textual
  by construction**): **CLOSED as an honest negative (2026-07-02).** The apparent
  win (10 concepts, acc 1.000 vs chance 0.091, 0 FP — `results/f3_inject_run.txt`)
  did NOT survive the generalization control: at 45 concepts, in-distribution acc
  0.909–0.953 but **held-out vectors at chance** (0.022 / 0.033, chance 0.022) on
  **both** Qwen3-0.6B and 8B. Both models memorize the exact injected vectors;
  neither reads the concept *direction*. Scale does not help.
  (`results/f3_inject_{06b,8b}_scale_run.txt`)

**Net verdict on the north: negative.** Do not cite F3 as a positive result. This is
what motivated the 2026-07 pivot to El Útero.

**Working discipline (critical):** every apparent positive here died or survived a
control (weak vs strong M2, injection-vs-steering, softmax-confidence baseline).
When continuing this line, **always build the adversarial control before believing
a result** — the honest-negative on P(IK) is the template.

Docs: `docs/{ANTHROPIC_NORTH, RESEARCH_PHASE_B, TARGET_SELECTION, TRAINED_INTROSPECTION, LORA_PLAN, PHASE_B_DESIGN}.md`.

## Core vs Archived

**Live:** `utero/` (+ `experiments/utero/`, `tests/test_utero_*.py`).

**Core, mature, not the frontier:** `kernel/`, `bridge/` (Yvyra coupling),
`introspection/` (the north, closed), `integration/formal_equations.py`,
`instrumentation/`, `datasets/`,
`core/{zeta_constants,vertex,tetrahedral_space}.py`, `utils/`.

**Archived 2026-06-08** — removed from the working tree, preserved on the
`legacy/pre-refocus-snapshot` branch (retrieve with
`git show legacy/pre-refocus-snapshot:<path>`):
- `psyche/` — Jungian/archetype consciousness (original formalism; superseded by the kernel)
- `integration/` hierarchical + IPUESA resilience stack (a parallel consciousness formalism the kernel never used)
- `evolution/` — GA optimizer that only tuned IPUESA hyperparameters
- `organism/` — Fi-Mi swarm artificial life (tangent to consciousness)
- `core/{zeta_memory,zeta_rnn,zeta_resonance}.py` — effectively unused

Note: `src/zeta_life/{psyche,evolution,organism}/` still exist on disk but contain
**only stale `__pycache__`** — nothing is tracked there. They are leftovers, not code.

The competing consciousness formalisms (psyche `ConsciousnessIndex`, hierarchical
`phi_global`) were archived with their packages. The canonical index is **Ψ**
(`formal_equations.py`, used by the live kernel); `OrganismState.integration_index`
(`kernel/organism_state.py`) remains as the organism-level aggregate.

## Key parameters

| Parameter | Typical | Description |
|-----------|---------|-------------|
| `M` | 15–40 | Number of oscillators / zeta zeros |
| `sigma` | 0.0–0.1 | Abel decay (0 = flat, all M live; 0.1 = ~4 effective) |
| `latent_dim` | 32 | World model latent dim |
| `obs_dim` | 4 | Observation/action dim |
| `reflect_interval` | 5 | Self-reflection cadence |
| `dream_interval` | 50 | Dream consolidation cadence |
| `action_mode` | reactive / efe | Reactive softmax vs expected-free-energy planning |
| `efe_n_samples` | 0 / 48 | EFE: add N sampled CONTINUOUS candidate actions (0 = one-hots only). Continuous + `efe_obs_norm="l1"` lets the planner reach non-vertex targets (see `exp_control.py`) |
| `efe_horizon` | 1 | EFE planning horizon (sustained-action rollout). >1 found YAGNI in the 4-D env |
| `efe_cem_iters` | 0 | EFE: Cross-Entropy Method refinement (0 = random shooting). Capability for hard action landscapes; no reliable gain in the unimodal control task (`exp_cem.py`) |
| `wm_disagreement_heads` | 0 | World-model ensemble heads for an epistemic (disagreement) signal (0 = off). Under a *controlled* comparison it gives **no reliable** exploration gain in the 4-D regime (`exp_curiosity.py`; an earlier apparent ~2x was an RNG confound, now fixed). Head masking uses a dedicated RNG; kept as a capability |
| `efe_epistemic_mode` | entropy / disagreement | EFE epistemic term: coarse outcome-entropy proxy vs real world-model disagreement |
| `dynamics_ensemble` / `wm_disagreement_heads` | 0 / 0 | epistemic source: **independent** one-step dynamics models (Plan2Explore-faithful) vs shared-latent readout heads. With a commensurate `efe_epistemic_weight`, disagreement-curiosity reliably drives exploration (`exp_curiosity.py`) |
| `action_mode` | reactive / efe / **dreamer** | `dreamer` = amortized actor+critic trained in imagination (value gradients); O(1) action cost, matches/beats search on control (`exp_dreamer.py`) |
| `imag_horizon` / `imag_rollouts` | 5 / 8 | Dreamer imagination horizon and rollout batch (per-step behaviour learning) |
| `critic_tau` / `return_norm` / `actor_grad_clip` | 0.98 / True / 100 | Dreamer stabilizers: EMA target critic, return-scale normalization, gradient clipping |
| `replay_capacity` / `replay_wm` | 10000 / True | DreamerV3 transition replay: imagine behaviour from re-encoded replayed states + ground the world model on diverse transitions (improves CartPole curve/peak; doesn't reach the ceiling — late collapse persists) |
| `action_dim` / `dreamer_reward` | None / kl | decouple action from obs space; `neg_distance` reward for regulation to a raw goal state (e.g. CartPole) |
| `precision_hypermodel` | False | epistemic depth ("A beautiful loop", Friston 2025): a hyper-model that PREDICTS per-channel precisions globally and reports a **second-order error over precision** (`StepResult.second_order_error`). OFF = byte-identical kernel. The signal spikes at regime change and is independent of free energy (|corr|≈0 vs Psi's 0.53) — see `precision_hypermodel.py`, `exp_epistemic_depth.py`, `docs/SCIENCE_PLAN.md` |

## Documentation

- **`docs/EL_UTERO.md` — READ THIS FIRST.** The live line: design sketch, the three
  principles, the two death modes, the open crossroads, and the **honest results
  ledger** (Nivel 1 → v5, each entry written only after its adversarial control,
  with the refutations kept in). Update its ledger when a new útero experiment lands.
- `docs/AUDIT_FIXES_2026.md` — 11 audited kernel implementation fixes (with before/after metrics)
- `docs/AGENCY_2026.md` — active-inference agency investigation (honest negative results)
- `docs/YVYRA_BRIDGE.md` — contract for feeding a live agent's experience into the kernel; the zeta-life side is implemented in `src/zeta_life/bridge/` (demo: `experiments/kernel/exp_yvyra_bridge.py`)
- `docs/theory/EXPERIMENTO_ZETA_VS_BASELINE.md` — zeta vs uniform/none/random (zeta == uniform)
- `docs/papers/conscious-kernel-paper.md` — **current thesis**: the active-inference Conscious Kernel (architecture, honest results, the "what helped / what didn't" ledger)
- `docs/SCIENCE_PLAN.md` — **the toy→instrument pipeline**: 6 phases (paired logging, Psi bench-validation via the Albantakis method, the precision hyper-model / epistemic depth, the Yvyra modes + blind re-scorer + pre-registration), each with its honest results. The master plan referenced by `instrumentation/`, `precision_hypermodel.py`, the `bridge/` modes, the `exp_psi_vs_free_energy`/`exp_epistemic_depth`/`exp_yvyra_experiment` experiments, and `deploy/zeta/`
- `docs/RELATED_WORK.md` — curated literature scan mapped to each kernel component (Dreamer, Plan2Explore, CLS, Butlin indicator properties, LLM+active-inference) with validate/inspire/SOTA-gap takeaways and a ranked "what to adopt" list
- `docs/INDICATOR_PROPERTIES.md` — honest, conservative audit of the kernel against Butlin et al. (2023) consciousness *indicator properties* (strong on PP/agency/embodiment, partial on GWT/recurrence/HOT, absent AST/HOT-4/GWT-4); the rigorous framework replacing Ψ-as-consciousness. Explicitly: indicators ≠ consciousness
- `docs/papers/zeta-life-framework-paper.md` — the original "zeta unification" paper (predates the kernel; its zeta thesis is partly falsified by the project's own evidence; superseded by the kernel paper)
- `docs/theory/REPORTE_ZETA_ORGANISM.md`, `docs/theory/ZETA_PSYCHE.md` — legacy subsystem reports

**The North (introspection program):**
- `docs/PHASE_B_DESIGN.md` — the Yvyra Phase-B experiment (expose Ψ + sham control); why it came back inconclusive (Ψ saturation)
- `docs/ANTHROPIC_NORTH.md` — verified dossier of Anthropic's interpretability/introspection work (SAEs, concept injection, model welfare) mapped to the north
- `docs/RESEARCH_PHASE_B.md` — the meta-problem, common-cause/confound analysis, and the privileged-access (Binder) test
- `docs/TARGET_SELECTION.md` — choosing the internal target (why P(IK)/uncertainty over IIT-integration, which saturates)
- `docs/LORA_PLAN.md` — how to train the P(IK) self-report + QLoRA-on-Blackwell config, verified
- `docs/TRAINED_INTROSPECTION.md` — can introspection be *trained*? methods, the Qwen-Scope SAE, the honest expectation

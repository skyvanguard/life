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
│   ├── utero/           # LIVE FRONTIER — self-rewriting substrate (9 modules; 1-D line + 2-D plane + sun + intelligence yardsticks)
│   ├── kernel/          # active-inference Conscious Kernel (21 files)
│   ├── bridge/          # Yvyra coupling — feed a live agent's experience to the kernel
│   ├── introspection/   # the north (closed) — Psi over an LLM's activations
│   ├── integration/     # formal_equations.py — the integration index Psi
│   ├── instrumentation/ # TickLogger — paired per-tick logging (science pipeline)
│   ├── datasets/        # real/synthetic signal loaders for Psi validation
│   ├── core/            # zeta_constants, vertex, tetrahedral geometry
│   └── utils/           # statistics helpers
├── experiments/
│   ├── utero/           # 34 experiments — the live line (Nivel 1/2, v1..v6 + controls, replica, anatomy, lineage/shadow, interaction)
│   ├── kernel/          # 31 kernel experiments
│   ├── introspection/   # the north — probe, P(IK) LoRA, injected-concept detection
│   └── datasets/        # 1 experiment (Psi on real data)
├── deploy/zeta/         # yvyra_kernel.py — the tick-driven entry point for Yvyra
├── tests/               # 52 test files (721 tests + 1 opt-in slow, ~110s)
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
PYTHONPATH=src python -m pytest tests/ -q          # full suite (712 tests, ~110s)
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
PYTHONPATH=src python experiments/utero/exp_utero_memoria_semillas.py  # v5 replica, 40 seeds (~13 min, 20 procs): INCONCLUSIVE, seed 35 = counterexample
PYTHONPATH=src python experiments/utero/exp_utero_anatomia.py   # anatomy 13 vs 35 (~3 min): self-repair = FERTILE plains (diverse, viable offspring), not geometry/memory
PYTHONPATH=src python experiments/utero/exp_utero_linaje_sombra.py  # MODES lineage filter + Bedau shadow, 40 seeds (~10 min): 2/40 DEFENSIBLE; shadow = 0 novelty (trivial copier takes over)
PYTHONPATH=src python experiments/utero/exp_utero_interaccion.py    # effective rule<->rule interaction (COPY / horizontal transfer), 40 seeds (~4 min): novelty is MUTO-driven, TH ~0 in plains
PYTHONPATH=src python experiments/utero/exp_utero_invasion.py       # v6: invasion of settled tissue, 40 seeds x {v5, v6, v6-shadow} + ablations (~15 min): PARTIAL -- typicity 2/40 -> 3/40, no monoculture (9.3 bits), self-repair 1/3; keeps worlds alive but frozen
PYTHONPATH=src python experiments/utero/exp_utero_invasion_control.py  # v6 control: invasion='siempre' (no threshold) + eq_window sweep 10/100/1000, 5 arms x 40 seeds (~25 min): THE HAND WORKS -- 'siempre' = 0/40 (pure churn, 245 invasions/tick), any eq_window 10..1000 = 3/40
PYTHONPATH=src python experiments/utero/exp_utero_mortalidad_infantil.py  # follow every plain-born child 500 ticks (~3 min): 100% born BLIND, one lethal child genome, 0% survive across 6 seeds -- plains are sterile at steady state
PYTHONPATH=src python experiments/utero/exp_utero_recombina.py      # v7: recombination at birth, 40 seeds x {v5, v7, v6+v7} (~20 min): NO EFFECT on typicity (3/40) -- children become viable (0% blind) but seed 35 collapses into a viable-clone monoculture
PYTHONPATH=src python experiments/utero/exp_utero_plano.py          # v8: the 2-D plane, 40 seeds x {p5, p6, p67} + shadows/ablations (~60 min) -- see the ledger
# The sun / intelligence program (docs/PLAN_INTELIGENCIA.md):
PYTHONPATH=src python experiments/utero/exp_utero_sol.py            # visible + consequential sun vs no-sun/shadow, R/A/L (~50 min): visible NOTHING; consequential fired VESTIGIO at the minimum threshold (3/40, p_binom 0.32) -- not believed
PYTHONPATH=src python experiments/utero/exp_utero_sol_replica.py    # replication: two other sun seeds + permuted season order (~40 min) -- see the ledger
PYTHONPATH=src python experiments/utero/exp_utero_sol_acople.py     # the heating sun (kappa=0.5) in 1-D: NO CONTACT (border follows the sun at 0.92, deaths 0.000: the mature tissue is a crystal)
PYTHONPATH=src python experiments/utero/exp_utero_sol_plano.py      # the sun on the 2-D plane, 5 arms incl. ciclo2 + R2 (~80 min): NOTHING (the plate saturates and goes inert)
PYTHONPATH=src python experiments/utero/exp_utero_sol_equilibrio.py # dissolution death under the sun (~45 min): NO CONTACT
PYTHONPATH=src python experiments/utero/exp_utero_sol_energia.py    # v9 metabolism under the sun (~45 min): environment essential, no vestige
PYTHONPATH=src python experiments/utero/exp_utero_sol_percepcion.py # v10 perception under the sun (~45 min): NO CONTACT / NOTHING. Eight pre-registered designs, eight negatives
PYTHONPATH=src python experiments/utero/exp_utero_sol_luz.py        # v11 photosynthesis (light on the whole tissue), break-even at the typical torus distance: EXTINCTION in both runs (with/without perception, e0 1 and 2). Tenth negative; program closed as an honest negative (PLAN §7)
PYTHONPATH=src python experiments/utero/exp_utero_sol_luzfinita.py  # v12 finite light (seasonal carrying capacity): the only intermediate regime of the series; 4 runs (sun seeds 0/1/2, 20k-40k ticks): NOTHING; the 'saving before famine' signal was accumulation drift (15/40 in the permuted arm)
PYTHONPATH=src python experiments/utero/exp_utero_sol_lentos.py     # v13 slow registers on the v12 ecology (~70 min): NOTHING (anticipation fires equally in the permuted arm). 14 runs, 13 designs, zero vestiges
PYTHONPATH=src python experiments/utero/exp_utero_control_positivo.py  # POSITIVE CONTROL: a hand-designed famine anticipator is viable (18/20), halves famine deaths; the A/L yardsticks don't see it, R2 does
PYTHONPATH=src python experiments/utero/exp_utero_invasion_ahorrador.py # invasion from rare: the anticipator is NOT selected (4-5/20 takeovers, order-independent, with or without birth cost). Program closed with a mechanistic explanation
PYTHONPATH=src python experiments/utero/exp_utero_hambruna.py          # v14: experimental evolution under a harsh famine + costly births, nothing seeded. Run 1 (sun seed 0): NADA on the primary R2_A; a post-hoc birth-drop signal in the ciclo2 control arm (A_n 9/40) triggered a declared replication (sun seed 1, detrended + season-matched controls): 2/40 -- a calendar false positive. 17 pre-registered emergence runs, zero vestiges
PYTHONPATH=src python experiments/utero/exp_utero_quemada.py           # v15: v14 + scorched earth (refractario=300, K-selection): NADA (R2_A ratio 1.29; L_A 6/40 vs controls 3-4). Fast recolonization was NOT the bottleneck. 18 pre-registered emergence runs, zero vestiges
PYTHONPATH=src python experiments/utero/exp_utero_alcance_operandos.py # THE FOURTH CAGE (structural, ~1 min): no variation operator writes operands -- MUTO/germinal write opcodes only, COPY moves existing rows. A world's (a,b,c) triples are frozen at the initial soup (6.06% of 4096); only 3/40 soups even contain the anticipator's parts. Explains the 18 negatives
PYTHONPATH=src python experiments/utero/exp_utero_total.py             # v16: v14 ecology + escritura_total (the variation can now write operands): NO CONTACT / NADA (continuous churn hides the famine; R2_A 1.30; L_A 1/40). 19 runs, zero vestiges; next: time and population scale
PYTHONPATH=src python experiments/utero/exp_utero_escala_evo.py        # §16 scale: does the OPEN substrate evolve at all? 4x time, ~3x population, 3 arms; primary = reflex adaptation (late/early famine mortality) vs shadow, plus R2_A: NADA -- and the late/early reading was confounded (it fell in the shadow too, which goes extinct); the shadow arm has been extinct in v14-§16, so '>= 2x shadow' was vacuous there. Next: per-capita adaptation vs a FROZEN arm
PYTHONPATH=src python experiments/utero/exp_utero_dfe.py               # §16b DFE of the variation operator (~10 min): open = 23 viable distinct variants/1000 ticks/world (21% of distinct children live 500 ticks; 71% of writes touch operands) vs closed 9 (99% opcode-only, 5% live). Mutational supply is not the bottleneck
PYTHONPATH=src python experiments/utero/exp_utero_evoluciona.py        # §17 does it evolve? per-capita famine mortality late/early, paired by seed against a FROZEN arm; open (v16) and closed (v14); 120k ticks, L0=9, 20 seeds: NO EVOLUCIONA -- per-capita famine mortality falls MORE in the frozen arm (0.19) than open (0.45) or closed (0.62); heritable variation is load, not adaptation. The substrate does not evolve under this ecology
PYTHONPATH=src python experiments/utero/exp_utero_heredabilidad.py     # §18 is there a heritable phenotype? per famine: is survival predicted by the genome (between-genome SS vs permutation), by state (energy, border) or by nothing; HEREDABLE / ESTADO / NADA pre-registered: NADA by the letter (20-world denominator with 5-7 extinctions); on usable worlds ENERGY predicts fate in 13/13 and 13/15, GENOME in 7/13 and 9/15 and repeatable across famines (8/10, 14/15). Heritable variation exists; it is not turned into adaptation
PYTHONPATH=src python experiments/utero/exp_utero_evoluciona2.py       # §20 = §17 with energy diffusion OFF (e_dif=0): does the public-good (shared local energy) neutralize individual selection? NO EVOLUCIONA (open 0.54 vs frozen 0.82, 9/16 pairs, p 0.40): not the main cause
PYTHONPATH=src python experiments/utero/exp_utero_seleccion_replicas.py # §21 does selection see genomes? 10 soups x 5 update orders on FROZEN worlds; Kendall W of final genome abundances vs permutation null. SELECCION 10/10 (the same genome sweeps to 100% in 5/5 replicates in 9/10 soups): selection on fixed programs is deterministic and strong; with §17, the bottleneck is the variation itself (error threshold)
PYTHONPATH=src python experiments/utero/exp_utero_tasa.py               # §22 mutation rate: §17 protocol with germinal write at p=1, 0.1, 0.02 vs frozen. NO EVOLUCIONA by the rule; graded trend (famine mortality 0.73 / 0.69 / 0.49 vs frozen 0.60): rate explains the load, not the absence of adaptation on this yardstick
PYTHONPATH=src python experiments/utero/exp_utero_jardin_comun.py       # §23 common garden: evolved dominant genome (open, 120k ticks; p=0.02 and p=1) vs the best fixed program of its soup, competing 8 vs 8 in a frozen world, two layouts. NEUTRAL in both regimes; and in ~half the seeds the two layouts give exactly (1.00, 0.00): competition is decided by initial POSITION, not genome. §21's determinism may be positional (its replicates kept soup positions)
PYTHONPATH=src python experiments/utero/exp_utero_posicion.py           # §24 position or program? frozen replicates with SHUFFLED positions (same genomes, same order) in the open-frontier and in a closed-frontier ecology (n0 = max_n = 64). PROGRAMA in both (open 9/9: the same genome sweeps from shuffled positions; closed 10/10 with 5-11 genomes coexisting under a reproducible ranking). Selection sees programs; position only breaks ties
PYTHONPATH=src python experiments/utero/exp_utero_evoluciona_cerrado.py # §25 §17 protocol in the CLOSED ecology (n0 = max_n = 64, interior competition, 5-11 genomes coexist): open p=0.02 / closed / frozen; per-capita famine mortality late/early vs frozen: NO CONTACT (famine mortality 0.005: with L0=9 the famine does not kill in the closed ecology). Hypothesis: the blindness probe flattens the income gradient
PYTHONPATH=src python experiments/utero/exp_utero_gradiente.py          # §26 income-gradient positive control: ANTISOL (legal program, matter 0.5 from the famine sun) vs ESPEJO (same form, random income), 4+4 seeded among 56 random in the closed frozen scarce-light ecology. GRADIENTE 17/20: ANTISOL sweeps to 100% in 15/20 worlds by 10k ticks, ESPEJO vanishes. The income gradient is real and strongly selectable; the failure of adaptation is one of PATH or YARDSTICK
PYTHONPATH=src python experiments/utero/exp_utero_rasgo.py              # §27 does open variation raise the REWARDED trait (mean light weight of matter during the famine) more than the frozen arm? closed scarce-light ecology, 4 arms, 120k ticks. NO EVOLUCIONA: the trait stays at 0.30-0.34 in all four arms over 59 famines (ratio 1.00). With a proven gradient, strong selection and enough supply, the variation never produces the trait: PATH
PYTHONPATH=src python experiments/utero/exp_utero_alcanzabilidad.py    # §28 reachability (~10 min, no evolution): one- and two-write neighbourhoods of ~50 legal evolved programs; legality and change of the rewarded trait. SIN SALTOS: of 20000 total writes none moves the trait +0.2, 0.19% move it +0.1, median 0 (a neutral plateau with rare small steps). Next: effective population size (§29)
PYTHONPATH=src python experiments/utero/exp_utero_sol_vara.py       # 1-D heating sun with the amended yardstick (not run: superseded by the plane/metabolism runs)
PYTHONPATH=src python experiments/utero/exp_utero_escala.py         # scale robustness (~40 min): 1024 cells = same typicity; 120 seeds -> v5 4.2%, v6 5.8%. The rarity is intrinsic to 1-D

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
| `ablacion.py` | The **pump-ablation protocol** (kill every cell whose code changed in the last 200 ticks; measure the sustained TAIL at +1000..+3000, not the recolonization pulse). Extracted from v5 and regression-tested against its published numbers (`UTERO_SLOW=1`). |
| `linaje.py` | `RastreadorLinaje` — the **MODES lineage-persistence filter**: a minted genome counts only if its line (cell continuity + SPAWN offspring) is still alive `t_filtro` ticks later. Fed per tick with `{coord: genome}` and `u.spawns`. |
| `plano.py` | **v8 — `UteroPlano`, the same substrate in 2-D** (von Neumann; registers vN,vE,vS,vO,v,R; birth direction `(a + |R[b]|·4) % 4` modulated by matter; 32×32 plate with walls, 8×8 live block, colonizable void; all flags inherited). Same interface (`genomas()`, `vaciar()`, `spawns`, `events`) so the yardstick runs unchanged via `fabrica=`. |
| `sol.py` | **The environment**: `Sol(seed, ticks, orden="ciclico"|"permutado")` — seasons A→B→C in fixed order (learnable regularity), durations from a logistic map in [300, 900] (typical but unpredictable), a day oscillation inside each season. `orden="permutado"` is the no-regularity control. |
| `inteligencia.py` | **The intelligence yardsticks** (docs/PLAN_INTELIGENCIA.md): `correr_series` (per-tick internal series), `regulacion`, `anticipacion` (expected-switch bump in long seasons, permutation null), `aprendizaje` (Spearman over recurrences, permutation null). Tested against an injected bump, noise and a reflex model. |
| `medidas.py` | `correr_medido(seed, flags, ticks, ..., fabrica=None)` — **one run with the full honest yardstick**: raw novelty, lineage-filtered novelty, ecology (bits), dominant-genome share, deaths/invasions/alive per tick, minting cause (birth vs rewrite); `shadow=` makes it the Bedau shadow run. Every experiment since v6 uses it. |

**Observation hooks on `UteroCreciente` (byte-identical when off, tested):** `log_events=True` fills
`u.events` (`{coord: {copy_writes, muto_writes, copy_distinct}}` from `execute(stats=)`) and
`u.spawns` (`[(mother_coord, child_coord)]`) each tick; `step()` returns `deaths`. `shadow_deaths=[...]`
is the **Bedau shadow run**: the probe is switched off and that many random cells die per tick instead.

**Critical: v1→v7 are flags on `UteroCreciente`, not separate classes.**
All defaults `False` = v1, byte-identical to the committed v1 results. Each flag is
one hypothesis about where the "cage" moved:

| Flag | Version | Hypothesis |
|------|---------|------------|
| *(none)* | v1 | async + growing space |
| `germinal=True` | v2 | offspring vary from the matter at birth (no RNG of ours) |
| `toroidal=True` | v3 | matter on a circle (`v' = R3 mod 1`) — expansive maps become expressible. Also switches the death probe to irrational separation (0 / 0.618…), since 0 and 1 are the same point on the torus |
| `muerte_equilibrio=True` (+`eq_eps`,`eq_window`) | v4 | still matter = dead standing |
| `memoria=True` | v5 | each cell retains its raw `R3` (internal potential, pre-wrap) and re-injects it next tick — 2nd-order dynamics |
| `invasion="asentada"` (or `"siempre"`) | v6 | the void is no longer the only colonizable ground: a `SPAWN` aimed at a LIVING neighbour whose matter has been still for `eq_window` ticks REPLACES it (child code, mother's matter, no memory) — rule↔rule interaction with net effect in settled tissue; replacement, not death (v4's desert). `"siempre"` = any living neighbour (no threshold; control) |
| `sol=Sol(...)` | env | the VOID (interior and beyond) carries `sol(t)` instead of 0: the sun lights everything that is not tissue. Visible only — NOTHING measurable (2026-09-26) |
| `sol_sonda=True` | env | the climate counts for persistence: the blindness probe is referenced to `(sol(t), sol(t)+h)` instead of `(0, h)` |
| `sol_eq_eps=ε, sol_eq_window=W` | env | "what becomes equal to the void is void": a cell whose matter matches the environment for W ticks is emptied. NO CONTACT (initial purge, then 0 deaths) |
| `energia=True` (+ `e0, e_mant, e_gan, e_dif, e_parto`) | v9 | **minimal metabolism**: maintenance per tick, harvest at the surface from the disequilibrium with the void, conservative diffusion, energy share at birth, death at e≤0. Makes the environment essential (no sun = death); no vestige |
| `energia_luz=True` | v11 | photosynthesis: every cell harvests `e_gan·|v − sol(t)|` (income depends on matter vs season, not geometry). Lifetime calibration shows a bifurcation: extinction or immortality; the intermediate regime (break-even ≈ 0.25) collapses into extinction at n=40 |
| `e_costo=c` | v12+ | births burn c energy (mother must hold > c). Did not change selection for the anticipator |
| `lentos=λ` | v13 | two **slow registers** per cell the rule reads and can only push slowly (`S ← S + λ(w − S)`): clocks/integrators at the season scale (τ = 1/λ). Measured internal memory before this: 6–150 ticks vs seasons of 300–900 |
| `orden_seed=k` | §21 | separate RNG for the asynchronous update ORDER; the initial soup stays fixed by `seed`. Replicates of the same world with other order noise (does the same genome win?). None = byte-identical |
| `tasa_germinal=p` | §22 | the child receives the germinal write only if frac(|mother's raw R3|·97) < p (matter-gated, no RNG of ours; declared hand). p=1 (default) = a write at every birth (~1 strong mutation per generation: error-threshold regime). 1.0 = byte-identical |
| `congelado=True` | §17 | **the null for 'does it evolve?'**: MUTO and COPY are inert and the germinal does not write, so children are exact copies; same physics, ecology and demography, no inheritance of change. Off = byte-identical |
| `escritura_total=True` | v16 | **the answer to the fourth cage**: MUTO and the germinal write the WHOLE instruction (op,a,b,c) from the registers (op from |R_b|, operands from |R_{b+1..b+3}| mod m, scaled to 16). Without it no operator writes operands and a world's triples are frozen at its soup. 84x more never-seen genomes, viable on the v14 ecology. Off = byte-identical |
| `refractario=T` | v15 | **scorched earth (K-selection)**: a dead cell's slot is uncolonizable (no colonization, no invasion) for T ticks; a SPAWN aimed at it fails like an occupied neighbour. Tests the mechanistic explanation of the sun program (fast recolonization makes famine survival worthless). T=0 byte-identical |
| `luz_finita=L0` | v12 | finite shared light L0·sol(t) split among living cells by |v−sol| weight: a carrying capacity that follows the season (A famine, B feast). The only intermediate regime found; no vestige in 4 runs |
| `percepcion=True` | v10 | the cell's energy enters its physics as a 5th read-only register (fields index mod 5): the only slow internal variable, readable. Requires `energia`. No vestige |
| `sol_acople=κ` | env | the sun HEATS the surface: border cells get `v ← (1−κ)v' + κ·sol(t)` after their rule; the only variant with real contact (border–sun corr 0.89) |
| `recombina=True` | v7 | **recombination at birth**: the child also takes instruction `b%K` (the SPAWN's locus field) from the mother's neighbour on the side opposite to the birth, if alive and of a different genome. Two parents, zero RNG — breaks the deterministic lethal fixed point of the germinal map that makes plains sterile (infant-mortality experiment) |

**The novelty yardstick (anti-illusion):** with random ordering, "it didn't cycle"
proves nothing. The honest measure is **never-before-seen genomes minted per
segment** (`self.seen`), because new code can only come from write events
(`MUTO`/`COPY`), never from the ordering RNG. Every experiment declares its
"visible hands" (seeded order, `max_n` wall, probe thresholds) in its docstring.

**Working discipline (same as the north):** define the yardstick *before* looking,
and build the adversarial control before believing a result. This line's ledger has
more refutations than wins — v2 dried up, v4 was **refuted** (desert, not
self-repair), the v3 win survived a noise-vs-function ablation, v5's self-repair is
n=1 seed — and the 40-seed replica (2026-09-26) kept it there: INCONCLUSIVE by the
pre-registered rule (only 2/40 seeds reach t≥8000 alive), seed 13 replicates, seed 35
(bigger engine, memory ON) does NOT self-repair, and ablation *re-ignites* stalled
memory-OFF worlds (35, 23). The 13-vs-35 anatomy then showed what differs: the
**fertility of the settled plains** (13: 80 distinct offspring genomes, 76% live >100
ticks; 35: 6 genomes, median life 1 tick — the v2 cage alive inside v5). Geometry,
slow reservoir, op capacity and memory-dependence were all refuted. Keep it that way.

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
- `docs/PLAN_INTELIGENCIA.md` — **the plan from order to intelligence** (status §8–§12: sixteen pre-registered emergence runs, a positive control and two invasion assays; anticipation is viable but not selected in this ecology; program closed with a mechanistic explanation): operational definition (regulation, anticipation, learning-by-recurrence, organization), the sun, the pre-registered notion of "vestige", controls and honest stop rules. Read before touching the sun program.
- `docs/papers/utero-paper.md` — **working draft of the útero paper** (Spanish): what it takes and what is not enough to sustain structural novelty in a self-rewriting substrate — the chain of cages, the honest yardstick, the anatomy/fertility/mortality mechanism, the three mechanisms and their ceiling, v8 pending.
- `docs/ESTADO_DEL_ARTE_UTERO.md` — **state of the art (2026-09-26)** for the útero line: BFF /
  Computational Life (+ its 2026 self-correction), Stringmol, AlChemy, Flow-Lenia, Evoloop,
  MODES / evolutionary activity, minimal-criterion (Soros/Stanley), Beer's autopoiesis. Table of
  who did what vs our three principles, **repetition risks**, **gaps**, what the literature says
  about our open crossroads, and the metrics to adopt (lineage-persistence filter, shadow run).
  Read before designing any new útero mechanism.
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

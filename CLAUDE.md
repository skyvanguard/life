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

> **Update (2026-10-26):** El Útero **closed** (§49, by the docs/NORTE.md rule); the
> frontier is back on the **kernel**, and the kernel is **the agent itself** (Fran):
> no Hermes/Yvyra or any other LLM as its vehicle -- experiments feed `ConsciousKernel`
> directly. Psi measured as a relative-surprise detector (`exp_psi_quiebres.py`).

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
│   ├── utero/           # CLOSED 2026-10-26 (§49) — self-rewriting substrate (10 modules; 1-D line + 2-D plane + sun + intelligence yardsticks)
│   ├── kernel/          # active-inference Conscious Kernel (21 files)
│   ├── bridge/          # Yvyra coupling — feed a live agent's experience to the kernel
│   ├── introspection/   # the north (closed) — Psi over an LLM's activations
│   ├── integration/     # formal_equations.py — the integration index Psi
│   ├── instrumentation/ # TickLogger — paired per-tick logging (science pipeline)
│   ├── datasets/        # real/synthetic signal loaders for Psi validation
│   ├── core/            # zeta_constants, vertex, tetrahedral geometry
│   └── utils/           # statistics helpers
├── experiments/
│   ├── utero/           # 71 experiments — the live line (Nivel 1/2, v1..v6 + controls, replica, anatomy, lineage/shadow, interaction)
│   ├── kernel/          # 53 kernel experiments (§K1-§K14: the kernel in its own world)
│   ├── introspection/   # the north — probe, P(IK) LoRA, injected-concept detection
│   └── datasets/        # 1 experiment (Psi on real data)
├── deploy/zeta/         # yvyra_kernel.py — the tick-driven entry point for Yvyra
├── tests/               # 65 test files (821 tests + 1 opt-in slow)
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
PYTHONPATH=src python -m pytest tests/ -q          # full suite (821 tests + 1 opt-in slow; ~110s alone, ~7 min on the shared machine)
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
PYTHONPATH=src python experiments/utero/exp_utero_rasgo_grande.py       # §29 effective population: §27 with an 8x larger closed line (N=512, L0=14; ~190 alive), open p=1 / closed / frozen, 12 seeds, 120k ticks: NO on the trait (0.37 everywhere; frozen reaches more anti-famine band, 0.55, than the heritable arms: error threshold on the trait). Unexpected: famine mortality 0.14 open vs 0.96 frozen (closed 0.29) -- load or regulation? §30
PYTHONPATH=src python experiments/utero/exp_utero_tasa_grande.py        # §30 N=512 with germinal rate 0.02 / 0.005 (+ closed, frozen): the trait, and births per capita by season to NO on the trait; famine mortality of p=0.02 below frozen in 12/12 worlds (0.15 vs 0.96), late/early in 11/12 (p 0.003); load rule fails, regulation rule passes at the threshold (A/B 9/12). Unregistered confound: density (138 vs 176 alive). §31 = density-matched frozen control
PYTHONPATH=src python experiments/utero/exp_utero_densidad.py           # §31 density control: open p=0.02 vs frozen matched by trajectory (random vaciar outside A to the open arm's alive count) vs plain frozen; famine per-capita mortality paired. INTERMEDIO by the letter (7/12), DENSIDAD by the evidence (matched frozen 0.18 vs open 0.15; density alone 11/12 vs frozen): §30's signal was load turned into density. No vestige
PYTHONPATH=src python experiments/utero/exp_utero_alcanzabilidad_inc.py # §32 reachability with INCREMENTAL writes (+-1 in one field) vs whole-row writes, same harness as §28. SIN ESCALERA (0.27% vs 0.22% for +0.05; zero for +0.2): the landscape is flat for any local operator. THE FIFTH CAGE: the program->matter map has no locality. Answer: v17 heritable continuous offset theta (§33)
PYTHONPATH=src python experiments/utero/exp_utero_parametros.py         # §33 v17: theta + open programs / theta alone / null (frozen programs, fixed theta) at N=512, L0=14, 12 seeds, 120k ticks; trait w_A paired vs null + circular concentration of theta. NO EVOLUCIONA (0.38-0.40 vs null 0.385): a SHIFT cannot change the mean distance to the sun of pseudo-random matter (design error recorded); the rewarded knob is the SPREAD. v17b `escala` (§34)
PYTHONPATH=src python experiments/utero/exp_utero_escala.py             # §34 v17b: theta + scale heritable with open / frozen programs vs null (both fixed), N=512, 12 seeds; trait w_A vs null, EVOLUCIONA in theta_s_solo by the pre-registered rule (10/12, 10/12, p 0.019; w_A 0.434 vs 0.385; mean scale 0.71): THE FIRST MEASURED DARWINIAN ADAPTATION IN THE UTERO. Evolution, not intelligence. Replication §35 pending
PYTHONPATH=src python experiments/utero/exp_utero_escala_replica.py     # §35 replication of §34 with sun seed 1 and soups 12-23, same rule. REPLICATED (10/12, 10/12, p 0.019; 0.423 vs 0.363): the first Darwinian adaptation in the utero is measured and replicated. Evolution of two heritable expression knobs, not intelligence
PYTHONPATH=src python experiments/utero/exp_utero_orden.py              # §36 THE ORDER QUESTION on the evolvable substrate: clima / ciclo2 / permutado / null with writable knobs (perillas) + perception; primary R2_A (famine mortality regular vs permuted, paired). NADA (clima < permutado 5/12, ratio 1.38; ciclo2 3/12): the substrate evolves but does not regulate by order; knobs are used equally with and without inheritance. Next: a heritable gain on the cell's own energy history (§37)
PYTHONPATH=src python experiments/utero/exp_utero_gpu_validacion.py    # §38 GPU engine validation (GPU, ~40 min): reproduce the gradient control (§26) and the first evolution (§34) on the batch engine
PYTHONPATH=src python experiments/utero/exp_utero_reflejo_gpu.py       # §37 on GPU (~45 min, 96 worlds in one batch): heritable gain on the cell's own energy history; R2_A clima/ciclo2 vs permutado
PYTHONPATH=src python experiments/utero/exp_utero_reflejo_campo_medio.py # §37b mean-field (numpy, ~1 min, no GPU): the gain g is a REFLEX (pays under any order, most under permuted) so §37 cannot yield a vestige by R2_A; but the order decides WHICH g pays
PYTHONPATH=src python experiments/utero/exp_utero_trasplante_gpu.py     # §39 RECIPROCAL TRANSPLANT on GPU (pre-registered, NOT RUN YET): evolve under clima / ciclo2 / permutado, assay each under both orders with a new calendar and fixed knobs; VESTIGIO = LOCAL-vs-FOREIGN advantage in both destinations (criterion amended before running)
PYTHONPATH=src python experiments/utero/exp_utero_ultraestable_gpu.py  # §43 CHANGE OF DIRECTION (GPU, ~45 min): Ashby's ULTRASTABILITY on the original physics -- a cell applies its self-rewrites only when its light income does not cover its maintenance; arms ultra / always / inverted / never. Learning in life, not evolution of populations. Pre-registered
PYTHONPATH=src python experiments/utero/exp_utero_modelo_reducido.py    # §39b REDUCED MODEL (numpy, 1 core, ~4 min; NOT the utero: iid output instead of programs): predicts NADA for the transplant with theta/s/g (12/24, 15/24); showed home-vs-away is confounded by habitat quality
PYTHONPATH=src python experiments/utero/exp_utero_modelo_reducido_q.py  # §40 reduced model + life-history knob (birth propensity by income level): predicts NADA (births fall everywhere alike)
PYTHONPATH=src python experiments/utero/exp_utero_orden_confirmatoria.py # §41 (with exp_utero_orden_oraculo / _torneo): oracle strategies, no mutation, reduced model. THE ENVIRONMENT DOES CONTAIN AN ORDER-DEPENDENT OPTIMUM: breed only in the season that FOLLOWS the famine (45/48 under clima, 48/48 reversed under ciclo2, 0.45 under permuted); always-breed is the worst
PYTHONPATH=src python experiments/utero/exp_utero_reflejo.py            # §37 frozen programs, heritable theta/s/g (reflejo): clima / ciclo2 / permutado / null; primary R2_A, secondary the sign of the gain. VESTIGIO / TIPOS DE TRANSICION / NADA pre-registered
PYTHONPATH=src python experiments/utero/exp_utero_tejido_plastico.py      # §45 plastic tissue (numpy prototype, ~25 min alone / 70 min shared): continuous per-cell rule learned in life by node perturbation (REINFORCE + eligibility trace) from the cell's OWN income; GENOTYPIC inheritance (amended 2026-10-25: learned weights die with the cell). RESULT (sol 0 + replica sol 1): APRENDE EN VIDA, SIN GENERALIZAR -- plastic > inverted/shuffled/frozen 16/16 in both suns, but regret 0.9 and G < 0 (re-learns every season); learning is MORTAL (lesion arm), direction matters (> pure Ashby 16/16), Lamarckian inheritance does not help. Unexpected: the frozen arm evolves a FAMINE SPECIALIST (0.45 in A, 0.17 in C) while the learner is a flat generalist (0.33). `calibrar` re-runs the constant-sun positive control; `replica k` other sun; `largo` = §45b 10x seasons: regret 0.90 -> 0.66, clean learning curves in A and C, stuck in B (the day moves faster than the rule): REACTOR, not generalizer
PYTHONPATH=src python experiments/utero/exp_utero_tejido_sentido.py       # §49 the §45 cell whose rule can READ its own income (fast tau 20 + slow tau 500): can a season-conditioned policy in W0 be the memory that survives the season? arms plastico/invertido/barajado/sin_plasticidad (with senses) + ciego (= §45 cell); RESULT: NADA on both suns (plastic with senses == ciego: 0.324 vs 0.327, G -0.20 vs -0.31); lifetimes measured: median 1410 ticks = two seasons, 28% see three -- a cell never sees the same season twice, so learning by recurrence is impossible by construction. The utero line is CLOSED by the NORTE.md rule; frontier back to the kernel
PYTHONPATH=src python experiments/utero/exp_utero_sol_vara.py       # 1-D heating sun with the amended yardstick (not run: superseded by the plane/metabolism runs)
PYTHONPATH=src python experiments/utero/exp_utero_escala.py         # scale robustness (~40 min): 1024 cells = same typicity; 120 seeds -> v5 4.2%, v6 5.8%. The rarity is intrinsic to 1-D

# Kernel:
PYTHONPATH=src python experiments/kernel/exp_conscious_kernel_validation.py
PYTHONPATH=src python experiments/kernel/exp_psi_quiebres.py        # 2026-10-26, the kernel ALONE (no Hermes): does Psi see rare large breaks in a predictable stream? 120 lives, 3 procs (~12 min): NO LO ENTIERRA by the letter -- rare breaks seen (hits 1.00, FA 0.03-0.07), frequent ones not (0.25-0.30), noise buries medium ones; ALTA never < 0.74 in 120 lives (the Phase B band was never reached)
PYTHONPATH=src python experiments/kernel/exp_psi_quiebres_componentes.py  # mechanism (~1 min): Phi_c fixed at 0.36; the episodic-memory bonus moves the threshold from 1.4x to 3.3x the mean free energy; Yvyra's fast memory was full (500/500)
PYTHONPATH=src python experiments/kernel/exp_mundo_propio.py        # §K1 (docs/MUNDO_PROPIO.md) the kernel in its OWN world: actions move a simplex state, 4 remapping regimes (3 recur, 1 novel late), efference-copy tests; 3 procs (~8 min): NO CONTROLA by the letter (9/12; 10% of visits get stuck); APRENDE 12/12 (learns the never-seen regime, frozen-after-infancy does not); RECUERDA 6/12 (no savings: re-learns every visit); DISTINGUE no (EXO 0.93 vs EFERENCIA 0.90). The world model has no complementary memory: dream/CLS never touch it
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_sueno.py control  # §K2 part 1, positive control of the mechanism (~10 min): the world model's SLEEP REPLAY (ConsciousKernel(wm_sleep_replay=...), sequences with BPTT vs one-step) on a babbled life; probe = in-context error on the regimes not being visited; STOP RULE before part 2. RESULT: retains 12/12 but as the EXACT AVERAGE of the lived regimes (no context: +0.003); amended attribution before part 2 (`relectura`)
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_sueno.py          # §K2 part 2 (~18 min): APRENDE Y RECUERDA by the letter (12/12, 12/12, 11/12; stuck visits 27 -> 1) -- the first positive verdict in the kernel's own world; attribution BY AVERAGING, not context (beyond-average 0/12): a generalist world model, not a repertoire; kernel arm reproduces §K1 exactly; DISTINGUE 10/12 not attributable to sleep
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_sueno.py replica  # §K2 replication, seeds 12-23 (~14 min): REPLICADO (12/12, 12/12, 10/12; stuck 1 vs 39), by averaging again; paired over 24 seeds the sleep speeds re-entry into KNOWN regimes 24/24 but also the NOVEL 17/24 -- the lived-specific part is 16/24 (p 0.08): mostly a generic better starting point
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_contexto.py calibracion  # §K3 calibration (seeds 100-102, babbled): only error_x4 (4x sleep dose + wm_error_input) leaves the averaging plateau (0.44 x average); the §K2 averaging was a TRAINING PLATEAU, not a capacity limit (offline pilot: 0.018 vs 0.103)
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_contexto.py control      # §K3 part 1 (~30 min): CONTEXTO_CTRL 11/12 (0.54 x average); dose alone 4/12, error input alone 0/12 -- both needed
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_contexto.py              # §K3 part 2 (~31 min): REPERTORIO by the letter (CONTEXTO 12/12 + APRENDE Y RECUERDA 12/12 x3, 0 stuck); DISTINGUE 12/12 (reported)
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_contexto.py replica      # §K3 replication, seeds 12-23 (~17 min): NOT REPLICATED (CONTEXTO 8/12 -> SIN REPERTORIO; behaviour 12/12 x3 again); DISTINGUE + paired vs no-sleep 12/12 (pre-registered): the kernel tells what it did from what happened to it. Post hoc: the NOVEL visit undoes the repertoire (ratio 0.4 -> 1.06) and sleep rebuilds it in ~2 cycles; pooled 20/24
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_gemelos.py humo         # §K4 smoke: newborn twins' clones give H = 0 exactly; a clone with its original's draws reproduces it
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_gemelos.py calibracion  # §K4 calibration (pairs 100-102, ~16 min): error_x4 H(T2) +0.74 3/3; kernel -0.51 (predicted DESVENTAJA, which then failed)
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_gemelos.py              # §K4 IDENTITY, twins raised in different worlds (pairs 0-11, ~63 min): IDENTIDAD (por el sueño) by the letter -- PERSISTE 12/12 after an exile as long as the childhood; kernel 9/12, paired 11/12; RECONOCE 8/12
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_gemelos.py replica      # §K4 replication (pairs 12-23, ~62 min): REPLICADO (PERSISTE 12/12, kernel 6/12, paired 12/12; pooled 24/24, 15/24, 23/24); RECONOCE 11/12 (pooled 19/24); RIGIDEZ 12/12 pre-registered: the kernel that keeps its childhood enters a never-lived world worse. Identity lives in the world model, not in self_embedding
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_crianza.py humo     # §K5 smoke (pair 0, short life): the dice twin equals its §K4 original at birth and then lives differently; prints the 'dos' schedule
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_crianza.py          # §K5 the price of identity and where it lives (pairs 0-11, ~95-120 min): Q1 crianza (home/school alternating vs one home) MENOS RIGIDO, CON IDENTIDAD (ACHICA 10/12, CONSERVA 12/12, INVIERTE 5/12); Q2 drift null of self_embedding (dice twins) LLEVA LA VIDA, NO LA NIÑEZ (CONTROL 12/12, LLEVA 11/12, NIÑEZ 7/12)
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_crianza.py replica  # §K5 replication (pairs 12-23, ~120 min): REPLICADO on both (pooled ACHICA 20/24, CONSERVA 23/24, LLEVA 23/24, NIÑEZ 14/24); the rigidity moves to the kernel WITHOUT sleep (58 stuck blocks in the alternating childhood); sleep attribution of identity weakens under 'dos' (paired 15/24)
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_coin.py calibracion  # §K6 calibration (seeds 100-102, ~9 min): coin (error_x4 + wm_contexts=6, COIN-style context experts) keeps the known regimes at 0.13 x the exact average through the NOVEL visit; error_x4 breaks (1.02-1.10)
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_coin.py              # §K6 (seeds 0-11, ~18 min): REPERTORIO ROBUSTO by the letter -- ROBUSTO 12/12 (NOVEL-end 0.14 vs error_x4 1.06), CONTEXTO 12/12, APRENDE Y RECUERDA, PAREADO 12/12
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_coin.py replica      # §K6 replication (seeds 12-23, ~19 min): REPLICADO (24/24 pooled on ROBUSTO, CONTEXTO, PAREADO); robust, not faster (known re-entry 16/24, NOVEL entry 13/24); spurious contexts in 9/24 lives
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_casas.py humo         # §K7 smoke (pair 0, short life): the loop reproduces the stored §K4 life (diff 0); newborn coin twins H(T0) = 0; the exile gets its own expert
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_casas.py calibracion  # §K7 calibration (pairs 100-102, ~31 min): coin (§K6 arm) under the §K5 upbringings; ELIGE 3/3, RIGIDEZ 3/3 (which then failed)
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_casas.py              # §K7 THE HOUSES, identity with a repertoire (pairs 0-11, ~137 min, 3 procs): IDENTIDAD EN EL REPERTORIO by the letter -- PERSISTE 12/12, ELIGE 11/12 (back home, both twins settle on their childhood expert); PAREADO 6/12 and RIGIDEZ 7/12 failed, ACHICA 10/12, EXILIO 11/12
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_casas.py replica      # §K7 replication (pairs 12-23; `replica reanudar` loads lives already on disk): REPLICADO (pooled PERSISTE 24/24, ELIGE 22/24, PAREADO 15/24, ACHICA 19/24, RIGIDEZ 15/24): the identity is which expert it goes back to; §K4's price nearly vanishes
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_separacion.py humo         # §K8 smoke (pair 0, short life): the loop reproduces the stored §K7 life (diff 0); newborn twins identical
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_separacion.py calibracion  # §K8 calibration (pairs 100-102, ~9 min): PERSISTE_SS 3/3, SUENO 3/3 (both misled)
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_separacion.py              # §K8 SLEEP OR SEPARATION, a 2x2 under 'una' (coin/error_x4 read; coin_sin_sueno/error_sin_sueno = wm_sleep_replay 0; pairs 0-11, ~28 min): POR EL SUENO by the letter -- PERSISTE_SS 7/12, SEPARA 6/12, SUENO 12/12; ELIGE_SS 5/12
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_separacion.py replica      # §K8 replication (pairs 12-23, ~29 min): REPLICADO (pooled PERSISTE_SS 14/24, SEPARA 14/24, SUENO 23/24; the sleep with one model, error input fixed, 22/24). Without sleep the home expert is kept frozen but coarse and hit by the first exile steps; the stale-snapshot hypothesis was refuted
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_separacion_foto.py  # §K8 mechanism (post hoc, ~10 min): 8 lives re-run with the contextual model instrumented (diff 0): the restored snapshot is taken 4-24 ticks into the exile, not in the childhood; the sleepless home expert is frozen through the exile (39/48) but hit at its start (0.087 -> 0.122) and coarse
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_ninez.py humo     # §K9 smoke (pair 0, short life): the childhood equals §K7's (diff 0), the whole life differs (the sleep stops)
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_ninez.py          # §K9 THE SLEEP OF THE CHILDHOOD (coin_ninez = coin with world-model sleep off from the exile on; every childhood verified vs §K7; pairs 0-11, ~31 min, no calibration): INDETERMINADO (PERSISTE_N 9/12, NINEZ 8/12, EXILIO 8/12); the precise home expert is hit by the first exile steps (0.005 -> 0.121, 23/24) and frozen
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_ninez.py replica  # §K9 replication (pairs 12-23; `replica reanudar`): HACE FALTA SEGUIR DURMIENDO -- NOT REPLICATED by the letter; pooled EXILIO 19/24, NINEZ 15/24, DANO 46/48: the childhood's precision does not reach the exile; the exile's sleep repairs it. Next: a snapshot in time
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_foto.py humo        # §K10 smoke: childhoods equal their reference (diff 0), the restored home expert stays precise through the exile
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_foto.py             # §K10 THE SNAPSHOT IN TIME (ContextualWorldModel(snapshot_lag=50): checkpoints after every sleep and every 50 ticks without one; arms coin_ninez_foto / coin_sin_sueno_foto; pairs 0-11, ~42 min): BASTA LA NINEZ -- FOTO A TIEMPO 22/24, PERSISTE_F 12/12, NINEZ_F 10/12, RESTO_F 5/12
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_foto.py replica     # §K10 replication (pairs 12-23, ~53 min): REPLICADO (pooled PERSISTE_F 23/24, NINEZ_F 20/24, RESTO_F 12/24); the never-sleeping repertoire with the snapshot in time persists 19/24 and chooses 22/24 -- §K8's POR EL SUENO was the lagged snapshot's
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_entre_suenos.py     # §K10 measurement (~8 min, 1 process): the slept home expert is precise only right after each sleep (0.004-0.006; median 0.012, up to 0.215 between sleeps); block-end probes are post-sleep
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_vigilia.py humo     # §K11 smoke (pair 0, short life): the coin re-run equals its §K7 life (diff 0); the awake probe only reads
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_vigilia.py          # §K11 THE WAKE THAT DOES NOT ERASE (ContextualWorldModel(wake_lr_scale=s): awake online steps at lr x s, sleep at the full rate; coin_vigilia = coin + s 0.1, coin re-run as the control with a probe 49 online steps after each sleep; pairs 0-11, ~122 min shared): PRECISA PERO LENTA -- EROSIONA 12/12 (coin home oracle 0.005 -> 0.042 awake), PRECISA 12/12 (0.009), PERSISTE_V 12/12, LENTO 12/12 (first exile block 0.970 vs 0.497)
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_vigilia.py replica  # §K11 replication (pairs 12-23, ~123 min): REPLICADO (24/24 pooled on every readout); the price is the entry into never-lived worlds (all 59 stuck blocks in the first two exile blocks); one awake rate does not give stability and plasticity -- next: a per-expert rate
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_madurez.py humo     # §K12 smoke (pair 0, short life): coin_vigilia re-run equals its §K11 life (diff 0); coin/coin_vigilia loaded from §K11
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_madurez.py          # §K12 MATURITY (ContextualWorldModel(wake_lr_scale_learning=1.0): slow wake (0.1) only while an expert explains its stream, full rate while newborn or failing; coin_madurez vs the stored §K11 coin / coin_vigilia; pairs 0-11, 25 lives, ~72 min shared): VIGILIA QUE NO BORRA -- PRECISA_M 12/12 (awake home oracle 0.009 vs coin 0.042), ENTRA 12/12 (first exile block 0.367 vs coin_vigilia 0.970; coin 0.497), PERSISTE_M 12/12, LENTO_M 3/12; 0 stuck blocks (coin 2, coin_vigilia 31); VUELVE 3/12 failed
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_madurez.py replica  # §K12 replication (pairs 12-23, ~69 min): REPLICADO (pooled PRECISA_M, ENTRA, PERSISTE_M 24/24; LENTO_M 4/24; 1 stuck block in 48 twins vs coin 3, coin_vigilia 59): a per-expert awake rate gives stability and plasticity; VUELVE 7/24 failed -- the home expert is intact (0.007), the cost is in the return
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_madurez_vuelta.py  # §K12 mechanism (post hoc, ~48 min, 16 lives re-run, diff 0): the home expert comes back intact and is DAMAGED by its own awake relearning on return (home error 0.007 -> 0.23 by tick 40, coin 0.09, until the next sleep): its running error carries the exile, so it 'does not explain' and learns at the full rate; slowing or freezing it removes VUELVE's excess (after-switch 0.083 -> 0.055, 7/8 and 6/8 twins)
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_regreso.py humo     # §K13 smoke (pair 0, short life): the coin_madurez re-run equals its §K12 life (diff 0); coin_regreso's main life equals coin_madurez's
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_regreso.py          # §K13 THE RETURN (ContextualWorldModel(slow_return=True): an established expert made active by a switch learns awake slowly until it explains, at most persist ticks; coin_regreso vs the stored coin / coin_vigilia / coin_madurez; pairs 0-11, 25 lives, ~60 min): VUELVE A CASA -- PROTEGE 12/12 (home T2 0.117 vs coin_madurez 0.168), VUELVE_R 11/12 (coin 0.146), CONSERVA_R and PERSISTE_R 12/12, RIGIDO_R T1 3/12, T2 1/12; the main life is coin_madurez's in 24/24 twins; after the switch home 0.054 vs 0.122; the price is 3/24 twins that go back to h in their sibling's home at T1
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_regreso.py replica  # §K13 replication (pairs 12-23, ~58 min): REPLICADO (pooled PROTEGE 24/24, VUELVE_R 22/24, CONSERVA_R and PERSISTE_R 24/24, RIGIDO_R T1 6/24, T2 3/24; after the switch home 0.056 vs coin_madurez 0.114, coin 0.064): the same arm keeps what sleep consolidates, enters the never-lived better than coin and returns home better than coin; the price is 9/96 twin-assays abroad that hold h slow in their sibling's home
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_escuela.py humo         # §K14 smoke (pair 0, short life): every coin re-run under 'dos' equals its §K7 life (diff 0)
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_escuela.py calibracion  # §K14 calibration (pairs 100-102, ~36 min): CONSERVA_D 3/3, ENTRA_D 1/3 (two twins stuck in the first exile block), VUELVE_D 2/3, PERSISTE_D 3/3
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_escuela.py              # §K14 THE SCHOOL (coin_regreso vs coin re-run, both under §K5's 'dos'; every coin re-run must equal its §K7 life; pairs 0-11, 48 lives, ~81 min resumed): NO AGUANTA: ENTRA_D, as predicted after the calibration -- verification 24/24; CONSERVA_D 12/12 (awake home oracle 0.015 vs 0.046), VUELVE_D 11/12 (home T2 0.145 vs 0.203), PERSISTE_D 12/12, ENTRA_D 7/12 (0.285 vs 0.327), RIGIDO_D T1 5/12, T2 4/12; the school already makes coin enter better (0.327 vs 0.497 under 'una', 12/12 pairs), so the arm's entry advantage shrinks to -0.02
PYTHONPATH=src python experiments/kernel/exp_mundo_propio_escuela.py replica      # §K14 replication (pairs 12-23)
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
| `gpu.py` | **The GPU batch engine** (`UteroGPU`): every world of an experiment as tensors (B worlds × N cells) on CUDA. The vectorized VM is EXACTLY `nivel2.execute` (tested); the soup is `UteroCreciente`'s (tested). Declared hand: the ORDER is a checkerboard (two half-steps per tick), not asynchronous — another incarnation, validated by reproducing §26 and §34 (`exp_utero_gpu_validacion.py`), not byte-identical to CPU. Closed worlds only (n0 = max_n). ~15 ms/tick for 48 worlds × 512 cells. **Long experiments run here, not on CPU process pools** (the machine is shared). VALIDATION (§38/§38b): reproduces the gradient control (19/20) and the LEVEL of the first evolution (11/12, 20/24) but NOT the within-run trend criterion (9/12, 16/24): not validated by the letter; use it with LEVEL readouts and confirm any positive on CPU (single core, reduced scale) before believing it. Runs are RESUMABLE: `correr(checkpoint=path, cada=5000)` saves exact state + series atomically under `data/ckpt/` and resumes from disk (tested identical to an uninterrupted run). |
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
| `parametros=ε` (+ `theta_fijo`) | v17 | **the answer to the fifth cage** (the program->matter map has no locality): a heritable continuous offset θ per cell added to the matter AFTER the probe; the child inherits θ ± ε·(2·frac(|mother's raw R3|·131) − 1) (matter-derived, no RNG of ours); `theta_fijo=True` keeps θ present but never perturbed (the null). Toroidal only. ε=0 = byte-identical |
| `escala=True` | v17b | with `parametros`: visible matter = (θ + s·output) mod 1, s ∈ [0,1] heritable (born at 1, perturbed ±ε from the mother's matter, clipped). The probe still sees the raw output: the physics must stay sensitive, only its expression in matter can be attenuated. `theta_fijo` freezes s too. Off = byte-identical |
| `perillas=True` | §36 | with `parametros`, `escala`, `lentos`: the physics can move its own expression in life: θ_eff = (θ + S1) mod 1, s_eff = clip(s + S2), S1/S2 the slow registers the rule pushes. Inheritance sets the baseline, behaviour shifts it. Off = byte-identical |
| `reflejo=ε_g` | §37 | a knob of the cell's OWN HISTORY: θ_eff += g·tanh((ē − e)/e0), ē a slow mean of the cell's energy (τ=200), g a heritable continuous gain (born 0, ±ε_g from the mother's matter, clipped to [−2,2]). Requires parametros, escala, energia. Off = byte-identical |
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
| `contextual_world_model.py` | §K6 `ContextualWorldModel` (`wm_contexts=K`): K `WorldModel` experts with hard context inference, spawn-on-unexplained and per-expert sleep (COIN-style) |
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
| `wm_sleep_replay` / `wm_sleep_seq_len` / `wm_sleep_batch` | 0 / 16 / 8 | §K2: the WORLD MODEL replays lived transitions in sleep (every `dream_interval`): N gradient steps on windows of consecutive ticks through its own recurrence with BPTT (seq_len 1 = context-free one-step replay). 0 = off, byte-identical (`tests/test_sleep_replay.py`) |
| `wm_error_input` | False | §K3: the world model's GRU also sees its own last prediction error (observation - prediction); zero in imagination and at the start of each sleep window. With 4x sleep replay it infers the hidden regime (context) instead of averaging. False = byte-identical (`tests/test_error_input.py`) |
| `wm_contexts` / `wm_context_kwargs` | 0 / None | §K6: a COIN-style repertoire -- K world-model experts allocated at birth, one active; hard switch on the running prediction error, a NEW expert (copy of the active one) when none explains for `persist` ticks, the old one restored to its pre-streak weights; each expert sleeps on its own transitions. With error_x4 it keeps the known regimes through a never-seen one (§K6, replicated 24/24). 0 = byte-identical (`tests/test_contextual_world_model.py`). `wm_context_kwargs` also takes `snapshot_lag` (§K10: checkpoints after every sleep and every L ticks; restores the latest >= L ticks old) and `wake_lr_scale` (§K11: awake steps at lr x s, sleep at the full rate; 1 = byte-identical) and `wake_lr_scale_learning` (§K12: the factor while an expert does not explain its stream -- newborn or running error above threshold; None = byte-identical) and `slow_return` (§K13: an established expert made active by a switch learns awake at wake_lr_scale until it explains, at most persist ticks; False = byte-identical) |
| `precision_hypermodel` | False | epistemic depth ("A beautiful loop", Friston 2025): a hyper-model that PREDICTS per-channel precisions globally and reports a **second-order error over precision** (`StepResult.second_order_error`). OFF = byte-identical kernel. The signal spikes at regime change and is independent of free energy (|corr|≈0 vs Psi's 0.53) — see `precision_hypermodel.py`, `exp_epistemic_depth.py`, `docs/SCIENCE_PLAN.md` |

## Documentation

- **`docs/NORTE.md` — the one-page north.** The invariant question (a system that is born empty, learns from its
  own experience in life and sustains an identity, without pretraining), what each of the five programs answered,
  where the kernel and the útero converge (§45 = a útero cell with the kernel's rule), and the current decision
  rule. Update it only when the question changes; add one line after every program closes.
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
- `docs/ESTADO_DEL_ARTE_APRENDER_EN_VIDA.md` — **state of the art (2026-10-25) for learning IN LIFE without
  pretraining**, written before running the §45 seasonal test: evolved plasticity (Najarro/Risi, LNDP, Medvid 2026
  anti-Hebb + regret), node perturbation (= REINFORCE + Fiete-Seung), mortal computation (Hinton, Ororbia-Friston),
  NCA with memory, basal cognition (GRN memory, single-cell habituation), one-shot structure learning (Friston 2025),
  Ashby/Di Paolo ultrastability, DGM/ASAL. Table vs the four §44 requirements, repetition risks, gaps, **the
  Lamarckian-inheritance flaw of the §45 prototype** (the child inherits the mother's LEARNED weights) and the
  pre-registered amendments (genotypic inheritance, regret vs oracle, mid-life lesion, two cheap arms). Plus a
  fiction section (Egan, Lem, Chiang, Watts, Rucker, Tchaikovsky, Borges, Bioy). Read before touching §45.
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

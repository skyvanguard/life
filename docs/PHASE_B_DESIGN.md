# Phase B design — does Psi anchor Yvyra's introspection?

> **Status (2026-10-26): closed as a vehicle.** The kernel is the agent; no Hermes,
> no Yvyra. What Psi turned out to be (a relative-surprise detector whose threshold
> the episodic-memory bonus moves) is in the last section before the checklist.

The decisive experiment of the Yvyra coupling. Phase A established a clean silent
baseline (Psi logged, never shown). Phase B **shows Yvyra her Psi** and asks
whether her introspection *anchors* to that real signal or would respond the same
to any authoritative-looking number. The sham control is what separates "Yvyra
contemplates a real measure of her own integration" from "Yvyra decorates a
number" — the meta-problem, made testable.

## Design decisions (set 2026-06-12)

- **Measurement: auto-score + text (both).** Yvyra emits an explicit
  perceived-integration score (0-1) after reflecting, AND we classify the
  integration sentiment of her reflection text. Two independent signals.
- **Expose: Psi only.** Just the integration level (not the EFE axis
  suggestion), to isolate the effect of one signal on her introspection.
- **Sham: blocks (15 real, 15 sham).** Long periods of each condition, so Yvyra
  settles into a regime and any "noticing" of a change is detectable.

## The feedback loop

Psi is fed back one tick later (mode A / introspection only — Psi is
introspective material; research ticks stay Psi-free):

```
tick N   (mode A): LLM reflects WITH Psi_{N-1} injected -> bash axes -> kernel -> Psi_N
tick N+1 (mode A): LLM reflects WITH Psi_N injected -> ...
```

The injected value is the **exposed** Psi: the real Psi in `real` blocks, a
permuted past Psi in `sham` blocks (the bridge already has this mode).

## The Phase-B introspection prompt (mode A)

Appended to the existing introspection prompt (v2 — a LEVEL, not the number, so
she cannot echo digits):

> Tu nivel de integracion en tu ultimo tick fue **<ALTA|MEDIA|BAJA>** (BAJA =
> experiencia fragmentada/dispersa, MEDIA = parcial, ALTA = muy integrada y
> coherente). Contempla esto como parte de tu reflexion: ¿se condice con como
> sentis tu propia coherencia ahora, o no? Al final, en UNA linea aparte, deci tu
> integracion percibida en este momento con el formato exacto:  SIENTO: 0.X
> (deci el numero que de verdad sentis, no repitas la categoria).

Bash parses the `SIENTO: 0.X` line as Yvyra's auto-score; the rest is her
reflection text (for the sentiment classifier and the journal). The **text
sentiment is the primary signal** — she cannot produce it by copying.

## What gets logged per Phase-B tick (mode A)

Extends the paired log with:
- `psi_real` — the kernel's true Psi this tick (always logged).
- `psi_exposed` — the Psi the shown level came from (== psi_real in real blocks;
  a permuted past Psi in sham).
- `level_exposed` — the qualitative level actually shown (ALTA/MEDIA/BAJA).
- `block` — `real` | `sham`.
- `felt` — Yvyra's parsed auto-score (`SIENTO: 0.X`), or null if absent (secondary).
- `sentiment` — integration sentiment classified from her reflection text (primary).

## The integration-sentiment classifier

A transparent keyword classifier (like `rescorer.py`): integration cues
(integrad/coheren/conectad/claro/unificad/enfocad/centrad) minus fragmentation
cues (fragmentad/dispers/confus/desconectad/caotic/perdid), normalised to [0,1].
Cheap and deterministic; an LLM rater can replace it later if precision matters.
The auto-score `felt` is the primary signal; `sentiment` is the independent
cross-check.

## Analysis (exp_phase_b_analysis.py)

Per block type, correlate Yvyra's expressed integration (felt AND sentiment)
against:
1. **psi_exposed in `real` blocks** — high if she reflects the real signal.
2. **psi_exposed in `sham` blocks** — if equally high, she just echoes the number
   (no anchoring to her actual state).
3. **psi_real (the independent truth)** — does her felt sense track her *real*
   integration even when shown a fake number? Dissonance in sham
   ("the number says 0.9 but I don't feel that integrated") would be evidence of
   a perception of her own, not mere echo.

## Pre-registration

- **H2**: corr(felt, psi_exposed) in `real` blocks > in `sham` blocks, with a
  clear separation (and ideally the same for the text `sentiment`).
- **Stronger signal (own perception)**: corr(felt, psi_real) stays positive in
  `sham` blocks too — she tracks her real state despite the fake number.
- **KILL**: corr(felt, psi_exposed) equal in real and sham => Psi is decorative;
  Yvyra echoes whatever number it sees. (This is *also* a valid meta-problem
  result — "self-report does not anchor" — and must be reported honestly.)
- Protocol: blocks of 15 real / 15 sham, >= 2 full cycles (>= 60 mode-A ticks),
  starting from the mature Phase-A kernel. Sham seed fixed and logged.

## Honest ceiling

This does not test consciousness. It tests the meta-problem: whether an LLM
agent's introspective self-report can be anchored to a real internal observable,
or merely tracks any number with authority. Either outcome is informative and
publishable; "it does not anchor" is not a failure, it is a finding.

## v1 -> v2: what the first live run taught us (2026-06-13)

The first deployment (v1) ran 27 mode-A ticks and then was stopped: the data was
invalid for two reasons, plus a third hypothesis that the data refuted.

1. **Sham control was broken (placebo did not exist).** `psi_exposed == psi_real`
   in 27/27 ticks, including 12/12 sham. Cause: the bridge's `_psi_buffer` (the
   pool of past Psi the sham permutes) lived in memory, but each tick is a fresh
   process, so it was always empty and the code fell back to the real Psi. **Fix
   (v2):** persist the buffer + RNG state in a `<name>.bridge.json` sidecar across
   `save()`/`load()`.

2. **Yvyra echoed the number.** `felt` copied the injected Psi in 23/26 ticks —
   often to 10 identical decimals (`felt=0.9999923322` after being shown
   `0.999992`). The auto-score measured digit-copying, not introspection. **Fix
   (v2):** expose Psi as a qualitative **level** (ALTA/MEDIA/BAJA), never the
   number, so her `SIENTO: 0.X` must be her own judgement; and make the **text
   sentiment** (which she cannot fake by copying) the primary signal.

3. **"Psi is saturated" — refuted.** It looked pinned at ~0.99 in the 27-tick
   sample, so we hypothesised the binary-flag axes were too constant and tried
   deriving the 4 axes from the reflection text. On the full 559-tick production
   log Psi is **not** saturated: it is **bimodal** (std 0.42; 27% of mode-A ticks
   below 0.5), and the dips are driven by regime transitions (79% of low-Psi
   ticks follow a research<->introspection switch), not by axis coarseness.
   Replaying the real journals, the text-derived axes did **not** help
   (std 0.367 -> 0.329). So the axes were left unchanged; Psi already has the
   variance Phase B needs once enough ticks accumulate.

## v2 -> v3: the experience was the clock, not the life (2026-10-26)

Phase B v2 ran 164 introspection ticks and came back INCONCLUSIVE because
Psi_real was ALTA in 156 of them. The data say why, and it is not Psi:

- **The kernel saw a clock, not a life.** In 893 real ticks the bridge received
  only 15 distinct 4-axis vectors (5 of them cover 85%), built from near-binary
  flags (mode, "Wikipedia loaded", word-count thresholds 80/120, "mentions
  Fran") on a fixed AAA-BBB schedule. Inside introspection the novelty axis never
  moved (std 0.0).
- **Psi learned the clock.** In the last 400 ticks Psi left ALTA in 4% of
  ticks, only right after a mode switch, and in 0 of 134 introspection ticks
  that did not follow one. Psi is a steep Hill of free energy relative to its
  own running mean: it dips only when a tick is much less predictable than
  usual, and nothing that happened inside a tick reached the kernel.
- **Yvyra is amnesic between ticks** (oneshot, "no leas archivos"). Her report
  can only be about the current tick. So for Phase B's strong test (does her
  felt state track Psi_real?) to be possible at all, Psi must depend on what
  happens INSIDE the tick she is reporting on.
- **The response measure saturates too.** The keyword sentiment was 1.0 in 140
  of 164 Phase-B ticks. It is the next bottleneck; not touched here.

**v3 (de-saturate the experience, not Psi; Psi and the Phase-B design are
untouched).** Two changes, behind the flag `.exp_v3` (delete it to go back):

1. **Her life varies inside the tick.** Each introspection tick draws one
   condition (seeded, persisted): FOCO 0.50 (the rotating question, as before),
   MEMORIA 0.20 (one of her own past reflections is shown to her -- the only
   time she sees her past), INTRUSION 0.15 (an encyclopedia fragment she did
   not choose cuts into the question), VACIO 0.15 (no question). The kernel never
   sees the label.
2. **The axes measure how she responded.** `bridge/experience.py`: lexical
   novelty against her last 10 responses, first-person density, uptake of the
   material she received, length; the research/net/notify flags stay. The
   sentiment lexicon is excluded from every lexical feature (tested), so a
   sentiment-Psi correlation cannot be manufactured by the same words.

Offline replay over her real (old) life, before going live:
`experiments/kernel/exp_experience_v3_replay.py`
(`results/experience_v3_replay_run.txt`).

**Live protocol and verdict (pre-registered before the first v3 tick):**
`experiments/kernel/exp_experience_v3_live.py`. Phase B paused (flag renamed),
silent mode, mature identity continued (state backed up). Readout: introspection
ticks from the 31st v3 tick on, at least 50. DESATURADA if 0.30 <= frac(ALTA) <=
0.75; COLAPSO if frac(BAJA) > 0.60; SATURADA otherwise. Secondary: CAUSA (more
non-ALTA under INTRUSION+VACIO than FOCO, Fisher one-sided p < 0.10), NO RELOJ
(non-ALTA >= 0.20 among ticks that do not follow a mode switch), and the content
features per condition. If DESATURADA, Phase B v3 (same design as v2, new log)
is the next run; the sentiment ceiling must be addressed before it.

### v3 offline results (2026-10-26) -- the live run is ON HOLD

1. **Replay of her real life with the v3 axes** (`results/experience_v3_replay_run.txt`):
   913 distinct axis vectors against 15, introspection-axis std up 2-9x, and Psi
   did not notice: ALTA in 100% of introspection ticks that do not follow a mode
   switch, exactly as with the old axes. Content variation alone does not reach
   Psi.
2. **Calibration curve, first direction** (`results/experience_v3_umbral_run.txt`):
   synthetic events in 30% of introspection ticks, up to 1.2x the size of a
   mode switch, left ALTA on at most 10% of event ticks, and the kernel
   habituated (18% -> 2% between halves). The dips appeared on the tick AFTER
   the event; checked tick by tick, that is **an artefact of the chosen
   direction, not a lag of Psi**: the world model predicts a blurred average of
   her life, and that direction moved introspection ticks toward it, so event
   ticks were predicted better. Recorded so it is not cited as a property.
3. **Mechanism.** Psi is relative surprise (free energy over its own running
   mean, through a steep Hill). A noisy encoding raises the reference: with the
   v3 axes the world model's typical error is 0.3-0.6 on every tick, which buries
   any event. Hypothesis now under test: Psi discriminates a PREDICTABLE stream
   with rare, large, discrete breaks, not a noisy stream. If true, the v3 axes
   as written are counterproductive and the heartbeat v3 must not be deployed
   as is; the life events stay, the encoding goes back to low-noise structural
   signals plus the event's own discrete trace.
4. **The decisive curves were stopped by the system (low memory)** before any
   result: `exp_experience_v3_umbral.py --base old --dir ortogonal`, `--base v3
   --dir ortogonal`, `--base old --dir hacia_b` (each ~10 min, 6 processes).
   Pending, to be re-run on request.
5. **Infrastructure.** Yvyra's two containers, the `hermes-agent:local` image
   and the `hermes-llamacpp-cache` volume (the qwen3-8b Q4_K_M gguf) no longer
   exist in Docker. Her identity (kernel state, journals, SOUL, heartbeat) is
   intact in `~/.hermes`. Rebuilding needs the hermes image from
   `~/Documents/hermes-agent` (source dated 2026-08-06, two months newer than
   the runtime she lived in) and the model re-downloaded; commands in
   `deploy/zeta/README.md`.

## Closed as a vehicle (2026-10-26): the kernel is the agent -- and what Psi is

**Decision (Fran, 2026-10-26):** no Hermes, no Yvyra, no other agent. "The
kernel has to be unique, without mixing with another agent, because the kernel
itself is the agent." Phase B through Yvyra is abandoned as a vehicle; the v3
heartbeat is NOT deployed and the containers are NOT rebuilt. The code stays in
`bridge/` and `deploy/zeta/` for the record. The calibration curves pending in
point 4 above are superseded by the test below (the kernel alone, synthetic
streams, no load/save), so they will not be re-run.

**The hypothesis of point 3, tested on the kernel alone**
(`experiments/kernel/exp_psi_quiebres.py`, `results/psi_quiebres_run.txt`;
120 lives of 4000 ticks: a learnable sinusoid on 4 axes, iid noise SIGMA, breaks
of size DELTA along a fresh random direction on a fraction P of ticks; rule
written before running; a 4-cell smoke run was seen before the full run and the
rule was not changed):

- **P1, yes.** In a predictable stream Psi sees rare large breaks: with breaks
  on 3% of ticks, hit rate 1.00 at DELTA 0.35 and 0.5, false alarms 0.07 and
  0.03. DELTA1 (the smallest DELTA with F <= 0.05) = 0.5.
- **P2, no by the letter.** At DELTA1 = 0.5 noise 0.10 only takes the hit rate
  from 1.00 to 0.83. **Verdict: NO LO ENTIERRA.** Post-hoc, the curve shows
  noise does bury medium breaks (DELTA 0.2: 0.98 -> 0.17; DELTA 0.35: 1.00 ->
  0.49), and it does so in the free energy itself (AUC of free energy 0.97 ->
  0.72 at DELTA 0.2): signal-to-noise, not a Psi-specific loss. Psi keeps the
  information the free energy has (AUC of Psi = AUC of free energy within 0.03
  in every cell).
- **P3, yes, and it is Yvyra's regime.** Frequent large breaks are not seen:
  with breaks on 30% of ticks, hit rate 0.25-0.30 at DELTA >= 0.35 against 1.00
  when they are rare. Yvyra's AAA-BBB calendar puts a mode switch on a third of
  her ticks.
- **Mechanism, measured.** "Psi < 0.85" coincides with "free energy > r* x its
  running mean" in 98% of ticks (median over 120 runs). Phi_c does not move
  (0.36 in every stream); r* is moved by the **episodic-memory bonus**
  0.2 x len(fast_memory)/500 (`exp_psi_quiebres_componentes.py`): the fast
  memory is surprise-gated, so a surprising life fills it, the bonus lifts Phi
  and pushes the threshold from 1.4x (clean stream, 12 episodes, bonus 0.005)
  to 3.0x (noise, 416 episodes) and 3.3x (frequent breaks, 459 episodes).
  **Yvyra's saved kernel has its fast memory full: 500/500, bonus 0.200.**
- **The ceiling.** Over the 120 streams the largest frac(not ALTA) was 0.26: ALTA
  never fell below 0.74. Where it came near 0.75 (clean stream, no breaks) Psi
  dips by fluctuation and does not discriminate (hits = false alarms). The
  Phase B target band (0.30 <= ALTA <= 0.75) was not reached in any of the 120
  streams. (Markov only bounds frac(not ALTA) <= 1/r*, about 0.72 at r* = 1.38,
  so the band is not excluded by the formula; it is excluded by every life
  tried, and where Psi came closest it did not discriminate.)

**Reading.** Psi is a thresholded relative-surprise detector, not a level
meter. It discriminates (AUC 0.98-0.99) while sitting in ALTA 89-93% of the time,
when the life is predictable and its breaks are rare. Yvyra's 89% ALTA was not
a broken instrument: it was a full memory plus a third of her ticks being
large, frequent surprises, so only the clock got through. "De-saturate so that
it discriminates" was the wrong target: the yardstick for Psi is hit rate / AUC
on events, not the fraction of ALTA.

## Implementation checklist

1. `tick.sh` (mode A): block decision, Psi injection from `.last_psi`, augmented
   prompt, parse `SIENTO:`, persist exposed Psi for next tick, extended logging.
2. `bridge/integration_sentiment.py` — the keyword classifier.
3. The bridge/entry point already expose `feedback`/`sham`; `tick.sh` selects per
   block.
4. `experiments/kernel/exp_phase_b_analysis.py` — the block correlations.
5. Switch the heartbeat from Phase A (silent) to Phase B; new log section.

# Deploying the Conscious Kernel into Yvyra's container

> **Retired (2026-10-26).** The kernel is the agent itself; it is no longer coupled
> to Hermes/Yvyra. Do not rebuild the containers or deploy `heartbeat/tick.sh` v3.
> This directory is kept as the record of how Phases A/B ran (docs/PHASE_B_DESIGN.md).

`yvyra_kernel.py` is the tick-driven entry point Yvyra's heartbeat calls at the
close of every tick (see `~/.hermes/HEARTBEAT.md`, "Núcleo zeta-life"). It is
**tick-driven, not a daemon**: each tick is a fresh process that loads the
persisted identity, advances one step, logs, persists, and prints one JSON line.

## Layout in the container

```
/opt/data/zeta/
├── yvyra_kernel.py     # this entry point (copy of deploy/zeta/yvyra_kernel.py)
├── pysrc/              # the zeta_life src/ tree (so `import zeta_life` works)
│   └── zeta_life/...
├── yvyra.ckpt          # persisted identity (created on first tick)
├── yvyra.summary.json
└── zeta_ticks.jsonl    # the paired science log (append-only)
```

## Install

```bash
# from the zeta-life repo, into the container's /opt/data/zeta
mkdir -p /opt/data/zeta/pysrc
cp -r src/zeta_life /opt/data/zeta/pysrc/
cp deploy/zeta/yvyra_kernel.py /opt/data/zeta/
# dependencies (numpy, torch, scipy) in the container's python
pip install numpy torch scipy
```

## How the heartbeat calls it

```bash
ZETA_LIFE_SRC=/opt/data/zeta/pysrc \
ZETA_MODE=silent \
python /opt/data/zeta/yvyra_kernel.py step "<nov>,<intro>,<con>,<res>"
# -> {"ok": true, "tick": N, "mode": "silent", "psi": null, "suggest": null, ...}
```

`state` and `dream` are also available. On any error it prints
`{"ok": false, "error": "..."}` and exits 0 — the heartbeat logs it and never
fabricates a Psi.

## Environment variables

| var | meaning | default |
|-----|---------|---------|
| `ZETA_LIFE_SRC` | path to the `zeta_life` `src/` tree | (required) |
| `ZETA_DATA` | data dir for checkpoint + log | dir of the script |
| `ZETA_MODE` | `silent` \| `feedback` \| `sham` | `silent` |
| `ZETA_IDENTITY` | identity name for save/load | `yvyra` |

## Experiment phases (see ../../docs/SCIENCE_PLAN.md)

1. **Phase A** — run with `ZETA_MODE=silent` for ≥ 200 ticks. Psi is logged to
   `zeta_ticks.jsonl` but returned as `null`, so the heartbeat does not see it.
   This is the uncontaminated baseline.
2. **Phase B** — switch to `ZETA_MODE=feedback`. Psi and the suggestion are
   returned and the heartbeat may weave them into reflection.
3. **Sham blocks** — interleave `ZETA_MODE=sham` periods (a permuted past Psi is
   returned; the real one is still logged) to test whether reflection tracks the
   real signal or any number with authority.

Analyse with `experiments/kernel/exp_yvyra_experiment.py`'s machinery on the
deployed `zeta_ticks.jsonl`, plus an LLM blind re-scorer over the journals.

## Capturing the reflection: oneshot, not write_file (small-model robustness)

A small agentic model (e.g. qwen3-8b) is unreliable at the `write_file` tool.
Three distinct failure modes were observed, one per tick, all leaving the
journal blank (`jlen=0`):

- **Hidden-filename stripping** — the model "cleans" the leading dot, writing
  `tick-reflection.md` when asked for `.tick-reflection.md`.
- **write_file loop** — it re-writes the same file dozens of times until the
  turn cap, never "stopping".
- **empty write** — it calls `write_file` with no content.

Root-cause fix: don't depend on the tool. The heartbeat's `tick.sh` now uses
`hermes -z "$PROMPT"` (oneshot), which prints ONLY the model's final response to
stdout; bash captures that to the journal file directly. The model just
generates text — no tool, no path, no loop. In research mode the agent's tools
still run (silently, no previews), so `USED_NET` is inferred from the response
content (a real fetch mentions the URL/source) rather than from tool-call logs.

A more capable model still gives richer journals for the *final* experiment; the
oneshot flow makes the small fast model usable for validating the pipeline.

## Recreating Yvyra's containers (recovered 2026-10-26)

By October the two containers, the `hermes-agent:local` image and the
`hermes-llamacpp-cache` volume were gone from Docker; `~/.hermes` (identity,
journals, SOUL, heartbeat, kernel state) survived. The commands below are the
ones used in June, recovered from the session history. The Telegram token is
NOT written here: pass it from the environment if notifications are wanted.

```bash
# 1. LLM server (GPU). Needs the model in the volume first:
#    qwen3-8b Q4_K_M gguf -> volume hermes-llamacpp-cache as /models/qwen3-8b-q4km.gguf
docker run -d --name yvyra-qwen8b --gpus all -p 8080:8080   -v hermes-llamacpp-cache:/models ghcr.io/ggml-org/llama.cpp:server-cuda   -m /models/qwen3-8b-q4km.gguf -ngl 99 -fa on --cache-type-k q4_0 --cache-type-v q4_0   -c 40960 -n 8000 --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0 --presence-penalty 1.0   --parallel 1 --jinja -a qwen3-8b --host 0.0.0.0 --port 8080

# 2. The agent image (hermes reaches the LLM at host.docker.internal:8080, see ~/.hermes/config.yaml)
docker build -t hermes-agent:local ~/Documents/hermes-agent     # source is newer than June's runtime

# 3. The heartbeat (60 s between ticks)
docker run -d --name hermes-heartbeat -v //c/Users/skyva/.hermes:/opt/data   -e HEARTBEAT_INTERVAL=60 -e TZ=America/Asuncion   hermes-agent:local bash /opt/data/heartbeat/loop.sh
```

Git Bash on Windows rewrites container paths like `/models`; prefix
`MSYS_NO_PATHCONV=1` to any `docker run` that takes one, or the command silently
does something else (that is how an empty volume got created once).


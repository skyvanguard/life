"""
COIN-style contextual world model (§K6 of docs/MUNDO_PROPIO.md).

§K3 gave the kernel's single world model a repertoire (seeing its own error and
with 4x sleep it infers which regime it is in), but a fragile one: one visit to a
never-seen regime overwrites the known ones (probe ratio 0.4 -> 1.06) and sleep
needs ~2 cycles to rebuild them. COIN (Heald, Lengyel & Wolpert 2021) keeps one
memory per inferred context and creates a NEW one when no known context explains
the evidence, instead of rewriting the old ones. This is a minimal, hard (MAP)
version of that principle built from the kernel's own WorldModel:

- K experts (each a WorldModel) are allocated at birth; one is in use at first.
- Every expert in use predicts every tick (from the same executed action) and
  tracks the stream with its own recurrence; only the ACTIVE one learns online.
- Each keeps a running prediction error r_c (EMA over ``tau`` ticks of
  ||obs - pred_c||).
- An expert is ESTABLISHED once its running error has been <= ``threshold``
  (it has explained the stream at least once). While the active expert is still
  learning its first context a high error is not evidence of a new one: no
  snapshot and no spawn until it is established.
- When the established active expert stops explaining (r_active > ``threshold``) a snapshot of
  its weights is taken. If it recovers, the snapshot is dropped. If another
  expert takes over, the old one is RESTORED to the snapshot and the transitions
  of the streak move to the new one's buffer: what was learned while it was
  failing is credited to the context that explains it, not to the old memory.
- SWITCH to the expert in use with the lowest r_c when it beats the active one by
  ``margin`` (r_best < (1 - margin) r_active), >= ``grace_switch`` ticks after the
  last change.
- SPAWN when every expert in use has r_c > ``threshold`` for ``persist``
  consecutive ticks, >= ``grace_spawn`` ticks after the last change, the active
  one established and a slot free: the next expert (not yet established) starts from the active one's CURRENT weights (it carries
  what it began to learn about the new context, and the general physics), and
  the active one is restored. The copy diverges by learning; the original is
  protected.
- Each transition (prev obs, action, obs) is stored in the buffer of the expert
  that predicted it; sleep replays each expert on its own buffer, the dose split
  in proportion to the buffer sizes (the total is the kernel's dose).

The defaults were explored with the error input on (the §K6 configuration): the
threshold is absolute, and without the error input an expert's running error
hovers near it and spurious contexts appear.

The kernel talks to it through the WorldModel interface (predict / observe /
update_from_error / imagine and the active expert's attributes).
"""

from __future__ import annotations

import copy

import torch
from torch import Tensor, nn

from .replay import ReplayBuffer
from .world_model import WorldModel, sleep_replay


class ContextualWorldModel(nn.Module):
    """A repertoire of world-model experts with hard context inference.

    Parameters
    ----------
    n_contexts : int
        Number of expert slots (allocated at birth; one in use at first).
    obs_dim, latent_dim, action_dim, learning_rate, error_input
        Passed to every :class:`WorldModel` expert.
    tau : float
        Ticks of the running prediction error (EMA rate 1/tau).
    threshold : float
        Running error above which a context does not explain the stream.
    margin : float
        Relative advantage needed to switch to another expert.
    persist : int
        Consecutive ticks with every expert above ``threshold`` before a spawn.
    grace_switch, grace_spawn : int
        Minimum ticks since the last change before a switch / a spawn.
    replay_capacity, replay_seed : int
        Capacity and base seed of the per-expert transition buffers.
    """

    def __init__(
        self,
        n_contexts: int,
        obs_dim: int = 4,
        latent_dim: int = 32,
        action_dim: int = 4,
        learning_rate: float = 0.005,
        error_input: bool = False,
        tau: float = 10.0,
        threshold: float = 0.08,
        margin: float = 0.2,
        persist: int = 30,
        grace_switch: int = 20,
        grace_spawn: int = 150,
        replay_capacity: int = 10000,
        replay_seed: int = 20261026,
    ) -> None:
        super().__init__()
        if n_contexts < 1:
            raise ValueError(f"n_contexts must be >= 1, got {n_contexts}")
        if tau < 1.0 or not 0.0 <= margin < 1.0 or threshold <= 0.0:
            raise ValueError("need tau >= 1, 0 <= margin < 1 and threshold > 0")
        self.n_contexts = n_contexts
        self.experts = nn.ModuleList([
            WorldModel(obs_dim, latent_dim, action_dim, learning_rate=learning_rate,
                       error_input=error_input)
            for _ in range(n_contexts)
        ])
        self.tau = tau
        self.threshold = threshold
        self.margin = margin
        self.persist = persist
        self.grace_switch = grace_switch
        self.grace_spawn = grace_spawn
        # Persisted with the weights: how many experts are in use and which is active.
        self.register_buffer("n_in_use", torch.tensor(1))
        self.register_buffer("active_index", torch.tensor(0))
        self.buffers = [ReplayBuffer(replay_capacity, seed=replay_seed + c)
                        for c in range(n_contexts)]
        self.running: list[float | None] = [None] * n_contexts
        self.established: list[bool] = [False] * n_contexts
        self.events: list[tuple[str, int, int]] = []
        self._preds: list[Tensor | None] = [None] * n_contexts
        self._predictor: int | None = None
        self._action: Tensor | None = None
        self._prev_obs: Tensor | None = None
        self._since = 0
        self._above = 0
        self._t = 0
        self._snapshot: tuple[dict, dict] | None = None
        self._streak = 0

    # ------------------------------------------------------------------
    # The active expert, as the kernel sees a WorldModel
    # ------------------------------------------------------------------

    @property
    def active(self) -> int:
        return int(self.active_index)

    @property
    def in_use(self) -> int:
        return int(self.n_in_use)

    @property
    def expert(self) -> WorldModel:
        return self.experts[self.active]

    @property
    def latent_state(self) -> Tensor:
        return self.expert.latent_state

    @property
    def _prior_latent(self) -> Tensor | None:
        return self.expert._prior_latent

    @_prior_latent.setter
    def _prior_latent(self, value: Tensor | None) -> None:
        self.expert._prior_latent = value

    @property
    def encoder(self) -> nn.Module:
        return self.expert.encoder

    @property
    def transition(self) -> nn.Module:
        return self.expert.transition

    @property
    def predictor(self) -> nn.Module:
        return self.expert.predictor

    @property
    def optimizer(self) -> torch.optim.Optimizer:
        return self.expert.optimizer

    @property
    def posterior_blend(self) -> float:
        return self.expert.posterior_blend

    @property
    def error_input(self) -> bool:
        return self.expert.error_input

    @property
    def temporal_dim(self) -> int:
        return 0

    def _transition_input(self, action: Tensor, temporal_feat: Tensor | None,
                          error: Tensor | None = None) -> Tensor:
        return self.expert._transition_input(action, temporal_feat, error)

    def encode(self, observation: Tensor) -> Tensor:
        return self.expert.encode(observation)

    def imagine(self, action_sequence: list[Tensor],
                temporal_feats: list[Tensor] | Tensor | None = None) -> list[Tensor]:
        return self.expert.imagine(action_sequence, temporal_feats)

    def imagine_grad(self, latent: Tensor, action: Tensor,
                     temporal_feat: Tensor | None = None) -> tuple[Tensor, Tensor]:
        return self.expert.imagine_grad(latent, action, temporal_feat)

    def disagreement(self, action: Tensor, temporal_feat: Tensor | None = None) -> float:
        return self.expert.disagreement(action, temporal_feat)

    # ------------------------------------------------------------------
    # One tick: predict -> update_from_error -> observe (the kernel's order)
    # ------------------------------------------------------------------

    def predict(self, action: Tensor, temporal_feat: Tensor | None = None) -> tuple[Tensor, Tensor]:
        """Every expert in use predicts from the executed action; returns the active one's."""
        if temporal_feat is not None:
            raise ValueError("ContextualWorldModel has no temporal features")
        self._action = action.detach().clone()
        out = None
        for c in range(self.in_use):
            pred, latent = self.experts[c].predict(action)
            self._preds[c] = pred.detach()
            if c == self.active:
                out = (pred, latent)
        self._predictor = self.active
        return out

    def update_from_error(self, error: Tensor) -> float:
        """Online step of the expert that made the prediction (its graph carries the error)."""
        c = self.active if self._predictor is None else self._predictor
        return self.experts[c].update_from_error(error)

    def observe(self, observation: Tensor) -> float:
        """Posterior step of every expert in use (only the predictor learns), store the
        transition in the predictor's buffer, then update the running errors and decide
        whether to switch or spawn."""
        obs = observation.detach()
        c0 = self.active if self._predictor is None else self._predictor
        loss = 0.0
        for c in range(self.in_use):
            value = self.experts[c].observe(observation, learn=(c == c0))
            if c == c0:
                loss = value
        if self._prev_obs is not None and self._action is not None:
            self.buffers[c0].add(self._prev_obs, self._action, obs)
            if self._snapshot is not None:
                self._streak += 1
        self._prev_obs = obs.clone()
        self._t += 1
        self._decide(obs)
        return loss

    # ------------------------------------------------------------------
    # Context inference
    # ------------------------------------------------------------------

    def _decide(self, obs: Tensor) -> None:
        n = self.in_use
        for c in range(n):
            p = self._preds[c]
            if p is None:
                continue
            e = float(torch.linalg.vector_norm(obs - p))
            r = self.running[c]
            self.running[c] = e if r is None else r + (e - r) / self.tau
            if self.running[c] <= self.threshold:
                self.established[c] = True
        self._since += 1
        a = self.active
        if self.running[a] is None:
            return
        if self.running[a] > self.threshold and self._snapshot is None and self.established[a]:
            self._snapshot = self._take(self.experts[a])
            self._streak = 0
        elif self.running[a] <= self.threshold and self._snapshot is not None:
            self._snapshot = None
        known = [c for c in range(n) if self.running[c] is not None]
        lo = min(self.running[c] for c in known)
        self._above = self._above + 1 if lo > self.threshold else 0
        best = min(known, key=lambda c: self.running[c])
        if (best != a and self._since >= self.grace_switch
                and self.running[best] < (1.0 - self.margin) * self.running[a]):
            self._hand_over(a, best)
            self.events.append(("switch", self._t, best))
        elif (self._above >= self.persist and self._since >= self.grace_spawn
              and self.established[a] and n < self.n_contexts):
            new = n
            dst, src = self.experts[new], self.experts[a]
            dst.load_state_dict(src.state_dict())
            dst.optimizer.load_state_dict(copy.deepcopy(src.optimizer.state_dict()))
            dst._prior_latent = None if src._prior_latent is None else src._prior_latent.detach().clone()
            dst._last_pred = None if src._last_pred is None else src._last_pred.clone()
            self.n_in_use.fill_(n + 1)
            self.running[new] = self.running[a]
            self._preds[new] = self._preds[a]
            self._hand_over(a, new)
            self.events.append(("spawn", self._t, new))

    def _hand_over(self, old: int, new: int) -> None:
        """Make `new` active; restore `old` to its pre-streak snapshot and move the
        streak's transitions to `new`."""
        if self._snapshot is not None:
            self._restore(self.experts[old], self._snapshot)
            for tr in self.buffers[old].take_last(self._streak):
                self.buffers[new].add(*tr)
        self._snapshot = None
        self._streak = 0
        self._above = 0
        self._since = 0
        self.active_index.fill_(new)

    @staticmethod
    def _take(wm: WorldModel) -> tuple[dict, dict]:
        params = {k: p.detach().clone() for k, p in wm.named_parameters()}
        return params, copy.deepcopy(wm.optimizer.state_dict())

    @staticmethod
    def _restore(wm: WorldModel, snap: tuple[dict, dict]) -> None:
        params, opt = snap
        with torch.no_grad():
            for k, p in wm.named_parameters():
                p.copy_(params[k])
        wm.optimizer.load_state_dict(opt)

    # ------------------------------------------------------------------
    # Sleep
    # ------------------------------------------------------------------

    def sleep(self, steps: int, seq_len: int, batch: int) -> float | None:
        """Replay each expert in use on its own buffer; `steps` split in proportion
        to the buffer sizes (largest remainder; buffers shorter than a window skip)."""
        sizes = [len(self.buffers[c]) if len(self.buffers[c]) >= seq_len else 0
                 for c in range(self.in_use)]
        total = sum(sizes)
        if total == 0:
            return None
        share = [steps * s // total for s in sizes]
        rest = sorted(range(len(sizes)), key=lambda c: -(steps * sizes[c] % total))
        for c in rest[: steps - sum(share)]:
            share[c] += 1
        loss = None
        for c, k in enumerate(share):
            if k:
                value = sleep_replay(self.experts[c], self.buffers[c], k, seq_len, batch)
                if c == self.active:
                    loss = value
        return loss

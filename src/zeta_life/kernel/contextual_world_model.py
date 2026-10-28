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
- ``snapshot_lag`` (§K10, 0 = off): the running error is an EMA, so it crosses the
  threshold a few ticks after the stream changed, and the snapshot taken then already
  holds the first steps learned on the new context (§K8/§K9: 4-24 ticks, and without
  sleep that damage is never repaired). With ``snapshot_lag = L`` the active expert is
  checkpointed at the end of every sleep, and every L ticks when it does not sleep,
  and the snapshot is the latest checkpoint at least L ticks old at the crossing:
  weights from before the change, as consolidated as they were then (online learning
  between two sleeps erodes what the sleep consolidated, so a checkpoint taken before a
  sleep would hold the eroded weights). Right after a change, with no checkpoint old
  enough yet, it falls back to the oldest one or to the current weights. ``restores``
  logs (tick of the restore, tick of the snapshot) for every restore.
- ``wake_lr_scale`` (§K11, 1 = off): the online (awake) steps of the learning expert use
  the optimizer's learning rate times this factor; sleep keeps the full rate. Online
  learning between two sleeps erodes what the sleep consolidated (§K10).
- ``wake_lr_scale_learning`` (§K12, None = off): the factor while an expert does not
  explain its stream -- not yet ESTABLISHED, or its running error above ``threshold``;
  ``wake_lr_scale`` then applies only while it is established and explains. One awake
  rate for all trades stability for plasticity (§K11: the slow wake keeps the
  consolidated experts and enters a never-lived world late). Learning fast while the
  established expert fails is protected by the snapshot: a spawn or a switch restores it.
- ``slow_return`` (§K13, False = off; needs ``wake_lr_scale_learning``): an established
  expert that becomes active again by a SWITCH learns awake at ``wake_lr_scale`` until it
  explains its stream or for at most ``persist`` ticks, then by the §K12 rule. Every expert
  predicts every tick, so the running error of an expert coming back carries the context
  it was not active in, and the switch is by margin, not by the threshold: under §K12 it
  came back "not explaining" and relearned at the full rate, which damaged it (home error
  x30) until the next sleep (§K12 mechanism). The cap: a wrong expert that comes back never
  explains, and without it it stayed slow until a spawn (``grace_spawn`` ticks).
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
from collections import deque
from contextlib import contextmanager

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
    wake_lr_scale : float
        Factor on the learning rate of the online (awake) steps; 1 = unchanged (§K11).
    wake_lr_scale_learning : float or None
        The factor while an expert does not explain its stream (not established, or
        running error above ``threshold``); None = ``wake_lr_scale`` (§K12).
    slow_return : bool
        An established expert made active by a switch learns awake at ``wake_lr_scale``
        until it explains its stream, for at most ``persist`` ticks (§K13); needs
        ``wake_lr_scale_learning``.
    snapshot_lag : int
        0 = the snapshot is taken when the running error crosses the threshold (§K6).
        L > 0 = checkpoint the active expert after every sleep and every L ticks without
        one, and restore the latest checkpoint at least L ticks old (§K10): weights from
        before the EMA's crossing lag.
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
        snapshot_lag: int = 0,
        wake_lr_scale: float = 1.0,
        wake_lr_scale_learning: float | None = None,
        slow_return: bool = False,
    ) -> None:
        super().__init__()
        if n_contexts < 1:
            raise ValueError(f"n_contexts must be >= 1, got {n_contexts}")
        if tau < 1.0 or not 0.0 <= margin < 1.0 or threshold <= 0.0:
            raise ValueError("need tau >= 1, 0 <= margin < 1 and threshold > 0")
        if snapshot_lag < 0:
            raise ValueError(f"snapshot_lag must be >= 0, got {snapshot_lag}")
        if not 0.0 < wake_lr_scale <= 1.0:
            raise ValueError(f"wake_lr_scale must be in (0, 1], got {wake_lr_scale}")
        if wake_lr_scale_learning is not None and not 0.0 < wake_lr_scale_learning <= 1.0:
            raise ValueError(f"wake_lr_scale_learning must be in (0, 1], got {wake_lr_scale_learning}")
        if slow_return and wake_lr_scale_learning is None:
            raise ValueError("slow_return needs wake_lr_scale_learning")
        self.wake_lr_scale = wake_lr_scale
        self.wake_lr_scale_learning = wake_lr_scale_learning
        self.slow_return = slow_return
        self._return_t: int | None = None
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
        self._snapshot_t: int | None = None
        self._streak = 0
        self.snapshot_lag = snapshot_lag
        self._ckpts: deque[tuple[int, tuple[dict, dict]]] = deque(maxlen=8)
        self.restores: list[tuple[int, int]] = []

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
        with self._despierto(c):
            return self.experts[c].update_from_error(error)

    def observe(self, observation: Tensor) -> float:
        """Posterior step of every expert in use (only the predictor learns), store the
        transition in the predictor's buffer, then update the running errors and decide
        whether to switch or spawn."""
        obs = observation.detach()
        c0 = self.active if self._predictor is None else self._predictor
        loss = 0.0
        for c in range(self.in_use):
            if c == c0:
                with self._despierto(c):
                    loss = self.experts[c].observe(observation, learn=True)
            else:
                self.experts[c].observe(observation, learn=False)
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
        if self._return_t is not None and (self._explica(a) or self._t - self._return_t >= self.persist):
            self._return_t = None
        if self.running[a] is None:
            return
        if self.snapshot_lag and (not self._ckpts or self._t - self._ckpts[-1][0] > self.snapshot_lag):
            self._checkpoint()
        if self.running[a] > self.threshold and self._snapshot is None and self.established[a]:
            previa = self._previa() if self.snapshot_lag else None
            if previa is None:
                self._snapshot_t, self._snapshot = self._t, self._take(self.experts[a])
            else:
                self._snapshot_t, self._snapshot = previa
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
            self._return_t = self._t if self.slow_return and self.established[best] else None
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
            self.restores.append((self._t, self._snapshot_t))
            for tr in self.buffers[old].take_last(self._streak):
                self.buffers[new].add(*tr)
        self._snapshot = None
        self._snapshot_t = None
        self._return_t = None
        self._ckpts.clear()
        self._streak = 0
        self._above = 0
        self._since = 0
        self.active_index.fill_(new)

    @contextmanager
    def _despierto(self, c: int):
        """Expert c's online learning rate: the optimizer's times wake_lr_scale, or times
        wake_lr_scale_learning while c does not explain its stream (not while it is the
        returning expert, with slow_return)."""
        aprende = (self.wake_lr_scale_learning is not None and not self._explica(c)
                   and not (self._return_t is not None and c == self.active))
        escala = self.wake_lr_scale_learning if aprende else self.wake_lr_scale
        if escala == 1.0:
            yield
            return
        wm = self.experts[c]
        base = [grupo["lr"] for grupo in wm.optimizer.param_groups]
        for grupo, lr in zip(wm.optimizer.param_groups, base):
            grupo["lr"] = lr * escala
        try:
            yield
        finally:
            for grupo, lr in zip(wm.optimizer.param_groups, base):
                grupo["lr"] = lr

    def _explica(self, c: int) -> bool:
        """Expert c is established and its running error is within the threshold."""
        r = self.running[c]
        return self.established[c] and r is not None and r <= self.threshold

    def _checkpoint(self) -> None:
        self._ckpts.append((self._t, self._take(self.experts[self.active])))

    def _previa(self) -> tuple[int, tuple[dict, dict]] | None:
        """The latest checkpoint at least snapshot_lag ticks old (else the oldest, else None)."""
        viejas = [c for c in self._ckpts if c[0] <= self._t - self.snapshot_lag]
        if viejas:
            return viejas[-1]
        return self._ckpts[0] if self._ckpts else None

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
        if self.snapshot_lag:
            self._checkpoint()
        return loss

"""Tests for the COIN-style contextual world model (wm_contexts, §K6 of docs/MUNDO_PROPIO.md)."""

from __future__ import annotations

import copy

import numpy as np
import pytest
import torch

from zeta_life.kernel import ConsciousKernel
from zeta_life.kernel.contextual_world_model import ContextualWorldModel
from zeta_life.kernel.replay import ReplayBuffer
from zeta_life.kernel.temporal_features import OscillatorBank


def _mover(s: torch.Tensor, a: torch.Tensor, k: int) -> torch.Tensor:
    s = (0.7 * s + 0.3 * torch.roll(a, k)).clamp(min=1e-6)
    return s / s.sum()


def _vivir(cwm: ContextualWorldModel, plan: list[tuple[int, int]], seed: int = 0, cada=None) -> None:
    """Drive the model the way the kernel does (predict -> update_from_error -> observe)
    on a babbled stream through the regimes of `plan` [(regime, ticks)]; `cada(cwm)` is
    called after every tick (the kernel's dream slot)."""
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    s = torch.full((4,), 0.25)
    for reg, n in plan:
        for _ in range(n):
            a = torch.tensor(rng.dirichlet(np.ones(4)), dtype=torch.float32)
            pred, _ = cwm.predict(a)
            s = _mover(s, a, reg)
            cwm.update_from_error(s - pred)
            cwm.observe(s)
            if cada is not None:
                cada(cwm)


def _copia(cwm: ContextualWorldModel) -> ContextualWorldModel:
    """Deep copy between ticks (the prior latents are non-leaf; they are only read detached)."""
    previos = [m._prior_latent for m in cwm.experts]
    for m in cwm.experts:
        m._prior_latent = None if m._prior_latent is None else m._prior_latent.detach()
    try:
        return copy.deepcopy(cwm)
    finally:
        for m, x in zip(cwm.experts, previos):
            m._prior_latent = x


class TestTakeLast:
    def test_removes_and_returns_oldest_first(self):
        rb = ReplayBuffer(capacity=20)
        for i in range(6):
            rb.add(torch.tensor([float(i)]), torch.tensor([0.0]), torch.tensor([i + 1.0]))
        out = rb.take_last(3)
        assert [float(o[0]) for o, _, _ in out] == [3.0, 4.0, 5.0]
        assert len(rb) == 3
        assert rb.take_last(10)[0][0].item() == 0.0 and len(rb) == 0
        assert rb.take_last(-1) == []


class TestContextInference:
    """With the error input (the configuration §K6 tests). Without it the expert's
    error hovers near the absolute threshold and spurious contexts appear (declared)."""

    def test_one_context_while_the_world_does_not_change(self):
        cwm = ContextualWorldModel(4, error_input=True)
        _vivir(cwm, [(0, 800)])
        assert cwm.in_use == 1 and cwm.events == []

    def test_spawns_on_a_new_regime_and_switches_back_on_a_known_one(self):
        cwm = ContextualWorldModel(4, error_input=True)
        _vivir(cwm, [(0, 600), (2, 600), (0, 300)])
        kinds = [(e[0], e[2]) for e in cwm.events]
        assert kinds[:2] == [("spawn", 1), ("switch", 0)]
        assert 600 < cwm.events[0][1] < 700 and 1200 < cwm.events[1][1] < 1260
        assert cwm.in_use == 2 and cwm.active == 0

    def test_inactive_expert_does_not_learn(self):
        cwm = ContextualWorldModel(4, error_input=True)
        _vivir(cwm, [(0, 600), (2, 400)])
        assert cwm.active == 1
        before = {k: p.detach().clone() for k, p in cwm.experts[0].named_parameters()}
        _vivir(cwm, [(2, 200)], seed=1)
        for k, p in cwm.experts[0].named_parameters():
            assert torch.equal(p, before[k]), k

    def test_spawn_restores_the_old_context_to_before_the_streak(self):
        cwm = ContextualWorldModel(4, error_input=True)
        _vivir(cwm, [(0, 600)])
        snap = {k: p.detach().clone() for k, p in cwm.experts[0].named_parameters()}
        _vivir(cwm, [(2, 300)], seed=1)
        assert cwm.in_use == 2
        # Between the last regime-0 tick and the snapshot the active expert still learned
        # a few ticks of regime 2 (until its running error crossed the threshold), so it
        # is close to -- not equal to -- its state at the change; but it must not have
        # learned the ~40 ticks of the streak.
        drift = max(float((p.detach() - snap[k]).abs().max()) for k, p in cwm.experts[0].named_parameters())
        moved = max(float((p.detach() - snap[k]).abs().max()) for k, p in cwm.experts[1].named_parameters())
        assert drift < moved

    @staticmethod
    def _pesos(cwm: ContextualWorldModel, c: int) -> dict:
        return {k: p.detach().clone() for k, p in cwm.experts[c].named_parameters()}

    def test_snapshot_lag_restores_weights_from_before_the_change(self):
        # §K10. Lag 0: the snapshot is taken when the EMA crosses the threshold, after the
        # change at tick 600. Lag 50, no sleep: the restored weights are exactly the
        # expert's at a tick before the change, at least 50 ticks before the restore's crossing.
        cwm0 = ContextualWorldModel(4, error_input=True)
        _vivir(cwm0, [(0, 600), (2, 300)])
        assert cwm0.restores and cwm0.restores[0][1] > 600
        cwm = ContextualWorldModel(4, error_input=True, snapshot_lag=50)
        pesos = {}
        _vivir(cwm, [(0, 600)], cada=lambda m: pesos.__setitem__(m._t, self._pesos(m, 0)))
        _vivir(cwm, [(2, 300)], seed=1)
        assert cwm.in_use == 2
        t_restore, t_foto = cwm.restores[0]
        assert t_foto <= 600 and t_foto in pesos
        for k, p in cwm.experts[0].named_parameters():
            assert torch.equal(p, pesos[t_foto][k]), k

    def test_snapshot_lag_with_sleep_restores_the_slept_weights(self):
        # With a sleep every 50 ticks the checkpoints are the weights right after each
        # sleep (online learning between sleeps erodes what the sleep consolidated).
        cwm = ContextualWorldModel(4, error_input=True, snapshot_lag=50)
        dormidos = {}

        def dormir(m):
            if m._t % 50 == 0:
                m.sleep(20, 8, 4)
                dormidos[m._t] = self._pesos(m, 0)

        _vivir(cwm, [(0, 600)], cada=dormir)
        _vivir(cwm, [(2, 300)], seed=1)
        assert cwm.in_use == 2
        t_foto = cwm.restores[0][1]
        assert t_foto <= 600 and t_foto in dormidos
        for k, p in cwm.experts[0].named_parameters():
            assert torch.equal(p, dormidos[t_foto][k]), k

    def test_snapshot_lag_must_be_non_negative(self):
        with pytest.raises(ValueError):
            ContextualWorldModel(4, snapshot_lag=-1)

    def test_wake_lr_scale_shrinks_the_online_step_and_restores_the_rate(self):
        # §K11: the awake steps use lr x scale; the optimizer's rate is back to its base
        # after the tick, so sleep keeps the full rate.
        deltas = {}
        for escala in (1.0, 0.1):
            torch.manual_seed(3)
            cwm = ContextualWorldModel(2, error_input=True, wake_lr_scale=escala)
            antes = {k: p.detach().clone() for k, p in cwm.experts[0].named_parameters()}
            _vivir(cwm, [(0, 1)])
            deltas[escala] = max(float((p.detach() - antes[k]).abs().max())
                                 for k, p in cwm.experts[0].named_parameters())
            assert all(grupo["lr"] == 0.005 for grupo in cwm.experts[0].optimizer.param_groups)
        assert 0.05 * deltas[1.0] < deltas[0.1] < 0.2 * deltas[1.0]

    @pytest.mark.parametrize("escala", [0.0, -0.5, 1.5])
    def test_wake_lr_scale_must_be_in_the_unit_interval(self, escala):
        with pytest.raises(ValueError):
            ContextualWorldModel(2, wake_lr_scale=escala)

    @staticmethod
    def _paso(cwm: ContextualWorldModel) -> float:
        antes = {k: p.detach().clone() for k, p in cwm.experts[cwm.active].named_parameters()}
        _vivir(cwm, [(0, 1)], seed=5)
        return max(float((p.detach() - antes[k]).abs().max())
                   for k, p in cwm.experts[cwm.active].named_parameters())

    def test_wake_lr_scale_learning_until_the_expert_explains_its_stream(self):
        # §K12: an expert learns awake at wake_lr_scale_learning (here the full rate) until
        # it is established and its running error is within the threshold, then at
        # wake_lr_scale; above the threshold again, at the full rate.
        def modelo(**kw) -> ContextualWorldModel:
            torch.manual_seed(3)
            return ContextualWorldModel(2, error_input=True, **kw)

        lleno = self._paso(modelo())
        assert self._paso(modelo(wake_lr_scale=0.1, wake_lr_scale_learning=1.0)) == lleno
        cwm = modelo(wake_lr_scale=0.1, wake_lr_scale_learning=1.0)
        cwm.established[0], cwm.running[0] = True, 0.0
        assert 0.05 * lleno < self._paso(cwm) < 0.2 * lleno
        cwm = modelo(wake_lr_scale=0.1, wake_lr_scale_learning=1.0)
        cwm.established[0], cwm.running[0] = True, 10.0
        assert self._paso(cwm) == lleno

    def test_wake_lr_scale_learning_none_is_byte_identical(self):
        pesos = []
        for kw in ({}, {"wake_lr_scale_learning": None}):
            torch.manual_seed(4)
            cwm = ContextualWorldModel(2, error_input=True, wake_lr_scale=0.1, **kw)
            _vivir(cwm, [(0, 200), (2, 100)])
            pesos.append([p.detach().clone() for p in cwm.experts[0].parameters()])
        assert all(torch.equal(a, b) for a, b in zip(*pesos))

    def test_wake_lr_scale_learning_home_slow_spawned_expert_fast(self):
        # The home expert explains its world and keeps the slow rate; the exile's expert
        # is born not established and learns at the full rate.
        torch.manual_seed(6)
        cwm = ContextualWorldModel(3, error_input=True, wake_lr_scale=0.1, wake_lr_scale_learning=1.0)
        _vivir(cwm, [(0, 600)])
        assert cwm._explica(0)
        _vivir(cwm, [(2, 60)])
        assert cwm.in_use == 2 and cwm.active == 1 and not cwm.established[1]
        rapido = self._paso(cwm)
        cwm.established[1], cwm.running[1] = True, 0.0
        assert self._paso(cwm) < 0.2 * rapido

    @pytest.mark.parametrize("escala", [0.0, -0.5, 1.5])
    def test_wake_lr_scale_learning_must_be_in_the_unit_interval(self, escala):
        with pytest.raises(ValueError):
            ContextualWorldModel(2, wake_lr_scale_learning=escala)

    @staticmethod
    def _hasta_volver(cwm: ContextualWorldModel) -> None:
        # Home (regime 0), an exile (regime 2) that spawns expert 1, then home until the
        # switch back to expert 0.
        _vivir(cwm, [(0, 600), (2, 600)])
        assert cwm.in_use == 2 and cwm.active == 1
        for t in range(400):
            _vivir(cwm, [(0, 1)], seed=100 + t)
            if cwm.active == 0:
                return
        raise AssertionError("no switch back to the home expert")

    def test_slow_return_the_returning_expert_learns_slow_until_it_explains(self):
        # §K13: an established expert made active by a switch learns awake at wake_lr_scale
        # while its running error (which carries the exile) is above the threshold; once it
        # explains, the §K12 rule again (above the threshold = the full rate).
        torch.manual_seed(7)
        cwm = ContextualWorldModel(3, error_input=True, wake_lr_scale=0.1, wake_lr_scale_learning=1.0,
                                   slow_return=True)
        self._hasta_volver(cwm)
        assert cwm._return_t is not None and cwm.established[0]
        cwm.running[0] = 10.0
        sin = _copia(cwm)
        sin._return_t = None
        lleno = self._paso(sin)
        assert 0.05 * lleno < self._paso(cwm) < 0.2 * lleno
        cwm.running[0] = 0.0
        _vivir(cwm, [(0, 1)], seed=9)
        assert cwm._return_t is None
        cwm.running[0] = 10.0
        sin = _copia(cwm)
        assert self._paso(cwm) == self._paso(sin) > 0.0

    def test_slow_return_lasts_at_most_persist_ticks(self):
        # A returning expert that does not explain is back on the §K12 rule after persist ticks.
        torch.manual_seed(7)
        cwm = ContextualWorldModel(3, error_input=True, wake_lr_scale=0.1, wake_lr_scale_learning=1.0,
                                   slow_return=True)
        self._hasta_volver(cwm)
        cwm.grace_switch = 10_000
        for t in range(cwm.persist):
            assert cwm._return_t is not None
            cwm.running[0] = 10.0
            _vivir(cwm, [(0, 1)], seed=200 + t)
        assert cwm._return_t is None

    def test_slow_return_false_is_byte_identical(self):
        pesos = []
        for kw in ({}, {"slow_return": False}, {"slow_return": True}):
            torch.manual_seed(7)
            cwm = ContextualWorldModel(2, error_input=True, wake_lr_scale=0.1, wake_lr_scale_learning=1.0, **kw)
            _vivir(cwm, [(0, 600), (2, 600), (0, 300)])
            assert ("switch", 0) in [(e[0], e[2]) for e in cwm.events]
            pesos.append([p.detach().clone() for p in cwm.parameters()])
        assert all(torch.equal(a, b) for a, b in zip(pesos[0], pesos[1]))
        assert not all(torch.equal(a, b) for a, b in zip(pesos[0], pesos[2]))

    def test_slow_return_a_spawn_is_not_a_return(self):
        torch.manual_seed(7)
        cwm = ContextualWorldModel(3, error_input=True, wake_lr_scale=0.1, wake_lr_scale_learning=1.0,
                                   slow_return=True)
        _vivir(cwm, [(0, 600), (2, 600)])
        assert ("spawn", 1) in [(e[0], e[2]) for e in cwm.events] and cwm._return_t is None

    def test_slow_return_needs_wake_lr_scale_learning(self):
        with pytest.raises(ValueError):
            ContextualWorldModel(2, slow_return=True)

    def test_streak_transitions_move_to_the_new_context(self):
        cwm = ContextualWorldModel(4, error_input=True)
        _vivir(cwm, [(0, 600), (2, 300)])
        n0, n1 = len(cwm.buffers[0]), len(cwm.buffers[1])
        assert n0 + n1 == 899
        assert 600 <= n0 < 640 and n1 > 260

    def test_slots_run_out_without_error(self):
        cwm = ContextualWorldModel(2, error_input=True)
        _vivir(cwm, [(0, 500), (1, 500), (2, 500)])
        assert cwm.in_use == 2


class TestSleepShare:
    def test_dose_is_split_by_buffer_size_and_sums_to_steps(self):
        cwm = ContextualWorldModel(3, error_input=True)
        _vivir(cwm, [(0, 600), (2, 300)])
        calls = []
        import zeta_life.kernel.contextual_world_model as mod
        orig = mod.sleep_replay
        try:
            mod.sleep_replay = lambda wm, buf, k, L, B: calls.append((len(buf), k)) or 0.0
            cwm.sleep(200, 16, 8)
        finally:
            mod.sleep_replay = orig
        assert sum(k for _, k in calls) == 200
        (n0, k0), (n1, k1) = calls
        assert abs(k0 / 200 - n0 / (n0 + n1)) < 0.01


class TestKernelIntegration:
    def _kernel(self, **kw) -> ConsciousKernel:
        return ConsciousKernel(obs_dim=4, action_mode="efe", preference=torch.tensor((0.7, 0.1, 0.1, 0.1)),
                               efe_n_samples=8, efe_obs_norm="l1", wm_error_input=True,
                               wm_sleep_replay=4, **kw)

    def test_off_is_the_single_world_model(self):
        torch.manual_seed(0)
        k = self._kernel()
        assert k.wm_contexts == 0 and k._sleep_replay is not None
        assert type(k.world_model).__name__ == "WorldModel"

    def test_runs_sleeps_and_spawns_in_a_life(self):
        torch.manual_seed(0)
        k = self._kernel(wm_contexts=3)
        assert k._sleep_replay is None
        rng = np.random.default_rng(0)
        s = torch.full((4,), 0.25)
        for t in range(1200):
            k.step(s)
            a = torch.tensor(rng.dirichlet(np.ones(4)), dtype=torch.float32)
            k.last_action = a
            s = _mover(s, a, 0 if t < 600 else 2)
        wm = k.world_model
        assert wm.in_use == 2 and wm.active == 1
        assert len(wm.buffers[0]) + len(wm.buffers[1]) == 1199

    def test_persistence_round_trip(self, tmp_path):
        torch.manual_seed(0)
        k = self._kernel(wm_contexts=3)
        rng = np.random.default_rng(0)
        s = torch.full((4,), 0.25)
        for t in range(900):
            k.step(s)
            a = torch.tensor(rng.dirichlet(np.ones(4)), dtype=torch.float32)
            k.last_action = a
            s = _mover(s, a, 0 if t < 600 else 2)
        k.save(str(tmp_path), "ctx")
        torch.manual_seed(5)
        k2 = self._kernel(wm_contexts=3)
        k2.load(str(tmp_path), "ctx")
        assert k2.world_model.in_use == k.world_model.in_use
        assert k2.world_model.active == k.world_model.active
        for (n, p), (_, q) in zip(k.world_model.named_parameters(), k2.world_model.named_parameters()):
            assert torch.equal(p, q), n

    @pytest.mark.parametrize("kw", [
        {"action_mode": "dreamer"},
        {"wm_disagreement_heads": 2},
        {"temporal_features": OscillatorBank.fourier(4)},
    ])
    def test_incompatible_configs_raise(self, kw):
        base = {"obs_dim": 4, "wm_contexts": 2}
        with pytest.raises(ValueError):
            ConsciousKernel(**{**base, **kw})

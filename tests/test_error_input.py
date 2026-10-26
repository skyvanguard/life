"""Tests for the world model's own prediction error as a transition input
(error_input / wm_error_input, §K3 of docs/MUNDO_PROPIO.md)."""

from __future__ import annotations

import pytest
import torch

from zeta_life.kernel import ConsciousKernel
from zeta_life.kernel.world_model import WorldModel


def _vida(k: ConsciousKernel, n: int, seed: int = 0) -> list[torch.Tensor]:
    """n steps on a simplex world the kernel's actions move; returns the actions."""
    torch.manual_seed(seed)
    s = torch.full((4,), 0.25)
    acts = []
    for _ in range(n):
        r = k.step(s)
        acts.append(r.action.detach().clone())
        s = (0.7 * s + 0.3 * torch.roll(r.action.detach(), 1)).clamp(min=1e-6)
        s = s / s.sum()
    return acts


class TestWorldModelErrorInput:
    def test_off_has_no_error_buffer_and_action_only_gru(self):
        wm = WorldModel(obs_dim=4, action_dim=4)
        assert not wm.error_input
        assert "last_error" not in wm.state_dict()
        assert wm.transition.input_size == 4

    def test_on_widens_the_gru_input(self):
        wm = WorldModel(obs_dim=4, action_dim=3, error_input=True)
        assert wm.transition.input_size == 3 + 4
        assert torch.equal(wm.last_error, torch.zeros(4))

    def test_observe_stores_observation_minus_prediction(self):
        torch.manual_seed(0)
        wm = WorldModel(obs_dim=4, error_input=True)
        pred, _ = wm.predict(torch.tensor([1.0, 0.0, 0.0, 0.0]))
        obs = torch.tensor([0.4, 0.3, 0.2, 0.1])
        wm.observe(obs)
        assert torch.allclose(wm.last_error, obs - pred.detach())

    def test_predict_feeds_the_stored_error(self):
        torch.manual_seed(1)
        wm = WorldModel(obs_dim=4, error_input=True)
        a = torch.tensor([0.1, 0.2, 0.3, 0.4])
        wm.predict(a)
        wm.observe(torch.tensor([0.25, 0.25, 0.25, 0.25]))
        z, e = wm.latent_state.clone(), wm.last_error.clone()
        with torch.no_grad():
            want = wm.predictor(wm.transition(torch.cat([a, e]).unsqueeze(0), z.unsqueeze(0)))[0]
        pred, _ = wm.predict(a)
        assert torch.allclose(pred.detach(), want)

    def test_imagine_uses_zero_error_and_keeps_state(self):
        torch.manual_seed(2)
        wm = WorldModel(obs_dim=4, error_input=True)
        wm.predict(torch.rand(4))
        wm.observe(torch.rand(4))
        z, e = wm.latent_state.clone(), wm.last_error.clone()
        a = torch.tensor([0.0, 1.0, 0.0, 0.0])
        out = wm.imagine([a])[0]
        with torch.no_grad():
            want = wm.predictor(wm.transition(torch.cat([a, torch.zeros(4)]).unsqueeze(0),
                                              z.unsqueeze(0)))[0]
        assert torch.allclose(out, want)
        assert torch.equal(wm.latent_state, z) and torch.equal(wm.last_error, e)

    def test_batched_paths_accept_the_extra_input(self):
        wm = WorldModel(obs_dim=4, error_input=True, dynamics_ensemble=2)
        z, p = wm.imagine_grad(torch.zeros(5, 32), torch.rand(5, 4))
        assert z.shape == (5, 32) and p.shape == (5, 4)
        wm.predict(torch.rand(4))
        wm.observe(torch.rand(4))
        assert wm.disagreement(torch.rand(4)) >= 0.0


class TestKernelErrorInput:
    def test_off_is_identical(self):
        torch.manual_seed(3)
        a = ConsciousKernel()
        torch.manual_seed(3)
        b = ConsciousKernel(wm_error_input=False)
        for x, y in zip(_vida(a, 80), _vida(b, 80)):
            assert torch.equal(x, y)

    def test_on_tracks_the_lived_error(self):
        torch.manual_seed(4)
        k = ConsciousKernel(wm_error_input=True)
        s = torch.full((4,), 0.25)
        k.step(s)
        assert float(k.world_model.last_error.abs().sum()) > 0.0

    def test_with_sleep_replay_lowers_replay_loss(self):
        k = ConsciousKernel(wm_error_input=True, wm_sleep_replay=1, wm_sleep_seq_len=8,
                            dream_interval=10_000)
        _vida(k, 200)
        first = k._sleep_world_model()
        for _ in range(40):
            last = k._sleep_world_model()
        assert first is not None and last < first

    def test_efe_kernel_runs_with_error_input(self):
        k = ConsciousKernel(wm_error_input=True, action_mode="efe",
                            preference=torch.tensor([0.7, 0.1, 0.1, 0.1]),
                            efe_n_samples=8, efe_obs_norm="l1", wm_sleep_replay=2,
                            dream_interval=20)
        acts = _vida(k, 45)
        assert all(torch.isfinite(a).all() for a in acts)

    def test_rssm_with_error_input_raises(self):
        with pytest.raises(ValueError):
            ConsciousKernel(wm_error_input=True, world_model_type="rssm")

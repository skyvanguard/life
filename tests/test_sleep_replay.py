"""Tests for the world model's sleep replay (wm_sleep_replay, §K2 of docs/MUNDO_PROPIO.md)."""

from __future__ import annotations

import pytest
import torch

from zeta_life.kernel import ConsciousKernel
from zeta_life.kernel.replay import ReplayBuffer
from zeta_life.kernel.temporal_features import OscillatorBank


def _vida(k: ConsciousKernel, n: int, seed: int = 0) -> list[torch.Tensor]:
    """n steps on a simplex world the kernel's actions move; returns the actions."""
    torch.manual_seed(seed)
    s = torch.full((4,), 0.25)
    acts = []
    for _ in range(n):
        r = k.step(s)
        acts.append(r.action.detach().clone())
        s = (0.7 * s + 0.3 * r.action.detach()).clamp(min=1e-6)
        s = s / s.sum()
    return acts


class TestSampleSequences:
    def test_windows_are_consecutive(self):
        rb = ReplayBuffer(capacity=50)
        for i in range(30):
            rb.add(torch.tensor([float(i)]), torch.tensor([-float(i)]), torch.tensor([i + 1.0]))
        obs, act, nxt = rb.sample_sequences(6, 5)
        assert obs.shape == (6, 5, 1) and act.shape == (6, 5, 1) and nxt.shape == (6, 5, 1)
        start = obs[:, :1, 0]
        assert torch.equal(obs[:, :, 0], start + torch.arange(5.0))
        assert torch.equal(act[:, :, 0], -obs[:, :, 0])
        assert torch.equal(nxt[:, :, 0], obs[:, :, 0] + 1)

    def test_windows_stay_inside_after_capacity_drop(self):
        rb = ReplayBuffer(capacity=10)
        for i in range(25):
            rb.add(torch.tensor([float(i)]), torch.tensor([0.0]), torch.tensor([i + 1.0]))
        obs, _, _ = rb.sample_sequences(40, 10)
        assert torch.equal(obs[:, :, 0], torch.arange(15.0, 25.0).expand(40, 10))

    def test_too_long_raises(self):
        rb = ReplayBuffer(capacity=10)
        for _ in range(3):
            rb.add(torch.rand(2), torch.rand(2), torch.rand(2))
        with pytest.raises(ValueError):
            rb.sample_sequences(2, 4)
        with pytest.raises(ValueError):
            rb.sample_sequences(2, 0)


class TestKernelSleepReplay:
    def test_off_has_no_buffer_and_is_identical(self):
        torch.manual_seed(1)
        a = ConsciousKernel()
        torch.manual_seed(1)
        b = ConsciousKernel(wm_sleep_replay=0)
        assert a._sleep_replay is None and b._sleep_replay is None
        for x, y in zip(_vida(a, 120), _vida(b, 120)):
            assert torch.equal(x, y)

    def test_on_acts_only_on_sleep_ticks(self):
        """Same seed: identical to the kernel without replay until the first sleep tick."""
        torch.manual_seed(2)
        a = ConsciousKernel(dream_interval=50)
        torch.manual_seed(2)
        b = ConsciousKernel(dream_interval=50, wm_sleep_replay=5)
        acts_a, acts_b = _vida(a, 50), _vida(b, 50)
        assert all(torch.equal(x, y) for x, y in zip(acts_a, acts_b))
        assert len(b._sleep_replay) == 49
        pa = torch.cat([p.flatten() for p in a.world_model.parameters()])
        pb = torch.cat([p.flatten() for p in b.world_model.parameters()])
        assert not torch.equal(pa, pb)  # the sleep at t = 50 trained b's world model

    def test_transitions_recorded_are_the_lived_ones(self):
        k = ConsciousKernel(wm_sleep_replay=1, dream_interval=1000)
        _vida(k, 20)
        obs, act, nxt = k._sleep_replay.sample_sequences(4, 19)
        assert torch.allclose(nxt[:, :-1], obs[:, 1:])  # next obs of one tick = obs of the next
        assert torch.allclose(act.sum(dim=-1), torch.ones(4, 19), atol=1e-5)

    def test_sleep_lowers_replay_loss(self):
        k = ConsciousKernel(wm_sleep_replay=1, wm_sleep_seq_len=8, dream_interval=10_000)
        _vida(k, 200)
        first = k._sleep_world_model()
        for _ in range(40):
            last = k._sleep_world_model()
        assert first is not None and last < first

    def test_not_enough_transitions_returns_none(self):
        k = ConsciousKernel(wm_sleep_replay=1, wm_sleep_seq_len=16, dream_interval=10_000)
        _vida(k, 5)
        assert k._sleep_world_model() is None

    def test_invalid_configs_raise(self):
        with pytest.raises(ValueError):
            ConsciousKernel(wm_sleep_replay=2, wm_sleep_seq_len=0)
        with pytest.raises(ValueError):
            ConsciousKernel(wm_sleep_replay=2, wm_sleep_batch=0)
        with pytest.raises(ValueError):
            ConsciousKernel(wm_sleep_replay=2, temporal_features=OscillatorBank.fourier(4))

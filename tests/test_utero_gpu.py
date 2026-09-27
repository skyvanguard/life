"""Tests del motor por lotes (utero/gpu.py). Corren en CPU (device="cpu") para no exigir GPU:
el VM vectorizado debe dar EXACTAMENTE lo mismo que nivel2.execute, y la sopa debe ser la de
UteroCreciente. El orden en damero es otra encarnación y se valida por experimento, no aquí."""

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from zeta_life.utero.creciente import UteroCreciente  # noqa: E402
from zeta_life.utero.gpu import M_REG, UteroGPU, vm  # noqa: E402
from zeta_life.utero.nivel2 import K, execute  # noqa: E402

SOL = np.full((1, 10), 0.3)


def _caso(rng, total: bool, frozen: bool, n_mundos: int = 120):
    code = np.zeros((n_mundos, 3, K, 4), dtype=np.int64)
    code[..., 0] = rng.integers(0, 10, size=(n_mundos, 3, K))
    code[..., 1:] = rng.integers(0, 16, size=(n_mundos, 3, K, 3))
    v = rng.uniform(0, 1, size=(n_mundos, 3))
    mem = rng.uniform(-3, 3, size=n_mundos)
    S = rng.uniform(-1, 1, size=(n_mundos, 2))
    viva = rng.random(size=(n_mundos, 3)) < 0.7
    viva[:, 1] = True
    vac = 0.3
    dt = torch.float64
    c = torch.as_tensor(code)
    al = torch.as_tensor(viva)
    vt = torch.as_tensor(v, dtype=dt)
    al_l = torch.roll(al, 1, dims=1)
    al_l[:, 0] = False
    al_r = torch.roll(al, -1, dims=1)
    al_r[:, -1] = False
    v_l = torch.roll(vt, 1, dims=1)
    v_r = torch.roll(vt, -1, dims=1)
    vl = torch.where(al_l, v_l, torch.full_like(vt, vac))
    vr = torch.where(al_r, v_r, torch.full_like(vt, vac))
    code_l = torch.roll(c, 1, dims=1)
    code_r = torch.roll(c, -1, dims=1)
    memt = torch.as_tensor(mem, dtype=dt).unsqueeze(1).expand(-1, 3)
    St = torch.as_tensor(S, dtype=dt).unsqueeze(1).expand(-1, 3, -1)
    r = torch.stack([vl, vt, vr, memt, St[..., 0], St[..., 1]], dim=-1).unsqueeze(0)
    assert r.shape[-1] == M_REG
    o = vm(c, r, code_l, code_r, al_l, al_r, torch.full((n_mundos, 1), total), torch.full((n_mundos, 1), frozen))
    for w in range(n_mundos):
        ctx = (code[w, 0] if viva[w, 0] else None, code[w, 1], code[w, 2] if viva[w, 2] else None)
        xtra = [float(S[w, 0]), float(S[w, 1])]
        out, own, spawn, raw = execute(code[w, 1], float(v[w, 0]) if viva[w, 0] else vac, float(v[w, 1]),
                                       float(v[w, 2]) if viva[w, 2] else vac, ctx, wrap=True,
                                       r3_init=float(mem[w]), extra=xtra, total=total, frozen=frozen)
        rf = o["r"][0, w, 1].numpy()
        assert rf[3] == raw, (w, rf[3], raw)
        assert (rf[3] % 1.0) == out
        assert rf[4] == xtra[0] and rf[5] == xtra[1]
        np.testing.assert_array_equal(o["own"][w, 1].numpy(), own)
        assert bool(o["has_spawn"][w, 1]) == (spawn is not None)
        if spawn is not None:
            side, pos, nuevo, _locus = spawn
            assert int(o["side"][w, 1]) == side and int(o["mpos"][w, 1]) == pos
            if total:
                np.testing.assert_array_equal(o["nuevo"][w, 1].numpy(), np.asarray(nuevo))
            else:
                assert int(o["nuevo"][w, 1, 0]) == nuevo


@pytest.mark.parametrize("total,frozen", [(False, False), (True, False), (False, True), (True, True)])
def test_vm_matches_cpu_execute_exactly(total, frozen):
    _caso(np.random.default_rng(7 + 2 * total + frozen), total, frozen)


def test_soup_matches_utero_creciente():
    for seed in (0, 13):
        cpu = UteroCreciente(n0=32, seed=seed, max_n=32, germinal=True, toroidal=True, parametros=0.05)
        g = UteroGPU([seed], 32, SOL, device="cpu", parametros=0.05)
        np.testing.assert_array_equal(g.code[0].numpy(), cpu.code)
        np.testing.assert_array_equal(g.v[0].numpy(), cpu.v)
        np.testing.assert_array_equal(g.theta[0].numpy(), cpu.theta)


def test_runs_closed_finite_and_frozen_world_never_mints():
    sol = np.tile(np.linspace(0.1, 0.5, 300), (2, 1))
    g = UteroGPU([3, 3], 64, sol, device="cpu", congelado=[True, False], escritura_total=True,
                 parametros=0.05, escala=True, reflejo=0.05, theta_fijo=[True, False])
    inicial = {g.code[0, i].numpy().tobytes() for i in range(64)}
    ser = g.correr(300)
    assert g.v.shape == (2, 64) and ser["vivas"].shape == (300, 2)
    assert torch.isfinite(g.v).all() and torch.isfinite(g.e).all()
    vivos = {g.code[0, i].numpy().tobytes() for i in range(64) if bool(g.alive[0, i])}
    assert vivos <= inicial                                  # mundo congelado: ningún genoma nuevo
    assert float(g.esc[0].min()) == 1.0 and float(g.g[0].abs().max()) == 0.0   # perillas fijas
    assert (ser["partos"].sum(axis=0) > 0).all()


def test_same_seed_same_run():
    sol = np.tile(np.linspace(0.1, 0.5, 120), (1, 1))
    a = UteroGPU([5], 48, sol, device="cpu", escritura_total=True, parametros=0.05, escala=True)
    b = UteroGPU([5], 48, sol, device="cpu", escritura_total=True, parametros=0.05, escala=True)
    a.correr(120)
    b.correr(120)
    assert torch.equal(a.code, b.code) and torch.equal(a.v, b.v)


def test_checkpoint_resume_is_identical_to_an_uninterrupted_run(tmp_path):
    sol = np.tile(np.linspace(0.1, 0.5, 200), (2, 1))
    kw = dict(device="cpu", escritura_total=True, parametros=0.05, escala=True, reflejo=0.05)
    entera = UteroGPU([5, 6], 48, sol, **kw)
    ref = entera.correr(200)
    ck = tmp_path / "ck.pt"
    a = UteroGPU([5, 6], 48, sol, **kw)
    a.correr(200, checkpoint=str(ck), cada=60)            # deja el punto de control del tick 180
    assert ck.exists()
    b = UteroGPU([5, 6], 48, sol, **kw)                   # proceso nuevo: reanuda desde el disco
    rea = b.correr(200, checkpoint=str(ck), cada=60)
    assert torch.equal(b.code, entera.code) and torch.equal(b.v, entera.v) and torch.equal(b.e, entera.e)
    for k in ref:
        np.testing.assert_array_equal(rea[k], ref[k])


def test_ultraestable_off_is_identical_and_gate_follows_the_energy_trend():
    sol = np.tile(np.full(150, 0.6), (3, 1))
    kw = dict(device="cpu", escritura_total=True, germinal=False, luz_finita=400.0)   # luz de sobra: la energía sólo sube
    base = UteroGPU([7], 48, sol[:1], **kw)
    apag = UteroGPU([7], 48, sol[:1], ultraestable=0, **kw)
    base.correr(150)
    apag.correr(150)
    assert torch.equal(base.code, apag.code) and torch.equal(base.v, apag.v)
    g = UteroGPU([7, 7, 7], 48, sol, ultraestable=[1, -1, 0], **kw)
    inicial = {g.code[0, i].numpy().tobytes() for i in range(48)}
    g.correr(150)

    def vivos(w):
        return {g.code[w, i].numpy().tobytes() for i in range(48) if bool(g.alive[w, i])}

    assert vivos(0) <= inicial               # le va bien -> conserva su regla: ningún genoma nuevo
    assert not (vivos(1) <= inicial)         # invertido: reescribe justo cuando le va bien
    assert not (vivos(2) <= inicial)         # apagado: reescribe siempre


def test_cortar_empties_the_block_and_the_tissue_can_regrow_into_it():
    sol = np.tile(np.full(400, 0.6), (2, 1))
    g = UteroGPU([3, 4], 64, sol, device="cpu", luz_finita=40.0, escritura_total=True)
    g.correr(50)
    g.cortar(20, 40)
    assert not bool(g.alive[:, 20:40].any())
    assert float(g.e[:, 20:40].abs().sum()) == 0.0
    g.correr(350)
    assert int(g.alive[:, 20:40].sum()) > 0          # el tejido vuelve a ocupar el tramo cortado

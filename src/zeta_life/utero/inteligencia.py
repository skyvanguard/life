"""
Las varas de inteligencia (docs/PLAN_INTELIGENCIA.md): regulación,
anticipación y aprendizaje por recurrencia, medidas sobre las series internas
de un tejido que vive bajo un sol, siempre contra un nulo.

Todo se calcula con permutaciones (numpy), sin librerías de estadística, y
cada función devuelve el estadístico, su p empírico y lo que usó como nulo.
"""

from __future__ import annotations

import numpy as np

from zeta_life.utero.creciente import MAX_N, N0, UteroCreciente

ACTIVIDAD_W = 100          # ventana de respuesta al inicio de una estación
TRANSITORIO = 150          # ticks tras el inicio que se excluyen de la anticipación
W_ANT = 50                 # media-ventana alrededor del instante esperado
MIN_PREVIAS = 5            # estaciones vistas antes de "esperar" algo


# ----------------------------------------------------------------- series
def correr_series(seed: int, flags: dict, sol, ticks: int, shadow: list | None = None,
                  fabrica=None, n0: int = N0, max_n: int = MAX_N) -> dict:
    """Correr y devolver las series internas por tick que usan las varas:
    vivas, muertes, reescrituras (genoma cambió), nacimientos, novedad cruda,
    materia media del interior (ambos vecinos vivos) y del borde (linda con
    vacío), y la actividad = (reescrituras + muertes + nacimientos) / vivas."""
    if fabrica is not None:
        u = fabrica(seed, shadow, sol=sol, **flags)
    else:
        u = UteroCreciente(n0=n0, seed=seed, max_n=max_n, germinal=True, toroidal=True,
                           log_events=True, shadow_deaths=shadow, sol=sol, **flags)
    seen: set = set(u.seen)
    prev: dict = {}
    keys = ("vivas", "muertes", "reescrituras", "nacimientos", "novedad", "v_int", "v_borde",
            "n_borde", "actividad")
    out = {k: np.zeros(ticks) for k in keys}
    for t in range(ticks):
        m = u.step()
        cg = u.genomas()
        rew = sum(1 for c, g in cg.items() if c in prev and prev[c] != g)
        new = 0
        for g in cg.values():
            if g not in seen:
                seen.add(g)
                new += 1
        prev = cg
        alive = u.alive
        idx = np.flatnonzero(alive)
        n = len(idx)
        if n:
            left_ok = np.zeros(n, dtype=bool)
            right_ok = np.zeros(n, dtype=bool)
            left_ok[idx > 0] = alive[idx[idx > 0] - 1]
            right_ok[idx < u.n - 1] = alive[idx[idx < u.n - 1] + 1]
            interior = left_ok & right_ok
            v = u.v[idx]
            out["v_int"][t] = v[interior].mean() if interior.any() else np.nan
            out["v_borde"][t] = v[~interior].mean() if (~interior).any() else np.nan
            out["n_borde"][t] = int((~interior).sum())
        else:
            out["v_int"][t] = out["v_borde"][t] = np.nan
        births = m["colonized"] + m.get("invaded", 0) + m.get("grown", 0)
        out["vivas"][t] = n
        out["muertes"][t] = m["deaths"]
        out["reescrituras"][t] = rew
        out["nacimientos"][t] = births
        out["novedad"][t] = new
        out["actividad"][t] = (rew + m["deaths"] + births) / max(n, 1)
    return out


# ------------------------------------------------------------- regulación
def regulacion(series_sol: dict, series_sin: dict, sol, maduro: tuple) -> dict:
    """¿El tejido se sostiene y amortigua? vivas (mediana, maduro) con y sin
    sol; amortiguación = var(materia interior) / var(sol) en maduro; acople del
    borde = corr(materia de borde, sol)."""
    a, b = maduro
    s = sol.serie[a:b]
    vi = series_sol["v_int"][a:b]
    vb = series_sol["v_borde"][a:b]
    ok_i, ok_b = ~np.isnan(vi), ~np.isnan(vb)
    amort = float(np.var(vi[ok_i]) / max(np.var(s), 1e-12)) if ok_i.sum() > 10 else float("nan")
    acople = float(np.corrcoef(vb[ok_b], s[ok_b])[0, 1]) if ok_b.sum() > 10 else float("nan")
    return dict(vivas_sol=float(np.median(series_sol["vivas"][a:b])),
                vivas_sin=float(np.median(series_sin["vivas"][a:b])),
                novedad_sol=float(series_sol["novedad"][a:b].sum()),
                novedad_sin=float(series_sin["novedad"][a:b].sum()),
                amortiguacion=amort, acople_borde=acople)


# ----------------------------------------------------------- anticipación
def _ventana_segura(ini: int, fin: int, esperado: int) -> tuple | None:
    """Intervalo dentro de la estación donde se puede colocar una ventana de
    2·W_ANT sin tocar el transitorio del inicio ni el instante esperado ni el
    final real. Devuelve (lo, hi) de centros válidos para el nulo, o None."""
    lo = ini + TRANSITORIO + W_ANT
    hi = min(esperado - 3 * W_ANT, fin - W_ANT)
    return (lo, hi) if hi > lo + 10 else None


def anticipacion(actividad: np.ndarray, sol, rng_seed: int = 0, n_perm: int = 500) -> dict:
    """En estaciones LARGAS (el cambio real llegó al menos 2·W_ANT ticks después
    del instante esperado = inicio + mediana de las duraciones ya vistas), ¿hay
    un exceso de actividad alrededor de ese instante esperado, sin que el sol
    haya cambiado? Estadístico = media sobre estaciones largas de
    [actividad en el esperado ± W] − [actividad en una ventana de control
    anterior en la misma estación]. Nulo: el mismo estadístico con el instante
    esperado reubicado al azar en la zona segura de cada estación."""
    rng = np.random.default_rng(rng_seed)
    est = sol.estaciones[:-1]
    eventos = []
    for k, (nombre, ini, fin) in enumerate(est):
        if k < MIN_PREVIAS:
            continue
        previas = [f - i for _, i, f in est[:k]]
        esperado = ini + int(np.median(previas))
        if fin - esperado < 2 * W_ANT:          # el cambio real llegó >= 100 ticks DESPUÉS
            continue                            # del instante esperado: estación "larga"
        seg = _ventana_segura(ini, fin, esperado)
        if seg is None:
            continue
        eventos.append((ini, fin, esperado, seg))
    if len(eventos) < 3:
        return dict(n=len(eventos), estadistico=float("nan"), p=float("nan"), nulo=None)

    def score(centros):
        vals = []
        for (ini, fin, esperado, seg), c in zip(eventos, centros):
            ctrl = actividad[c - 3 * W_ANT:c - W_ANT]
            obj = actividad[c - W_ANT:c + W_ANT]
            vals.append(obj.mean() - ctrl.mean())
        return float(np.mean(vals))

    real = score([e[2] for e in eventos])
    nulo = np.array([score([int(rng.integers(lo, hi)) for (_, _, _, (lo, hi)) in eventos])
                     for _ in range(n_perm)])
    p = float((np.sum(nulo >= real) + 1) / (n_perm + 1))
    return dict(n=len(eventos), estadistico=real, p=p,
                nulo=(float(nulo.mean()), float(nulo.std())))


# ------------------------------------------- aprendizaje por recurrencia
def aprendizaje(actividad: np.ndarray, sol, rng_seed: int = 0, n_perm: int = 2000) -> dict:
    """¿La respuesta a una estación cambia con la repetición? Respuesta_k =
    actividad media en los ACTIVIDAD_W ticks tras el inicio de la k-ésima
    ocurrencia del régimen, menos la media de los ACTIVIDAD_W previos.
    Estadístico = Spearman(k, respuesta_k) promediado sobre regímenes. Nulo:
    permutar el orden de las ocurrencias. Negativo = habituación."""
    rng = np.random.default_rng(rng_seed)
    por_regimen: dict = {}
    for nombre, ini, fin in sol.estaciones[1:-1]:
        if ini - ACTIVIDAD_W < 0 or ini + ACTIVIDAD_W > len(actividad):
            continue
        resp = actividad[ini:ini + ACTIVIDAD_W].mean() - actividad[ini - ACTIVIDAD_W:ini].mean()
        por_regimen.setdefault(nombre, []).append(resp)

    def spearman(x, y):
        rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
        if rx.std() == 0 or ry.std() == 0:
            return 0.0
        return float(np.corrcoef(rx, ry)[0, 1])

    rhos, nulos = {}, []
    for nombre, resps in por_regimen.items():
        if len(resps) < 4:
            continue
        k = np.arange(len(resps))
        rhos[nombre] = spearman(k, np.array(resps))
    if not rhos:
        return dict(n=0, rho=float("nan"), p=float("nan"), por_regimen={})
    real = float(np.mean(list(rhos.values())))
    for _ in range(n_perm):
        vals = []
        for nombre, resps in por_regimen.items():
            if len(resps) < 4:
                continue
            r = np.array(resps)
            rng.shuffle(r)
            vals.append(spearman(np.arange(len(r)), r))
        nulos.append(np.mean(vals))
    nulos = np.array(nulos)
    p = float((np.sum(np.abs(nulos) >= abs(real)) + 1) / (n_perm + 1))
    return dict(n=sum(len(v) for v in por_regimen.values()), rho=real, p=p, por_regimen=rhos)

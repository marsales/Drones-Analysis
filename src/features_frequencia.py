# -*- coding: utf-8 -*-
"""Características no domínio da frequência.

Convenções (decisão D8):
- média removida da janela antes da FFT;
- janela de Hann;
- espectro de amplitude unilateral normalizado A(f) = 2·|X(f)| / Σw[n]
  (sem o fator 2 em DC e em Nyquist), de modo que uma senoide de amplitude A
  apareça com altura ≈ A;
- potências por banda calculadas sobre a PSD unilateral
  (scipy.signal.periodogram, window='hann', detrend='constant',
  scaling='density'), integradas na banda pela regra do trapézio.
"""

import numpy as np
from scipy import signal

FS = 10_000  # Hz

# Bandas de frequência (Hz) — definidas após inspeção dos espectros médios
# (CHECKPOINT 3): a região 200–600 Hz concentra os harmônicos que mais
# diferenciam as condições e por isso ficou numa banda própria.
BANDAS = {
    "B1_0_200": (0.0, 200.0),
    "B2_200_600": (200.0, 600.0),
    "B3_600_1000": (600.0, 1000.0),
    "B4_1000_2500": (1000.0, 2500.0),
    "B5_2500_5000": (2500.0, 5000.0),
}


def espectro_amplitude(x, fs=FS):
    """Espectro de amplitude unilateral de uma janela, com Hann e média removida.

    Retorna (f, A): frequências em Hz e amplitudes em u.a.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    w = signal.windows.hann(n)
    xw = (x - x.mean()) * w
    X = np.fft.rfft(xw)
    A = np.abs(X) / w.sum()
    A[1:] *= 2.0
    if n % 2 == 0:  # bin de Nyquist existe e não é duplicado
        A[-1] /= 2.0
    f = np.fft.rfftfreq(n, d=1.0 / fs)
    return f, A


def psd(x, fs=FS):
    """PSD unilateral (u.a.²/Hz) com Hann e remoção da média."""
    f, p = signal.periodogram(
        np.asarray(x, dtype=float),
        fs=fs,
        window="hann",
        detrend="constant",
        scaling="density",
    )
    return f, p


def features_frequencia(x, fs=FS, bandas=BANDAS):
    """Características espectrais de uma janela x.

    Retorna: freq_dominante [Hz], mag_pico_dominante [u.a.], potência total e
    por banda [u.a.²] (+ frações), centroide espectral [Hz] e entropia
    espectral normalizada [0–1].
    """
    f_a, A = espectro_amplitude(x, fs=fs)
    # frequência dominante: argmax da amplitude, excluindo DC (bin 0)
    k = 1 + int(np.argmax(A[1:]))
    out = {"freq_dominante": f_a[k], "mag_pico_dominante": A[k]}

    f_p, P = psd(x, fs=fs)
    pot_total = np.trapezoid(P, f_p)
    out["potencia_total"] = pot_total
    for nome, (f1, f2) in bandas.items():
        sel = (f_p >= f1) & (f_p < f2)
        pot = np.trapezoid(P[sel], f_p[sel]) if sel.sum() > 1 else 0.0
        out[f"pot_{nome}"] = pot
        out[f"frac_{nome}"] = pot / pot_total if pot_total > 0 else np.nan

    soma_p = P.sum()
    out["centroide_espectral"] = float((f_p * P).sum() / soma_p) if soma_p > 0 else np.nan

    # entropia espectral normalizada: −Σ p·log2(p) / log2(K), p = P/ΣP
    p_norm = P[P > 0] / soma_p
    out["entropia_espectral"] = float(-(p_norm * np.log2(p_norm)).sum() / np.log2(P.size))
    return out

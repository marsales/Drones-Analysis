# -*- coding: utf-8 -*-
"""Características no domínio do tempo, calculadas sobre o sinal bruto de cada janela.

Convenções:
- desvio padrão populacional (ddof = 0);
- curtose de Pearson (não excedente): vale 3 para um sinal gaussiano;
- unidades: u.a. (unidade do piezo não documentada), u.a.² para potência.
"""

import numpy as np
from scipy import stats


def features_tempo(x):
    """Calcula as características temporais de uma janela x (1D).

    Retorna um dicionário: media, rms, potencia_media, desvio_padrao,
    pico_absoluto, pico_a_pico, fator_crista, curtose, assimetria.
    """
    x = np.asarray(x, dtype=float)
    media = x.mean()
    potencia = np.mean(x**2)
    rms = np.sqrt(potencia)
    desvio = x.std(ddof=0)
    pico = np.max(np.abs(x))
    return {
        "media": media,
        "rms": rms,
        "potencia_media": potencia,
        "desvio_padrao": desvio,
        "pico_absoluto": pico,
        "pico_a_pico": x.max() - x.min(),
        "fator_crista": pico / rms if rms > 0 else np.nan,
        "curtose": stats.kurtosis(x, fisher=False),  # Pearson: gaussiana = 3
        "assimetria": stats.skew(x),
    }

# -*- coding: utf-8 -*-
"""Estilo e funções de apoio para as figuras do projeto.

Cores fixas em todas as figuras: saudável = azul, danificada = vermelho.
"""

from pathlib import Path

import matplotlib.pyplot as plt

COR_SAUDAVEL = "#1f77b4"
COR_DANIFICADA = "#d62728"
CORES = {"saudavel": COR_SAUDAVEL, "danificada": COR_DANIFICADA}
ROTULOS = {"saudavel": "Saudável", "danificada": "Danificada"}

PASTA_FIGURAS = Path("figures")


def configurar_estilo():
    """Estilo global das figuras (fontes legíveis no PDF do relatório)."""
    plt.rcParams.update(
        {
            "figure.dpi": 100,
            "savefig.dpi": 150,
            "font.size": 11,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "legend.fontsize": 10,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "figure.constrained_layout.use": True,
        }
    )


def salvar_figura(fig, nome, pasta=PASTA_FIGURAS):
    """Salva a figura em PNG (150 dpi) e PDF vetorial em figures/."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    fig.savefig(pasta / f"{nome}.png")
    fig.savefig(pasta / f"{nome}.pdf")

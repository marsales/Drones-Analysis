# -*- coding: utf-8 -*-
"""Divisão dos sinais em janelas de duração fixa, sem sobreposição."""

import numpy as np

FS = 10_000          # Hz — taxa de amostragem do piezo
JANELA_S = 1.0       # s — duração de cada janela (Δf = 1 Hz)


def janelar(x, fs=FS, janela_s=JANELA_S):
    """Divide o sinal x em janelas consecutivas de janela_s segundos.

    Descarta a sobra final incompleta. Retorna um array (n_janelas, n_amostras).
    """
    n_por_janela = int(round(janela_s * fs))
    n_janelas = len(x) // n_por_janela
    return np.asarray(x[: n_janelas * n_por_janela]).reshape(n_janelas, n_por_janela)


def janelas_com_ids(reg, fs=FS, janela_s=JANELA_S):
    """Janela o sinal do piezo de um registro, preservando os IDs.

    Retorna (janelas, lista_de_metadados), em que cada item da lista contém
    registro_id, gravacao_fisica_id, janela_idx, t_inicio_s e os metadados do nome.
    """
    from .carregamento import gravacao_fisica_id

    meta = reg["meta"]
    jan = janelar(reg["piezo"]["x"], fs=fs, janela_s=janela_s)
    ids = []
    for i in range(jan.shape[0]):
        ids.append(
            {
                "registro_id": meta["registro_id"],
                "gravacao_fisica_id": gravacao_fisica_id(meta),
                "janela_idx": i,
                "t_inicio_s": i * janela_s,
                "condicao": meta["condicao"],
                "tipo_falha": meta["falha"],
                "severidade": meta["severidade"],
                "velocidade": meta["velocidade"],
                "config": meta["config"],
                "repeticao": meta["repeticao"],
            }
        )
    return jan, ids

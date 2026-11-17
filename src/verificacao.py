# -*- coding: utf-8 -*-
"""Verificações de integridade dos registros (requisito 3.1.3)."""

import numpy as np
import pandas as pd

from .carregamento import listar_arquivos, carregar_registro, PASTA_DATASET


def verificar_registros(pasta=PASTA_DATASET):
    """Verificações por registro: NaN/Inf, uniformidade do tempo, fs declarada ×
    medida, saturação, segmentos constantes, média e transientes (razão entre o
    desvio padrão do 1º/último segundo e o global). Retorna um DataFrame."""
    linhas = []
    for caminho in listar_arquivos(pasta):
        reg = carregar_registro(caminho)
        m = reg["meta"]
        x, t, fs = reg["piezo"]["x"], reg["piezo"]["t"], reg["piezo"]["fs"]
        dt = np.diff(t)
        d0 = np.diff(x) == 0
        if d0.any():
            idx = np.flatnonzero(np.diff(np.concatenate(([False], d0, [False])).astype(int)))
            max_const = int((idx[1::2] - idx[::2]).max()) + 1
        else:
            max_const = 1
        nfs = int(fs)
        linha = {
            "registro_id": m["registro_id"],
            "condicao": m["condicao"],
            "velocidade": m["velocidade"],
            "config": m["config"],
            "n_amostras": x.size,
            "duracao_s": x.size / fs,
            "fs_declarada": fs,
            "fs_medida": 1.0 / np.median(dt),
            "dt_desvio_max": float(np.max(np.abs(dt - 1.0 / fs))),
            "n_nan": int(np.isnan(x).sum()),
            "n_inf": int(np.isinf(x).sum()),
            "media": float(x.mean()),
            "std": float(x.std()),
            "n_amostras_no_max": int((x == x.max()).sum()),
            "max_seq_constante": max_const,
            "razao_std_inicio": float(x[:nfs].std() / x.std()),
            "razao_std_fim": float(x[-nfs:].std() / x.std()),
            "data": reg["piezo"]["data"],
        }
        if "imu" in reg:
            imu = reg["imu"]["xyz"]
            linha["imu_n_nan"] = int(np.isnan(imu).sum())
            linha["imu_media_z"] = float(imu[2].mean())
        linhas.append(linha)
    return pd.DataFrame(linhas)


def verificar_duplicatas_c1_c2(pasta=PASTA_DATASET):
    """Compara amostra a amostra os pares saudáveis C1 × C2 (mesma SP e R).

    Retorna um DataFrame com uma linha por par e a coluna 'identicos'.
    """
    sinais = {}
    for caminho in listar_arquivos(pasta):
        reg = carregar_registro(caminho)
        m = reg["meta"]
        if m["condicao"] == "saudavel" and m["config"] in (1, 2):
            sinais.setdefault((m["velocidade"], m["repeticao"]), {})[m["config"]] = reg["piezo"]["x"]
    linhas = []
    for (sp, r), d in sorted(sinais.items()):
        linhas.append(
            {
                "velocidade": sp,
                "repeticao": r,
                "identicos": 1 in d and 2 in d and bool(np.array_equal(d[1], d[2])),
            }
        )
    return pd.DataFrame(linhas)

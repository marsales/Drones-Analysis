# -*- coding: utf-8 -*-
"""Extração completa: percorre os registros com motor ligado (SP1–3), janela os
sinais e calcula as características temporais e espectrais de cada janela.

Também acumula os espectros médios de amplitude por condição × velocidade
(somente gravações físicas únicas — as duplicatas C2 saudáveis são puladas) e o
espectro médio dos registros SP0_C4 (piso de ruído, motores parados).
"""

import numpy as np
import pandas as pd

from .carregamento import listar_arquivos, carregar_registro, PASTA_DATASET
from .janelamento import janelas_com_ids
from .features_tempo import features_tempo
from .features_frequencia import features_frequencia, espectro_amplitude


def extrair_features_e_espectros(pasta=PASTA_DATASET, verboso=False):
    """Retorna (df_janelas, f, espectros_medios).

    - df_janelas: uma linha por janela, com IDs, metadados, rótulo e todas as
      características temporais e espectrais;
    - f: eixo de frequências do espectro de amplitude (janela de 1 s);
    - espectros_medios: dict {'saudavel_SP1', ..., 'danificada_SP3',
      'ruido_SP0_C4'} com a média das magnitudes sobre as janelas.
    """
    linhas = []
    soma, cont = {}, {}
    f_axis = None
    for caminho in listar_arquivos(pasta):
        reg = carregar_registro(caminho)
        m = reg["meta"]
        jan, ids = janelas_com_ids(reg)
        if m["velocidade"] == 0:
            chave = "ruido_SP0_C4"  # só espectro de referência, sem características
        else:
            chave = f"{m['condicao']}_SP{m['velocidade']}"
            for i in range(jan.shape[0]):
                linha = dict(ids[i])
                linha["rotulo"] = m["condicao"]
                linha.update(features_tempo(jan[i]))
                linha.update(features_frequencia(jan[i]))
                linhas.append(linha)
        # espectro médio: pula as duplicatas C2 saudáveis (mesma gravação física)
        if not (m["condicao"] == "saudavel" and m["config"] == 2):
            for i in range(jan.shape[0]):
                f_axis, A = espectro_amplitude(jan[i])
                if chave not in soma:
                    soma[chave] = np.zeros_like(A)
                    cont[chave] = 0
                soma[chave] += A
                cont[chave] += 1
        if verboso:
            print(f"  {m['registro_id']}: {jan.shape[0]} janelas")
    espectros = {k: soma[k] / cont[k] for k in soma}
    return pd.DataFrame(linhas), f_axis, espectros

# -*- coding: utf-8 -*-
"""Leitura dos arquivos .mat do dataset DronePropB e montagem da tabela de metadados.

Convenção dos nomes: F{falha}_SV{severidade}_SP{velocidade}_C{config}[_R{repetição}].mat
- F0_SV0 = hélice saudável; F1, F2, F3 = tipos de falha (não documentados individualmente).
- SP0_C4 = motores parados (referência de ruído).
"""

import re
from pathlib import Path

import numpy as np
from scipy.io import loadmat

# Caminho padrão do dataset (relativo à raiz do repositório)
PASTA_DATASET = (
    Path("DronePropB Ground Testing Dataset for Commercial Drones with Defective Propellers")
    / "DronePropB Ground Testing Dataset"
)

PADRAO_NOME = re.compile(
    r"^F(?P<falha>\d)_SV(?P<severidade>\d)_SP(?P<velocidade>\d)_C(?P<config>\d)(?:_R(?P<repeticao>\d))?$"
)


def interpretar_nome(nome_arquivo):
    """Extrai os metadados codificados no nome do arquivo (sem extensão).

    Retorna um dicionário com falha, severidade, velocidade, config, repeticao
    (None se ausente) e condicao ('saudavel' ou 'danificada').
    """
    m = PADRAO_NOME.match(Path(nome_arquivo).stem)
    if m is None:
        raise ValueError(f"Nome fora da convenção esperada: {nome_arquivo}")
    d = {k: (int(v) if v is not None else None) for k, v in m.groupdict().items()}
    d["registro_id"] = Path(nome_arquivo).stem
    d["condicao"] = "saudavel" if d["falha"] == 0 else "danificada"
    return d


def gravacao_fisica_id(meta):
    """ID da gravação física: colapsa as duplicatas C1/C2 dos registros saudáveis.

    Nos saudáveis, F0_SV0_SP{s}_C1_R{r} e F0_SV0_SP{s}_C2_R{r} contêm dados
    idênticos amostra a amostra; ambas recebem o mesmo ID '..._C1C2'.
    """
    if meta["condicao"] == "saudavel" and meta["config"] in (1, 2):
        return f"F0_SV0_SP{meta['velocidade']}_R{meta['repeticao']}_C1C2"
    return meta["registro_id"]


def carregar_registro(caminho):
    """Carrega um arquivo .mat e devolve um dicionário com os sinais e metadados.

    Chaves: meta (dict do nome), piezo (dict com x, t, fs, data) e, se presente,
    imu (dict com X/Y/Z, t, fs).
    """
    caminho = Path(caminho)
    mat = loadmat(caminho, squeeze_me=False)
    meta = interpretar_nome(caminho.name)
    reg = {"meta": meta, "caminho": caminho}

    acc = mat["AccData"][0, 0]
    reg["piezo"] = {
        "x": np.asarray(acc["Vib_Data"]).ravel().astype(float),
        "t": np.asarray(acc["t"]).ravel().astype(float),
        "fs": float(np.asarray(acc["samplingRate"]).ravel()[0]),
        "data": str(np.asarray(acc["DATE"]).ravel()[0]) if "DATE" in acc.dtype.names else "",
    }

    if "IMUData" in mat:
        imu = mat["IMUData"][0, 0]
        dados = np.asarray(imu["Vib_Data"]).astype(float)  # shape (3, N): eixos X, Y, Z
        reg["imu"] = {
            "xyz": dados,
            "t": np.asarray(imu["t"]).ravel().astype(float),
            "fs": float(np.asarray(imu["samplingRate"]).ravel()[0]),
        }
    return reg


def listar_arquivos(pasta=PASTA_DATASET):
    """Lista ordenada de todos os .mat do dataset."""
    return sorted(Path(pasta).glob("*.mat"))


def montar_tabela_metadados(pasta=PASTA_DATASET):
    """Percorre todos os .mat e monta a tabela de metadados (lista de dicts).

    Não mantém os sinais em memória: lê, extrai os campos e descarta.
    """
    linhas = []
    for caminho in listar_arquivos(pasta):
        reg = carregar_registro(caminho)
        meta = reg["meta"]
        pz = reg["piezo"]
        n = pz["x"].size
        linha = {
            "registro_id": meta["registro_id"],
            "condicao": meta["condicao"],
            "tipo_falha": meta["falha"],
            "severidade": meta["severidade"],
            "velocidade": meta["velocidade"],
            "config": meta["config"],
            "repeticao": meta["repeticao"],
            "sensor": "piezo",
            "eixo": "1 canal (eixo não documentado)",
            "unidade": "u.a.",
            "fs_hz": pz["fs"],
            "n_amostras": n,
            "duracao_s": n / pz["fs"],
            "data": pz["data"],
            "gravacao_fisica_id": gravacao_fisica_id(meta),
            "tem_imu": "imu" in reg,
        }
        if "imu" in reg:
            linha["imu_fs_hz"] = reg["imu"]["fs"]
            linha["imu_n_amostras"] = reg["imu"]["xyz"].shape[1]
        linhas.append(linha)
    # flag de duplicata: True para a cópia C2 de cada gravação física saudável
    vistos = set()
    for linha in linhas:
        gid = linha["gravacao_fisica_id"]
        linha["duplicata"] = gid in vistos
        vistos.add(gid)
    return linhas

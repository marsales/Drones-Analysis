# Análise de sinais de vibração de drones

Projeto de CIN0020 — Sinais e Sistemas (UFPE/CIn), 2026.2.

### Grupo 1
- Fernando Luis Campelo dos Anjos
- Ludmila Cabral Lopes Magnani
- Marina Rodas Sales

## O que é

Análise de sinais reais de aceleração de drones com hélices **saudáveis** e **danificadas** (dataset **DronePropB**), nos domínios do **tempo** e da **frequência**: verificação e janelamento dos dados, extração de características por janela, espectros via FFT, estudo de resolução espectral e aliasing, e análise de separabilidade/redundância das características — base para a etapa de classificação da 2ª entrega.

## Estrutura do repositório

```
├── DronePropB .../            # dataset (111 arquivos .mat) — já incluído no repositório
├── notebooks/
│   └── entrega1_analise_sinais.ipynb   # notebook completo da 1ª entrega
├── src/                       # funções reutilizáveis
│   ├── carregamento.py        # leitura dos .mat, parsing dos nomes, metadados, deduplicação
│   ├── verificacao.py         # verificações de integridade (NaN, fs, saturação, duplicatas)
│   ├── janelamento.py         # janelas de 1 s com IDs
│   ├── features_tempo.py      # características temporais
│   ├── features_frequencia.py # FFT, espectro, PSD, bandas, centroide, entropia
│   ├── extracao.py            # passada única de extração (features + espectros médios)
│   └── graficos.py            # estilo e salvamento das figuras
├── figures/                   # figuras geradas (PNG 150 dpi + PDF vetorial)
├── results/                   # tabelas CSV (registros, features por janela, resumos)
└── relatorio/                 # relatório parcial em LaTeX
```

## Como rodar

### No Google Colab

Abra `notebooks/entrega1_analise_sinais.ipynb` no Colab e execute tudo (*Runtime → Run all*). A primeira célula clona este repositório (o dataset está incluído) e ajusta os caminhos automaticamente.

### Localmente

```bash
git clone https://github.com/marsales/Drones-Analysis.git
cd Drones-Analysis
pip install -r requirements.txt
jupyter notebook notebooks/entrega1_analise_sinais.ipynb
```

Dependências: `numpy`, `scipy`, `pandas`, `matplotlib` (ver `requirements.txt`). O notebook roda do início ao fim sem intervenção; a extração completa percorre os 111 arquivos e leva alguns minutos.

## Dataset

**DronePropB — Ground Testing Dataset for Commercial Drones with Defective Propellers.**
Ismail, M. A. A.; Elshaar, M. E.; Abdalla, A.; Quan, Q. (2024). Mendeley Data, V1.
DOI: [10.17632/xkvfjmm8zg.1](https://doi.org/10.17632/xkvfjmm8zg.1) — licença CC BY 4.0.

Convenção dos nomes: `F{falha}_SV{severidade}_SP{velocidade}_C{config}[_R{repetição}].mat` (`F0_SV0` = saudável). **Arquivos usados na análise:** todos os 108 registros com motor ligado (SP1–SP3, C1–C3) do acelerômetro piezoelétrico (`AccData`, 10 kHz); os 3 registros `F0_SV0_SP0_C4_R*` (motores parados) entram apenas como referência de piso de ruído. Os arquivos do dataset não são modificados pelo código.

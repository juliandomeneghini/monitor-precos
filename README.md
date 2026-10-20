# Monitor de Preços

Scraper que coleta diariamente o catálogo de [books.toscrape.com](https://books.toscrape.com),
armazena o histórico de preços em SQLite e roda de forma automatizada no GitHub Actions.

![Status da coleta](https://github.com/SEU-USUARIO/monitor-precos/actions/workflows/scraper.yml/badge.svg)

---

## O que o projeto faz

Coleta os 1000 livros do catálogo, extraindo título, preço e URL de cada item.
Cada execução grava os preços na tabela de histórico e registra o próprio
resultado (início, fim, quantidade e status) numa tabela de log.

O scraper roda todo dia às 06:00 (horário de Brasília) via GitHub Actions,
sem intervenção manual.

## Estrutura
monitor-precos/ ├── .github/workflows/scraper.yml # automação diária ├── data/precos.db # banco SQLite (versionado de propósito) ├── scraper.py # coleta e orquestração ├── database.py # acesso ao SQLite ├── ver.py # inspeção dos dados no terminal ├── app.py # dashboard em Streamlit ├── exportar.py # exportação para CSV ├── testar.py # diagnóstico rápido do projeto ├── simular_demo.py # gera histórico fictício para o gráfico ├── requirements.txt # dependências da coleta └── requirements-dev.txt # dependências do dashboard

Copiar

## Modelo de dados

Três tabelas:

| Tabela | Função |
|---|---|
| `produtos` | catálogo único (id, título, url) — `url` é `UNIQUE` |
| `historico_precos` | cada leitura de preço, com timestamp |
| `execucoes` | log de cada rodada: início, fim, itens, status, erro |

A separação é intencional: `produtos` responde "o que eu monitoro",
`historico_precos` responde "como o preço evoluiu" e `execucoes` responde
"a coleta de hoje funcionou". Misturar as três numa tabela só tornaria
impossível responder a segunda e a terceira.

## Como rodar

Pré-requisito: Python 3.13 ou superior.

```bash
git clone https://github.com/SEU-USUARIO/monitor-precos.git
cd monitor-precos

python -m venv .venv
# Windows
.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt

python database.py   # cria as tabelas
python scraper.py    # coleta o catálogo (aprox. 2 minutos)
python ver.py        # inspeciona os dados no terminal
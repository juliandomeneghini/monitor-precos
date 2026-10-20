# Monitor de Preços

Scraper em Python que coleta os 1000 livros do [books.toscrape.com](https://books.toscrape.com), guarda o histórico de preços em SQLite e roda sozinho todos os dias via GitHub Actions.

![Status da coleta](https://github.com/juliandomeneghini/monitor-precos/actions/workflows/scraper.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.13+-blue)
![Licença](https://img.shields.io/badge/licen%C3%A7a-estudo-lightgrey)

---

## Por que este projeto existe

A maior parte dos scrapers de tutorial para no `print()`. Este foi construído com as perguntas que aparecem quando o código precisa rodar sem ninguém olhando:

- Como evitar que rodar duas vezes duplique 1000 linhas no banco?
- Como saber, depois de duas semanas, que a coleta do dia 12 falhou?
- Como garantir que a URL montada está correta antes de gravar 404 no histórico?

Cada decisão abaixo responde a uma dessas perguntas — e está no código, não só no texto.

## Resultado

| Métrica | Valor |
|---|---|
| Livros monitorados | 1000 |
| Registros de preço acumulados | 2240 (6 execuções) |
| Tempo por coleta | ~1min45s (50 páginas, sequencial) |
| Execuções registradas | 6, todas com status `sucesso` |

## Arquitetura

```
GitHub Actions (cron diário)
        │
        ▼
   scraper.py ──► requests + BeautifulSoup
        │              │
        │              ▼
        │        50 páginas × 20 itens
        ▼
   database.py ──► SQLite (data/precos.db)
        │
        ├──► produtos          (1000 linhas, url UNIQUE)
        ├──► historico_precos  (1 linha por leitura)
        └──► execucoes         (log de cada rodada)
```

## Estrutura de arquivos

```
monitor-precos/
├── .github/workflows/scraper.yml   # automação diária
├── data/precos.db                  # banco SQLite (versionado de propósito)
├── scraper.py                      # coleta e orquestração
├── database.py                     # acesso ao SQLite
├── ver.py                          # inspeção no terminal
├── app.py                          # dashboard em Streamlit
├── exportar.py                     # exportação para CSV
├── testar.py                       # diagnóstico rápido
├── simular_demo.py                 # histórico fictício (só demonstração)
├── requirements.txt                # dependências da coleta
└── requirements-dev.txt            # dependências do dashboard
```

## Modelo de dados

Três tabelas, cada uma respondendo a uma pergunta diferente:

| Tabela | Pergunta que responde | Chave |
|---|---|---|
| `produtos` | "O que eu monitoro?" | `url` é `UNIQUE` |
| `historico_precos` | "Como o preço evoluiu?" | FK para `produtos` |
| `execucoes` | "A coleta de hoje funcionou?" | `id` auto |

Misturar as três numa tabela só tornaria impossível responder a segunda e a terceira. A separação é o desenho, não um detalhe.

## Como rodar

Pré-requisito: Python 3.13 ou superior.

```bash
git clone https://github.com/juliandomeneghini/monitor-precos.git
cd monitor-precos

python -m venv .venv
# Windows
.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt

python database.py   # cria as tabelas
python scraper.py    # coleta o catálogo (~2 minutos)
python ver.py        # inspeciona os dados
```

Dashboard:

```bash
pip install -r requirements-dev.txt
streamlit run app.py
```

Verificação rápida de saúde:

```bash
python testar.py
```

## Decisões técnicas

**SQLite em vez de Postgres.** Volume pequeno (1000 produtos, ~1000 registros por execução), acesso de um processo só, e o banco precisa viajar junto com o repositório. Um servidor de banco aqui seria infraestrutura sem retorno.

**O banco é versionado de propósito.** Arquivos `.db` normalmente ficam fora do Git. Aqui ele é o produto: o histórico acumulado é o resultado do trabalho, não artefato de build. Repositório versiona resultado, não só código.

**`urljoin` ancorado numa constante `BASE`.** A primeira versão montava URLs com `replace()` e `lstrip()` e gerava endereços sem `/catalogue/` — 404 silencioso. A correção não foi remendar a string, foi ancorar o `urljoin` em `BASE` em vez de na URL da página corrente. Resultado determinístico, independente do formato do `href` que o site devolver.

**`INSERT OR IGNORE` + `UNIQUE` na URL.** Rodar o scraper seis vezes manteve `produtos` em 1000 linhas e `historico_precos` em 2240. Sem essa restrição, o banco teria 6000 produtos duplicados e nenhuma série temporal confiável.

**Log de execução em tabela, não em print.** Um `print` some quando o terminal fecha. A tabela `execucoes` guarda início, fim, quantidade, status e erro — então uma falha no dia 12 é visível hoje, sem abrir log de runner.

**Falha de preço não passa silenciosa.** O `except ValueError` original fazia o item desaparecer. Agora ele emite `[aviso]` com o texto cru, para que uma queda de 1000 para 997 itens tenha explicação rastreável.

## Limitações declaradas

**Os preços não variam.** O `books.toscrape.com` é site de demonstração, estático, e declara no próprio HTML que os preços foram atribuídos aleatoriamente. Duas execuções seguidas produzem médias idênticas ao centavo (£35.07), e o gráfico de histórico aparece como linha reta. É característica do alvo, não falha do projeto — e é exatamente por isso que ele foi escolhido: permite testar a arquitetura sem risco de uso indevido.

**Dados de demonstração.** `simular_demo.py` gera histórico fictício apenas para ilustrar o gráfico do README. Exige a flag `--confirmar-simulacao` e **não faz parte do fluxo de coleta**. Qualquer gráfico a partir dele é identificado como fictício.

**Coleta sequencial.** 1,5 s entre páginas, 50 páginas em ~1min45s — dentro do limite do runner com folga. Paralelizar aumentaria o risco de bloqueio num site pequeno, sem ganho real.

**Crescimento do histórico.** Cada execução adiciona ~1000 linhas. Em um ano, o banco chega a dezenas de MB. Próximo passo natural seria arquivar por ano ou mover para repositório separado. Hoje não é problema; é dívida mapeada.

## Automação

O workflow `.github/workflows/scraper.yml` roda:

- **Cron:** `0 9 * * *` (09:00 UTC = 06:00 em Brasília)
- **Manual:** aba Actions → "Coleta diaria de precos" → Run workflow
- Commit do banco atualizado de volta no repositório, via `github-actions[bot]`

O cron do GitHub pode atrasar de 5 a 40 minutos em horário de pico — é documentado e esperado. O agendamento é diário, não pontual.

## Licença

Projeto de estudo, sem fins comerciais. Os dados pertencem ao [books.toscrape.com](https://books.toscrape.com), site destinado à prática de web scraping.

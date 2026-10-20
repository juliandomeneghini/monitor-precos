import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

import database

BASE = "https://books.toscrape.com/catalogue/"
SITE = "https://books.toscrape.com/"
HEADERS = {"User-Agent": "MonitorPrecos/1.0 (projeto de estudo)"}


def limpar_preco(texto):
    numero = re.sub(r"[^\d.]", "", texto.replace(",", ""))
    return float(numero)


def extrair_pagina(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    itens = []
    for card in soup.select("article.product_pod"):
        link = card.select_one("h3 a")
        preco_el = card.select_one("p.price_color")
        if not link or not preco_el:
            continue

        try:
            preco = limpar_preco(preco_el.get_text())
        except ValueError:
            continue

        itens.append(
            {
                "titulo": link.get("title", "").strip(),
                "url": urljoin(BASE, link["href"]),
                "preco": preco,
            }
        )
    return itens, soup


def rastrear(max_paginas=3):
    url = BASE + "page-1.html"
    todos = []
    for n in range(1, max_paginas + 1):
        print(f"Página {n}: {url}")
        itens, soup = extrair_pagina(url)
        if not itens:
            break
        todos.extend(itens)
        proximo = soup.select_one("li.next > a")
        if not proximo:
            break
        url = urljoin(url, proximo["href"])
        time.sleep(1.5)
    return todos


def main():
    database.criar_tabelas()
    exec_id = database.iniciar_execucao()
    try:
        itens = rastrear(max_paginas=3)
        if not itens:
            database.finalizar_execucao(exec_id, 0, "falha", "nenhum item coletado")
            print("Nenhum item coletado. Verifique os seletores.")
            return
        gravados = database.salvar_itens(itens)
        database.finalizar_execucao(exec_id, gravados, "sucesso")
        print(f"{len(itens)} coletados, {gravados} gravados no histórico.")
    except Exception as e:
        database.finalizar_execucao(exec_id, 0, "erro", str(e)[:500])
        raise


if __name__ == "__main__":
    main()

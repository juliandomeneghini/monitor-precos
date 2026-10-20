import csv
import sqlite3
from pathlib import Path

con = sqlite3.connect("data/precos.db")
Path("saida").mkdir(exist_ok=True)

consultas = {
    "produtos.csv": "SELECT id, titulo, url FROM produtos",
    "historico.csv": """
        SELECT p.titulo, h.preco, h.coletado_em
          FROM historico_precos h
          JOIN produtos p ON p.id = h.produto_id
      ORDER BY h.coletado_em, p.titulo
    """,
    "execucoes.csv": "SELECT * FROM execucoes",
}

for nome, sql in consultas.items():
    cur = con.execute(sql)
    colunas = [d[0] for d in cur.description]
    with open(Path("saida") / nome, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(colunas)
        w.writerows(cur)
    print(f"gerado: saida/{nome}")

con.close()

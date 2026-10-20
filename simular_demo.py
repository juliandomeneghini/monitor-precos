"""
Script APENAS para gerar dados de demonstracao no grafico do README.

NAO faz parte do fluxo de coleta.
NAO deve ser executado sobre o banco de producao.

Uso:
    python simular_demo.py --confirmar-simulacao
"""

import sys

if "--confirmar-simulacao" not in sys.argv:
    raise SystemExit(
        "Este script insere precos SIMULADOS no banco.\n"
        "Se voce realmente quer isso, rode:\n"
        "  python simular_demo.py --confirmar-simulacao"
    )


import random
import sqlite3
from datetime import datetime, timedelta

random.seed(42)
con = sqlite3.connect("data/precos.db")
cur = con.cursor()

produtos = cur.execute("SELECT id FROM produtos").fetchall()
base = {pid: 10 + (pid % 40) for (pid,) in produtos}

hoje = datetime.now()
for dias in range(30, 0, -1):
    data = (hoje - timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S")
    for pid in base:
        preco = round(base[pid] * random.uniform(0.85, 1.15), 2)
        cur.execute(
            "INSERT INTO historico_precos (produto_id, preco, coletado_em) VALUES (?, ?, ?)",
            (pid, preco, data),
        )

con.commit()
con.close()
print("30 dias de historico simulado inseridos.")

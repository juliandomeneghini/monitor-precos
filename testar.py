import ast
import sqlite3
import sys
from pathlib import Path

print("1. Sintaxe do scraper.py")
try:
    ast.parse(Path("scraper.py").read_text(encoding="utf-8"))
    print("   ok")
except SyntaxError as e:
    print(f"   FALHOU: linha {e.lineno}: {e.msg}")
    sys.exit(1)

print("2. Imports")
try:
    import scraper  # noqa: F401

    print("   ok")
except Exception as e:
    print(f"   FALHOU: {e}")
    sys.exit(1)

print("3. Banco")
db = Path("data/precos.db")
if not db.exists():
    print("   banco nao existe ainda (rode python database.py)")
else:
    con = sqlite3.connect(db)
    for t in ("produtos", "historico_precos", "execucoes"):
        try:
            n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"   {t:20} {n:>5}")
        except sqlite3.OperationalError as e:
            print(f"   {t:20} ERRO: {e}")
    ultima = con.execute(
        "SELECT inicio, itens_coletados, status, erro FROM execucoes "
        "ORDER BY id DESC LIMIT 1"
    ).fetchone()
    print(f"   ultima execucao: {ultima}")
    con.close()

print("4. Amostra de URLs")
if db.exists():
    con = sqlite3.connect(db)
    for (u,) in con.execute("SELECT url FROM produtos LIMIT 3"):
        print(f"   {u}")
    con.close()

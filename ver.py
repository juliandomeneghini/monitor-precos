import sqlite3
from pathlib import Path

DB = Path("data/precos.db")

if not DB.exists():
    raise SystemExit(
        "data/precos.db nao existe. Rode: python database.py e python scraper.py"
    )

con = sqlite3.connect(DB)
cur = con.cursor()

print("=" * 60)
print("CONTAGENS")
print("=" * 60)
for t in ("produtos", "historico_precos", "execucoes"):
    try:
        n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:20} {n:>6} linhas")
    except sqlite3.OperationalError as e:
        print(f"  {t:20} ERRO: {e}")

print()
print("=" * 60)
print("EXECUCOES")
print("=" * 60)
for r in cur.execute("""
    SELECT id, inicio, fim, itens_coletados, status, COALESCE(erro, '')
      FROM execucoes ORDER BY id DESC LIMIT 10
"""):
    print(f"  #{r[0]:<3} {r[1]} -> {r[2]}  {r[3]:>4} itens  {r[4]:<8} {r[5]}")

print()
print("=" * 60)
print("TOP 10 MAIS CAROS (ultima coleta)")
print("=" * 60)
for titulo, preco in cur.execute("""
    WITH u AS (
        SELECT produto_id, preco,
               ROW_NUMBER() OVER (PARTITION BY produto_id
                                  ORDER BY coletado_em DESC) AS rn
          FROM historico_precos
    )
    SELECT p.titulo, u.preco
      FROM u JOIN produtos p ON p.id = u.produto_id
     WHERE u.rn = 1
     ORDER BY u.preco DESC
     LIMIT 10
"""):
    print(f"  £ {preco:>7.2f}  {titulo[:55]}")

print()
print("=" * 60)
print("PRECO MEDIO POR EXECUCAO")
print("=" * 60)
for r in cur.execute("""
    SELECT substr(coletado_em, 1, 16) AS quando,
           COUNT(*), ROUND(AVG(preco), 2), ROUND(MIN(preco), 2), ROUND(MAX(preco), 2)
      FROM historico_precos
     GROUP BY quando
     ORDER BY quando DESC
"""):
    print(f"  {r[0]}  n={r[1]:<5} media=£{r[2]:<7} min=£{r[3]:<7} max=£{r[4]}")

print()
print("=" * 60)
print("AMOSTRA DE URLs (clique para validar)")
print("=" * 60)
for (u,) in cur.execute("SELECT url FROM produtos LIMIT 3"):
    print(f"  {u}")

con.close()

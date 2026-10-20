import sqlite3

con = sqlite3.connect("data/precos.db")
cur = con.cursor()

print("=== CONTAGENS ===")
for t in ("produtos", "historico_precos", "execucoes"):
    n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"{t:20} {n:>5} linhas")

print("\n=== ULTIMAS EXECUCOES ===")
for r in cur.execute("""SELECT id, inicio, fim, itens_coletados, status
                          FROM execucoes ORDER BY id DESC LIMIT 5"""):
    print(r)

print("\n=== TOP 10 MAIS CAROS ===")
for r in cur.execute("""SELECT p.titulo, h.preco, h.coletado_em
                          FROM historico_precos h
                          JOIN produtos p ON p.id = h.produto_id
                      ORDER BY h.preco DESC LIMIT 10"""):
    print(r)

print("\n=== VARIACAO ENTRE AS DUAS ULTIMAS COLETAS ===")
for r in cur.execute("""
    WITH u AS (
        SELECT produto_id, preco,
               ROW_NUMBER() OVER (PARTITION BY produto_id
                                  ORDER BY coletado_em DESC) AS rn
        FROM historico_precos
    )
    SELECT p.titulo,
           MAX(CASE WHEN rn=1 THEN preco END) AS atual,
           MAX(CASE WHEN rn=2 THEN preco END) AS anterior
      FROM u JOIN produtos p ON p.id = u.produto_id
     GROUP BY p.titulo
     HAVING anterior IS NOT NULL AND atual <> anterior
     ORDER BY ABS(atual - anterior) DESC
     LIMIT 10
"""):
    print(r)

con.close()

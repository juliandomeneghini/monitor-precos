import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = "data/precos.db"


def conectar():
    Path("data").mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def criar_tabelas():
    con = conectar()
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            titulo TEXT NOT NULL,
            primeira_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS historico_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL REFERENCES produtos(id),
            preco REAL NOT NULL,
            coletado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS execucoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inicio TIMESTAMP,
            fim TIMESTAMP,
            itens_coletados INTEGER DEFAULT 0,
            status TEXT,
            erro TEXT
        );
    """)
    con.commit()
    con.close()


def iniciar_execucao():
    """Abre um registro na tabela execucoes e devolve o id."""
    con = conectar()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO execucoes (inicio, status) VALUES (?, ?)",
        (datetime.now().isoformat(sep=" ", timespec="seconds"), "em_andamento"),
    )
    con.commit()
    exec_id = cur.lastrowid
    con.close()
    return exec_id


def finalizar_execucao(exec_id, itens=0, status="sucesso", erro=None):
    """Fecha o registro da execucao com resultado."""
    con = conectar()
    cur = con.cursor()
    cur.execute(
        """UPDATE execucoes
              SET fim = ?, itens_coletados = ?, status = ?, erro = ?
            WHERE id = ?""",
        (
            datetime.now().isoformat(sep=" ", timespec="seconds"),
            itens,
            status,
            erro,
            exec_id,
        ),
    )
    con.commit()
    con.close()


def salvar_itens(itens):
    con = conectar()
    cur = con.cursor()
    novos = 0
    for it in itens:
        cur.execute(
            "INSERT OR IGNORE INTO produtos (url, titulo) VALUES (?, ?)",
            (it["url"], it["titulo"]),
        )
        cur.execute("SELECT id FROM produtos WHERE url = ?", (it["url"],))
        linha = cur.fetchone()
        if not linha:
            continue
        cur.execute(
            "INSERT INTO historico_precos (produto_id, preco) VALUES (?, ?)",
            (linha[0], it["preco"]),
        )
        novos += 1
    con.commit()
    con.close()
    return novos


def resumo_execucoes(limite=10):
    """Consulta rapida para o README/analise: ultimas execucoes."""
    con = conectar()
    cur = con.cursor()
    cur.execute(
        """SELECT id, inicio, fim, itens_coletados, status, erro
             FROM execucoes
         ORDER BY id DESC
            LIMIT ?""",
        (limite,),
    )
    for linha in cur.fetchall():
        print(linha)
    con.close()


if __name__ == "__main__":
    criar_tabelas()
    print("Tabelas criadas em", DB_PATH)

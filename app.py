import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Monitor de Precos", layout="wide")
st.title("Monitor de Precos - Books to Scrape")

con = sqlite3.connect("data/precos.db")

col1, col2, col3 = st.columns(3)
for col, tabela, rotulo in zip(
    (col1, col2, col3),
    ("produtos", "historico_precos", "execucoes"),
    ("Livros monitorados", "Registros de preco", "Execucoes"),
):
    n = pd.read_sql(f"SELECT COUNT(*) AS n FROM {tabela}", con)["n"][0]
    col.metric(rotulo, f"{n:,}".replace(",", "."))

df = pd.read_sql(
    """
    SELECT p.titulo, h.preco, h.coletado_em
      FROM historico_precos h
      JOIN produtos p ON p.id = h.produto_id
""",
    con,
)

execucoes = pd.read_sql(
    "SELECT id, inicio, itens_coletados, status FROM execucoes ORDER BY id DESC", con
)
con.close()

st.subheader("Historico de preco por livro")
produto = st.selectbox("Livro", sorted(df["titulo"].unique()))
serie = (
    df[df["titulo"] == produto]
    .sort_values("coletado_em")
    .set_index("coletado_em")["preco"]
)

col_a, col_b = st.columns([2, 1])
with col_a:
    st.line_chart(serie)
with col_b:
    st.metric("Preco atual", f"£ {serie.iloc[-1]:.2f}")
    st.metric("Minimo", f"£ {serie.min():.2f}")
    st.metric("Maximo", f"£ {serie.max():.2f}")

st.subheader("Execucoes")
st.dataframe(execucoes, use_container_width=True)

st.subheader("Catalogo")
st.dataframe(
    df.sort_values("coletado_em", ascending=False).head(100),
    use_container_width=True,
)

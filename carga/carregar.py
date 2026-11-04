"""Pipeline ERP → bruto → organizado → relatorio.

Em produção, a leitura é feita na API do ERP por uma Azure Function, todo dia às 8h,
e o banco é Azure SQL. Nesta demo, o "ERP" são os JSON de dados_exemplo/erp_simulado
e o banco é um arquivo SQLite, para qualquer pessoa rodar sem configurar nada.

Regras que o código segue:
- o ERP é só leitura;
- o bruto só recebe linhas (o banco recusa UPDATE e DELETE);
- organizado e relatorio são refeitos a cada carga a partir do bruto;
- o que some do ERP entre cargas vai para organizado_exclusoes, que só cresce.
"""
import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ERP = RAIZ / "dados_exemplo" / "erp_simulado"
BANCO = RAIZ / "demo.db"
CHAVES = {"clientes": "codigo_cliente", "produtos": "codigo_produto", "notas": "numero_nf"}


def ler_erp(entidade):
    """Lê página por página, como na API: para quando chega na última."""
    pagina = 1
    while True:
        arquivo = ERP / f"{entidade}_p{pagina}.json"
        if not arquivo.exists():
            raise FileNotFoundError(f"Página {pagina} de {entidade} não encontrada. Rode gerar_dados_ficticios.py")
        texto = arquivo.read_text(encoding="utf-8")
        resposta = json.loads(texto)
        yield pagina, texto
        if resposta["pagina"] >= resposta["total_de_paginas"]:
            break
        pagina += 1


def gravar_bruto(con, carga_id, agora):
    for entidade in CHAVES:
        for pagina, texto in ler_erp(entidade):
            con.execute(
                "INSERT INTO bruto_paginas (carga_id, entidade, pagina, hash, carregado_em, json) VALUES (?,?,?,?,?,?)",
                (carga_id, entidade, pagina, hashlib.sha256(texto.encode()).hexdigest(), agora, texto))


def registros_da_carga(con, entidade, carga_id):
    linhas = con.execute(
        "SELECT json FROM bruto_paginas WHERE entidade = ? AND carga_id = ? ORDER BY pagina",
        (entidade, carga_id)).fetchall()
    return [r for (texto,) in linhas for r in json.loads(texto)["registros"]]


def registrar_exclusoes(con, carga_id, agora):
    if carga_id == 1:
        return 0
    novas = 0
    for entidade, chave in CHAVES.items():
        atuais = {r[chave] for r in registros_da_carga(con, entidade, carga_id)}
        for r in registros_da_carga(con, entidade, carga_id - 1):
            if r[chave] not in atuais:
                con.execute("INSERT INTO organizado_exclusoes VALUES (?,?,?,?)",
                            (entidade, str(r[chave]), agora, json.dumps(r, ensure_ascii=False)))
                novas += 1
    return novas


def montar_organizado(con, carga_id):
    con.executescript("""
        DROP TABLE IF EXISTS organizado_clientes;
        DROP TABLE IF EXISTS organizado_produtos;
        DROP TABLE IF EXISTS organizado_notas;
        DROP TABLE IF EXISTS organizado_itens;
        CREATE TABLE organizado_clientes (codigo_cliente INTEGER PRIMARY KEY, nome TEXT, cidade TEXT, uf TEXT);
        CREATE TABLE organizado_produtos (codigo_produto INTEGER PRIMARY KEY, descricao TEXT, linha TEXT, preco_tabela REAL);
        CREATE TABLE organizado_notas    (numero_nf INTEGER PRIMARY KEY, data_emissao TEXT, codigo_cliente INTEGER);
        CREATE TABLE organizado_itens    (numero_nf INTEGER, codigo_produto INTEGER, quantidade INTEGER, valor_unitario REAL);
    """)
    con.executemany("INSERT INTO organizado_clientes VALUES (:codigo_cliente,:nome,:cidade,:uf)",
                    registros_da_carga(con, "clientes", carga_id))
    con.executemany("INSERT INTO organizado_produtos VALUES (:codigo_produto,:descricao,:linha,:preco_tabela)",
                    registros_da_carga(con, "produtos", carga_id))
    notas = registros_da_carga(con, "notas", carga_id)
    con.executemany("INSERT INTO organizado_notas VALUES (:numero_nf,:data_emissao,:codigo_cliente)", notas)
    con.executemany("INSERT INTO organizado_itens VALUES (?,?,?,?)",
                    [(n["numero_nf"], i["codigo_produto"], i["quantidade"], i["valor_unitario"])
                     for n in notas for i in n["itens"]])


def main():
    con = sqlite3.connect(BANCO)
    con.executescript((RAIZ / "sql" / "schema.sql").read_text(encoding="utf-8"))
    agora = datetime.now().isoformat(timespec="seconds")
    carga_id = (con.execute("SELECT max(carga_id) FROM bruto_paginas").fetchone()[0] or 0) + 1
    with con:
        gravar_bruto(con, carga_id, agora)
        exclusoes = registrar_exclusoes(con, carga_id, agora)
        montar_organizado(con, carga_id)
        con.executescript((RAIZ / "sql" / "relatorio_views.sql").read_text(encoding="utf-8"))
    total = con.execute("SELECT count(*), round(sum(valor_total), 2) FROM relatorio_vendas").fetchone()
    print(f"Carga {carga_id} concluída: {total[0]} itens de venda, R$ {total[1]:,.2f}; "
          f"{exclusoes} exclusões registradas.")
    con.close()


if __name__ == "__main__":
    main()

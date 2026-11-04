"""Relatório comercial a partir das views relatorio_*.

Gera em saida/: vendas por mês (com variação mês a mês), curva ABC de clientes
e clientes parados (sem comprar há mais de 60 dias).
"""
import csv
import sqlite3
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
DIAS_PARADO = 60


def salvar(nome, cabecalho, linhas):
    with (SAIDA / nome).open("w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.writer(f, delimiter=";")
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)


def main():
    SAIDA.mkdir(exist_ok=True)
    con = sqlite3.connect(RAIZ / "demo.db")

    meses = con.execute("SELECT mes, vendas, notas, clientes, ticket_medio FROM relatorio_vendas_mes ORDER BY mes").fetchall()
    linhas, anterior = [], None
    for mes, vendas, notas, clientes, ticket in meses:
        variacao = f"{(vendas / anterior - 1) * 100:+.1f}%" if anterior else ""
        linhas.append((mes, vendas, notas, clientes, ticket, variacao))
        anterior = vendas
    salvar("vendas_por_mes.csv", ["mes", "vendas", "notas", "clientes", "ticket_medio", "vs_mes_anterior"], linhas)

    por_cliente = con.execute("""SELECT cliente, round(sum(valor_total), 2) AS vendas
                                 FROM relatorio_vendas GROUP BY cliente ORDER BY vendas DESC""").fetchall()
    total = sum(v for _, v in por_cliente)
    acumulado, abc = 0, []
    for cliente, vendas in por_cliente:
        acumulado += vendas
        fatia = acumulado / total
        abc.append((cliente, vendas, f"{fatia * 100:.1f}%", "A" if fatia <= 0.8 else "B" if fatia <= 0.95 else "C"))
    salvar("curva_abc_clientes.csv", ["cliente", "vendas", "acumulado", "classe"], abc)

    hoje = date.fromisoformat(con.execute("SELECT max(data_emissao) FROM relatorio_vendas").fetchone()[0])
    parados = []
    for cliente, ultima, vendas in con.execute("""SELECT cliente, max(data_emissao), round(sum(valor_total), 2)
                                                  FROM relatorio_vendas GROUP BY cliente"""):
        dias = (hoje - date.fromisoformat(ultima)).days
        if dias > DIAS_PARADO:
            parados.append((cliente, ultima, dias, vendas))
    parados.sort(key=lambda x: -x[3])
    salvar("clientes_parados.csv", ["cliente", "ultima_compra", "dias_sem_comprar", "vendas_historicas"], parados)

    classe_a = sum(1 for x in abc if x[3] == "A")
    print(f"{len(meses)} meses · {classe_a} de {len(abc)} clientes fazem 80% das vendas · "
          f"{len(parados)} clientes parados há mais de {DIAS_PARADO} dias. Arquivos em {SAIDA}")


if __name__ == "__main__":
    main()

"""Gera um ERP simulado com dados 100% fictícios.

Imita o formato paginado de uma API de ERP (pagina, total_de_paginas, registros)
para o pipeline ser testado sem acesso a nenhum sistema real.
Também gera uma planilha de sell-out com erros de propósito, para o validador.
"""
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ERP = RAIZ / "dados_exemplo" / "erp_simulado"
random.seed(42)

CIDADES = ["Campinas", "Ribeirão Preto", "Santos", "Jundiaí", "Osasco", "Guarulhos"]
TIPOS = ["Restaurante", "Bar", "Mercado", "Empório", "Hotel"]
LINHAS = {
    "Vinho tinto": (45, 180), "Vinho branco": (40, 150), "Espumante": (55, 220),
    "Destilado": (70, 320), "Cerveja especial": (12, 35),
}


def paginar(entidade, registros, por_pagina=50):
    total = (len(registros) + por_pagina - 1) // por_pagina
    for i in range(total):
        pagina = {"pagina": i + 1, "total_de_paginas": total,
                  "registros": registros[i * por_pagina:(i + 1) * por_pagina]}
        (ERP / f"{entidade}_p{i + 1}.json").write_text(
            json.dumps(pagina, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    ERP.mkdir(parents=True, exist_ok=True)
    for antigo in ERP.glob("*.json"):
        antigo.unlink()

    clientes = [{"codigo_cliente": 1000 + i,
                 "nome": f"{random.choice(TIPOS)} Fictício {i:03d}",
                 "cidade": random.choice(CIDADES), "uf": "SP"} for i in range(1, 81)]

    produtos = []
    for i in range(1, 41):
        linha = random.choice(list(LINHAS))
        minimo, maximo = LINHAS[linha]
        produtos.append({"codigo_produto": 5000 + i, "descricao": f"{linha} Exemplo {i:02d}",
                         "linha": linha, "preco_tabela": round(random.uniform(minimo, maximo), 2)})

    # Poucos clientes concentram as compras (curva ABC realista)
    pesos = [random.paretovariate(1.2) for _ in clientes]
    # Alguns clientes param de comprar no meio do período
    parados = set(random.sample([c["codigo_cliente"] for c in clientes], 8))

    notas, numero, inicio = [], 20000, date(2026, 1, 1)
    for dia in range(300):
        data = inicio + timedelta(days=dia)
        if data.weekday() >= 5:
            continue
        for _ in range(random.randint(2, 7)):
            cliente = random.choices(clientes, weights=pesos)[0]
            if cliente["codigo_cliente"] in parados and dia > 200:
                continue
            numero += 1
            itens = []
            for produto in random.sample(produtos, random.randint(1, 4)):
                itens.append({"codigo_produto": produto["codigo_produto"],
                              "quantidade": random.randint(1, 24),
                              "valor_unitario": round(produto["preco_tabela"] * random.uniform(0.9, 1.05), 2)})
            notas.append({"numero_nf": numero, "data_emissao": data.isoformat(),
                          "codigo_cliente": cliente["codigo_cliente"], "itens": itens})

    paginar("clientes", clientes)
    paginar("produtos", produtos)
    paginar("notas", notas)
    gerar_planilha_sellout(notas[-60:], produtos)
    print(f"ERP simulado: {len(clientes)} clientes, {len(produtos)} produtos, {len(notas)} notas em {ERP}")


def gerar_planilha_sellout(notas, produtos):
    """Planilha do mês com problemas plantados, para mostrar o validador."""
    precos = {p["codigo_produto"]: p["preco_tabela"] for p in produtos}
    linhas = []
    for nota in notas:
        for item in nota["itens"]:
            linhas.append({"numero_nf": nota["numero_nf"], "data_emissao": nota["data_emissao"],
                           "codigo_cliente": nota["codigo_cliente"], "codigo_produto": item["codigo_produto"],
                           "quantidade": item["quantidade"], "valor_unitario": item["valor_unitario"]})
    # ⛔ mesma NF para dois clientes
    linhas.append({**linhas[0], "codigo_cliente": linhas[0]["codigo_cliente"] + 1})
    # ⛔ cliente sem cadastro
    linhas[3]["codigo_cliente"] = 9999
    # ⛔ campo obrigatório em branco
    linhas[5]["codigo_produto"] = ""
    # ⛔ data inválida
    linhas[7]["data_emissao"] = "2026-02-30"
    # ⚠️ preço muito fora da tabela
    linhas[9]["valor_unitario"] = round(precos[linhas[9]["codigo_produto"]] * 3, 2)
    # ⚠️ quantidade estranha
    linhas[11]["quantidade"] = 900
    # ⚠️ venda num domingo
    linhas[13]["data_emissao"] = "2026-10-25"

    destino = RAIZ / "dados_exemplo" / "planilha_sellout.csv"
    with destino.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(linhas[0]), delimiter=";")
        escritor.writeheader()
        escritor.writerows(linhas)


if __name__ == "__main__":
    main()

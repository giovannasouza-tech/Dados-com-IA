"""Revisa a planilha de sell-out antes de gerar o arquivo para a indústria.

⛔ Erros que impedem o envio: NF com dois clientes, cliente sem cadastro,
   campo obrigatório em branco, data inválida.
⚠️ Pontos para conferir: preço fora da tabela, quantidade estranha,
   venda em dia sem faturamento (fim de semana).

O arquivo só é gerado se não houver erro, ou se a pessoa liberar com --liberar.
Nenhum dado é inventado: o que falta é apontado, não preenchido.

Uso:  python automacoes/validar_sellout.py [--liberar]
"""
import csv
import sqlite3
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PLANILHA = RAIZ / "dados_exemplo" / "planilha_sellout.csv"
OBRIGATORIOS = ["numero_nf", "data_emissao", "codigo_cliente", "codigo_produto", "quantidade", "valor_unitario"]
LIMITE_PRECO = 0.30        # mais de 30% de diferença da tabela
LIMITE_QUANTIDADE = 200    # unidades numa linha


def revisar(linhas, clientes, precos):
    erros, avisos = [], []
    clientes_por_nf = defaultdict(set)
    for n, linha in enumerate(linhas, start=2):  # linha 1 é o cabeçalho
        vazios = [c for c in OBRIGATORIOS if not linha.get(c, "").strip()]
        if vazios:
            erros.append(f"linha {n}: campo obrigatório em branco ({', '.join(vazios)})")
            continue
        clientes_por_nf[linha["numero_nf"]].add(linha["codigo_cliente"])
        if int(linha["codigo_cliente"]) not in clientes:
            erros.append(f"linha {n}: cliente {linha['codigo_cliente']} sem cadastro no ERP")
        try:
            dia = date.fromisoformat(linha["data_emissao"])
        except ValueError:
            erros.append(f"linha {n}: data inválida ({linha['data_emissao']})")
            dia = None
        if dia and dia.weekday() >= 5:
            avisos.append(f"linha {n}: venda num {'sábado' if dia.weekday() == 5 else 'domingo'} ({dia})")
        tabela = precos.get(int(linha["codigo_produto"]))
        if tabela and abs(float(linha["valor_unitario"]) / tabela - 1) > LIMITE_PRECO:
            avisos.append(f"linha {n}: preço R$ {linha['valor_unitario']} contra R$ {tabela:.2f} de tabela")
        if int(linha["quantidade"]) > LIMITE_QUANTIDADE:
            avisos.append(f"linha {n}: quantidade {linha['quantidade']} fora do comum")
    for nf, codigos in clientes_por_nf.items():
        if len(codigos) > 1:
            erros.insert(0, f"NF {nf} aparece para {len(codigos)} clientes ({', '.join(sorted(codigos))})")
    return erros, avisos


def gerar_txt(linhas):
    destino = RAIZ / "saida" / "sellout.txt"
    destino.parent.mkdir(exist_ok=True)
    with destino.open("w", encoding="utf-8") as f:
        for l in linhas:
            if all(l.get(c, "").strip() for c in OBRIGATORIOS):
                f.write("|".join(l[c] for c in OBRIGATORIOS) + "\n")
    return destino


def main():
    con = sqlite3.connect(RAIZ / "demo.db")
    clientes = {c for (c,) in con.execute("SELECT codigo_cliente FROM organizado_clientes")}
    precos = dict(con.execute("SELECT codigo_produto, preco_tabela FROM organizado_produtos"))
    with PLANILHA.open(encoding="utf-8") as f:
        linhas = list(csv.DictReader(f, delimiter=";"))

    erros, avisos = revisar(linhas, clientes, precos)
    print(f"Planilha revisada: {len(linhas)} linhas\n")
    print(f"⛔ Erros que impedem o envio ({len(erros)}):")
    print("\n".join(f"   - {e}" for e in erros) or "   nenhum")
    print(f"\n⚠️ Pontos para conferir ({len(avisos)}):")
    print("\n".join(f"   - {a}" for a in avisos) or "   nenhum")

    if erros and "--liberar" not in sys.argv:
        print("\nArquivo NÃO gerado. Corrija os erros ou rode com --liberar.")
        sys.exit(1)
    print(f"\nArquivo gerado: {gerar_txt(linhas)}")


if __name__ == "__main__":
    main()

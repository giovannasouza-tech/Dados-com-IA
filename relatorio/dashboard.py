"""Gera dashboard/painel.svg: o painel comercial como imagem, para ver direto no GitHub.

Em produção esse painel é o Power BI; aqui é um SVG feito só com Python,
lendo as mesmas views relatorio_*.
"""
import sqlite3
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FUNDO, TINTA, TINTA2, GRADE, AZUL = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6"
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def reais(v, curto=False):
    if curto:
        return f"R$ {v / 1000:,.0f} mil".replace(",", ".")
    return f"R$ {v:,.0f}".replace(",", ".")


def texto(x, y, conteudo, tam=13, cor=TINTA, peso=400, ancora="start"):
    return (f'<text x="{x}" y="{y}" font-size="{tam}" fill="{cor}" font-weight="{peso}" '
            f'text-anchor="{ancora}">{escape(str(conteudo))}</text>')


def main():
    con = sqlite3.connect(RAIZ / "demo.db")
    total, notas, clientes = con.execute(
        "SELECT sum(valor_total), count(DISTINCT numero_nf), count(DISTINCT codigo_cliente) FROM relatorio_vendas").fetchone()
    meses = con.execute("SELECT mes, vendas FROM relatorio_vendas_mes ORDER BY mes").fetchall()
    top = con.execute("""SELECT cliente, sum(valor_total) v FROM relatorio_vendas
                         GROUP BY cliente ORDER BY v DESC LIMIT 6""").fetchall()
    linhas = con.execute("""SELECT linha, sum(valor_total) v FROM relatorio_vendas
                            GROUP BY linha ORDER BY v DESC""").fetchall()

    L, A = 960, 640
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{L}" height="{A}" viewBox="0 0 {L} {A}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif">',
         f'<rect width="{L}" height="{A}" rx="12" fill="{FUNDO}"/>',
         texto(32, 44, "Painel comercial · dados fictícios", 20, peso=600),
         texto(32, 66, f"{MESES[int(meses[0][0][5:]) - 1]}–{MESES[int(meses[-1][0][5:]) - 1]}/{meses[-1][0][:4]} · "
                       "gerado por relatorio/dashboard.py a partir das views relatorio_*", 12, TINTA2)]

    # Indicadores
    kpis = [("Vendas", reais(total)), ("Notas de venda", f"{notas:,}".replace(",", ".")),
            ("Ticket médio", reais(total / notas)), ("Clientes que compraram", str(clientes))]
    for i, (rotulo, valor) in enumerate(kpis):
        x = 32 + i * 228
        s.append(f'<rect x="{x}" y="88" width="212" height="76" rx="8" fill="#ffffff" stroke="{GRADE}"/>')
        s.append(texto(x + 16, 114, rotulo, 12, TINTA2))
        s.append(texto(x + 16, 146, valor, 24, peso=600))

    # Vendas por mês (barras verticais)
    x0, y0, larg, alt = 84, 230, 490, 330
    s.append(texto(32, 206, "Vendas por mês", 14, peso=600))
    maximo = max(v for _, v in meses)
    escala = maximo * 1.1
    for frac in (0, 0.5, 1):
        y = y0 + alt - alt * frac * maximo / escala
        s.append(f'<line x1="{x0}" x2="{x0 + larg}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRADE}"/>')
        s.append(texto(x0 - 6, y + 4, reais(maximo * frac, True) if frac else "0", 10, TINTA2, ancora="end"))
    passo = larg / len(meses)
    destaque = {0, len(meses) - 1, max(range(len(meses)), key=lambda i: meses[i][1])}
    for i, (mes, v) in enumerate(meses):
        h = alt * v / escala
        x = x0 + i * passo + 6
        w = passo - 12
        y = y0 + alt - h
        s.append(f'<path d="M{x:.1f},{y0 + alt} V{y + 4:.1f} Q{x:.1f},{y:.1f} {x + 4:.1f},{y:.1f} H{x + w - 4:.1f} '
                 f'Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + 4:.1f} V{y0 + alt} Z" fill="{AZUL}">'
                 f'<title>{MESES[int(mes[5:]) - 1]}/{mes[:4]}: {reais(v)}</title></path>')
        s.append(texto(x + w / 2, y0 + alt + 16, MESES[int(mes[5:]) - 1], 11, TINTA2, ancora="middle"))
        if i in destaque:
            s.append(texto(x + w / 2, y - 6, reais(v, True), 10, TINTA, ancora="middle"))

    # Maiores clientes e vendas por linha (barras horizontais)
    def ranking(titulo, dados, y_inicio, n):
        s.append(texto(612, y_inicio, titulo, 14, peso=600))
        maior = dados[0][1]
        for i, (nome, v) in enumerate(dados[:n]):
            y = y_inicio + 22 + i * 30
            w = 200 * v / maior
            s.append(texto(612, y + 11, nome.replace(" Fictício", ""), 11, TINTA2))
            s.append(f'<rect x="{612}" y="{y + 16}" width="{w:.1f}" height="8" rx="4" fill="{AZUL}">'
                     f'<title>{escape(nome)}: {reais(v)}</title></rect>')
            s.append(texto(612 + w + 8, y + 24, reais(v, True), 10))

    ranking("Clientes que mais compraram", top, 206, 5)
    ranking("Vendas por linha de produto", linhas, 410, 5)

    s.append("</svg>")
    destino = RAIZ / "dashboard" / "painel.svg"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text("\n".join(s), encoding="utf-8")
    print(f"Painel salvo em {destino}")


if __name__ == "__main__":
    main()

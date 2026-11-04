# Dados com IA

**BI de ponta a ponta construído com IA: do ERP ao Power BI, com carga automática, banco em camadas e automações de negócio.**

Sou Giovanna, analista de dados júnior e estudante de Banco de Dados. Este repositório é uma **versão de demonstração** de um projeto que construí e mantenho em produção numa distribuidora de bebidas. A arquitetura, as regras e a lógica são as mesmas; o código foi reescrito do zero e **todos os dados são fictícios**.

---

## O problema

Vendas, compras e estoque ficavam só dentro do ERP. Os relatórios eram montados à mão em Excel, e o envio mensal de sell-out para a indústria era rejeitado por erros na planilha (a mesma nota para dois clientes, cliente sem cadastro, data inválida).

## O que construí

```
ERP (API)  →  Azure Functions (todo dia às 8h)  →  Azure SQL  →  Power BI
                                                 bruto → organizado → relatorio
```

| Peça | O que faz | Na demo |
| --- | --- | --- |
| **Carga automática** | Lê a API do ERP página por página, só leitura, e grava a resposta original | [`carga/carregar.py`](carga/carregar.py) |
| **Banco em camadas** | `bruto` protegido contra alteração, `organizado` refeito a cada carga, histórico de exclusões | [`sql/`](sql/) |
| **Relatório comercial** | Vendas por mês com variação, curva ABC de clientes, clientes parados | [`relatorio/gerar_relatorio.py`](relatorio/gerar_relatorio.py) |
| **Validador de sell-out** | Revisa a planilha antes de gerar o arquivo: ⛔ barra erros e ⚠️ aponta o que conferir | [`automacoes/validar_sellout.py`](automacoes/validar_sellout.py) |
| **Regras do agente de IA** | O que o agente pode e não pode fazer, escrito como prompt | [`CLAUDE.md`](CLAUDE.md) |

Em produção, o Power BI lê as views `relatorio` e mostra três páginas: Visão geral, Clientes e Produtos.

## Rodar a demo

Só precisa de Python 3.10 ou mais novo, sem instalar nada:

```bash
python rodar_demo.py
```

Saída esperada (resumida):

```
ERP simulado: 80 clientes, 40 produtos, 935 notas
Carga 1 concluída: 2404 itens de venda, R$ 3,194,206.75; 0 exclusões registradas.
10 meses · 6 de 63 clientes fazem 80% das vendas · 36 clientes parados há mais de 60 dias.

⛔ Erros que impedem o envio (5):
   - NF 20878 aparece para 2 clientes (1011, 9999)
   - NF 20876 aparece para 2 clientes (1011, 1012)
   - linha 5: cliente 9999 sem cadastro no ERP
   - linha 7: campo obrigatório em branco (codigo_produto)
   - linha 9: data inválida (2026-02-30)

⚠️ Pontos para conferir (3):
   - linha 11: preço R$ 235.71 contra R$ 78.57 de tabela
   - linha 13: quantidade 900 fora do comum
   - linha 15: venda num domingo (2026-10-25)

Arquivo NÃO gerado. Corrija os erros ou rode com --liberar.
```

Os relatórios ficam em `saida/`. Para ver a proteção do bruto, tente apagar uma linha de `bruto_paginas` em `demo.db`: o banco recusa.

## Como usei IA

- **Claude Code como par de programação:** todo o projeto foi construído conversando com o agente. Cada mudança vira um pull request que eu reviso antes de aprovar.
- **Prompt engineering como regra de negócio:** o [`CLAUDE.md`](CLAUDE.md) define limites que o agente segue sempre. Entre eles: o ERP é só leitura, o histórico nunca é apagado, a revisão vem antes de gerar e nenhum dado é inventado.
- **Agente com ferramentas:** no projeto real, o agente consulta o ERP, o banco e o GitHub por conectores, e investiga divergências nota por nota.

## Mais detalhes

- [Arquitetura](docs/arquitetura.md): cada peça, as três camadas e por que cada escolha.
- [Decisões](docs/decisoes.md): o que foi decidido e por quê.

## Tecnologias

Python · SQL · Azure Functions · Azure SQL · Key Vault · Power BI (PBIP/TMDL) · API REST · Git/GitHub · Claude Code

---

[LinkedIn](https://linkedin.com/in/giovannadesouzapereira) · giovannasouza.tech@gmail.com

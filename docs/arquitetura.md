# Arquitetura

## Em produção

```
ERP (API)  →  Azure Functions (Python, todo dia às 8h)  →  Azure SQL  →  Power BI
```

| Peça | Papel | Por quê |
| --- | --- | --- |
| **API do ERP** | Fonte de vendas, compras, estoque e clientes | Só métodos de leitura: o pipeline nunca altera o ERP |
| **Azure Functions** (Flex Consumption) | Roda a carga em horário fixo e avisa por e-mail se falhar | Custa centavos, sem servidor para manter e sem endereço público |
| **Azure SQL** (serverless) | Guarda as três camadas | "Dorme" quando parado e cabe na cota gratuita |
| **Key Vault** e identidade gerenciada | Chaves do ERP e acesso ao banco sem senha no código | Nenhum segredo no repositório |
| **Power BI** (PBIP) | Painel comercial, lendo as views `relatorio` | Projeto em texto (TMDL), versionado no Git |

## As três camadas

| Camada | O que guarda | Regra |
| --- | --- | --- |
| `bruto` | A resposta do ERP inteira, como veio, página por página | Só acrescenta. O banco recusa UPDATE e DELETE (`DENY` em produção, trigger na demo) |
| `organizado` | Tabelas limpas, com as colunas que os relatórios usam | Refeitas a cada carga a partir do bruto. A exceção é `exclusoes`, que só cresce |
| `relatorio` | Views com os nomes de coluna que o Power BI espera | Trocar a origem dos dados não muda o painel |

O bruto é o seguro do projeto: se uma regra de limpeza estiver errada, ou se a empresa trocar de ERP, tudo pode ser refeito sem consultar a fonte de novo.

## Na demo

Para rodar em qualquer computador, a demo troca a API pelos JSON em `dados_exemplo/erp_simulado/` (no mesmo formato paginado) e o Azure SQL por um arquivo SQLite. A lógica das camadas é a mesma.

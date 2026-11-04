# Decisões e por quê

**Sem Data Lake no começo.** O plano inicial guardava a resposta original do ERP num Data Lake. Guardar no próprio banco (camada `bruto`) preserva o mesmo histórico com uma peça a menos para criar, pagar e manter.

**Bruto protegido pelo banco, não só pelo código.** Uma regra escrita só no código pode ser esquecida num script novo. Com `DENY` (e o trigger na demo), o próprio banco recusa apagar ou alterar o histórico.

**Histórico de exclusões.** Quando uma nota some do ERP entre duas cargas, ela vai para `organizado.exclusoes` com o último conteúdo conhecido. Isso responde à pergunta "esse número mudou por quê?".

**Revisar antes de gerar.** O envio de sell-out barra o que é impossível (a mesma NF para dois clientes) e só aponta o que é estranho (preço fora da tabela). A planilha de quem conhece o negócio é a referência: um ajuste feito de propósito não é "corrigido" pelo programa.

**Não inventar dado.** Se falta um campo, o programa aponta e consulta a fonte. Nunca preenche com um valor padrão.

**Custo.** A infraestrutura inteira (banco serverless, Function e Key Vault) fica em poucos reais por mês, com alerta de orçamento.

**IA como par de programação.** O código foi escrito com o Claude Code, que segue as regras do `CLAUDE.md`. Toda mudança vira um pull request revisado antes de entrar.

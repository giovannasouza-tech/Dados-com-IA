# Regras para o agente de IA neste repositório

Este arquivo é lido pelo Claude Code em toda sessão. No projeto real, regras como estas transformam um assistente genérico num agente que conhece o negócio.

## Dados
1. **Só dados fictícios aqui.** Nenhum nome de cliente, produto, servidor, chave ou valor real. Na dúvida, não entra.
2. **Não inventar dado.** Se faltar um valor, aponte e diga onde buscar. Nunca preencha com um padrão.

## ERP
3. **O ERP é só leitura.** Use só métodos de consulta. Se algo precisar mudar lá, mostre o que mudar e a pessoa faz manualmente.

## Banco
4. **A camada `bruto` nunca é apagada nem alterada**, só recebe linhas novas. `organizado` e `relatorio` podem ser refeitas a partir dela.
5. **PR que mexe no banco leva "⚠️ MEXE NO BANCO" no título** e diz o que muda.

## Sell-out
6. **Revisar antes de gerar.** Mostre primeiro os ⛔ erros que impedem o envio e os ⚠️ pontos para conferir. Só gere o arquivo sem erros ou com a liberação da pessoa.
7. **A planilha de quem conhece o negócio é a referência.** Um ajuste feito de propósito fica como está. O impossível barra o envio.

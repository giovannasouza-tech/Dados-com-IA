DROP VIEW IF EXISTS relatorio_vendas;
CREATE VIEW relatorio_vendas AS
SELECT n.numero_nf,
       n.data_emissao,
       substr(n.data_emissao, 1, 7)          AS mes,
       c.codigo_cliente,
       c.nome                                AS cliente,
       c.cidade,
       p.codigo_produto,
       p.descricao                           AS produto,
       p.linha,
       i.quantidade,
       i.valor_unitario,
       round(i.quantidade * i.valor_unitario, 2) AS valor_total
FROM organizado_notas n
JOIN organizado_itens    i ON i.numero_nf = n.numero_nf
JOIN organizado_clientes c ON c.codigo_cliente = n.codigo_cliente
JOIN organizado_produtos p ON p.codigo_produto = i.codigo_produto;

DROP VIEW IF EXISTS relatorio_vendas_mes;
CREATE VIEW relatorio_vendas_mes AS
SELECT mes,
       round(sum(valor_total), 2)                              AS vendas,
       count(DISTINCT numero_nf)                               AS notas,
       count(DISTINCT codigo_cliente)                          AS clientes,
       round(sum(valor_total) / count(DISTINCT numero_nf), 2)  AS ticket_medio
FROM relatorio_vendas
GROUP BY mes;

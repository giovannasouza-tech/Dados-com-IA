-- Banco em três camadas (na demo em SQLite; em produção, Azure SQL com schemas).
--   bruto       cópia original de tudo o que veio do ERP. Só recebe linhas novas.
--   organizado  tabelas limpas, refeitas a cada carga a partir do bruto.
--   relatorio   views prontas para o Power BI.

CREATE TABLE IF NOT EXISTS bruto_paginas (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    carga_id     INTEGER NOT NULL,
    entidade     TEXT    NOT NULL,
    pagina       INTEGER NOT NULL,
    hash         TEXT    NOT NULL,
    carregado_em TEXT    NOT NULL,
    json         TEXT    NOT NULL
);

-- Proteção do bruto: nenhuma linha pode ser alterada ou apagada.
-- Em produção isso é feito com DENY UPDATE, DELETE para o usuário da carga.
CREATE TRIGGER IF NOT EXISTS bruto_sem_update BEFORE UPDATE ON bruto_paginas
BEGIN SELECT RAISE(ABORT, 'A área bruto só recebe linhas novas'); END;
CREATE TRIGGER IF NOT EXISTS bruto_sem_delete BEFORE DELETE ON bruto_paginas
BEGIN SELECT RAISE(ABORT, 'A área bruto nunca é apagada'); END;

-- Histórico do que sumiu do ERP entre uma carga e outra. Só cresce.
CREATE TABLE IF NOT EXISTS organizado_exclusoes (
    entidade      TEXT NOT NULL,
    chave         TEXT NOT NULL,
    percebido_em  TEXT NOT NULL,
    ultimo_json   TEXT NOT NULL
);

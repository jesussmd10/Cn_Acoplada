CREATE TABLE tickets (
    ticket_id         VARCHAR(36) PRIMARY KEY,
    title             VARCHAR(255) NOT NULL,
    description       TEXT,
    status            VARCHAR(20) DEFAULT 'to do' CHECK (status IN ('to do', 'doing', 'done', 'blocked')),
    priority          VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critic')),
    position          INTEGER DEFAULT 0,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date          DATE,
    tags              JSONB
);
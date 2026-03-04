-- Включаем расширение для UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Основная таблица
CREATE TABLE pages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT NOT NULL UNIQUE,
    title TEXT,
    html_content TEXT,
    crawl_depth INTEGER NOT NULL DEFAULT 0,
    http_status_code INTEGER,
    parent_task_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT fk_parent_task 
        FOREIGN KEY (parent_task_id) 
        REFERENCES pages(id) 
        ON DELETE SET NULL,
    
    CONSTRAINT valid_url_length 
        CHECK (char_length(url) <= 2048)
);

-- Индексы
CREATE INDEX idx_pages_url ON pages(url);
CREATE INDEX idx_pages_created_at ON pages(created_at);
CREATE INDEX idx_pages_parent ON pages(parent_task_id);

-- Индексы для поиска (требуют расширение pg_trgm)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_pages_url_trgm ON pages USING gin (url gin_trgm_ops);
CREATE INDEX idx_pages_title_trgm ON pages USING gin (title gin_trgm_ops);

-- Триггер для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_pages
    BEFORE UPDATE ON pages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
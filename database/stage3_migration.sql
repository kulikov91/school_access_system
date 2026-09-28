-- Финальное расширение БД. Без удаления существующих данных.
ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS old_value TEXT;
ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS new_value TEXT;

CREATE INDEX IF NOT EXISTS idx_tags_uid ON tags(uid);
CREATE INDEX IF NOT EXISTS idx_access_log_event_type ON access_log(event_type);

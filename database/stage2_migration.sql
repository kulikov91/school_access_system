-- Этап 2. Безопасное расширение существующей БД: данные Stage 1 не удаляются.
CREATE TABLE IF NOT EXISTS users (
    id_user INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role VARCHAR(30) NOT NULL,
    id_parent INTEGER NULL REFERENCES parents(id_parent) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_user_role CHECK (role IN ('sysadmin', 'director', 'deputy', 'security', 'parent'))
);

CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

CREATE TABLE IF NOT EXISTS audit_log (
    id_audit INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_user INTEGER NULL REFERENCES users(id_user) ON DELETE SET NULL,
    action VARCHAR(80) NOT NULL,
    object_type VARCHAR(80),
    object_id VARCHAR(100),
    details TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(id_user);

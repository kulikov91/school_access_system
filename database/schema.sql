DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS access_log CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS student_parents CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS parents CASCADE;
DROP TABLE IF EXISTS students CASCADE;

CREATE TABLE students (
    id_student INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    class_name VARCHAR(20) NOT NULL
);

CREATE INDEX idx_students_last_name ON students(last_name);
CREATE INDEX idx_students_class_name ON students(class_name);

CREATE TABLE parents (
    id_parent INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL
);

CREATE INDEX idx_parents_phone ON parents(phone);
CREATE INDEX idx_parents_email ON parents(email);

CREATE TABLE student_parents (
    id_student INTEGER NOT NULL REFERENCES students(id_student) ON DELETE CASCADE,
    id_parent INTEGER NOT NULL REFERENCES parents(id_parent) ON DELETE CASCADE,
    relationship VARCHAR(50) NOT NULL,
    PRIMARY KEY (id_student, id_parent)
);

CREATE INDEX idx_student_parents_parent ON student_parents(id_parent);

CREATE TABLE employees (
    id_employee INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    position VARCHAR(100) NOT NULL
);

CREATE INDEX idx_employees_last_name ON employees(last_name);

-- В MVP метка принадлежит только ученику.
CREATE TABLE tags (
    id_tag INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_student INTEGER NOT NULL REFERENCES students(id_student) ON DELETE CASCADE,
    uid VARCHAR(100) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    CONSTRAINT chk_tag_status CHECK (status IN ('active', 'blocked'))
);

CREATE INDEX idx_tags_student ON tags(id_student);

CREATE TABLE access_log (
    id_record INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_tag INTEGER NOT NULL REFERENCES tags(id_tag),
    event_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(10) NOT NULL,
    CONSTRAINT chk_event_type CHECK (event_type IN ('IN', 'OUT'))
);

CREATE INDEX idx_access_log_tag ON access_log(id_tag);
CREATE INDEX idx_access_log_event_time ON access_log(event_time);

CREATE TABLE notifications (
    id_notification INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_parent INTEGER NOT NULL REFERENCES parents(id_parent),
    id_record INTEGER NOT NULL REFERENCES access_log(id_record),
    text TEXT NOT NULL,
    sent_at TIMESTAMP NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'created',
    CONSTRAINT chk_notification_status
        CHECK (status IN ('created', 'sent', 'error'))
);

CREATE INDEX idx_notifications_parent ON notifications(id_parent);
CREATE INDEX idx_notifications_record ON notifications(id_record);

-- Тестовые данные
INSERT INTO students (last_name, first_name, middle_name, class_name)
VALUES ('Иванов', 'Иван', 'Иванович', '7А');

INSERT INTO parents (last_name, first_name, middle_name, phone, email)
VALUES ('Иванова', 'Мария', 'Петровна', '+79990000000', 'ivanova@example.com');

INSERT INTO student_parents (id_student, id_parent, relationship)
VALUES (1, 1, 'мать');

INSERT INTO tags (id_student, uid, status)
VALUES (1, 'A001', 'active');

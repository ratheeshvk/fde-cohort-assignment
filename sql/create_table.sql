-- Placeholder table for classroom assignment.
-- Rename the table and columns when requirements are finalized.

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'todo',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Useful later if you rename often during class:
-- DROP TABLE IF EXISTS tasks;

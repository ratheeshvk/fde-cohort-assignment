-- =====================================================================
-- Performance Review Database (PostgreSQL)
-- Tables: employees, review_periods, performance_reviews, admins
-- =====================================================================

-- Optional: create and connect to a dedicated database
-- CREATE DATABASE performance_db;
-- \c performance_db

BEGIN;

-- Drop in dependency order (safe to re-run)
DROP TABLE IF EXISTS performance_reviews;
DROP TABLE IF EXISTS review_periods;
DROP TABLE IF EXISTS employees;

-- ---------------------------------------------------------------------
-- employees
-- ---------------------------------------------------------------------
CREATE TABLE employees (
    id           SERIAL        PRIMARY KEY,
    employee_id  VARCHAR(20)   NOT NULL UNIQUE,          -- e.g. EMP101
    name         VARCHAR(100)  NOT NULL,
    department   VARCHAR(100)  NULL,
    email        VARCHAR(100)  NULL,
    status       VARCHAR(20)   DEFAULT 'Active'
                 CHECK (status IN ('Active', 'Inactive'))
);

-- ---------------------------------------------------------------------
-- review_periods
-- ---------------------------------------------------------------------
CREATE TABLE review_periods (
    id          SERIAL       PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL,                   -- e.g. H1 2026
    start_date  DATE         NOT NULL,
    end_date    DATE         NOT NULL,
    status      VARCHAR(20)  DEFAULT 'Open'
                CHECK (status IN ('Open', 'Closed')),
    CONSTRAINT chk_period_dates CHECK (end_date >= start_date)
);

-- ---------------------------------------------------------------------
-- performance_reviews
-- ---------------------------------------------------------------------
CREATE TABLE performance_reviews (
    id               SERIAL        PRIMARY KEY,
    employee_id      INTEGER       NOT NULL
                     REFERENCES employees(id) ON DELETE CASCADE,
    period_id        INTEGER       NOT NULL
                     REFERENCES review_periods(id) ON DELETE CASCADE,
    quality_rating   INTEGER       NOT NULL CHECK (quality_rating  BETWEEN 1 AND 5),
    delivery_rating  INTEGER       NOT NULL CHECK (delivery_rating BETWEEN 1 AND 5),
    teamwork_rating  INTEGER       NOT NULL CHECK (teamwork_rating BETWEEN 1 AND 5),
    -- Calculated automatically from the three ratings
    average_rating   DECIMAL(3,2)  GENERATED ALWAYS AS (
                         ROUND((quality_rating + delivery_rating + teamwork_rating) / 3.0, 2)
                     ) STORED,
    comments         TEXT,
    created_at       TIMESTAMP     DEFAULT NOW(),
    -- One review per employee per period
    CONSTRAINT uq_employee_period UNIQUE (employee_id, period_id)
);

-- Helpful indexes for lookups
CREATE INDEX idx_reviews_employee ON performance_reviews(employee_id);
CREATE INDEX idx_reviews_period   ON performance_reviews(period_id);

-- ---------------------------------------------------------------------
-- admins (login accounts; not dropped above, so re-running keeps logins)
-- Only an argon2 hash is stored. Create the first admin with backend/init_db.py.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS admins (
    id             SERIAL       PRIMARY KEY,
    username       VARCHAR(50)  NOT NULL UNIQUE,
    password_hash  TEXT         NOT NULL,
    created_at     TIMESTAMP    DEFAULT NOW()
);

COMMIT;

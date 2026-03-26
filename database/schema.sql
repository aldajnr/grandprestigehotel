PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  username      TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role          TEXT NOT NULL CHECK(role IN ('Admin','Manager','Receptionist')),
  created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS guests (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name      TEXT NOT NULL,
  national_id    TEXT NOT NULL,
  phone          TEXT NOT NULL,
  room           TEXT NOT NULL,
  checkin_date   TEXT NOT NULL,
  checkout_date  TEXT NOT NULL,
  payment_method TEXT,
  notes          TEXT,
  status         TEXT NOT NULL DEFAULT 'active',
  cancelled_by   INTEGER,
  cancel_reason  TEXT,
  created_by     INTEGER NOT NULL,
  created_at     TEXT NOT NULL,
  FOREIGN KEY(created_by) REFERENCES users(id),
  FOREIGN KEY(cancelled_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id    INTEGER,
  username   TEXT,
  role       TEXT,
  action     TEXT NOT NULL,
  record_id  TEXT,
  ip_address TEXT,
  notes      TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_guests_created_at ON guests(created_at);
CREATE INDEX IF NOT EXISTS idx_guests_status ON guests(status);
CREATE INDEX IF NOT EXISTS idx_guests_room ON guests(room);

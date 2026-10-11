CREATE TABLE items (
    id          serial PRIMARY KEY,
    name        text NOT NULL,
    description text NOT NULL DEFAULT '',
    weight_kg   numeric(5,2) NOT NULL CHECK (weight_kg > 0),
    price       numeric(10,2) NOT NULL CHECK (price > 0),
    quantity    integer NOT NULL DEFAULT 0,
    half_of     integer REFERENCES items(id),
    is_active   boolean NOT NULL DEFAULT true,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX items_active_name_uq ON items (lower(name)) WHERE is_active;

CREATE TABLE admin_users (
    id            serial PRIMARY KEY,
    username      text NOT NULL UNIQUE,
    password_hash text NOT NULL,
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE audit_log (
    id         bigserial PRIMARY KEY,
    actor      text NOT NULL,
    action     text NOT NULL,
    item_id    integer,
    detail     jsonb NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now()
);

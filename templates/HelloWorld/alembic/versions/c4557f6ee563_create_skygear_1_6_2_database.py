"""create skygear 1.6.2 database

Revision ID: c4557f6ee563
Revises:
Create Date: 2018-11-09 17:35:40.010974

"""
from alembic import op
import sqlalchemy as sa


from skygear_helper import SCHEMA_NAME

# revision identifiers, used by Alembic.
revision = 'c4557f6ee563'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(sa.text(
        'CREATE SCHEMA IF NOT EXISTS {schema_name}'.format(
            schema_name=SCHEMA_NAME
        )
    ))
    op.execute(sa.text(
        'SET search_path TO {schema_name}, public'.format(
            schema_name=SCHEMA_NAME
        )
    ))
    op.execute(sa.text('''
        CREATE TABLE IF NOT EXISTS _version (
            version_num character varying(32) NOT NULL
        )
    '''))

    # pylama:ignore=E501
    op.execute(sa.text('''
CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;
CREATE EXTENSION IF NOT EXISTS citext WITH SCHEMA public;
CREATE TABLE IF NOT EXISTS public.pending_notification (
    id SERIAL NOT NULL PRIMARY KEY,
    op text NOT NULL,
    appname text NOT NULL,
    recordtype text NOT NULL,
    record jsonb NOT NULL
);
CREATE OR REPLACE FUNCTION public.notify_record_change() RETURNS TRIGGER AS $$
    DECLARE
        affected_record RECORD;
        inserted_id integer;
    BEGIN
        IF (TG_OP = 'DELETE') THEN
            affected_record := OLD;
        ELSE
            affected_record := NEW;
        END IF;
        INSERT INTO public.pending_notification (op, appname, recordtype, record)
            VALUES (TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME, row_to_json(affected_record)::jsonb)
            RETURNING id INTO inserted_id;
        PERFORM pg_notify('record_change', inserted_id::TEXT);
        RETURN affected_record;
    END;
$$ LANGUAGE plpgsql;
CREATE TABLE IF NOT EXISTS _auth (
    id text PRIMARY KEY,
    password text,
    provider_info jsonb,
    token_valid_since timestamp without time zone,
    last_seen_at timestamp without time zone,
    disabled boolean NOT NULL DEFAULT FALSE,
    disabled_message text,
    disabled_expiry timestamp without time zone
);
CREATE TABLE IF NOT EXISTS _role (
    id text PRIMARY KEY,
    by_default boolean DEFAULT FALSE,
    is_admin boolean DEFAULT FALSE
);
CREATE TABLE IF NOT EXISTS _auth_role (
    auth_id text REFERENCES _auth (id) NOT NULL,
    role_id text REFERENCES _role (id) NOT NULL,
    PRIMARY KEY (auth_id, role_id)
);
CREATE TABLE IF NOT EXISTS _asset (
    id text PRIMARY KEY,
    content_type text NOT NULL,
    size bigint NOT NULL
);
CREATE TABLE IF NOT EXISTS _device (
    id text PRIMARY KEY,
    auth_id text REFERENCES _auth (id),
    type text NOT NULL,
    token text,
    topic text,
    last_registered_at timestamp without time zone NOT NULL,
    UNIQUE (auth_id, type, token)
);
CREATE INDEX IF NOT EXISTS _device_token_last_registered_at_idx ON _device (token, last_registered_at);
CREATE TABLE IF NOT EXISTS _subscription (
    id text NOT NULL,
    auth_id text NOT NULL,
    device_id text REFERENCES _device (id) ON DELETE CASCADE NOT NULL,
    type text NOT NULL,
    notification_info jsonb,
    query jsonb,
    PRIMARY KEY(auth_id, device_id, id)
);
CREATE TABLE IF NOT EXISTS _friend (
    left_id text NOT NULL,
    right_id text REFERENCES _auth (id) NOT NULL,
    PRIMARY KEY(left_id, right_id)
);
CREATE TABLE IF NOT EXISTS _follow (
    left_id text NOT NULL,
    right_id text REFERENCES _auth (id) NOT NULL,
    PRIMARY KEY(left_id, right_id)
);
CREATE TABLE IF NOT EXISTS _record_creation (
    record_type text NOT NULL,
    role_id text,
    UNIQUE (record_type, role_id),
    FOREIGN KEY (role_id) REFERENCES _role(id)
);
CREATE INDEX IF NOT EXISTS _record_creation_unique_record_type ON _record_creation (record_type);
CREATE TABLE IF NOT EXISTS _record_default_access (
    record_type text NOT NULL,
    default_access jsonb,
    UNIQUE (record_type)
);
CREATE INDEX IF NOT EXISTS _record_default_access_unique_record_type ON _record_default_access (record_type);
CREATE TABLE IF NOT EXISTS _record_field_access (
    record_type text NOT NULL,
    record_field text NOT NULL,
    user_role text NOT NULL,
    writable boolean NOT NULL,
    readable boolean NOT NULL,
    comparable boolean NOT NULL,
    discoverable boolean NOT NULL,
    PRIMARY KEY (record_type, record_field, user_role)
);
CREATE TABLE IF NOT EXISTS "user" (
    _id text,
    _database_id text,
    _owner_id text,
    _access jsonb,
    _created_at timestamp without time zone NOT NULL,
    _created_by text,
    _updated_at timestamp without time zone NOT NULL,
    _updated_by text,
    username citext,
    email citext,
    last_login_at timestamp without time zone,
    PRIMARY KEY(_id, _database_id, _owner_id),
    UNIQUE (_id)
);
ALTER TABLE "user" DROP CONSTRAINT IF EXISTS auth_record_keys_user_username_key;
ALTER TABLE "user" ADD CONSTRAINT auth_record_keys_user_username_key UNIQUE (username);
ALTER TABLE "user" DROP CONSTRAINT IF EXISTS auth_record_keys_user_email_key;
ALTER TABLE "user" ADD CONSTRAINT auth_record_keys_user_email_key UNIQUE (email);
CREATE OR REPLACE VIEW _user AS
    SELECT
        a.id,
        a.password,
        u.username,
        u.email,
        a.provider_info AS auth,
        a.token_valid_since,
        u.last_login_at,
        a.last_seen_at
    FROM _auth AS a
    JOIN "user" AS u ON u._id = a.id;
DELETE FROM _record_field_access;
INSERT INTO _record_field_access
  (record_type, record_field, user_role, writable, readable, comparable, discoverable)
VALUES
  ('user', 'username', '_any_user', 'FALSE', 'TRUE', 'TRUE', 'TRUE');
INSERT INTO _record_field_access
  (record_type, record_field, user_role, writable, readable, comparable, discoverable)
VALUES
  ('user', 'username', '_owner', 'TRUE', 'TRUE', 'TRUE', 'TRUE');
INSERT INTO _record_field_access
  (record_type, record_field, user_role, writable, readable, comparable, discoverable)
VALUES
  ('user', 'email', '_any_user', 'FALSE', 'TRUE', 'TRUE', 'TRUE');
INSERT INTO _record_field_access
  (record_type, record_field, user_role, writable, readable, comparable, discoverable)
VALUES
  ('user', 'email', '_owner', 'TRUE', 'TRUE', 'TRUE', 'TRUE');
CREATE TABLE IF NOT EXISTS _sso_oauth (
  user_id text NOT NULL,
  provider text NOT NULL,
  principal_id text NOT NULL,
  token_response jsonb,
  profile jsonb,
  _created_at timestamp without time zone NOT NULL,
  _updated_at timestamp without time zone NOT NULL,
  PRIMARY KEY (provider, principal_id),
  UNIQUE (user_id, provider)
);
CREATE TABLE IF NOT EXISTS _sso_custom_token (
  user_id text NOT NULL PRIMARY KEY,
  principal_id text NOT NULL,
  _created_at timestamp without time zone NOT NULL,
  UNIQUE (principal_id)
);
CREATE TABLE IF NOT EXISTS _password_history (
    id TEXT PRIMARY KEY,
    auth_id TEXT NOT NULL,
    password TEXT NOT NULL,
    logged_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);
CREATE INDEX IF NOT EXISTS _password_history_auth_id_logged_at ON _password_history (auth_id, logged_at DESC);
CREATE TABLE IF NOT EXISTS _verify_code (
    id TEXT PRIMARY KEY,
    auth_id TEXT NOT NULL,
    record_key TEXT NOT NULL,
    record_value TEXT NOT NULL,
    code TEXT NOT NULL,
    consumed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);
CREATE INDEX IF NOT EXISTS _verify_code_auth_id_code_consumed ON _verify_code (auth_id, code, consumed);
    '''))

    # set the version number
    op.execute(sa.text('''
        DELETE FROM _version;
        INSERT INTO _version (version_num) VALUES ('{version_num}')
    '''.format(version_num='7469be11899e')))


def downgrade():
    op.execute(sa.text('''
        DROP SCHEMA IF EXISTS {schema_name} CASCADE
    '''.format(schema_name=SCHEMA_NAME)))

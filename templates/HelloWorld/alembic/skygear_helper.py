import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


SCHEMA_NAME = os.environ['SCHEMA_NAME']


def _build_fkey(src_col, dst_table):
    return 'fk_' + src_col + '_' + dst_table + '_id'


def make_asset_fkey():
    return sa.ForeignKey('{}._asset.id'.format(SCHEMA_NAME))


def add_fkey(src_table, src_col, dst_table):
    fk_name = _build_fkey(src_col, dst_table)
    op.create_foreign_key(
        fk_name,
        src_table,
        dst_table,
        [src_col],
        ['_id'],
        source_schema=SCHEMA_NAME,
        referent_schema=SCHEMA_NAME,
    )


def make_skygear_columns():
    return [
        sa.Column('_id', sa.Text, unique=True, primary_key=True),
        sa.Column('_database_id', sa.Text, primary_key=True),
        sa.Column('_owner_id', sa.Text, primary_key=True),
        sa.Column('_access', JSONB),
        sa.Column('_created_at', sa.DateTime, nullable=False),
        sa.Column('_created_by', sa.Text),
        sa.Column('_updated_at', sa.DateTime, nullable=False),
        sa.Column('_updated_by', sa.Text),
    ]

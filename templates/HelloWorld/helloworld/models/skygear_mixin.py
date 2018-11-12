import uuid

import arrow
import sqlalchemy as sa
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy_utils import ArrowType

from .skygear import SGAccessControlList


def _id_factory():
    return str(uuid.uuid4())


def _now():
    return arrow.utcnow()


class SkygearRecordMixin:
    id = sa.Column(
        '_id',
        sa.Text,
        primary_key=True,
        default=lambda: _id_factory()
    )
    database_id = sa.Column(
        '_database_id',
        sa.Text,
        nullable=False,
        default=''
    )
    owner_id = sa.Column('_owner_id', sa.Text, nullable=False, default='_god')
    access = sa.Column(
        '_access',
        MutableList.as_mutable(SGAccessControlList),
        default=lambda: MutableList(),
    )
    created_by = sa.Column('_created_by', sa.Text, default='')
    created_at = sa.Column(
        '_created_at',
        ArrowType,
        default=lambda: _now(),
        server_default=sa.func.now(),
        nullable=False,
    )
    updated_by = sa.Column('_updated_by', sa.Text, default='')
    updated_at = sa.Column(
        '_updated_at',
        ArrowType,
        default=lambda: _now(),
        server_default=sa.func.now(),
        onupdate=lambda: _now(),
        nullable=False,
    )

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

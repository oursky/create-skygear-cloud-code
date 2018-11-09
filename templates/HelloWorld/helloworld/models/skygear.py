import os

import sqlalchemy as sa
from sqlalchemy import orm, types
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict

from .base import SCHEMA_NAME, Base

SG_ACE_TYPE_PUBLIC = 'public'
SG_ACE_TYPE_ROLE = 'role'
SG_ACE_TYPE_USER = 'user'

SG_ACE_LEVEL_READ = 'read'
SG_ACE_LEVEL_WRITE = 'write'  # write implies read access

ASSET_URL_PREFIX = os.environ.get('ASSET_STORE_URL_PREFIX',
                                  'http://localhost:3000/files')


class SGAsset(Base):
    __tablename__ = '_asset'

    id = sa.Column(sa.Text, primary_key=True, nullable=False)
    content_type = sa.Column(sa.Text, nullable=False)
    size = sa.Column(sa.Integer, nullable=False)

    @property
    def url(self):
        return '{}/{}'.format(ASSET_URL_PREFIX, self.id)


class SGAccessControlList(types.TypeDecorator):

    impl = JSONB

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        if not isinstance(value, list):
            return value

        return [item.to_dict() for item in value]

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        if not isinstance(value, list):
            return value

        return [SGAccessControlEntity.from_dict(item) for item in value]


# immutable class representing a Skygear ACE
class SGAccessControlEntity:
    def __init__(self, type_, level, public=False, role=None, user_id=None):
        assert type_ in [
            SG_ACE_TYPE_PUBLIC,
            SG_ACE_TYPE_ROLE,
            SG_ACE_TYPE_USER,
        ]
        assert level in [
            SG_ACE_LEVEL_READ,
            SG_ACE_LEVEL_WRITE,
        ]

        self._type = type_
        self._public = public
        self._role = role
        self._user_id = user_id
        self._level = level

    @classmethod
    def public_entity(cls, level):
        return cls(SG_ACE_TYPE_PUBLIC, level, public=True)

    @classmethod
    def role_entity(cls, role, level):
        return cls(SG_ACE_TYPE_ROLE, level, role=role)

    @classmethod
    def user_entity(cls, user_id, level):
        return cls(SG_ACE_TYPE_USER, level, user_id=user_id)

    @classmethod
    def from_dict(cls, d):
        level = d['level']

        if d.get('public', None):
            return cls.public_entity(level)

        role = d.get('role', None)
        if role:
            return cls.role_entity(role, level)

        user_id = d.get('user_id', None)
        if user_id:
            return cls.user_entity(user_id, level)

        raise ValueError('Invalid Skygear ACE = %s' % d)

    def __repr__(self):
        return 'SGAccessControlEntity({!r}, {!r}, {!r}, {!r}, {!r})'.format(
            self._type,
            self._level,
            self._public,
            self._role,
            self._user_id,
        )

    def __eq__(self, other):
        return (
            self._type == other._type
            and self._public == other._public
            and self._role == other._role
            and self._user_id == other._user_id
            and self._level == other._level
        )

    def to_dict(self):
        level = self._level
        type_ = self._type

        assert level in [
            SG_ACE_LEVEL_READ,
            SG_ACE_LEVEL_WRITE,
        ]

        if type_ == SG_ACE_TYPE_PUBLIC:
            return {
                'public': True,
                'level': level,
            }
        elif type_ == SG_ACE_TYPE_ROLE:
            return {
                'role': self._role,
                'level': level,
            }
        elif type_ == SG_ACE_TYPE_USER:
            return {
                'user_id': self._user_id,
                'level': level,
            }

        raise ValueError('Unrecgonized Skygear ACE type = %s' % type_)


class SGRole(Base):
    __tablename__ = '_role'

    id = sa.Column(sa.Text, primary_key=True)
    is_admin = sa.Column(sa.Boolean)


class SGUser(Base):
    __tablename__ = '_user'

    id = sa.Column(sa.Text, primary_key=True)
    username = sa.Column(sa.Text)
    password = sa.Column(sa.Text)


class SGAuth(Base):
    __tablename__ = '_auth'

    id = sa.Column(sa.Text, primary_key=True)
    password = sa.Column(sa.Text)
    provider_info = sa.Column(
        MutableDict.as_mutable(sa.dialects.postgresql.JSONB)
    )

    def get_phone(self):
        if not self.provider_info:
            return None
        for key, _ in self.provider_info.items():
            if 'phone' in key:
                return key.split(':')[1]
        return None

    def get_facebook_auth_data(self):
        if not self.provider_info:
            return None
        for key, value in self.provider_info.items():
            if 'facebook' in key:
                return value
        return None

    def get_wechat_auth_data(self):
        if not self.provider_info:
            return None
        for key, value in self.provider_info.items():
            if 'wechat' in key:
                return value
        return None


class SGAuthRole(Base):
    __tablename__ = '_auth_role'

    auth_id = sa.Column(
        sa.Text,
        sa.ForeignKey('%s._auth.id' % SCHEMA_NAME),
        primary_key=True
    )
    role_id = sa.Column(
        sa.Text,
        sa.ForeignKey('%s._role.id' % SCHEMA_NAME),
        primary_key=True
    )

    user = orm.relationship('SGAuth')
    role = orm.relationship('SGRole')


class SGDevice(Base):
    __tablename__ = '_device'

    id = sa.Column(sa.Text, primary_key=True)
    auth_id = sa.Column(
        sa.Text,
        sa.ForeignKey('%s._auth.id' % SCHEMA_NAME),
        primary_key=True
    )
    type = sa.Column(sa.Text, nullable=False)
    token = sa.Column(sa.Text)
    topic = sa.Column(sa.Text)
    last_registered_at = sa.Column(sa.DateTime, nullable=False)

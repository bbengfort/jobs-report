from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
usa_states = Table('usa_states', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('fips', Unicode(length=5)),
    Column('name', Unicode(length=255), nullable=False),
    Column('abbr', Unicode(length=2)),
    Column('region', Unicode(length=15)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['usa_states'].columns['region'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['usa_states'].columns['region'].drop()

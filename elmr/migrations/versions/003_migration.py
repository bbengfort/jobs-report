from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
states_series = Table('states_series', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('state_id', Integer),
    Column('series_id', Integer),
    Column('adjusted', Boolean, default=ColumnDefault(False)),
    Column('dataset', Unicode(length=255), nullable=False),
    Column('source', Unicode(length=255)),
    Column('category', Unicode(length=255)),
)

usa_states = Table('usa_states', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('fips', Unicode(length=5)),
    Column('name', Unicode(length=255), nullable=False),
    Column('abbr', Unicode(length=2)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['states_series'].create()
    post_meta.tables['usa_states'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['states_series'].drop()
    post_meta.tables['usa_states'].drop()

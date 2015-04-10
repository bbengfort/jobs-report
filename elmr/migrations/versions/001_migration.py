from sqlalchemy import *
from migrate import *
from datetime import datetime


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
ingestions = Table('ingestions', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('title', Unicode(length=255)),
    Column('version', Unicode(length=10), nullable=False),
    Column('start_year', Date, nullable=False),
    Column('end_year', Date, nullable=False),
    Column('duration', Float, nullable=False),
    Column('num_series', Integer, default=ColumnDefault(0)),
    Column('num_added', Integer, default=ColumnDefault(0)),
    Column('num_fetched', Integer, default=ColumnDefault(0)),
    Column('timestamp', DateTime(timezone=True), nullable=False,
           default=ColumnDefault(datetime.now)),
)

records = Table('records', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('series_id', Integer),
    Column('period', Date, nullable=False),
    Column('value', Float, nullable=False),
    Column('footnote', Unicode(length=255)),
)

series = Table('series', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('blsid', Unicode(length=255)),
    Column('title', Unicode(length=255)),
    Column('source', Unicode(length=255)),
    Column('is_primary', Boolean, default=ColumnDefault(False)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['ingestions'].create()
    post_meta.tables['records'].create()
    post_meta.tables['series'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['ingestions'].drop()
    post_meta.tables['records'].drop()
    post_meta.tables['series'].drop()

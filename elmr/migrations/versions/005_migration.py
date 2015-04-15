from sqlalchemy import *
from migrate import *

from elmr.utils import slugify

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
    Column('slug', Unicode(length=255)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['states_series'].columns['slug'].create()

    # Insert the slug tables
    conn = migrate_engine.connect()

    query = "SELECT id, dataset, category FROM states_series"
    for row in conn.execute(query):
        idx, dataset, category = row
        slug = None
        if category:
            slug = slugify(category)
        else:
            slug = slugify(dataset)

        if slug:
            query = "UPDATE states_series SET slug='%s' WHERE id=%s" % (slug, idx)
            conn.execute(query)

    conn.close()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['states_series'].columns['slug'].drop()

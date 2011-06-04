from relstorage.storage             import RelStorage
from relstorage.adapters.postgresql import PostgreSQLAdapter
from relvlast                       import Relvlast
from bundle_config                  import config

dsn = "dbname='{database}' user='{username}' host='{host}' port='{port}'"\
      "password='{password}'".format(**config['postgres'])
storage = lambda: RelStorage(PostgreSQLAdapter(dsn))
app = Relvlast(storage=storage)

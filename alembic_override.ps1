$env:DATABASE_URL = 'sqlite:///C:/sf_collab_db/sf_collab_dev.db'
$env:SQLALCHEMY_DATABASE_URI = 'sqlite:///C:/sf_collab_db/sf_collab_dev.db'
flask db upgrade

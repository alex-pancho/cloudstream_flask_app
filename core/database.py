from pydal import DAL, Field
from pathlib import Path

db_path = Path(__file__).parent.parent / "data" / "repositories.db"

# SQLite файл
db = DAL(f"sqlite://{db_path}")

db.define_table(
    "repositories",
    Field("name"),
    Field("url", unique=True),
    Field("description"),
    Field("manifest_version", "integer"),
)

db.commit()
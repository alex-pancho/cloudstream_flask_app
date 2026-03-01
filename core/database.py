from pydal import DAL, Field
from pathlib import Path

db_path = Path(__file__).parent.parent / "data"
file_path = db_path / "repositories.db"

# SQLite файл
db = DAL(
    f"sqlite://{file_path}", 
    folder=str(db_path), 
    migrate=True,
)

if "repositories" not in db.tables:
    db.define_table(
        "repositories",
        Field("name"),
        Field("url", unique=True),
        Field("description"),
        Field("manifest_version", "integer"),
    )

db.commit()

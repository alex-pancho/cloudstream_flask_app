from datetime import datetime, timezone
try:
    from pydal import DAL, Field
except ImportError:
    class DAL:
        pass
    class Field:
        pass
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

if "plugins" not in db.tables:
    db.define_table(
        "plugins",
        Field("repository_id", "reference repositories", required=True),

        Field("name", "string", required=True),
        Field("version", "string"),
        Field("lang", "string"),
        Field("description", "text"),

        Field("kt_url", "string", required=True),
        Field("base_url", "string"),

        Field("created_at", "datetime",
              default=lambda: datetime.now(timezone.utc)),

        migrate=True,
    )

if "stream_cache" not in db.tables:
    db.define_table(
        "stream_cache",
        Field("plugin_name", "string", required=True),
        Field("title", "string", required=True),
        Field("url", "string", required=True),
        Field("created_at", "datetime",
                default=lambda: datetime.now(timezone.utc))
    )

db.commit()


def get_db() -> DAL:
    """Returns the global DAL instance."""
    return db

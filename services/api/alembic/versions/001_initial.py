revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    from alembic import op

    from app.db import Base
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    from alembic import op

    from app.db import Base
    from app import models  # noqa: F401

    Base.metadata.drop_all(bind=op.get_bind())

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_add_product_name_cn"
down_revision = "0002_add_is_cover_to_images"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("product_name_cn", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("products", "product_name_cn")


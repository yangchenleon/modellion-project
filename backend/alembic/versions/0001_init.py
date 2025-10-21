from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_name", sa.Text(), nullable=True),
        sa.Column("price", sa.Text(), nullable=True),
        sa.Column("release_date", sa.Text(), nullable=True),
        sa.Column("article_content", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=False, unique=True),
        sa.Column("product_tag", sa.Text(), nullable=True),
        sa.Column("series", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("price_value", sa.Integer(), nullable=True),
        sa.Column("release_date_value", sa.Date(), nullable=True),
    )
    op.create_index(
        "ix_products_common",
        "products",
        ["product_name", "price", "release_date", "product_tag", "series", "created_at"],
    )
    op.create_index("ix_products_price_value", "products", ["price_value"]) 
    op.create_index("ix_products_release_date_value", "products", ["release_date_value"]) 

    op.create_table(
        "images",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("image_filename", sa.Text(), nullable=False),
        sa.Column("image_hash", sa.Text(), nullable=True, unique=True),
        sa.Column("minio_path", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("product_id", "image_filename", name="uq_product_image_filename"),
    )
    op.create_index("ix_images_product_id", "images", ["product_id"]) 

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="readonly"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_index("ix_images_product_id", table_name="images")
    op.drop_table("images")
    op.drop_index("ix_products_release_date_value", table_name="products")
    op.drop_index("ix_products_price_value", table_name="products")
    op.drop_index("ix_products_common", table_name="products")
    op.drop_table("products")

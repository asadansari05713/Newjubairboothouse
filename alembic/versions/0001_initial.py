"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-09-04 00:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('admins',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False, unique=True),
        sa.Column('password', sa.String(length=255), nullable=False)
    )

    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False, unique=True),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('whatsapp', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.String(length=50), nullable=True),
        sa.Column('updated_at', sa.String(length=50), nullable=True)
    )

    op.create_table('products',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Available'),
        sa.Column('image_url', sa.String(length=255), nullable=True),
        sa.Column('images', sa.Text(), nullable=True),
        sa.Column('sizes', sa.Text(), nullable=True)
    )

    op.create_table('sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('session_id', sa.String(length=255), nullable=False, unique=True),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('user_type', sa.String(length=20), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Integer(), nullable=False, server_default='1')
    )

    op.create_table('user_favourites',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('user_email', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.String(length=50), nullable=True)
    )

    op.create_table('feedback',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('feedback')
    op.drop_table('user_favourites')
    op.drop_table('sessions')
    op.drop_table('products')
    op.drop_table('users')
    op.drop_table('admins')



"""initial_migration

Revision ID: e1b36479a831
Revises: 
Create Date: 2026-06-12 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'e1b36479a831'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # ایجاد جدول user
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=False),
        sa.Column('usertype', sa.String(length=128), nullable=False),
        sa.Column('is_super_admin', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('phone'),
        sa.UniqueConstraint('username')
    )
    
    # ایجاد جدول contents
    op.create_table('contents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employer_name', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=150), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('image_file', sa.String(length=100), nullable=True),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('is_visible', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('short_description', sa.Text(), nullable=True),
        sa.Column('full_content', sa.Text(), nullable=True),
        sa.Column('video_url', sa.String(length=200), nullable=True),
        sa.Column('gallery_images', sa.Text(), nullable=True),
        sa.Column('tags', sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # ایجاد جدول contact_messages
    op.create_table('contact_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # ایجاد جدول utm_coordinates
    op.create_table('utm_coordinates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('easting', sa.Float(), nullable=False),
        sa.Column('northing', sa.Float(), nullable=False),
        sa.Column('zone', sa.Integer(), nullable=False),
        sa.Column('hemisphere', sa.String(length=1), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('utm_coordinates')
    op.drop_table('contact_messages')
    op.drop_table('contents')
    op.drop_table('user')
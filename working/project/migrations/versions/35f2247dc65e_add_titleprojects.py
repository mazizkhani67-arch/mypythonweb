"""add titleprojects

Revision ID: 35f2247dc65e
Revises: c6f01da0fc84
Create Date: 2026-06-15 18:47:28.038667

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35f2247dc65e'
down_revision = 'c6f01da0fc84'
branch_labels = None
depends_on = None


# migrations/versions/35f2247dc65e_add_titleprojects.py

def upgrade():
    # اضافه کردن ستون به صورت nullable (قابل پذیرش NULL)
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.VARCHAR(length=200), nullable=True))
    
    # اختصاص مقدار پیش‌فرض به رکوردهای موجود
    op.execute("UPDATE projects SET title = 'بدون عنوان' WHERE title IS NULL")
    
    # تغییر ستون به NOT NULL
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.alter_column('title', existing_type=sa.VARCHAR(length=200), nullable=False)

def downgrade():
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_column('title')

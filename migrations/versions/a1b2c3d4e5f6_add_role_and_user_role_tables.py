"""add role, permission and user_role tables

Revision ID: a1b2c3d4e5f6
Revises: 53246183bde2
Create Date: 2024-12-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '53246183bde2'
branch_labels = None
depends_on = None


def upgrade():
    # Create role table
    op.create_table(
        'role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_name'), 'role', ['name'], unique=True)

    # Create permission table
    op.create_table(
        'permission',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('module', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_permission_name'), 'permission', ['name'], unique=True)
    op.create_index(op.f('ix_permission_module'), 'permission', ['module'], unique=False)

    # Create role_permission junction table
    op.create_table(
        'role_permission',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
        sa.ForeignKeyConstraint(['permission_id'], ['permission.id'], ),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

    # Create user_role junction table (with extra metadata fields)
    op.create_table(
        'user_role',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('assigned_by', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['assigned_by'], ['user.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # Insert default roles
    op.execute("""
        INSERT INTO role (name, description, is_default, created_at, updated_at)
        VALUES
            ('admin', '管理員', false, NOW(), NOW()),
            ('moderator', '協助管理員', false, NOW(), NOW()),
            ('user', '一般用戶', true, NOW(), NOW())
    """)

    # Assign user role to all existing users
    op.execute("""
        INSERT INTO user_role (user_id, role_id, assigned_at)
        SELECT u.id, r.id, NOW()
        FROM user u
        CROSS JOIN role r
        WHERE r.name = 'user'
    """)
    # Note: Permissions are synced on app startup via sync_permissions()


def downgrade():
    op.drop_table('user_role')
    op.drop_table('role_permission')
    op.drop_index(op.f('ix_permission_module'), table_name='permission')
    op.drop_index(op.f('ix_permission_name'), table_name='permission')
    op.drop_table('permission')
    op.drop_index(op.f('ix_role_name'), table_name='role')
    op.drop_table('role')

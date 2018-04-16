"""empty message

Revision ID: c35e9bbece72
Revises: 
Create Date: 2018-04-16 13:14:47.083924

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c35e9bbece72'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('organization',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('password', sa.String(length=128), nullable=True),
    sa.Column('refresh_token', sa.String(length=64), nullable=True),
    sa.Column('refresh_token_expiry', sa.DateTime(), nullable=True),
    sa.Column('firebase_uid', sa.String(length=256), nullable=True),
    sa.Column('first_name', sa.String(length=256), nullable=True),
    sa.Column('last_name', sa.String(length=256), nullable=True),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('organization_user',
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.Enum('owner', 'member', name='organization_user_roles'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('organization_id', 'user_id')
    )
    op.create_table('team',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.Column('organization_role', sa.Enum('admin', 'write', 'read', name='project_roles'), nullable=True),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.Column('team_role', sa.Enum('admin', 'write', 'read', name='project_roles'), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('user_role', sa.Enum('admin', 'write', 'read', name='project_roles'), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['team.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('team_user',
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.Enum('maintainer', 'member', name='team_user_roles'), nullable=False),
    sa.ForeignKeyConstraint(['team_id'], ['team.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('team_id', 'user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('team_user')
    op.drop_table('project')
    op.drop_table('team')
    op.drop_table('organization_user')
    op.drop_table('user')
    op.drop_table('organization')
    # ### end Alembic commands ###

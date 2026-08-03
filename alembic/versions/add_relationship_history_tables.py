"""add relationship history tables

Revision ID: add_relationship_history
Revises: 0115eab0c5d5
Create Date: 2026-07-29 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_relationship_history'
down_revision = '0115eab0c5d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tutor_group_assignments table
    op.create_table(
        'tutor_group_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tutor_id', sa.Integer(), sa.ForeignKey('tutors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('group_id', sa.Integer(), sa.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('removed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for tutor_group_assignments
    op.create_index(
        'ix_active_group_tutor_assignment', 'tutor_group_assignments',
        ['group_id', 'removed_at']
    )
    op.create_index(
        'ix_active_tutor_assignment', 'tutor_group_assignments',
        ['tutor_id', 'removed_at']
    )
    op.create_index(
        'uq_one_active_tutor_per_group', 'tutor_group_assignments',
        ['group_id'], unique=True,
        postgresql_where=sa.text('removed_at IS NULL')
    )

    # Create student_group_memberships table
    op.create_table(
        'student_group_memberships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('group_id', sa.Integer(), sa.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for student_group_memberships
    op.create_index(
        'ix_active_group_membership', 'student_group_memberships',
        ['group_id', 'left_at']
    )
    op.create_index(
        'ix_active_student_membership', 'student_group_memberships',
        ['student_id', 'left_at']
    )


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_active_student_membership', table_name='student_group_memberships')
    op.drop_index('ix_active_group_membership', table_name='student_group_memberships')
    
    # Drop student_group_memberships table
    op.drop_table('student_group_memberships')
    
    # Drop indexes
    op.drop_index('uq_one_active_tutor_per_group', table_name='tutor_group_assignments')
    op.drop_index('ix_active_tutor_assignment', table_name='tutor_group_assignments')
    op.drop_index('ix_active_group_tutor_assignment', table_name='tutor_group_assignments')
    
    # Drop tutor_group_assignments table
    op.drop_table('tutor_group_assignments')

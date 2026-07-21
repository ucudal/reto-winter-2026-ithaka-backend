"""update schema per new spec

Revision ID: a1b2c3d4e5f6
Revises: 223393d05097
Create Date: 2026-07-21 09:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '223393d05097'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Drop tables that are being replaced ──────────────────────────────
    # assignments table is replaced by direct FKs on groups
    op.execute("DROP TABLE IF EXISTS assignments CASCADE")

    # ── 2. Drop old documents table (will be recreated with new schema) ──────
    op.drop_table('documents')

    # ── 3. Add entity_type enum ──────────────────────────────────────────────
    postgresql.ENUM('GROUP', 'MEETING', 'DELIVERABLE', 'SUPPORT_MATERIAL', name='entity_type').create(op.get_bind(), checkfirst=True)

    # ── 4. Recreate documents as polymorphic ─────────────────────────────────
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', postgresql.ENUM('GROUP', 'MEETING', 'DELIVERABLE', 'SUPPORT_MATERIAL', name='entity_type', create_type=False), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('platform', postgresql.ENUM('DRIVE', 'SHAREPOINT', name='document_platform', create_type=False), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    # Index for fast polymorphic lookups
    op.create_index('ix_documents_entity', 'documents', ['entity_type', 'entity_id'])

    # ── 5. Alter groups table ────────────────────────────────────────────────
    op.add_column('groups', sa.Column('major', sa.String(length=120), nullable=True))
    op.add_column('groups', sa.Column('status', sa.String(length=30), nullable=False, server_default='Active'))
    op.add_column('groups', sa.Column('business_tutor_id', sa.Integer(), nullable=True))
    op.add_column('groups', sa.Column('technical_tutor_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_groups_business_tutor', 'groups', 'tutors',
        ['business_tutor_id'], ['id'], ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_groups_technical_tutor', 'groups', 'tutors',
        ['technical_tutor_id'], ['id'], ondelete='SET NULL'
    )

    # ── 6. Alter students table ──────────────────────────────────────────────
    op.add_column('students', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_students_user', 'students', 'users',
        ['user_id'], ['id'], ondelete='SET NULL'
    )

    # ── 7. Alter tutors table ────────────────────────────────────────────────
    op.add_column('tutors', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_tutors_user', 'tutors', 'users',
        ['user_id'], ['id'], ondelete='SET NULL'
    )

    # ── 8. Alter meetings table ──────────────────────────────────────────────
    # Replace tutor_id FK with tutor_ids JSONB
    op.drop_constraint('meetings_tutor_id_fkey', 'meetings', type_='foreignkey')
    op.drop_column('meetings', 'tutor_id')
    op.add_column('meetings', sa.Column(
        'tutor_ids',
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=True
    ))

    # ── 9. Drop TutoringType enum (no longer used) ───────────────────────────
    op.execute("DROP TYPE IF EXISTS tutoring_type")


def downgrade() -> None:
    # ── Reverse meetings ──────────────────────────────────────────────────────
    op.drop_column('meetings', 'tutor_ids')
    op.add_column('meetings', sa.Column('tutor_id', sa.Integer(), nullable=False, server_default='0'))
    op.create_foreign_key(
        'meetings_tutor_id_fkey', 'meetings', 'tutors',
        ['tutor_id'], ['id'], ondelete='CASCADE'
    )

    # ── Reverse tutors ────────────────────────────────────────────────────────
    op.drop_constraint('fk_tutors_user', 'tutors', type_='foreignkey')
    op.drop_column('tutors', 'user_id')

    # ── Reverse students ──────────────────────────────────────────────────────
    op.drop_constraint('fk_students_user', 'students', type_='foreignkey')
    op.drop_column('students', 'user_id')

    # ── Reverse groups ────────────────────────────────────────────────────────
    op.drop_constraint('fk_groups_technical_tutor', 'groups', type_='foreignkey')
    op.drop_constraint('fk_groups_business_tutor', 'groups', type_='foreignkey')
    op.drop_column('groups', 'technical_tutor_id')
    op.drop_column('groups', 'business_tutor_id')
    op.drop_column('groups', 'status')
    op.drop_column('groups', 'major')

    # ── Reverse documents ─────────────────────────────────────────────────────
    op.drop_index('ix_documents_entity', table_name='documents')
    op.drop_table('documents')
    op.execute("DROP TYPE IF EXISTS entity_type")

    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('deliverable_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('platform', sa.Enum('DRIVE', 'SHAREPOINT', name='document_platform'), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['deliverable_id'], ['deliverables.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── Restore assignments table ─────────────────────────────────────────────
    op.create_table(
        'assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('tutor_id', sa.Integer(), nullable=False),
        sa.Column('tutoring_type', sa.Enum('BUSINESS', 'TECHNICAL', name='tutoring_type'), nullable=False),
        sa.Column('assignment_date', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tutor_id'], ['tutors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('group_id', 'tutor_id', 'tutoring_type', name='uq_assignment_group_tutor_type'),
    )

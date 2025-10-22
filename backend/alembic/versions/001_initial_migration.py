"""Initial migration

Revision ID: 001
Revises:
Create Date: 2025-10-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create campaigns table
    op.create_table(
        'campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('target_audience_hint', sa.String(length=500), nullable=True),
        sa.Column('locales', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('language_pref', sa.String(length=10), nullable=True),
        sa.Column('channels', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tone', sa.String(length=50), nullable=True),
        sa.Column('cta', sa.String(length=255), nullable=True),
        sa.Column('icp', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('queries', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('linkedin_copy', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('reddit_copy', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('facebook_copy', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('policy_review', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaigns_id'), 'campaigns', ['id'], unique=False)
    op.create_index(op.f('ix_campaigns_product_name'), 'campaigns', ['product_name'], unique=False)

    # Create performance_metrics table
    op.create_table(
        'performance_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=False),
        sa.Column('sends', sa.Integer(), nullable=True),
        sa.Column('opens', sa.Integer(), nullable=True),
        sa.Column('clicks', sa.Integer(), nullable=True),
        sa.Column('replies', sa.Integer(), nullable=True),
        sa.Column('positive_replies', sa.Integer(), nullable=True),
        sa.Column('neutral_replies', sa.Integer(), nullable=True),
        sa.Column('negative_replies', sa.Integer(), nullable=True),
        sa.Column('conversions', sa.Integer(), nullable=True),
        sa.Column('conversion_rate', sa.Float(), nullable=True),
        sa.Column('reply_rate', sa.Float(), nullable=True),
        sa.Column('positive_rate', sa.Float(), nullable=True),
        sa.Column('date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_performance_metrics_id'), 'performance_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_performance_metrics_campaign_id'), 'performance_metrics', ['campaign_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_performance_metrics_campaign_id'), table_name='performance_metrics')
    op.drop_index(op.f('ix_performance_metrics_id'), table_name='performance_metrics')
    op.drop_table('performance_metrics')
    op.drop_index(op.f('ix_campaigns_product_name'), table_name='campaigns')
    op.drop_index(op.f('ix_campaigns_id'), table_name='campaigns')
    op.drop_table('campaigns')

"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-03-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('username', sa.String(100), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('api_id', sa.Integer(), nullable=False),
        sa.Column('api_hash', sa.String(100), nullable=False),
        sa.Column('session_string', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), server_default='inactive'),
        sa.Column('warmup_stage', sa.Integer(), server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index('ix_users_id', 'users', ['id'])

    # Personas table
    op.create_table(
        'personas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('interests', sa.JSON(), server_default='[]'),
        sa.Column('tone', sa.String(50), server_default='friendly'),
        sa.Column('language_style', sa.Text(), nullable=True),
        sa.Column('sample_messages', sa.JSON(), server_default='[]'),
        sa.Column('keywords_to_engage', sa.JSON(), server_default='[]'),
        sa.Column('keywords_to_avoid', sa.JSON(), server_default='[]'),
        sa.Column('response_templates', sa.JSON(), server_default='{}'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_personas_id', 'personas', ['id'])

    # Campaigns table
    op.create_table(
        'campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('persona_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), server_default='draft'),
        sa.Column('target_keywords', sa.JSON(), server_default='[]'),
        sa.Column('target_industries', sa.JSON(), server_default='[]'),
        sa.Column('product_info', sa.Text(), nullable=True),
        sa.Column('call_to_action', sa.Text(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('daily_message_limit', sa.Integer(), server_default='50'),
        sa.Column('daily_dm_limit', sa.Integer(), server_default='10'),
        sa.Column('settings', sa.JSON(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['persona_id'], ['personas.id'])
    )
    op.create_index('ix_campaigns_id', 'campaigns', ['id'])

    # Groups table
    op.create_table(
        'groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('username', sa.String(100), nullable=True),
        sa.Column('invite_link', sa.String(500), nullable=True),
        sa.Column('member_count', sa.Integer(), server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('left_at', sa.DateTime(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('message_count', sa.Integer(), server_default='0'),
        sa.Column('is_target', sa.Boolean(), server_default='true'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'])
    )
    op.create_index('ix_groups_id', 'groups', ['id'])
    op.create_index('ix_groups_campaign_status', 'groups', ['campaign_id', 'status'])

    # Messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_message_id', sa.BigInteger(), nullable=True),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.Column('sender_telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('sender_username', sa.String(100), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('reply_to_message_id', sa.BigInteger(), nullable=True),
        sa.Column('is_bot_message', sa.Boolean(), server_default='false'),
        sa.Column('is_dm', sa.Boolean(), server_default='false'),
        sa.Column('sentiment', sa.String(20), nullable=True),
        sa.Column('intent', sa.String(50), nullable=True),
        sa.Column('lead_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id']),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'])
    )
    op.create_index('ix_messages_id', 'messages', ['id'])
    op.create_index('ix_messages_group_created', 'messages', ['group_id', 'created_at'])
    op.create_index('ix_messages_campaign_created', 'messages', ['campaign_id', 'created_at'])

    # Leads table
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_user_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(100), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('source_group_id', sa.Integer(), nullable=True),
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), server_default='new'),
        sa.Column('score', sa.Float(), server_default='0.0'),
        sa.Column('contact_method', sa.String(50), nullable=True),
        sa.Column('first_contact_at', sa.DateTime(), nullable=True),
        sa.Column('last_contact_at', sa.DateTime(), nullable=True),
        sa.Column('contact_count', sa.Integer(), server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), server_default='[]'),
        sa.Column('custom_data', sa.JSON(), server_default='{}'),
        sa.Column('converted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_group_id'], ['groups.id']),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id']),
        sa.UniqueConstraint('telegram_user_id', 'campaign_id', name='uq_lead_user_campaign')
    )
    op.create_index('ix_leads_id', 'leads', ['id'])
    op.create_index('ix_leads_status', 'leads', ['status'])
    op.create_index('ix_leads_campaign_status', 'leads', ['campaign_id', 'status'])

    # Warm-up metrics table
    op.create_table(
        'warm_up_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('messages_sent', sa.Integer(), server_default='0'),
        sa.Column('messages_received', sa.Integer(), server_default='0'),
        sa.Column('groups_joined', sa.Integer(), server_default='0'),
        sa.Column('groups_left', sa.Integer(), server_default='0'),
        sa.Column('dms_sent', sa.Integer(), server_default='0'),
        sa.Column('dms_received', sa.Integer(), server_default='0'),
        sa.Column('reactions_given', sa.Integer(), server_default='0'),
        sa.Column('warmup_stage', sa.Integer(), server_default='1'),
        sa.Column('score', sa.Float(), server_default='0.0'),
        sa.Column('flags', sa.JSON(), server_default='[]'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.UniqueConstraint('user_id', 'date', name='uq_warmup_user_date')
    )
    op.create_index('ix_warm_up_metrics_id', 'warm_up_metrics', ['id'])
    op.create_index('ix_warmup_user_date', 'warm_up_metrics', ['user_id', 'date'])


def downgrade() -> None:
    op.drop_table('warm_up_metrics')
    op.drop_table('leads')
    op.drop_table('messages')
    op.drop_table('groups')
    op.drop_table('campaigns')
    op.drop_table('personas')
    op.drop_table('users')

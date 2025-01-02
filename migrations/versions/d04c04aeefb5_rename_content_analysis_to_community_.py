"""rename_content_analysis_to_community_analysis

Revision ID: d04c04aeefb5
Revises: add_name_and_source
Create Date: 2025-01-01 21:52:34.981769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd04c04aeefb5'
down_revision: Union[str, None] = 'add_name_and_source'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename the content_analysis table to community_analysis
    op.execute('ALTER TABLE content_analysis RENAME TO community_analysis')
    
    # Rename the foreign key constraint
    op.execute('''
        ALTER TABLE marketing_research 
        RENAME COLUMN content_analysis_id TO community_analysis_id
    ''')
    
    # Drop the old foreign key constraint
    op.execute('''
        ALTER TABLE marketing_research 
        DROP CONSTRAINT IF EXISTS marketing_research_content_analysis_id_fkey
    ''')
    
    # Add the new foreign key constraint
    op.execute('''
        ALTER TABLE marketing_research 
        ADD CONSTRAINT marketing_research_community_analysis_id_fkey 
        FOREIGN KEY (community_analysis_id) 
        REFERENCES community_analysis(id)
    ''')


def downgrade() -> None:
    # Rename the community_analysis table back to content_analysis
    op.execute('ALTER TABLE community_analysis RENAME TO content_analysis')
    
    # Rename the foreign key constraint back
    op.execute('''
        ALTER TABLE marketing_research 
        RENAME COLUMN community_analysis_id TO content_analysis_id
    ''')
    
    # Drop the new foreign key constraint
    op.execute('''
        ALTER TABLE marketing_research 
        DROP CONSTRAINT IF EXISTS marketing_research_community_analysis_id_fkey
    ''')
    
    # Add back the old foreign key constraint
    op.execute('''
        ALTER TABLE marketing_research 
        ADD CONSTRAINT marketing_research_content_analysis_id_fkey 
        FOREIGN KEY (content_analysis_id) 
        REFERENCES content_analysis(id)
    ''')

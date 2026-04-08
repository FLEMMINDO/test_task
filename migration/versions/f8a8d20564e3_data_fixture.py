"""Data_fixture

Revision ID: f8a8d20564e3
Revises: 5686b7c1653c
Create Date: 2026-04-08 22:03:56.106573

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8a8d20564e3'
down_revision: Union[str, Sequence[str], None] = '5686b7c1653c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema"""
    op.execute("""
        INSERT INTO users (full_name, email, hashed_password, role, registered_at) VALUES
            ('TestUser1', 'test@mail.ru', '$2b$12$ZBlVadY18zK2JiHfpe60zelSC0l6ZrABXygSnwKKGd0vLMGjgylSa', 'user', NOW()),
            ('TestAdmin1', 'testAdm@mail.ru', '$2b$12$ZBlVadY18zK2JiHfpe60zelSC0l6ZrABXygSnwKKGd0vLMGjgylSa', 'admin', NOW())
    """)
    
    op.execute("""
        INSERT INTO accounts (user_id, amount)
        SELECT id, 0 FROM users WHERE email = 'test@mail.ru'
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM accounts WHERE user_id IN (SELECT id FROM users WHERE full_name ='TestUser1')")
    op.execute("DELETE FROM users WHERE full_name IN ('TestUser1', 'TestAdmin1')")

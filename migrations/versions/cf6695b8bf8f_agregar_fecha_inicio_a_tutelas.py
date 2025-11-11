"""agregar_fecha_inicio_a_tutelas

Revision ID: cf6695b8bf8f
Revises: 002_agregar_auditoria_EJEMPLO
Create Date: 2025-11-02 20:23:45.630505

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf6695b8bf8f'
down_revision: Union[str, Sequence[str], None] = '002_agregar_auditoria_EJEMPLO'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (Las líneas duplicadas "from alembic import op" y "import sqlalchemy as sa" se eliminaron)

def upgrade() -> None:
    """Upgrade schema."""
    # ### INICIO DE CORREPosible Causa:
    op.add_column('tutelas', sa.Column('fecha_inicio', sa.String(), nullable=True))
    # ### FIN DE CORRECCIÓN ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### INICIO DE CORRECCIÓN ###
    op.drop_column('tutelas', 'fecha_inicio')
    # ### FIN DE CORRECCIÓN ###
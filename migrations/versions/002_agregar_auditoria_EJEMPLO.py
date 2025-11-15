"""EJEMPLO: Agregar columna de auditoría a portal_users

Revision ID: 002_agregar_auditoria_EJEMPLO
Revises: 001_initial_schema
Create Date: 2025-11-01 11:01:00.000000

"""

from alembic import op
import sqlalchemy as sa


# Identificador de la revisión
revision = "002_agregar_auditoria_EJEMPLO"
down_revision = "001_initial_schema"  # Apunta a la migración anterior
branch_labels = None
depends_on = None


def upgrade():
    """
    Agrega una columna 'modificado_por' a la tabla 'portal_users'
    """
    # SQLite requiere "batch_alter_table" para modificar tablas
    with op.batch_alter_table("portal_users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("modificado_por", sa.String(length=100), nullable=True)
        )

    print("Columna 'modificado_por' agregada a 'portal_users'.")


def downgrade():
    """
    Elimina la columna 'modificado_por' de la tabla 'portal_users'
    """
    with op.batch_alter_table("portal_users", schema=None) as batch_op:
        batch_op.drop_column("modificado_por")

    print("Columna 'modificado_por' eliminada de 'portal_users'.")

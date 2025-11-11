"""Migración inicial con el schema base del Sistema Montero

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-11-01 11:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# Identificador de la revisión
revision = "001_initial_schema"
down_revision = None  # Esta es la primera migración
branch_labels = None
depends_on = None


def upgrade():
    """
    Crea todas las tablas iniciales del sistema.
    Basado en el DICTAMEN_SISTEMA_MONTERO.md
    """

    # Tabla: portal_users
    op.create_table(
        "portal_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "fecha_creacion",
            sa.TIMESTAMP(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=True,
        ),
        sa.Column("ultimo_acceso", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    print("Tabla 'portal_users' creada.")

    # Tabla: empresas
    op.create_table(
        "empresas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre_empresa", sa.Text(), nullable=False),
        sa.Column("tipo_identificacion_empresa", sa.Text(), nullable=True),
        sa.Column("nit", sa.Text(), nullable=False),
        sa.Column("direccion_empresa", sa.Text(), nullable=True),
        sa.Column("telefono_empresa", sa.Text(), nullable=True),
        sa.Column("correo_empresa", sa.Text(), nullable=True),
        sa.Column("departamento_empresa", sa.Text(), nullable=True),
        sa.Column("ciudad_empresa", sa.Text(), nullable=True),
        sa.Column("ibc_empresa", sa.REAL(), nullable=True),
        sa.Column("afp_empresa", sa.Text(), nullable=True),
        sa.Column("arl_empresa", sa.Text(), nullable=True),
        sa.Column("rep_legal_nombre", sa.Text(), nullable=True),
        sa.Column("rep_legal_tipo_id", sa.Text(), nullable=True),
        sa.Column("rep_legal_numero_id", sa.Text(), nullable=True),
        sa.Column(
            "fecha_registro",
            sa.TIMESTAMP(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nit"),
    )
    op.create_index(
        op.f("ix_empresas_nombre_empresa"), "empresas", ["nombre_empresa"], unique=False
    )
    print("Tabla 'empresas' creada.")

    # Tabla: novedades
    op.create_table(
        "novedades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client", sa.Text(), nullable=True),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column("priority", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("radicado", sa.Text(), nullable=True),
        sa.Column("creationDate", sa.Text(), nullable=True),
        sa.Column("updateDate", sa.Text(), nullable=True),
        sa.Column("assignedTo", sa.Text(), nullable=True),
        sa.Column("history", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_novedades_client"), "novedades", ["client"], unique=False)
    op.create_index(
        op.f("ix_novedades_radicado"), "novedades", ["radicado"], unique=False
    )
    print("Tabla 'novedades' creada.")

    # Tabla: credenciales_plataforma
    op.create_table(
        "credenciales_plataforma",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plataforma", sa.Text(), nullable=False),
        sa.Column("usuario", sa.Text(), nullable=True),
        sa.Column("contrasena", sa.Text(), nullable=True),  # Encriptada
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("ruta_documento_txt", sa.Text(), nullable=True),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.TIMESTAMP(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_credenciales_plataforma_plataforma"),
        "credenciales_plataforma",
        ["plataforma"],
        unique=False,
    )
    print("Tabla 'credenciales_plataforma' creada.")


def downgrade():
    """
    Revierte todas las tablas iniciales del sistema.
    """
    op.drop_table("credenciales_plataforma")
    op.drop_table("novedades")
    op.drop_table("empresas")
    op.drop_table("portal_users")
    print("Todas las tablas iniciales eliminadas.")

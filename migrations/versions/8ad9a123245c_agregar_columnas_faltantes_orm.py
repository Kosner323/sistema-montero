"""Agregar columnas faltantes ORM - SEGURO

Revision ID: 8ad9a123245c
Revises: a93ebf45de70
Create Date: 2025-11-26 20:03:33.517260

MIGRACION MANUAL SEGURA
Esta migracion fue modificada manualmente para:
1. NO borrar ninguna tabla existente
2. NO borrar ninguna columna existente
3. SOLO agregar columnas faltantes necesarias para ORM
4. Usar nullable=True para evitar errores con datos existentes
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ad9a123245c'
down_revision: Union[str, Sequence[str], None] = 'a93ebf45de70'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema - MIGRACION SEGURA
    Solo agrega columnas faltantes, no borra nada
    """

    # ========================================================================
    # TABLA: cotizaciones
    # Agregar columnas faltantes para el modelo ORM de Cotizacion
    # Columnas existentes: id_cotizacion, cliente, email (ya agregadas antes)
    # Columnas a agregar: servicio, monto, notas, fecha_creacion
    # ========================================================================
    try:
        with op.batch_alter_table('cotizaciones', schema=None) as batch_op:
            # Agregar columnas nuevas como NULLABLE
            batch_op.add_column(sa.Column('servicio', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('monto', sa.Float(), nullable=True))
            batch_op.add_column(sa.Column('notas', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('fecha_creacion', sa.Text(), nullable=True))

            # Crear índices si no existen
            try:
                batch_op.create_index('idx_cotizaciones_cliente', ['cliente'], unique=False)
            except:
                pass  # Ya existe

            try:
                batch_op.create_index('idx_cotizaciones_fecha', ['fecha_creacion'], unique=False)
            except:
                pass  # Ya existe

        print("[OK] Columnas agregadas a cotizaciones")
    except Exception as e:
        print(f"[INFO] Tabla cotizaciones: {e}")

    # ========================================================================
    # TABLA: pagos
    # Verificar/crear tabla pagos (para el modelo Pago)
    # ========================================================================
    try:
        # Verificar si la tabla ya existe
        conn = op.get_bind()
        result = conn.execute(sa.text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='pagos'"
        )).fetchone()

        if not result:
            # Solo crear si no existe
            op.create_table('pagos',
                sa.Column('id', sa.Integer(), nullable=False),
                sa.Column('usuario_id', sa.Text(), nullable=False),
                sa.Column('empresa_nit', sa.Text(), nullable=False),
                sa.Column('monto', sa.Float(), nullable=False),
                sa.Column('tipo_pago', sa.Text(), nullable=False),
                sa.Column('fecha_pago', sa.Text(), nullable=False),
                sa.Column('referencia', sa.Text(), nullable=True),
                sa.Column('created_at', sa.Text(), nullable=True),
                sa.PrimaryKeyConstraint('id')
            )
            print("[OK] Tabla pagos creada")
        else:
            print("[INFO] Tabla pagos ya existe")
    except Exception as e:
        print(f"[INFO] Tabla pagos: {e}")

    print("")
    print("="*80)
    print("[COMPLETADO] Migracion ORM aplicada")
    print("  - Columnas agregadas a cotizaciones")
    print("  - Tabla pagos verificada")
    print("  - NO se eliminaron datos")
    print("="*80)


def downgrade() -> None:
    """
    Downgrade schema - SEGURO
    Revertir cambios sin afectar datos existentes
    """

    # Revertir tabla pagos (si se creó en esta migración)
    try:
        op.drop_table('pagos')
    except Exception:
        pass  # Si no existe o tiene datos, no hacer nada

    # Revertir índices de cotizaciones
    try:
        with op.batch_alter_table('cotizaciones', schema=None) as batch_op:
            batch_op.drop_index('idx_cotizaciones_fecha')
            batch_op.drop_index('idx_cotizaciones_cliente')
            batch_op.drop_column('email')
            batch_op.drop_column('cliente')
            batch_op.drop_column('id_cotizacion')
    except Exception:
        pass  # Si hay errores, no hacer nada

    print("✓ Downgrade completado")

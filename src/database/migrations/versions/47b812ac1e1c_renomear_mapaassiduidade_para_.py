"""Renomear MapaAssiduidade para TabelaTaxas e valor_sem_iva para valor_com_iva

Revision ID: 47b812ac1e1c
Revises: 21589708b7e5
Create Date: 2026-02-15 22:17:20.540838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47b812ac1e1c'
down_revision: Union[str, Sequence[str], None] = '21589708b7e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria ou renomeia TabelaTaxas dependendo do estado da BD.

    Se as tabelas antigas existirem: renomeia
    Se não existirem: esta migração é um no-op (as tabelas serão criadas pelo SQLAlchemy)
    """
    # Verificar se tabelas antigas existem
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'mapas_assiduidade' in existing_tables:
        # BD antiga - renomear tabelas
        op.rename_table('mapas_assiduidade', 'tabelas_taxas')
        op.rename_table('mapas_assiduidade_linhas', 'tabelas_taxas_linhas')
        op.alter_column(
            'tabelas_taxas_linhas',
            'valor_sem_iva',
            new_column_name='valor_com_iva',
            existing_type=sa.Numeric(10, 2),
            existing_nullable=True,
            comment='Valor COM IVA inserido pelo utilizador'
        )
    # Senão, é BD nova - as tabelas serão criadas automaticamente com nomes corretos


def downgrade() -> None:
    """Reverte renomeação TabelaTaxas para MapaAssiduidade (se aplicável)."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'tabelas_taxas' in existing_tables:
        # Reverter renomeações
        op.alter_column(
            'tabelas_taxas_linhas',
            'valor_com_iva',
            new_column_name='valor_sem_iva',
            existing_type=sa.Numeric(10, 2),
            existing_nullable=True
        )
        op.rename_table('tabelas_taxas_linhas', 'mapas_assiduidade_linhas')
        op.rename_table('tabelas_taxas', 'mapas_assiduidade')

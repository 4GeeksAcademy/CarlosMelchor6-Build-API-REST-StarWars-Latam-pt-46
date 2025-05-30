"""empty message

Revision ID: 912191d7916d
Revises: a5cffa318ac2
Create Date: 2025-05-03 02:47:14.525177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '912191d7916d'
down_revision = 'a5cffa318ac2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('people',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('people_id', sa.Integer(), nullable=False),
    sa.Column('data_of_people', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('planets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('planets_id', sa.Integer(), nullable=False),
    sa.Column('data_of_planets', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_people_favorites',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('person_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['person_id'], ['people.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'person_id')
    )
    op.create_table('user_planet_favorites',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('planet_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['planet_id'], ['planets.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'planet_id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_name', sa.String(length=120), nullable=False))
        batch_op.add_column(sa.Column('first_name', sa.String(length=120), nullable=False))
        batch_op.add_column(sa.Column('last_name', sa.String(length=120), nullable=False))
        batch_op.add_column(sa.Column('subscription_date', sa.DateTime(), nullable=False))
        batch_op.create_unique_constraint(None, ['user_name'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('subscription_date')
        batch_op.drop_column('last_name')
        batch_op.drop_column('first_name')
        batch_op.drop_column('user_name')

    op.drop_table('user_planet_favorites')
    op.drop_table('user_people_favorites')
    op.drop_table('planets')
    op.drop_table('people')
    # ### end Alembic commands ###

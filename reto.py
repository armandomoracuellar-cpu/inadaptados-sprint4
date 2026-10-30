

# SISTEMA DE GESTIÓN DE INADAPTADOS v6 — entrega final del Sprint 4
# Base: PostgreSQL local. Para levantarlo desde cero: una base vacía + alembic upgrade head.
# Pega cada archivo completo debajo de su encabezado.

# ===== basedatos.py =====
# TODO: la cadena de conexión vive aquí y en ningún otro lado.

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

URL_BASE_DE_DATOS = "postgresql+psycopg://postgres:estacion934@localhost:5432/inadaptados"

motor = create_engine(URL_BASE_DE_DATOS)
Sesion = sessionmaker(bind=motor)

class Base(DeclarativeBase):
    pass



# ===== modelos.py =====
# TODO: Alumno, Tarea, TareaUrgente, Curso e Inscripcion. Cada relación lleva arriba
#       un comentario que explica por qué se modeló así.


##Se modeló así porque la tabla de alumnos solo necesita el ID nombre y agregue el email que es uno por alumno
##Ademas se pone la relación que tiene con tareas (un alumno muchas tareas), inscripciones (un alumno muchas inscripciones)
## y curasos (un alumno muchos cursos) al final se pone la etiqueta de la tabla

from basedatos import Base

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import date


class Alumno(Base):
    __tablename__ = "alumnos"

    id:Mapped[int] = mapped_column(primary_key= True)
    nombre: Mapped[str] = mapped_column(String(100))
    email:Mapped[str] = mapped_column(String(200))
    

    tareas: Mapped[list["Tarea"]] = relationship(back_populates="alumno", order_by="Tarea.id")
    inscripciones: Mapped[list["Inscripcion"]] = relationship(back_populates="alumno", order_by="Inscripcion.id")
    cursos: Mapped[list["Curso"]] = relationship(secondary="inscripciones", back_populates="alumnos", order_by="Curso.id")

    def __repr__(self):
        return f"<Alumno {self.id}: {self.nombre}>"

##Se modeló así porque la tabla de tareas solo necesita el ID, descripcion,completada, el tipo (para sanebr si es urgente, fecha limite y el id del alumno (como llave foranea) que correpsonde a esa tarea y agregue el email que es uno por alumno
##Ademas se pone la relación que tiene con alumnos, se agrega su relacion polimorfica que permite que cuando el tipo de un registro sea normal devolvera la clase de Tarea. Al finale stan lso metodos de taarea 
##para marcarla como completada y cambiar su estatus y poara mostrar la tarea


class Tarea(Base):
    __tablename__ = "tareas"

    id:Mapped[int] = mapped_column(primary_key= True)
    descripcion: Mapped[str] = mapped_column(String(200))
    completada:Mapped[bool] = mapped_column(default=False)
    tipo:Mapped[str] = mapped_column(String(20), default="normal")
    fecha_limite:Mapped[str | None] = mapped_column(String(40), default=None)
    alumno_id:Mapped[int] = mapped_column(ForeignKey("alumnos.id"))

    alumno:Mapped["Alumno"] = relationship(back_populates="tareas")

    __mapper_args__ = {"polymorphic_on" : "tipo", "polymorphic_identity" : "normal"}

    def completar(self):
        self.completada = True

    def mostrar(self):
        estado = "completada" if self.completada else "pendiente"
        return f"{self.descripcion} ({estado})"

##Se modeló así porque es una clase que hereda de Tarea, con la relacion polimorfica distingue los que su tipo sea urgente para ejecutar el metodo mostrar exclusivo de tarea urgente

class TareaUrgente(Tarea):

    __mapper_args__ = {"polymorphic_identity" : "urgente"}
    def mostrar(self):
        return f"URGENTE! {super().mostrar()} vence el {self.fecha_limite}"


##Se modeló así porque la tabla de cursos solo necesita el ID nombre y agregue el profesor que es uno por curso
##Ademas se pone la relación que tiene con inscripciones (muchas por curso)
## y alumnos comos econdary al final se pone la etiqueta de la tabla

class Curso(Base):
    __tablename__ = "cursos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    profesor: Mapped[str] = mapped_column(String(100))

    inscripciones: Mapped[list["Inscripcion"]] = relationship(
        back_populates="curso", order_by="Inscripcion.id"
    )

    alumnos: Mapped[list["Alumno"]] = relationship(secondary="inscripciones", back_populates="cursos", order_by="Alumno.id")

    def __repr__(self):
        return f"<Curso {self.id}: {self.nombre}>"


##Se modeló así porque la tabla de inscripciones que hace la relacion de muchos a muchos entre alumnos y cursos solo necesita el ID alumno_id y curso_id como llaves foraaneas y
## agregue fecha de inscripcion que es una por inscripcion. Ademas se pone el UniqueContsrain que es una calse que ayuda a evitar registros duplicados donde solo puede haber 
## un curso con un alumno una sola vez. Se agregan als relaciones con alumno y curso y al final su etiqueta


class Inscripcion(Base):
    __tablename__ = "inscripciones"

    id: Mapped[int] = mapped_column(primary_key=True)

    alumno_id: Mapped[int] = mapped_column(ForeignKey("alumnos.id"))
    curso_id: Mapped[int] = mapped_column(ForeignKey("cursos.id"))

    fecha_inscripcion: Mapped[date] = mapped_column(default=date.today)

    __table_args__ = (
        UniqueConstraint("alumno_id", "curso_id", name="uq_alumno_curso"),
    )  ##EVITAR REGISTROS REPETIDOS

    alumno: Mapped["Alumno"] = relationship(back_populates="inscripciones")
    curso: Mapped["Curso"] = relationship(back_populates="inscripciones")

    def __repr__(self):
        return f"<Inscripcion alumno={self.alumno_id} curso={self.curso_id}>"

# ===== gestor.py =====
# TODO

from modelos import Tarea, TareaUrgente
from excepciones import TareaNoEncontradaError

class GestorDeTareas:
    def __init__(self, sesion):
        self._sesion = sesion

    def agregar_tarea(self, descripcion, alumno_id):
        tarea = Tarea(descripcion = descripcion, alumno_id = alumno_id)
        self._sesion.add(tarea)
        self._sesion.commit()
        return tarea

    def agregar_tarea_urgente(self, descripcion, fecha_limite, alumno_id):
            tarea = TareaUrgente(descripcion = descripcion, fecha_limite = fecha_limite, alumno_id = alumno_id)
            self._sesion.add(tarea)
            self._sesion.commit()
            return tarea

    def listar_tareas(self):
        for tarea in self._sesion.query(Tarea).order_by(Tarea.id).all():
            print(tarea.mostrar())

    def marcar_completada(self, tarea_id):
        tarea = self._sesion.get(Tarea, tarea_id)
        if tarea is None:
            raise TareaNoEncontradaError(f"No existe una tarea con id {tarea_id}")
        tarea.completar()
        self._sesion.commit()

    def total_pendientes(self):
        return self._sesion.query(Tarea).filter_by(completada = False).count()


# ===== excepciones.py =====
# TODO

class TareaNoEncontradaError(Exception):
    pass


# ===== main.py =====
# TODO

from basedatos import Sesion
from modelos import Tarea, Inscripcion, TareaUrgente, Curso, Alumno
from datetime import date

sesion = Sesion()

sesion.add_all(
    [
        Alumno(nombre="Ximena Ruvalcaba", email="ximenaruvalcaba@inadaptados"),
        Alumno(nombre="Juan Perez", email="juanperez@inadaptados"),
        Alumno(nombre="Adriana Santos", email="adrianasantos@inadaptados"),
    ]
)
sesion.commit()  

sesion.add_all(
    [
        TareaUrgente(descripcion="Revisar video 1", completada=False, fecha_limite="29/10/2026", alumno_id=1),
        TareaUrgente(descripcion="Enviar informe mensual", completada=False, fecha_limite="30/10/2026", alumno_id=1),
        Tarea(descripcion="Comprar café para la oficina", completada=True, fecha_limite="02/11/2026", alumno_id=2),
        TareaUrgente(descripcion="Planificar sprint de desarrollo", completada=False, fecha_limite="03/11/2026", alumno_id=2),
        Tarea(descripcion="Actualizar documentación del proyecto", completada=False, fecha_limite="05/11/2026", alumno_id=3),
    ]
)

sesion.add_all(
    [
        Curso(nombre="Python 1", profesor="Juan Salazar"),
        Curso(nombre="Bases de Datos SQL", profesor="María Rodríguez"),
        Curso(nombre="Desarrollo Web con React", profesor="Carlos Mendoza"),
        Curso(nombre="Introducción a la Inteligencia Artificial", profesor="Ana Gómez"),
        Curso(nombre="Estructuras de Datos y Algoritmos", profesor="Luis Torres"),
    ]
)
sesion.commit()  

sesion.add_all(
    [
        Inscripcion(alumno_id=1, curso_id=2, fecha_inscripcion="29/10/2026"),
        Inscripcion(alumno_id=3, curso_id=1, fecha_inscripcion="29/10/2026"),
        Inscripcion(alumno_id=2, curso_id=4, fecha_inscripcion="30/10/2026"),
        Inscripcion(alumno_id=1, curso_id=3, fecha_inscripcion="31/10/2026"),
        Inscripcion(alumno_id=3, curso_id=2, fecha_inscripcion="01/11/2026"),
    ]
)
sesion.commit()


# ===== alembic/env.py (los tres lugares que editaste) =====
# TODO
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from basedatos import Base, URL_BASE_DE_DATOS
import modelos 

config = context.config
config.set_main_option("sqlalchemy.url", URL_BASE_DE_DATOS)

target_metadata = Base.metadata

# ===== alembic/versions/<identificador>_<mensaje>.py (un encabezado por migración) =====
# TODO

# (.venv) PS C:\Users\arman\OneDrive\Escritorio\POO\ENTREGABLE_SPRINT4> alembic revision --autogenerate -m "crear tablas iniciales"
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.schemas
# INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.tables
# INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.types
# INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.constraints
# INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.defaults
# INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.comments
# INFO  [alembic.autogenerate.compare.tables] Detected added table 'alumnos'
# INFO  [alembic.autogenerate.compare.tables] Detected added table 'cursos'
# INFO  [alembic.autogenerate.compare.tables] Detected added table 'inscripciones'
# INFO  [alembic.autogenerate.compare.tables] Detected added table 'tareas'
# Generating C:\Users\arman\OneDrive\Escritorio\POO\ENTREGABLE_SPRINT4\alembic\versions\9df33c16c368_crear_tablas_iniciales.py ...  done

# Alembic (alembic/versions/9df33c16c368_crear_tablas_iniciales.py)

"""crear tablas iniciales

Revision ID: 9df33c16c368
Revises: 
Create Date: 2026-10-29 19:21:56.361628

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9df33c16c368'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('alumnos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cursos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('profesor', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nombre')
    )
    op.create_table('inscripciones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('alumno_id', sa.Integer(), nullable=False),
    sa.Column('curso_id', sa.Integer(), nullable=False),
    sa.Column('fecha_inscripcion', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['alumno_id'], ['alumnos.id'], ),
    sa.ForeignKeyConstraint(['curso_id'], ['cursos.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('alumno_id', 'curso_id', name='uq_alumno_curso')
    )
    op.create_table('tareas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('descripcion', sa.String(length=200), nullable=False),
    sa.Column('completada', sa.Boolean(), nullable=False),
    sa.Column('tipo', sa.String(length=20), nullable=False),
    sa.Column('fecha_limite', sa.String(length=40), nullable=True),
    sa.Column('alumno_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['alumno_id'], ['alumnos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tareas')
    op.drop_table('inscripciones')
    op.drop_table('cursos')
    op.drop_table('alumnos')
    # ### end Alembic commands ###


# ===== Comprobación desde una base vacía (pega las salidas como comentarios) =====
# alembic upgrade head:
# TODO

# (.venv) PS C:\Users\arman\OneDrive\Escritorio\POO\ENTREGABLE_SPRINT4> alembic upgrade head
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# INFO  [alembic.runtime.migration] Running upgrade  -> 9df33c16c368, crear tablas iniciales

# alembic history:
# TODO

# (.venv) PS C:\Users\arman\OneDrive\Escritorio\POO\ENTREGABLE_SPRINT4> alembic history
# <base> -> 9df33c16c368 (head), crear tablas iniciales

# alembic downgrade -1 + alembic current, y alembic upgrade head + alembic current:
# TODO

# (.venv) PS C:\Users\arman\OneDrive\Escritorio\POO\ENTREGABLE_SPRINT4> alembic downgrade -1 
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# INFO  [alembic.runtime.migration] Running downgrade 9df33c16c368 -> , crear tablas iniciales

# (.venv) PS C:\Users\arman\OneDrive\Escritorio\POO\ENTREGABLE_SPRINT4> alembic current
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.

# (.venv) PS C:\Users\arman\OneDrive\Escritorio\POO\ENTREGABLE_SPRINT4> alembic upgrade head
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# INFO  [alembic.runtime.migration] Running upgrade  -> 9df33c16c368, crear tablas iniciales

# (.venv) PS C:\Users\arman\OneDrive\Escritorio\POO\ENTREGABLE_SPRINT4> alembic current
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# 9df33c16c368 (head)

# python main.py:
# TODO

from basedatos import Sesion
from modelos import Tarea, Inscripcion, TareaUrgente, Curso, Alumno
from datetime import date

sesion = Sesion()

sesion.add_all(
    [
        Alumno(nombre="Ximena Ruvalcaba", email="ximenaruvalcaba@inadaptados"),
        Alumno(nombre="Juan Perez", email="juanperez@inadaptados"),
        Alumno(nombre="Adriana Santos", email="adrianasantos@inadaptados"),
    ]
)
sesion.commit()  

sesion.add_all(
    [
        TareaUrgente(descripcion="Revisar video 1", completada=False, fecha_limite="29/10/2026", alumno_id=1),
        TareaUrgente(descripcion="Enviar informe mensual", completada=False, fecha_limite="30/10/2026", alumno_id=1),
        Tarea(descripcion="Comprar café para la oficina", completada=True, fecha_limite="02/11/2026", alumno_id=2),
        TareaUrgente(descripcion="Planificar sprint de desarrollo", completada=False, fecha_limite="03/11/2026", alumno_id=2),
        Tarea(descripcion="Actualizar documentación del proyecto", completada=False, fecha_limite="05/11/2026", alumno_id=3),
    ]
)

sesion.add_all(
    [
        Curso(nombre="Python 1", profesor="Juan Salazar"),
        Curso(nombre="Bases de Datos SQL", profesor="María Rodríguez"),
        Curso(nombre="Desarrollo Web con React", profesor="Carlos Mendoza"),
        Curso(nombre="Introducción a la Inteligencia Artificial", profesor="Ana Gómez"),
        Curso(nombre="Estructuras de Datos y Algoritmos", profesor="Luis Torres"),
    ]
)
sesion.commit()  

sesion.add_all(
    [
        Inscripcion(alumno_id=1, curso_id=2, fecha_inscripcion="29/10/2026"),
        Inscripcion(alumno_id=3, curso_id=1, fecha_inscripcion="29/10/2026"),
        Inscripcion(alumno_id=2, curso_id=4, fecha_inscripcion="30/10/2026"),
        Inscripcion(alumno_id=1, curso_id=3, fecha_inscripcion="31/10/2026"),
        Inscripcion(alumno_id=3, curso_id=2, fecha_inscripcion="01/11/2026"),
    ]
)
sesion.commit()


# ===== Repositorio =====
# Enlace a tu repositorio de GitHub y los mensajes de tus commits del sprint:
# TODO
# https://github.com/armandomoracuellar-cpu/inadaptados-sprint4

# 095fb22 (HEAD -> main, origin/main) Entrega final Sprint 4: modelos, base de datos y gestor
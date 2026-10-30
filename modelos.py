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

class TareaUrgente(Tarea):

    __mapper_args__ = {"polymorphic_identity" : "urgente"}
    def mostrar(self):
        return f"URGENTE! {super().mostrar()} vence el {self.fecha_limite}"

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


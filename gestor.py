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
        
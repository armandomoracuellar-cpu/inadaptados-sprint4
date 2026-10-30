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

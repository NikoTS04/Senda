class SendaException(Exception):
    """Base exception for Senda domain exceptions"""
    pass

class EscritoNoEncontradoException(SendaException):
    def __init__(self, escrito_id: int):
        super().__init__(f"El escrito con ID {escrito_id} no existe.")
        self.escrito_id = escrito_id

class ComentarioNoEncontradoException(SendaException):
    def __init__(self, comentario_id: int):
        super().__init__(f"El comentario con ID {comentario_id} no existe.")
        self.comentario_id = comentario_id

class AccesoDenegadoException(SendaException):
    def __init__(self, mensaje: str = "No tiene permisos para realizar esta accion."):
        super().__init__(mensaje)

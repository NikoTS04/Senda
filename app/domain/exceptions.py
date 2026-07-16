class SendaException(Exception):
    """Base exception for Senda domain exceptions"""
    pass

class EscritoNoEncontradoException(SendaException):
    def __init__(self, escrito_id: int):
        super().__init__(f"El escrito con ID {escrito_id} no existe.")
        self.escrito_id = escrito_id

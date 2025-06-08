
from models.tables import PredictionsUser


def exist_user(user_id: int, db) -> bool:
    """
    Verifica si un usuario existe en la base de datos.

    Args:
        user_id (int): ID del usuario a verificar.
        db: Sesión de la base de datos.

    Returns:
        bool: True si el usuario existe, False en caso contrario.
    """
    user = db.query(PredictionsUser).filter(PredictionsUser.user_id == user_id).first()
    if not user:
        return False
    return True
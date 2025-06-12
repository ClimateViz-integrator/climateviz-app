
from models.tables import User


def exist_user(user_id: int | None, db) -> bool:
    """
    Verifica si un usuario existe en la base de datos.
    Si no se proporciona un user_id, se considera como válido.

    Args:
        user_id (int | None): ID del usuario a verificar.
        db: Sesión de la base de datos.

    Returns:
        bool: True si el usuario existe o no se proporciona user_id, False en caso contrario.
    """
    if user_id is None:
        return True
    user = db.query(User).filter(User.id == user_id).first()
    return user is not None

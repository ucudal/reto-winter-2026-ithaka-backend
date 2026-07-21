"""Crea un usuario Coordinator inicial para poder probar el login.

Uso:  python seed.py
"""
from app.core.db.session import SessionLocal
from app.core.models.enums import UserRole
from app.core.models.user import User
from app.core.security import hash_password

EMAIL = "Pedro@ucu.edu.uy"
PASSWORD = "Pedro1234"


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == EMAIL).first()
        if existing is not None:
            print(f"Ya existe un usuario con email {EMAIL}, no hago nada.")
            return
        db.add(
            User(
                name="Coordinador Ithaka",
                email=EMAIL,
                role=UserRole.COORDINATOR,
                password_hash=hash_password(PASSWORD),
            )
        )
        db.commit()
        print(f"Coordinator creado -> email: {EMAIL}  password: {PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

import sys
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from app.core.db.session import SessionLocal
from app.core.models import (
    Base, User, Cohort, Stage, Tutor, Group, Student,
    Deliverable, Meeting, SupportMaterial, Document, Comment
)
from app.core.models.enums import UserRole, TutorRole, DocumentPlatform, EntityType
from app.core.security import hash_password


def seed_database(force: bool = False):
    db: Session = SessionLocal()

    try:
        print("Iniciando seeder de la base de datos...")

        if force:
            print("Limpiando datos existentes...")
            db.query(Comment).delete()
            db.query(Document).delete()
            db.query(SupportMaterial).delete()
            db.query(Meeting).delete()
            db.query(Deliverable).delete()
            db.query(Student).delete()
            db.query(Group).delete()
            db.query(Tutor).delete()
            db.query(Stage).delete()
            db.query(Cohort).delete()
            db.query(User).delete()
            db.commit()
        elif db.query(Cohort).first():
            print("La base de datos ya contiene datos. Usa 'python seed.py --force' para sobrescribir.")
            return

        # 1. Crear Usuarios
        print("- Creando Usuarios...")
        default_pwd_hash = hash_password("password")
        u_coord = User(name="Sofía Martínez", email="coord@ithaka.ucu.edu.uy", role=UserRole.COORDINATOR, password_hash=default_pwd_hash)
        u_tut1 = User(name="María Pérez", email="maria.perez@ithaka.ucu.edu.uy", role=UserRole.BUSINESS_TUTOR, password_hash=default_pwd_hash)
        u_tut2 = User(name="Diego Ramírez", email="diego.ramirez@ithaka.ucu.edu.uy", role=UserRole.TECHNICAL_TUTOR, password_hash=default_pwd_hash)
        u_tut3 = User(name="Lucía Gómez", email="lucia.gomez@ithaka.ucu.edu.uy", role=UserRole.BUSINESS_TUTOR, password_hash=default_pwd_hash)
        u_std1 = User(name="Ana Fernández", email="ana.fernandez@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash)
        u_std2 = User(name="Luca Rossi", email="luca.rossi@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash)
        
        db.add_all([u_coord, u_tut1, u_tut2, u_tut3, u_std1, u_std2])
        db.flush()

        # 2. Crear Cohorte
        print("- Creando Cohorte...")
        cohort_2026_1 = Cohort(
            year=2026,
            semester=1,
            start_date=date(2026, 3, 1),
            end_date=date(2026, 7, 30),
            status="Active",
            notes="Cohorte Otoño 2026 - Enfoque Sostenibilidad y GovTech"
        )
        db.add(cohort_2026_1)
        db.flush()

        # 3. Crear Etapas
        print("- Creando Etapas...")
        stage_1 = Stage(
            cohort_id=cohort_2026_1.id,
            name="Validación de Problema",
            order=1,
            key_dates=[
                {"description": "Pitch Inicial", "date": "2026-03-15"},
                {"description": "Entrega Mapa de Empatía", "date": "2026-03-30"}
            ]
        )
        stage_2 = Stage(
            cohort_id=cohort_2026_1.id,
            name="Modelo de Negocio",
            order=2,
            key_dates=[
                {"description": "Presentación BMC", "date": "2026-04-20"}
            ]
        )
        stage_3 = Stage(
            cohort_id=cohort_2026_1.id,
            name="Prototipado y MVP",
            order=3,
            key_dates=[
                {"description": "Demo Day Interno", "date": "2026-06-10"}
            ]
        )
        db.add_all([stage_1, stage_2, stage_3])
        db.flush()

        # 4. Crear Tutores
        print("- Creando Tutores...")
        tutor_b1 = Tutor(
            user_id=u_tut1.id,
            name="María Pérez",
            role=TutorRole.BUSINESS,
            specialty="Modelos de Negocio SaaS & Finanzas",
            max_capacity=60,
            availability="Lunes y Miércoles 14:00 - 18:00",
            status="Active"
        )
        tutor_t1 = Tutor(
            user_id=u_tut2.id,
            name="Diego Ramírez",
            role=TutorRole.TECHNICAL,
            specialty="Arquitectura Cloud & Desarrollos Web/Mobile",
            max_capacity=40,
            availability="Martes y Jueves 09:00 - 13:00",
            status="Active"
        )
        tutor_b2 = Tutor(
            user_id=u_tut3.id,
            name="Lucía Gómez",
            role=TutorRole.BUSINESS,
            specialty="Marketing Digital & Validación de Mercado",
            max_capacity=50,
            availability="Viernes 10:00 - 16:00",
            status="Active"
        )
        db.add_all([tutor_b1, tutor_t1, tutor_b2])
        db.flush()

        # 5. Crear Grupos
        print("- Creando Grupos...")
        group_1 = Group(
            name="EcoRoute",
            cohort_id=cohort_2026_1.id,
            current_stage_id=stage_2.id,
            idea="Plataforma de optimización de rutas de recolección de residuos reciclables para empresas e industrias.",
            major="Ingeniería en Informática",
            status="Active",
            business_tutor_id=tutor_b1.id,
            technical_tutor_id=tutor_t1.id
        )
        group_2 = Group(
            name="HealthPulse",
            cohort_id=cohort_2026_1.id,
            current_stage_id=stage_1.id,
            idea="Sistema de monitoreo remoto para pacientes mayores basado en dispositivos IoT de bajo costo.",
            major="Ingeniería Biomédica",
            status="Active",
            business_tutor_id=tutor_b2.id,
            technical_tutor_id=tutor_t1.id
        )
        db.add_all([group_1, group_2])
        db.flush()

        # 6. Crear Estudiantes
        print("- Creando Estudiantes...")
        std_1 = Student(user_id=u_std1.id, name="Ana Fernández", email="ana.fernandez@correo.ucu.edu.uy", major="Ingeniería en Informática", group_id=group_1.id)
        std_2 = Student(user_id=u_std2.id, name="Luca Rossi", email="luca.rossi@correo.ucu.edu.uy", major="Ingeniería en Informática", group_id=group_1.id)
        std_3 = Student(name="Mateo Silva", email="mateo.silva@correo.ucu.edu.uy", major="Licenciatura en Negocios", group_id=group_2.id)
        std_4 = Student(name="Camila Torres", email="camila.torres@correo.ucu.edu.uy", major="Ingeniería Biomédica", group_id=group_2.id)
        db.add_all([std_1, std_2, std_3, std_4])
        db.flush()

        # 7. Crear Entregables
        print("- Creando Entregables...")
        deliv_1 = Deliverable(group_id=group_1.id, stage_id=stage_1.id, expected_date=date(2026, 3, 30), status="Approved")
        deliv_2 = Deliverable(group_id=group_1.id, stage_id=stage_2.id, expected_date=date(2026, 4, 20), status="Pending")
        deliv_3 = Deliverable(group_id=group_2.id, stage_id=stage_1.id, expected_date=date(2026, 3, 30), status="Pending")
        db.add_all([deliv_1, deliv_2, deliv_3])
        db.flush()

        # 8. Crear Reuniones
        print("- Creando Reuniones...")
        meet_1 = Meeting(
            group_id=group_1.id,
            tutor_ids=[tutor_b1.id, tutor_t1.id],
            date=datetime(2026, 4, 10, 15, 0, tzinfo=timezone.utc),
            participants=[std_1.id, std_2.id],
            notes="Se discutió la propuesta de valor y la factibilidad técnica del algoritmo de ruteo.",
            next_steps="Ajustar BMC para segmento B2B y armar prototipo de arquitectura en AWS.",
            hours_spent=2.5,
            links=[{"type": "Drive", "url": "https://drive.google.com/ecoroute-minuta-1"}]
        )
        db.add(meet_1)

        # 9. Crear Materiales de Apoyo
        print("- Creando Materiales de Apoyo...")
        mat_1 = SupportMaterial(stage_id=stage_1.id, title="Plantilla de Mapa de Empatía", url="https://drive.google.com/template-empatia")
        mat_2 = SupportMaterial(stage_id=stage_2.id, title="Business Model Canvas Template", url="https://drive.google.com/template-bmc")
        db.add_all([mat_1, mat_2])
        db.flush()

        # 10. Crear Documentos Polimórficos
        print("- Creando Documentos Polimórficos...")
        doc_group = Document(entity_type=EntityType.GROUP, entity_id=group_1.id, url="https://drive.google.com/ecoroute-repo-general", platform=DocumentPlatform.DRIVE, order=1)
        doc_deliv = Document(entity_type=EntityType.DELIVERABLE, entity_id=deliv_1.id, url="https://sharepoint.com/ecoroute-reporte-validacion", platform=DocumentPlatform.SHAREPOINT, order=1)
        db.add_all([doc_group, doc_deliv])

        # 11. Crear Comentarios
        print("- Creando Comentarios...")
        comm_1 = Comment(tutor_id=tutor_b1.id, deliverable_id=deliv_1.id, content="Excelente trabajo en las entrevistas de validación. La muestra de 20 empresas fue muy representativa.")
        db.add(comm_1)

        db.commit()
        print("¡Seeder ejecutado con éxito! Base de datos poblada.")

    except Exception as e:
        db.rollback()
        print(f"Error durante la ejecución del seeder: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    seed_database(force=force_flag)

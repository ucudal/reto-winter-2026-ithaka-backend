import sys
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from app.core.db.session import SessionLocal
from app.core.models import (
    Base, User, Cohort, Stage, Tutor, Group, Student,
    Deliverable, Meeting, SupportMaterial, Document,
    Comment, Checkpoint
)
from app.core.models.enums import UserRole, TutorRole, DocumentPlatform, EntityType
from app.core.models.meeting import MeetingStatus
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
            db.query(Checkpoint).delete()
            db.query(Student).delete()
            db.query(Group).delete()
            db.query(Tutor).delete()
            db.query(Stage).delete()
            db.query(Cohort).delete()
            db.query(User).delete()
            db.commit()
        elif db.query(Cohort).first():
            print("La base de datos ya contiene datos. Usa 'python app/core/db/seed.py --force' para sobrescribir.")
            return

        default_pwd_hash = hash_password("password")

        # 1. Crear Usuarios (25 Usuarios: 1 Coord, 8 Tutores, 16 Estudiantes)
        print("- Creando Usuarios (25)...")
        users = [
            User(name="Sofía Martínez", email="coord@ithaka.ucu.edu.uy", role=UserRole.COORDINATOR, password_hash=default_pwd_hash),
            # Tutores
            User(name="María Pérez", email="maria.perez@ithaka.ucu.edu.uy", role=UserRole.BUSINESS_TUTOR, password_hash=default_pwd_hash),
            User(name="Diego Ramírez", email="diego.ramirez@ithaka.ucu.edu.uy", role=UserRole.TECHNICAL_TUTOR, password_hash=default_pwd_hash),
            User(name="Lucía Gómez", email="lucia.gomez@ithaka.ucu.edu.uy", role=UserRole.BUSINESS_TUTOR, password_hash=default_pwd_hash),
            User(name="Carlos Alcaraz", email="carlos.alcaraz@ithaka.ucu.edu.uy", role=UserRole.TECHNICAL_TUTOR, password_hash=default_pwd_hash),
            User(name="Elena Rostova", email="elena.rostova@ithaka.ucu.edu.uy", role=UserRole.BUSINESS_TUTOR, password_hash=default_pwd_hash),
            User(name="Fernando Torres", email="fernando.torres@ithaka.ucu.edu.uy", role=UserRole.BUSINESS_TUTOR, password_hash=default_pwd_hash),
            User(name="Patricia Suárez", email="patricia.suarez@ithaka.ucu.edu.uy", role=UserRole.TECHNICAL_TUTOR, password_hash=default_pwd_hash),
            User(name="Gonzalo Méndez", email="gonzalo.mendez@ithaka.ucu.edu.uy", role=UserRole.BUSINESS_TUTOR, password_hash=default_pwd_hash),
            # Estudiantes
            User(name="Ana Fernández", email="ana.fernandez@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Luca Rossi", email="luca.rossi@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Mateo Silva", email="mateo.silva@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Camila Torres", email="camila.torres@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Joaquín Olivera", email="joaquin.olivera@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Valentina Morales", email="valentina.morales@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Gabriel Méndez", email="gabriel.mendez@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Isabella Castro", email="isabella.castro@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Rodrigo Bentancur", email="rodrigo.bentancur@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Martina Domínguez", email="martina.dominguez@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Nicolás Acosta", email="nicolas.acosta@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Sofía Cabrera", email="sofia.cabrera@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Tomás Roldán", email="tomas.roldan@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Florencia Paz", email="florencia.paz@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Agustín Benítez", email="agustin.benitez@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
            User(name="Luciana Vega", email="luciana.vega@correo.ucu.edu.uy", role=UserRole.STUDENT, password_hash=default_pwd_hash),
        ]
        db.add_all(users)
        db.flush()

        u_coord = users[0]
        tutor_users = users[1:9]
        student_users = users[9:25]

        # 2. Crear Cohortes (15 Cohortes)
        print("- Creando Cohortes (15)...")
        cohorts = [
            Cohort(year=2023, semester=1, start_date=date(2023, 3, 1), end_date=date(2023, 7, 30), status="Finished", notes="Cohorte Otoño 2023"),
            Cohort(year=2023, semester=2, start_date=date(2023, 8, 1), end_date=date(2023, 12, 20), status="Finished", notes="Cohorte Primavera 2023"),
            Cohort(year=2024, semester=1, start_date=date(2024, 3, 1), end_date=date(2024, 7, 30), status="Finished", notes="Cohorte Otoño 2024"),
            Cohort(year=2024, semester=2, start_date=date(2024, 8, 1), end_date=date(2024, 12, 20), status="Finished", notes="Cohorte Primavera 2024"),
            Cohort(year=2025, semester=1, start_date=date(2025, 3, 1), end_date=date(2025, 7, 30), status="Finished", notes="Cohorte Otoño 2025"),
            Cohort(year=2025, semester=2, start_date=date(2025, 8, 1), end_date=date(2025, 12, 20), status="Finished", notes="Cohorte Primavera 2025 - FinTech & Health"),
            Cohort(year=2026, semester=1, start_date=date(2026, 3, 1), end_date=date(2026, 7, 30), status="Active", notes="Cohorte Otoño 2026 - Enfoque Sostenibilidad y GovTech"),
            Cohort(year=2026, semester=2, start_date=date(2026, 8, 1), end_date=date(2026, 12, 20), status="Planned", notes="Cohorte Primavera 2026 - AI & Robotics"),
            Cohort(year=2027, semester=1, start_date=date(2027, 3, 1), end_date=date(2027, 7, 30), status="Planned", notes="Cohorte Otoño 2027 - Biotech"),
            Cohort(year=2027, semester=2, start_date=date(2027, 8, 1), end_date=date(2027, 12, 20), status="Planned", notes="Cohorte Primavera 2027 - EdTech"),
            Cohort(year=2028, semester=1, start_date=date(2028, 3, 1), end_date=date(2028, 7, 30), status="Planned", notes="Cohorte Otoño 2028 - AgTech Advanced"),
            Cohort(year=2028, semester=2, start_date=date(2028, 8, 1), end_date=date(2028, 12, 20), status="Planned", notes="Cohorte Primavera 2028 - Deep Tech"),
            Cohort(year=2029, semester=1, start_date=date(2029, 3, 1), end_date=date(2029, 7, 30), status="Planned", notes="Cohorte Otoño 2029 - Quantum Computing"),
            Cohort(year=2029, semester=2, start_date=date(2029, 8, 1), end_date=date(2029, 12, 20), status="Planned", notes="Cohorte Primavera 2029 - CleanEnergy"),
            Cohort(year=2030, semester=1, start_date=date(2030, 3, 1), end_date=date(2030, 7, 30), status="Planned", notes="Cohorte Otoño 2030 - SpaceTech"),
        ]
        db.add_all(cohorts)
        db.flush()
        cohort_active = cohorts[6]

        # 3. Crear Etapas (15 Etapas)
        print("- Creando Etapas (15)...")
        stages = [
            Stage(cohort_id=cohort_active.id, name="Validación de Problema", order=1, key_dates=[{"description": "Pitch Inicial", "date": "2026-03-15"}, {"description": "Entrega Mapa de Empatía", "date": "2026-03-30"}]),
            Stage(cohort_id=cohort_active.id, name="Modelo de Negocio", order=2, key_dates=[{"description": "Presentación BMC", "date": "2026-04-20"}]),
            Stage(cohort_id=cohort_active.id, name="Prototipado y MVP", order=3, key_dates=[{"description": "Demo Day Interno", "date": "2026-06-10"}]),
            Stage(cohort_id=cohort_active.id, name="Pruebas de Campo", order=4, key_dates=[{"description": "Lanzamiento Piloto", "date": "2026-06-25"}]),
            Stage(cohort_id=cohort_active.id, name="Estrategia Go-to-Market", order=5, key_dates=[{"description": "Plan Comercial", "date": "2026-07-10"}]),
            Stage(cohort_id=cohorts[0].id, name="Fase Inicial 2023-1", order=1, key_dates=[]),
            Stage(cohort_id=cohorts[0].id, name="Fase Final 2023-1", order=2, key_dates=[]),
            Stage(cohort_id=cohorts[1].id, name="Fase Única 2023-2", order=1, key_dates=[]),
            Stage(cohort_id=cohorts[2].id, name="Ideación 2024", order=1, key_dates=[]),
            Stage(cohort_id=cohorts[2].id, name="Cierre 2024", order=2, key_dates=[]),
            Stage(cohort_id=cohorts[5].id, name="Validación 2025-2", order=1, key_dates=[]),
            Stage(cohort_id=cohorts[5].id, name="Aceleración 2025-2", order=2, key_dates=[]),
            Stage(cohort_id=cohorts[7].id, name="Preparación 2026-2", order=1, key_dates=[]),
            Stage(cohort_id=cohorts[8].id, name="Diseño Biotech 2027", order=1, key_dates=[]),
            Stage(cohort_id=cohorts[9].id, name="Lanzamiento EdTech 2027", order=1, key_dates=[]),
        ]
        db.add_all(stages)
        db.flush()
        stage_1, stage_2, stage_3, stage_4, stage_5 = stages[0:5]

        # 4. Crear Tutores (15 Tutores)
        print("- Creando Tutores (15)...")
        tutors = [
            Tutor(user_id=tutor_users[0].id, name="María Pérez", role=TutorRole.BUSINESS, specialty="Modelos SaaS & Finanzas", max_capacity=60, availability="Lunes y Miércoles 14:00-18:00", status="Active", linkedin_url="https://www.linkedin.com/in/maria-perez-ithaka"),
            Tutor(user_id=tutor_users[1].id, name="Diego Ramírez", role=TutorRole.TECHNICAL, specialty="Arquitectura Cloud & Mobile", max_capacity=40, availability="Martes y Jueves 09:00-13:00", status="Active", linkedin_url="https://www.linkedin.com/in/diego-ramirez-ithaka"),
            Tutor(user_id=tutor_users[2].id, name="Lucía Gómez", role=TutorRole.BUSINESS, specialty="Marketing & Validación", max_capacity=50, availability="Viernes 10:00-16:00", status="Active", linkedin_url="https://www.linkedin.com/in/lucia-gomez-ithaka"),
            Tutor(user_id=tutor_users[3].id, name="Carlos Alcaraz", role=TutorRole.TECHNICAL, specialty="Ciberseguridad & DevSecOps", max_capacity=30, availability="Lunes y Viernes 09:00-12:00", status="Active", linkedin_url="https://www.linkedin.com/in/carlos-alcaraz-ithaka"),
            Tutor(user_id=tutor_users[4].id, name="Elena Rostova", role=TutorRole.BUSINESS, specialty="Estrategia Comercial B2B", max_capacity=45, availability="Miércoles y Jueves 15:00-19:00", status="Active", linkedin_url="https://www.linkedin.com/in/elena-rostova-ithaka"),
            Tutor(user_id=tutor_users[5].id, name="Fernando Torres", role=TutorRole.BUSINESS, specialty="Propiedad Intelectual", max_capacity=20, availability="Martes 14:00-18:00", status="Active", linkedin_url="https://www.linkedin.com/in/fernando-torres-ithaka"),
            Tutor(user_id=tutor_users[6].id, name="Patricia Suárez", role=TutorRole.TECHNICAL, specialty="Inteligencia Artificial & Datos", max_capacity=35, availability="Lunes 10:00-14:00", status="Active", linkedin_url="https://www.linkedin.com/in/patricia-suarez-ithaka"),
            Tutor(user_id=tutor_users[7].id, name="Gonzalo Méndez", role=TutorRole.BUSINESS, specialty="Finanzas Corporativas & Pitch", max_capacity=50, availability="Jueves 10:00-16:00", status="Active", linkedin_url=None),
            Tutor(name="Valentina Ríos", role=TutorRole.TECHNICAL, specialty="Diseño UX/UI & Prototipado", max_capacity=40, availability="Miércoles 09:00-15:00", status="Active", linkedin_url=None),
            Tutor(name="Esteban Benítez", role=TutorRole.BUSINESS, specialty="Desarrollo Internacional", max_capacity=25, availability="Viernes 14:00-18:00", status="Active", linkedin_url=None),
            Tutor(name="Romina Franco", role=TutorRole.TECHNICAL, specialty="DevOps & Infraestructura", max_capacity=30, availability="Lunes 14:00-18:00", status="Active", linkedin_url="https://www.linkedin.com/in/romina-franco"),
            Tutor(name="Ignacio Varela", role=TutorRole.BUSINESS, specialty="Levantamiento de Capital", max_capacity=40, availability="Martes 10:00-14:00", status="Active", linkedin_url=None),
            Tutor(name="Camila Paez", role=TutorRole.BUSINESS, specialty="Growth Hacking & Analytics", max_capacity=35, availability="Jueves 14:00-18:00", status="Inactive", linkedin_url=None),
            Tutor(name="Matías Soria", role=TutorRole.TECHNICAL, specialty="Blockchain & Smart Contracts", max_capacity=30, availability="Viernes 09:00-13:00", status="Inactive", linkedin_url=None),
            Tutor(name="Victoria Morales", role=TutorRole.BUSINESS, specialty="Liderazgo & Gestión de Equipos", max_capacity=50, availability="Miércoles 10:00-16:00", status="Inactive", linkedin_url=None),
        ]
        db.add_all(tutors)
        db.flush()
        t_b1, t_t1, t_b2, t_t2, t_b3, t_b4, t_t3, t_b5 = tutors[0:8]

        # 5. Crear Grupos (15 Grupos)
        print("- Creando Grupos (15)...")
        groups = [
            Group(name="EcoRoute", cohort_id=cohort_active.id, current_stage_id=stage_2.id, idea="Plataforma de optimización de rutas de recolección de residuos.", major="Ingeniería en Informática", status="Active", business_tutor_id=t_b1.id, technical_tutor_id=t_t1.id),
            Group(name="HealthPulse", cohort_id=cohort_active.id, current_stage_id=stage_1.id, idea="Sistema de monitoreo remoto para pacientes mayores basado en IoT.", major="Ingeniería Biomédica", status="Active", business_tutor_id=t_b2.id, technical_tutor_id=t_t1.id),
            Group(name="AgroSmart", cohort_id=cohort_active.id, current_stage_id=stage_3.id, idea="Sensores inteligentes para optimizar el riego agrícola.", major="Ingeniería Industrial", status="Active", business_tutor_id=t_b1.id, technical_tutor_id=t_t2.id),
            Group(name="EduFlow", cohort_id=cohort_active.id, current_stage_id=stage_1.id, idea="Plataforma adaptativa de aprendizaje con Inteligencia Artificial.", major="Licenciatura en Educación", status="Active", business_tutor_id=t_b3.id, technical_tutor_id=t_t2.id),
            Group(name="FinTrack", cohort_id=cohort_active.id, current_stage_id=stage_4.id, idea="Gestión automatizada de finanzas para freelancers y PYMEs.", major="Licenciatura en Negocios", status="Active", business_tutor_id=t_b1.id, technical_tutor_id=t_t1.id),
            Group(name="SolarGrid", cohort_id=cohort_active.id, current_stage_id=stage_2.id, idea="Intercambio de energía solar entre pares mediante Blockchain.", major="Ingeniería Eléctrica", status="Active", business_tutor_id=t_b2.id, technical_tutor_id=t_t2.id),
            Group(name="BioPack", cohort_id=cohorts[5].id, current_stage_id=stages[11].id, idea="Empaques biodegradables a partir de residuos orgánicos marinos.", major="Ingeniería Química", status="Active", business_tutor_id=t_b3.id, technical_tutor_id=t_t1.id),
            Group(name="LogiTrack", cohort_id=cohorts[5].id, current_stage_id=stages[11].id, idea="Trazabilidad fría para transporte de vacunas e insumos médicos.", major="Ingeniería Industrial", status="Active", business_tutor_id=t_b1.id, technical_tutor_id=t_t2.id),
            Group(name="UrbanMobility", cohort_id=cohorts[0].id, current_stage_id=stages[6].id, idea="Estaciones de micro-movilidad eléctrica para campus universitarios.", major="Diseño Industrial", status="Inactive", business_tutor_id=t_b2.id, technical_tutor_id=t_t1.id),
            Group(name="CyberShield", cohort_id=cohort_active.id, current_stage_id=stage_5.id, idea="Auditoría automatizada de vulnerabilidades para startups.", major="Ingeniería en Informática", status="Active", business_tutor_id=t_b3.id, technical_tutor_id=t_t2.id),
            Group(name="NutriBot", cohort_id=cohort_active.id, current_stage_id=stage_1.id, idea="Asistente nutricional IA para dietas clínicas personalizadas.", major="Licenciatura en Nutrición", status="Active", business_tutor_id=t_b4.id, technical_tutor_id=t_t3.id),
            Group(name="WaterClean", cohort_id=cohort_active.id, current_stage_id=stage_2.id, idea="Filtros de nanotecnología para potabilización de agua rural.", major="Ingeniería Química", status="Active", business_tutor_id=t_b5.id, technical_tutor_id=t_t1.id),
            Group(name="RecyclePay", cohort_id=cohort_active.id, current_stage_id=stage_3.id, idea="Sistema de incentivos económicos por reciclar botellas.", major="Licenciatura en Negocios", status="Active", business_tutor_id=t_b1.id, technical_tutor_id=t_t3.id),
            Group(name="SafeDrive", cohort_id=cohorts[2].id, current_stage_id=stages[8].id, idea="Detección de fatiga en conductores mediante visión computacional.", major="Ingeniería en Informática", status="Inactive", business_tutor_id=t_b2.id, technical_tutor_id=t_t2.id),
            Group(name="CargoFly", cohort_id=cohorts[3].id, current_stage_id=stages[9].id, idea="Drones de entrega rápida de muestras biológicas entre hospitales.", major="Ingeniería Biomédica", status="Inactive", business_tutor_id=t_b4.id, technical_tutor_id=t_t3.id),
        ]
        db.add_all(groups)
        db.flush()

        # 6. Crear Estudiantes (16 Estudiantes)
        print("- Creando Estudiantes (16)...")
        students = [
            Student(user_id=student_users[0].id, name="Ana Fernández", email="ana.fernandez@correo.ucu.edu.uy", major="Ingeniería en Informática", group_id=groups[0].id, is_graduation_project=True, linkedin_url="https://www.linkedin.com/in/ana-fernandez"),
            Student(user_id=student_users[1].id, name="Luca Rossi", email="luca.rossi@correo.ucu.edu.uy", major="Ingeniería en Informática", group_id=groups[0].id, is_graduation_project=False, linkedin_url="https://www.linkedin.com/in/luca-rossi"),
            Student(user_id=student_users[2].id, name="Mateo Silva", email="mateo.silva@correo.ucu.edu.uy", major="Licenciatura en Negocios", group_id=groups[1].id, is_graduation_project=True, linkedin_url=None),
            Student(user_id=student_users[3].id, name="Camila Torres", email="camila.torres@correo.ucu.edu.uy", major="Ingeniería Biomédica", group_id=groups[1].id, is_graduation_project=False, linkedin_url="https://www.linkedin.com/in/camila-torres"),
            Student(user_id=student_users[4].id, name="Joaquín Olivera", email="joaquin.olivera@correo.ucu.edu.uy", major="Ingeniería Industrial", group_id=groups[2].id, is_graduation_project=True, linkedin_url="https://www.linkedin.com/in/joaquin-olivera"),
            Student(user_id=student_users[5].id, name="Valentina Morales", email="valentina.morales@correo.ucu.edu.uy", major="Licenciatura en Educación", group_id=groups[3].id, is_graduation_project=True, linkedin_url="https://www.linkedin.com/in/valentina-morales"),
            Student(user_id=student_users[6].id, name="Gabriel Méndez", email="gabriel.mendez@correo.ucu.edu.uy", major="Licenciatura en Negocios", group_id=groups[4].id, is_graduation_project=False, linkedin_url=None),
            Student(user_id=student_users[7].id, name="Isabella Castro", email="isabella.castro@correo.ucu.edu.uy", major="Ingeniería Eléctrica", group_id=groups[5].id, is_graduation_project=True, linkedin_url="https://www.linkedin.com/in/isabella-castro"),
            Student(user_id=student_users[8].id, name="Rodrigo Bentancur", email="rodrigo.bentancur@correo.ucu.edu.uy", major="Ingeniería Química", group_id=groups[6].id, is_graduation_project=False, linkedin_url=None),
            Student(user_id=student_users[9].id, name="Martina Domínguez", email="martina.dominguez@correo.ucu.edu.uy", major="Ingeniería en Informática", group_id=groups[9].id, is_graduation_project=True, linkedin_url="https://www.linkedin.com/in/martina-dominguez"),
            Student(user_id=student_users[10].id, name="Nicolás Acosta", email="nicolas.acosta@correo.ucu.edu.uy", major="Licenciatura en Nutrición", group_id=groups[10].id, is_graduation_project=True, linkedin_url=None),
            Student(user_id=student_users[11].id, name="Sofía Cabrera", email="sofia.cabrera@correo.ucu.edu.uy", major="Ingeniería Química", group_id=groups[11].id, is_graduation_project=False, linkedin_url="https://www.linkedin.com/in/sofia-cabrera"),
            Student(user_id=student_users[12].id, name="Tomás Roldán", email="tomas.roldan@correo.ucu.edu.uy", major="Licenciatura en Negocios", group_id=groups[12].id, is_graduation_project=True, linkedin_url=None),
            Student(user_id=student_users[13].id, name="Florencia Paz", email="florencia.paz@correo.ucu.edu.uy", major="Ingeniería en Informática", group_id=groups[13].id, is_graduation_project=False, linkedin_url=None),
            Student(user_id=student_users[14].id, name="Agustín Benítez", email="agustin.benitez@correo.ucu.edu.uy", major="Ingeniería Biomédica", group_id=groups[14].id, is_graduation_project=True, linkedin_url="https://www.linkedin.com/in/agustin-benitez"),
            Student(user_id=student_users[15].id, name="Luciana Vega", email="luciana.vega@correo.ucu.edu.uy", major="Ingeniería Industrial", group_id=groups[7].id, is_graduation_project=False, linkedin_url=None),
        ]
        db.add_all(students)
        db.flush()

        # 7. Crear Checkpoints (15 Checkpoints)
        print("- Creando Checkpoints (15)...")
        default_questions_template = [
            {"id": 1, "text": "¿Participaste en todas las reuniones de tutoría del equipo acordadas hasta la fecha?", "answer": None},
            {"id": 2, "text": "¿Identificas algún bloqueo o dificultad técnica/de negocio en el desarrollo del proyecto?", "answer": None},
            {"id": 3, "text": "Calificación general del progreso y compromiso del grupo (1 al 5)", "answer": None},
        ]

        checkpoints = [
            Checkpoint(group_id=groups[0].id, cohort_id=cohort_active.id, title="Checkpoint trimestral - EcoRoute", due_date=date(2026, 8, 12), status="Pending", questions=default_questions_template),
            Checkpoint(group_id=groups[1].id, cohort_id=cohort_active.id, title="Checkpoint trimestral - HealthPulse", due_date=date(2026, 8, 12), status="Pending", questions=default_questions_template),
            Checkpoint(group_id=groups[2].id, cohort_id=cohort_active.id, title="Checkpoint trimestral - AgroSmart", due_date=date(2026, 8, 12), status="Pending", questions=default_questions_template),
            Checkpoint(group_id=groups[3].id, cohort_id=cohort_active.id, title="Checkpoint trimestral - EduFlow", due_date=date(2026, 8, 12), status="Pending", questions=default_questions_template),
            Checkpoint(group_id=groups[4].id, cohort_id=cohort_active.id, title="Checkpoint trimestral - FinTrack", due_date=date(2026, 8, 12), status="Pending", questions=default_questions_template),
            Checkpoint(group_id=groups[5].id, cohort_id=cohort_active.id, title="Checkpoint trimestral - SolarGrid", due_date=date(2026, 8, 12), status="Pending", questions=default_questions_template),
            Checkpoint(group_id=groups[6].id, cohort_id=cohort_active.id, title="Checkpoint trimestral - BioPack", due_date=date(2026, 8, 12), status="Pending", questions=default_questions_template),
            Checkpoint(group_id=groups[7].id, cohort_id=cohort_active.id, title="Checkpoint trimestral - UrbanMobility", due_date=date(2026, 8, 12), status="Pending", questions=default_questions_template),
            Checkpoint(group_id=groups[8].id, cohort_id=cohort_active.id, title="Checkpoint trimestral - FoodWaste", due_date=date(2026, 8, 12), status="Pending", questions=default_questions_template),
            Checkpoint(group_id=groups[9].id, cohort_id=cohort_active.id, title="Checkpoint trimestral - CyberShield", due_date=date(2026, 8, 12), status="Pending", questions=default_questions_template),
            Checkpoint(group_id=groups[10].id, cohort_id=cohort_active.id, title="Checkpoint trimestral - NutriBot", due_date=date(2026, 8, 12), status="Pending", questions=default_questions_template),
            Checkpoint(group_id=groups[11].id, cohort_id=cohort_active.id, title="Checkpoint trimestral - WaterClean", due_date=date(2026, 8, 12), status="Pending", questions=default_questions_template),
            Checkpoint(group_id=groups[12].id, cohort_id=cohort_active.id, title="Checkpoint trimestral - RecyclePay", due_date=date(2026, 8, 12), status="Pending", questions=default_questions_template),
            Checkpoint(group_id=groups[13].id, cohort_id=cohorts[2].id, title="Checkpoint trimestral - SafeDrive", due_date=date(2025, 6, 30), status="Completed", questions=[{"id": 1, "text": "¿El grupo tuvo asistencia regular?", "answer": "Si"}, {"id": 2, "text": "¿Hubo bloqueos?", "answer": "No"}, {"id": 3, "text": "Calificación", "answer": "5"}]),
            Checkpoint(group_id=groups[14].id, cohort_id=cohorts[3].id, title="Checkpoint trimestral - CargoFly", due_date=date(2025, 11, 30), status="Completed", questions=[{"id": 1, "text": "¿El grupo tuvo asistencia regular?", "answer": "Si"}, {"id": 2, "text": "¿Hubo bloqueos?", "answer": "No"}, {"id": 3, "text": "Calificación", "answer": "4"}]),
        ]
        db.add_all(checkpoints)
        db.flush()

        # 8. Crear Entregables (15 Entregables)
        print("- Creando Entregables (15)...")
        deliverables = [
            Deliverable(group_id=groups[0].id, stage_id=stage_1.id, expected_date=date(2026, 3, 30), status="Approved"),
            Deliverable(group_id=groups[0].id, stage_id=stage_2.id, expected_date=date(2026, 4, 20), status="Pending"),
            Deliverable(group_id=groups[1].id, stage_id=stage_1.id, expected_date=date(2026, 3, 30), status="Pending"),
            Deliverable(group_id=groups[2].id, stage_id=stage_3.id, expected_date=date(2026, 6, 10), status="Approved"),
            Deliverable(group_id=groups[3].id, stage_id=stage_1.id, expected_date=date(2026, 3, 30), status="Submitted"),
            Deliverable(group_id=groups[4].id, stage_id=stage_4.id, expected_date=date(2026, 6, 25), status="Pending"),
            Deliverable(group_id=groups[5].id, stage_id=stage_2.id, expected_date=date(2026, 4, 20), status="Approved"),
            Deliverable(group_id=groups[6].id, stage_id=stages[11].id, expected_date=date(2025, 11, 15), status="Approved"),
            Deliverable(group_id=groups[7].id, stage_id=stages[11].id, expected_date=date(2025, 11, 20), status="Approved"),
            Deliverable(group_id=groups[9].id, stage_id=stage_5.id, expected_date=date(2026, 7, 10), status="Pending"),
            Deliverable(group_id=groups[10].id, stage_id=stage_1.id, expected_date=date(2026, 3, 30), status="Pending"),
            Deliverable(group_id=groups[11].id, stage_id=stage_2.id, expected_date=date(2026, 4, 20), status="Submitted"),
            Deliverable(group_id=groups[12].id, stage_id=stage_3.id, expected_date=date(2026, 6, 10), status="Pending"),
            Deliverable(group_id=groups[13].id, stage_id=stages[8].id, expected_date=date(2024, 6, 15), status="Approved"),
            Deliverable(group_id=groups[14].id, stage_id=stages[9].id, expected_date=date(2024, 11, 20), status="Approved"),
        ]
        db.add_all(deliverables)
        db.flush()

        # 9. Crear Reuniones (15 Reuniones)
        print("- Creando Reuniones (15)...")
        meetings = [
            Meeting(group_id=groups[0].id, tutor_ids=[t_b1.id, t_t1.id], status=MeetingStatus.HELD, date=datetime(2026, 4, 10, 15, 0, tzinfo=timezone.utc), participants=[{"student_id": students[0].id, "attended": True}, {"student_id": students[1].id, "attended": True}], summary="Se ajustó el modelo de negocio y se definió el prototipo técnico.", notes="Propuesta de valor y ruteo.", next_steps="Ajustar BMC B2B.", hours_spent=2.5, links=[{"type": "Drive", "url": "https://drive.google.com/ecoroute-minuta-1"}]),
            Meeting(group_id=groups[1].id, tutor_ids=[t_b2.id], status=MeetingStatus.HELD, date=datetime(2026, 4, 12, 10, 0, tzinfo=timezone.utc), participants=[{"student_id": students[2].id, "attended": True}, {"student_id": students[3].id, "attended": False}], summary="Revisión de hipótesis de clientes y mapa de empatía.", notes="Hipótesis de clientes.", next_steps="Realizar 5 entrevistas.", hours_spent=1.5, links=[{"type": "Drive", "url": "https://drive.google.com/healthpulse-minuta-1"}]),
            Meeting(group_id=groups[2].id, tutor_ids=[t_t1.id], status=MeetingStatus.SCHEDULED, date=datetime(2026, 4, 15, 16, 0, tzinfo=timezone.utc), participants=[{"student_id": students[4].id, "attended": False}], summary=None, notes="Hardware e integración LoRaWAN.", next_steps="Validar batería.", hours_spent=2.0, links=[{"type": "Drive", "url": "https://drive.google.com/agrosmart-minuta-1"}]),
            Meeting(group_id=groups[3].id, tutor_ids=[t_b3.id], status=MeetingStatus.SCHEDULED, date=datetime(2026, 4, 18, 11, 0, tzinfo=timezone.utc), participants=[{"student_id": students[5].id, "attended": False}], summary=None, notes="Definición de modelo pedagógico.", next_steps="Diseñar encuestas a docentes.", hours_spent=1.0, links=[]),
            Meeting(group_id=groups[4].id, tutor_ids=[t_b1.id, t_t1.id], status=MeetingStatus.HELD, date=datetime(2026, 4, 20, 14, 0, tzinfo=timezone.utc), participants=[{"student_id": students[6].id, "attended": True}], summary="Se revisó la integración de APIs bancarias.", notes="Integración de APIs bancarias.", next_steps="Revisar seguridad Open Banking.", hours_spent=3.0, links=[]),
            Meeting(group_id=groups[5].id, tutor_ids=[t_t2.id], status=MeetingStatus.HELD, date=datetime(2026, 4, 22, 9, 0, tzinfo=timezone.utc), participants=[{"student_id": students[7].id, "attended": True}], summary="Avance en smart contracts de transferencia solar.", notes="Smart contracts de transferencia solar.", next_steps="Desplegar en Testnet.", hours_spent=2.0, links=[]),
            Meeting(group_id=groups[6].id, tutor_ids=[t_b3.id], status=MeetingStatus.HELD, date=datetime(2025, 10, 10, 15, 0, tzinfo=timezone.utc), participants=[{"student_id": students[8].id, "attended": True}], summary="Certificaciones de compostabilidad en curso.", notes="Certificaciones de compostabilidad.", next_steps="Enviar muestras a laboratorio.", hours_spent=1.5, links=[]),
            Meeting(group_id=groups[7].id, tutor_ids=[t_b1.id], status=MeetingStatus.HELD, date=datetime(2025, 10, 12, 16, 0, tzinfo=timezone.utc), participants=[], summary="Pruebas de sensores térmicos completadas.", notes="Pruebas de sensores térmicos.", next_steps="Ajustar alertas por SMS.", hours_spent=2.0, links=[]),
            Meeting(group_id=groups[8].id, tutor_ids=[t_b2.id], status=MeetingStatus.HELD, date=datetime(2023, 5, 14, 11, 0, tzinfo=timezone.utc), participants=[], summary="Cierre de proyecto con métricas finales presentadas.", notes="Cierre de proyecto y métricas finales.", next_steps="Presentación a autoridades.", hours_spent=1.0, links=[]),
            Meeting(group_id=groups[9].id, tutor_ids=[t_t2.id], status=MeetingStatus.SCHEDULED, date=datetime(2026, 4, 25, 10, 0, tzinfo=timezone.utc), participants=[{"student_id": students[9].id, "attended": False}], summary=None, notes="Escaneo de vulnerabilidades inicial.", next_steps="Priorizar parches críticos.", hours_spent=2.5, links=[]),
            Meeting(group_id=groups[10].id, tutor_ids=[t_b4.id], status=MeetingStatus.SCHEDULED, date=datetime(2026, 4, 26, 14, 0, tzinfo=timezone.utc), participants=[{"student_id": students[10].id, "attended": False}], summary=None, notes="Revision de algoritmos nutricionales.", next_steps="Validación con médicos.", hours_spent=1.5, links=[]),
            Meeting(group_id=groups[11].id, tutor_ids=[t_b5.id], status=MeetingStatus.SCHEDULED, date=datetime(2026, 4, 27, 9, 0, tzinfo=timezone.utc), participants=[{"student_id": students[11].id, "attended": False}], summary=None, notes="Pruebas de calidad de agua.", next_steps="Ajuste de filtros.", hours_spent=2.0, links=[]),
            Meeting(group_id=groups[12].id, tutor_ids=[t_b1.id], status=MeetingStatus.SCHEDULED, date=datetime(2026, 4, 28, 15, 0, tzinfo=timezone.utc), participants=[{"student_id": students[12].id, "attended": False}], summary=None, notes="Red de comercios adheridos.", next_steps="Firmar convenios.", hours_spent=1.5, links=[]),
            Meeting(group_id=groups[13].id, tutor_ids=[t_t2.id], status=MeetingStatus.CANCELLED, date=datetime(2024, 4, 10, 11, 0, tzinfo=timezone.utc), participants=[{"student_id": students[13].id, "attended": False}], summary=None, notes="Entrenamiento de modelo de visión. Reunión cancelada por el tutor.", next_steps="Reprogramar entrenamiento de modelo.", hours_spent=None, links=[]),
            Meeting(group_id=groups[14].id, tutor_ids=[t_t3.id], status=MeetingStatus.CANCELLED, date=datetime(2024, 9, 15, 16, 0, tzinfo=timezone.utc), participants=[{"student_id": students[14].id, "attended": False}], summary=None, notes="Rutas de vuelo de drones. Reunión cancelada, permisos de ANAC pendientes.", next_steps="Reagendar tras aprobación de permisos.", hours_spent=None, links=[]),
        ]
        db.add_all(meetings)

        # 10. Crear Materiales de Apoyo (15 Materiales)
        print("- Creando Materiales de Apoyo (15)...")
        materials = [
            SupportMaterial(stage_id=stage_1.id, title="Plantilla de Mapa de Empatía", url="https://drive.google.com/template-empatia"),
            SupportMaterial(stage_id=stage_2.id, title="Business Model Canvas Template", url="https://drive.google.com/template-bmc"),
            SupportMaterial(stage_id=stage_3.id, title="Guía de Pruebas de Usuario y MVP", url="https://drive.google.com/guia-mvp"),
            SupportMaterial(stage_id=stage_4.id, title="Checklist de Pruebas de Campo", url="https://drive.google.com/checklist-campo"),
            SupportMaterial(stage_id=stage_5.id, title="Framework de Estrategia Go-To-Market", url="https://drive.google.com/gtm-framework"),
            SupportMaterial(stage_id=stage_1.id, title="Guía de Entrevistas de Problema", url="https://drive.google.com/guia-entrevistas"),
            SupportMaterial(stage_id=stage_2.id, title="Calculadora de Unit Economics", url="https://drive.google.com/unit-economics"),
            SupportMaterial(stage_id=stage_3.id, title="Plantilla de Feedback de Prototipo", url="https://drive.google.com/feedback-prototipo"),
            SupportMaterial(stage_id=stage_4.id, title="Guía de Alianzas Comerciales", url="https://drive.google.com/guia-alianzas"),
            SupportMaterial(stage_id=stage_5.id, title="Pitch Deck Template 2026", url="https://drive.google.com/pitch-deck-template"),
            SupportMaterial(stage_id=stage_1.id, title="Matriz de Stakeholders", url="https://drive.google.com/matriz-stakeholders"),
            SupportMaterial(stage_id=stage_2.id, title="Guía de Análisis de Competencia", url="https://drive.google.com/analisis-competencia"),
            SupportMaterial(stage_id=stage_3.id, title="Manual de Arquitectura Cloud Básica", url="https://drive.google.com/arquitectura-cloud"),
            SupportMaterial(stage_id=stage_4.id, title="Plantilla de Métricas de Retención", url="https://drive.google.com/metricas-retencion"),
            SupportMaterial(stage_id=stage_5.id, title="Modelo de Contrato Comercial B2B", url="https://drive.google.com/contrato-b2b"),
        ]
        db.add_all(materials)
        db.flush()

        # 11. Crear Documentos Polimórficos (15 Documentos)
        print("- Creando Documentos Polimórficos (15)...")
        documents = [
            Document(entity_type=EntityType.GROUP, entity_id=groups[0].id, url="https://drive.google.com/ecoroute-repo-general", platform=DocumentPlatform.DRIVE, order=1),
            Document(entity_type=EntityType.DELIVERABLE, entity_id=deliverables[0].id, url="https://sharepoint.com/ecoroute-reporte-validacion", platform=DocumentPlatform.SHAREPOINT, order=1),
            Document(entity_type=EntityType.GROUP, entity_id=groups[1].id, url="https://drive.google.com/healthpulse-pitch", platform=DocumentPlatform.DRIVE, order=2),
            Document(entity_type=EntityType.GROUP, entity_id=groups[2].id, url="https://drive.google.com/agrosmart-datasheet", platform=DocumentPlatform.DRIVE, order=1),
            Document(entity_type=EntityType.DELIVERABLE, entity_id=deliverables[3].id, url="https://drive.google.com/agrosmart-mvp-spec", platform=DocumentPlatform.DRIVE, order=1),
            Document(entity_type=EntityType.GROUP, entity_id=groups[3].id, url="https://drive.google.com/eduflow-canvas", platform=DocumentPlatform.DRIVE, order=1),
            Document(entity_type=EntityType.GROUP, entity_id=groups[4].id, url="https://sharepoint.com/fintrack-api", platform=DocumentPlatform.SHAREPOINT, order=1),
            Document(entity_type=EntityType.GROUP, entity_id=groups[5].id, url="https://sharepoint.com/solargrid-contracts", platform=DocumentPlatform.SHAREPOINT, order=1),
            Document(entity_type=EntityType.DELIVERABLE, entity_id=deliverables[6].id, url="https://drive.google.com/solargrid-bmc", platform=DocumentPlatform.DRIVE, order=1),
            Document(entity_type=EntityType.GROUP, entity_id=groups[9].id, url="https://drive.google.com/cybershield-scanner", platform=DocumentPlatform.DRIVE, order=1),
            Document(entity_type=EntityType.GROUP, entity_id=groups[10].id, url="https://drive.google.com/nutribot-spec", platform=DocumentPlatform.DRIVE, order=1),
            Document(entity_type=EntityType.GROUP, entity_id=groups[11].id, url="https://sharepoint.com/waterclean-lab-report", platform=DocumentPlatform.SHAREPOINT, order=1),
            Document(entity_type=EntityType.DELIVERABLE, entity_id=deliverables[11].id, url="https://drive.google.com/waterclean-bmc", platform=DocumentPlatform.DRIVE, order=1),
            Document(entity_type=EntityType.GROUP, entity_id=groups[12].id, url="https://drive.google.com/recyclepay-deck", platform=DocumentPlatform.DRIVE, order=1),
            Document(entity_type=EntityType.DELIVERABLE, entity_id=deliverables[13].id, url="https://sharepoint.com/safedrive-report", platform=DocumentPlatform.SHAREPOINT, order=1),
        ]
        db.add_all(documents)

        # 12. Crear Comentarios (15 Comentarios)
        print("- Creando Comentarios (15)...")
        comments = [
            Comment(tutor_id=t_b1.id, deliverable_id=deliverables[0].id, content="Excelente trabajo en las entrevistas de validación. La muestra de 20 empresas fue muy representativa."),
            Comment(tutor_id=t_b2.id, deliverable_id=deliverables[2].id, content="Recuerden profundizar en los pain points de las instituciones de salud."),
            Comment(tutor_id=t_t1.id, deliverable_id=deliverables[3].id, content="Prototipo probado en campo con resultados prometedores de batería."),
            Comment(tutor_id=t_b3.id, deliverable_id=deliverables[4].id, content="Buen enfoque inicial. Sugiero validar la propuesta con directores de institutos."),
            Comment(tutor_id=t_b1.id, deliverable_id=deliverables[5].id, content="Definir con claridad el modelo de comisión por transacción."),
            Comment(tutor_id=t_t2.id, deliverable_id=deliverables[6].id, content="Revisar costos de gas en la red ethereum antes del deploy final."),
            Comment(tutor_id=t_b3.id, deliverable_id=deliverables[7].id, content="Documentación completa de compostabilidad aprobada."),
            Comment(tutor_id=t_b1.id, deliverable_id=deliverables[8].id, content="El cliente de prueba confirmó satisfacción con la prueba piloto."),
            Comment(tutor_id=t_t2.id, deliverable_id=deliverables[9].id, content="Sugerencias de parches de seguridad adjuntadas en el reporte."),
            Comment(tutor_id=t_b2.id, deliverable_id=deliverables[1].id, content="Pendiente de revisar la estructura de costos fijos."),
            Comment(tutor_id=t_b4.id, deliverable_id=deliverables[10].id, content="Avanzar en la revisión nutricional con el comité ético."),
            Comment(tutor_id=t_b5.id, deliverable_id=deliverables[11].id, content="Los análisis bacteriológicos de agua dieron dentro de norma."),
            Comment(tutor_id=t_b1.id, deliverable_id=deliverables[12].id, content="Buena aceptación de los comercios para la prueba inicial."),
            Comment(tutor_id=t_t2.id, deliverable_id=deliverables[13].id, content="Precisión del modelo de visión computacional superior al 95%."),
            Comment(tutor_id=t_t3.id, deliverable_id=deliverables[14].id, content="Permisos de vuelo en zona urbana otorgados condicionalmente."),
        ]
        db.add_all(comments)

        db.commit()
        print("¡Seeder ejecutado con éxito! Base de datos poblada con al menos 15 registros por tabla.")

    except Exception as e:
        db.rollback()
        print(f"Error durante la ejecución del seeder: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    seed_database(force=force_flag)
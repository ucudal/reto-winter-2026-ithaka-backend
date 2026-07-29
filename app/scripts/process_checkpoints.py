"""
Script CLI para ejecucion periodica via Kubernetes CronJob.
Analiza la cohorte activa, los grupos en curso y genera los Checkpoints trimestrales en la base de datos PostgreSQL.
"""
import sys
import logging
from datetime import date, timedelta
from sqlalchemy import select

from app.core.db.session import SessionLocal
from app.core.models.cohort import Cohort
from app.core.models.group import Group
from app.core.models.checkpoint import Checkpoint

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("checkpoints_cron")


def run_checkpoint_process():
    logger.info("Starting Checkpoints CronJob execution...")
    db = SessionLocal()

    try:
        # 1. Obtener cohorte activa
        active_cohort = db.scalar(
            select(Cohort).where(Cohort.status == "Active").order_by(Cohort.start_date.desc())
        )

        if not active_cohort:
            logger.info("No active cohort found. Skipping checkpoint processing.")
            return

        logger.info(
            f"Processing checkpoints for Cohort #{active_cohort.id} ({active_cohort.year} - {active_cohort.semester}° Semestre)"
        )

        # 2. Obtener grupos activos de la cohorte
        groups = db.scalars(
            select(Group).where(Group.cohort_id == active_cohort.id, Group.status == "Active")
        ).all()

        logger.info(f"Found {len(groups)} active group(s) in current cohort.")

        today = date.today()
        due_date = today + timedelta(days=14)
        created_count = 0

        default_questions = [
            {"id": 1, "text": "¿Participaste en todas las reuniones de tutoría del equipo acordadas hasta la fecha?", "answer": None},
            {"id": 2, "text": "¿Identificas algún bloqueo o dificultad técnica/de negocio en el desarrollo del proyecto?", "answer": None},
            {"id": 3, "text": "Calificación general del progreso y compromiso del grupo (1 al 5)", "answer": None},
        ]

        for group in groups:
            # Crear e insertar el registro de Checkpoint en PostgreSQL
            checkpoint = Checkpoint(
                group_id=group.id,
                cohort_id=active_cohort.id,
                title=f"Checkpoint Trimestral - {group.name}",
                due_date=due_date,
                status="Pending",
                questions=default_questions,
            )
            db.add(checkpoint)
            created_count += 1
            logger.info(f"Created Checkpoint for Group '{group.name}' (ID: {group.id}, Due: {due_date.isoformat()})")

        db.commit()
        logger.info(f"Checkpoints process completed successfully. Total created in DB: {created_count}")

    except Exception as err:
        db.rollback()
        logger.error(f"Error during Checkpoint CronJob execution: {err}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run_checkpoint_process()

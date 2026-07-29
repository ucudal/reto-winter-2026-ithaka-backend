from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models.tutor_group_assignment import TutorGroupAssignment
from app.core.models.student_group_membership import StudentGroupMembership


class GroupAlreadyHasActiveTutorException(Exception):
    pass


class NoActiveAssignmentException(Exception):
    pass


class NoActiveMembershipException(Exception):
    pass


def get_active_tutor_assignment(db: Session, group_id: int) -> TutorGroupAssignment | None:
    stmt = select(TutorGroupAssignment).where(
        TutorGroupAssignment.group_id == group_id,
        TutorGroupAssignment.removed_at.is_(None),
    )
    return db.execute(stmt).scalar_one_or_none()


def assign_tutor(db: Session, tutor_id: int, group_id: int) -> TutorGroupAssignment:
    existing = get_active_tutor_assignment(db, group_id)
    if existing:
        raise GroupAlreadyHasActiveTutorException(group_id)

    new_assignment = TutorGroupAssignment(tutor_id=tutor_id, group_id=group_id)
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment


def unassign_tutor(db: Session, group_id: int) -> TutorGroupAssignment:
    assignment = get_active_tutor_assignment(db, group_id)
    if not assignment:
        raise NoActiveAssignmentException(group_id)

    assignment.removed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(assignment)
    return assignment


def get_group_tutor_history(db: Session, group_id: int) -> list[TutorGroupAssignment]:
    stmt = (
        select(TutorGroupAssignment)
        .where(TutorGroupAssignment.group_id == group_id)
        .order_by(TutorGroupAssignment.assigned_at)
    )
    return list(db.execute(stmt).scalars().all())


def get_active_student_memberships(db: Session, group_id: int) -> list[StudentGroupMembership]:
    stmt = select(StudentGroupMembership).where(
        StudentGroupMembership.group_id == group_id,
        StudentGroupMembership.left_at.is_(None),
    )
    return list(db.execute(stmt).scalars().all())


def add_student_to_group(db: Session, student_id: int, group_id: int) -> StudentGroupMembership:
    # Check if student is already in this group
    existing = select(StudentGroupMembership).where(
        StudentGroupMembership.student_id == student_id,
        StudentGroupMembership.group_id == group_id,
        StudentGroupMembership.left_at.is_(None),
    )
    existing_membership = db.execute(existing).scalar_one_or_none()
    
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student {student_id} is already a member of group {group_id}"
        )

    new_membership = StudentGroupMembership(student_id=student_id, group_id=group_id)
    db.add(new_membership)
    db.commit()
    db.refresh(new_membership)
    return new_membership


def remove_student_from_group(db: Session, student_id: int, group_id: int) -> StudentGroupMembership:
    stmt = select(StudentGroupMembership).where(
        StudentGroupMembership.student_id == student_id,
        StudentGroupMembership.group_id == group_id,
        StudentGroupMembership.left_at.is_(None),
    )
    membership = db.execute(stmt).scalar_one_or_none()
    
    if not membership:
        raise NoActiveMembershipException(f"No active membership found for student {student_id} in group {group_id}")

    membership.left_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(membership)
    return membership


def get_group_student_history(db: Session, group_id: int) -> list[StudentGroupMembership]:
    stmt = (
        select(StudentGroupMembership)
        .where(StudentGroupMembership.group_id == group_id)
        .order_by(StudentGroupMembership.joined_at)
    )
    return list(db.execute(stmt).scalars().all())


def get_student_group_history(db: Session, student_id: int) -> list[StudentGroupMembership]:
    stmt = (
        select(StudentGroupMembership)
        .where(StudentGroupMembership.student_id == student_id)
        .order_by(StudentGroupMembership.joined_at)
    )
    return list(db.execute(stmt).scalars().all())

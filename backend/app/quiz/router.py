from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .schemas import CreateQuiz, UpdateQuiz
from .. import db as database
from ..auth import get_current_user

router = APIRouter()




# ==================== GET ====================

@router.get("/from-user")
async def get_quizzes_by_user(
        user: database.User = Depends(get_current_user),
        db: Session = Depends(database.get_db)):
    quizzes: list[database.Quiz] = database.get_quizzes_by_user(db, user_id=user.id)
    return quizzes


@router.get("/{quiz_id}")
async def get_quiz_by_id(quiz_id: int, db: Session = Depends(database.get_db)):
    quiz = database.get_quiz_by_id(db, quiz_id=quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return quiz

# ==================== POST ====================

@router.post("/create")
async def create_quiz(quiz_info: CreateQuiz, db: Session = Depends(database.get_db)):
    quiz = database.create_quiz(db, title=quiz_info.title, description=quiz_info.description, creator_id=quiz_info.creator_id)
    return quiz


# ==================== PUT ====================
@router.put("/{quiz_id}")
async def update_quiz(
        quiz_id: int,
        quiz_info: UpdateQuiz,
        user: database.User = Depends(get_current_user),
        db: Session = Depends(database.get_db)):
    quiz = database.get_quiz_by_id(db, quiz_id=quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if quiz.creator_id != user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    quiz = database.update_quiz(db, quiz_id=quiz_id, title=quiz_info.title, description=quiz_info.description, is_published=quiz_info.is_published)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return quiz




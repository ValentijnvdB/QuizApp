from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, select
from typing import Optional
from datetime import datetime, UTC
import random
import string

from app.db.models import (
    User, Quiz, Question, Session as SessionModel,
    Participant, Answer, SessionStatus, QuestionType, RefreshToken
)


# ==================== USER CRUD ====================

def create_user(db: Session, username: str, email: str, hashed_password: str) -> User:
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created user with id {user.id}")
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    stmt = select(User).where(User.id == user_id)
    return db.scalars(stmt).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    return db.scalars(stmt).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    return db.scalars(stmt).first()

# ==================== TOKEN CRUD ====================

def add_refresh_token(db: Session, user_id: int, token: str, expires_at: datetime) -> Optional[RefreshToken]:
    token = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(token)
    db.commit()
    db.refresh(token)
    return token

def get_refresh_token_by_token(db: Session, token: str) -> Optional[RefreshToken]:
    stmt = select(RefreshToken).where(RefreshToken.token == token)
    return db.scalars(stmt).first()

def revoke_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    rt = get_refresh_token_by_token(db, token)
    if not rt:
        return None

    rt.revoked = True
    db.commit()
    db.refresh(rt)
    return rt


# ==================== QUIZ CRUD ====================

def create_quiz(db: Session, title: str, description: str, creator_id: int) -> Quiz:
    quiz = Quiz(title=title, description=description, creator_id=creator_id)
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


def get_quiz_by_id(db: Session, quiz_id: int) -> Optional[Quiz]:
    stmt = select(Quiz).where(Quiz.id == quiz_id)
    return db.scalars(stmt).first()


def get_quizzes_by_user(db: Session, user_id: int) -> list[Quiz]:
    stmt = select(Quiz).where(Quiz.creator_id == user_id).order_by(desc(Quiz.created_at))
    return db.scalars(stmt).all()


def update_quiz(db: Session, quiz_id: int, title: str = None, description: str = None, is_published: bool = None) -> Optional[Quiz]:
    quiz = get_quiz_by_id(db, quiz_id)
    if not quiz:
        return None

    if title is not None:
        quiz.title = title
    if description is not None:
        quiz.description = description
    if is_published is not None:
        quiz.is_published = is_published

    db.commit()
    db.refresh(quiz)
    return quiz


def delete_quiz(db: Session, quiz_id: int) -> bool:
    stmt = select(Quiz).where(Quiz.id == quiz_id)
    quiz = db.scalars(stmt).first()
    if not quiz:
        return False

    db.delete(quiz)
    db.commit()
    return True


# ==================== QUESTION CRUD ====================

def create_question(
    db: Session,
    quiz_id: int,
    content: str,
    question_type: QuestionType,
    order: int,
    options: str = None,
    correct_answer: str = None,
    media_url: str = None,
    media_type: str = None,
    points: int = 10,
    time_limit: int = 30
) -> Question:
    question = Question(
        quiz_id=quiz_id,
        order=order,
        type=question_type,
        content=content,
        options=options,
        correct_answer=correct_answer,
        media_url=media_url,
        media_type=media_type,
        points=points,
        time_limit=time_limit
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def get_question_by_id(db: Session, question_id: int) -> Optional[Question]:
    stmt = select(Question).where(Question.id == question_id)
    return db.scalars(stmt).first()


def get_questions_by_quiz(db: Session, quiz_id: int) -> list[Question]:
    stmt = select(Question).where(Question.quiz_id == quiz_id).order_by(Question.order)
    return db.scalars(stmt).all()


def update_question(db: Session, question_id: int, **kwargs) -> Optional[Question]:
    question = get_question_by_id(db, question_id)
    if not question:
        return None

    for key, value in kwargs.items():
        if value is not None and hasattr(question, key):
            setattr(question, key, value)

    db.commit()
    db.refresh(question)
    return question


def delete_question(db: Session, question_id: int) -> bool:
    stmt = select(Question).where(Question.id == question_id)
    question = db.scalars(stmt).first()
    if not question:
        return False

    db.delete(question)
    db.commit()
    return True


# ==================== SESSION CRUD ====================

def generate_session_code() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))


def create_session(db: Session, quiz_id: int, host_id: int) -> SessionModel:
    code = generate_session_code()
    while db.scalars(select(SessionModel).where(SessionModel.code == code)).first():
        code = generate_session_code()

    session = SessionModel(
        quiz_id=quiz_id,
        host_id=host_id,
        code=code,
        status=SessionStatus.WAITING
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_by_code(db: Session, code: str) -> Optional[SessionModel]:
    stmt = select(SessionModel).where(SessionModel.code == code)
    return db.scalars(stmt).first()


def get_session_by_id(db: Session, session_id: int) -> Optional[SessionModel]:
    stmt = select(SessionModel).where(SessionModel.id == session_id)
    return db.scalars(stmt).first()


def start_session(db: Session, session_id: int) -> Optional[SessionModel]:
    stmt = select(SessionModel).where(SessionModel.id == session_id)
    session = db.scalars(stmt).first()
    if not session:
        return None

    session.status = SessionStatus.ACTIVE
    session.started_at = datetime.now(UTC)
    db.commit()
    db.refresh(session)
    return session


def end_session(db: Session, session_id: int) -> Optional[SessionModel]:
    stmt = select(SessionModel).where(SessionModel.id == session_id)
    session = db.scalars(stmt).first()
    if not session:
        return None

    session.status = SessionStatus.ENDED
    session.ended_at = datetime.now(UTC)
    db.commit()
    db.refresh(session)
    return session


def update_session_question(db: Session, session_id: int, question_index: int) -> Optional[SessionModel]:
    session = get_session_by_id(db, session_id)
    if not session:
        return None

    session.current_question_index = question_index
    db.commit()
    db.refresh(session)
    return session


# ==================== PARTICIPANT CRUD ====================

def create_participant(db: Session, session_id: int, name: str) -> Participant:
    participant = Participant(session_id=session_id, name=name)
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


def get_participant_by_id(db: Session, participant_id: int) -> Optional[Participant]:
    stmt = select(Participant).where(Participant.id == participant_id)
    return db.scalars(stmt).first()


def get_participants_by_session(db: Session, session_id: int) -> list[Participant]:
    stmt = select(Participant).where(Participant.session_id == session_id).order_by(Participant.joined_at)
    return db.scalars(stmt).all()


def update_participant_score(db: Session, participant_id: int, points_to_add: int) -> Optional[Participant]:
    participant = get_participant_by_id(db, participant_id)
    if not participant:
        return None

    participant.total_score += points_to_add
    db.commit()
    db.refresh(participant)
    return participant


def get_session_leaderboard(db: Session, session_id: int) -> list[Participant]:
    stmt = select(Participant).where(Participant.session_id == session_id).order_by(desc(Participant.total_score))
    return db.scalars(stmt).all()


# ==================== ANSWER CRUD ====================

def submit_answer(
    db: Session,
    session_id: int,
    participant_id: int,
    question_id: int,
    answer_text: str,
    time_taken: float = None
) -> Answer:
    question_stmt = select(Question).where(Question.id == question_id)
    question = db.scalars(question_stmt).first()

    is_correct = False
    score = 0

    if question and question.correct_answer:
        is_correct = answer_text.strip().lower() == question.correct_answer.strip().lower()
        if is_correct:
            score = question.points
            update_participant_score(db, participant_id, score)

    answer = Answer(
        session_id=session_id,
        participant_id=participant_id,
        question_id=question_id,
        answer_text=answer_text,
        is_correct=is_correct,
        score=score,
        time_taken=time_taken
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


def get_answer(db: Session, session_id: int, participant_id: int, question_id: int) -> Optional[Answer]:
    stmt = select(Answer).where(
        and_(
            Answer.session_id == session_id,
            Answer.participant_id == participant_id,
            Answer.question_id == question_id
        )
    )
    return db.scalars(stmt).first()


def get_answers_for_question(db: Session, session_id: int, question_id: int) -> list[Answer]:
    stmt = select(Answer).where(
        and_(Answer.session_id == session_id, Answer.question_id == question_id)
    )
    return db.scalars(stmt).all()


def score_answer(db: Session, answer_id: int, score: int) -> Optional[Answer]:
    stmt = select(Answer).where(Answer.id == answer_id)
    answer = db.scalars(stmt).first()
    if not answer:
        return None

    old_score = answer.score or 0
    score_diff = score - old_score

    answer.score = score
    answer.is_correct = score > 0

    update_participant_score(db, answer.participant_id, score_diff)

    db.commit()
    db.refresh(answer)
    return answer

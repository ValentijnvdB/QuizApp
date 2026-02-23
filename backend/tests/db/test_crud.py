import os
from typing import Any, Generator

import pytest

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from dotenv import load_dotenv

# load environment
load_dotenv('./test.env')

# ---------------------------------------------------------------------------
# Import application code – adjust the import paths as needed
# ---------------------------------------------------------------------------
from app.db.models import (
    Base,
    User,
    Quiz,
    Question,
    Session as SessionModel,
    Participant,
    Answer,
    SessionStatus,
    QuestionType,
)
import app.db.crud as crud

# ---------------------------------------------------------------------------
# Database URL
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

# ---------------------------------------------------------------------------
# Engine / session factory (module-scoped so we pay connection cost once)
# ---------------------------------------------------------------------------
engine = create_engine(DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(bind=engine)


# ---------------------------------------------------------------------------
# Ensure tables exist before the test suite runs
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    # Uncomment to drop tables after the full suite:
    # Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------------------------
# Core fixture: one DB session per test, wrapped in a rolled-back transaction
# ---------------------------------------------------------------------------
@pytest.fixture()
def db() -> Generator[Session, Any, None]:
    """
    Yields a SQLAlchemy Session whose changes are rolled back after each test.

    Uses a nested transaction (SAVEPOINT) so that code under test can call
    db.commit() without actually committing to the database.
    """
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ===========================================================================
# Factory helpers
# Update these as model fields or signatures change.
# ===========================================================================

def make_user(db, username="alice", email="alice@example.com", password="hashed") -> User:
    return crud.create_user(db, username=username, email=email, hashed_password=password)


def make_quiz(db, creator_id: int, title="My Quiz", description="desc") -> Quiz:
    return crud.create_quiz(db, title=title, description=description, creator_id=creator_id)


def make_question(
    db,
    quiz_id: int,
    content="What is 2+2?",
    question_type=QuestionType.MULTIPLE_CHOICE,
    order=1,
    options='["2","3","4","5"]',
    correct_answer="4",
    points=10,
    time_limit=30,
) -> Question:
    return crud.create_question(
        db,
        quiz_id=quiz_id,
        content=content,
        question_type=question_type,
        order=order,
        options=options,
        correct_answer=correct_answer,
        points=points,
        time_limit=time_limit,
    )


def make_session(db, quiz_id: int, host_id: int) -> SessionModel:
    return crud.create_session(db, quiz_id=quiz_id, host_id=host_id)


def make_participant(db, session_id: int, name="Bob") -> Participant:
    return crud.create_participant(db, session_id=session_id, name=name)


# ===========================================================================
# USER tests
# ===========================================================================

class TestUserCrud:
    def test_create_user_returns_user_with_id(self, db):
        user = make_user(db)
        assert user.id is not None
        assert user.username == "alice"
        assert user.email == "alice@example.com"

    def test_get_user_by_id(self, db):
        user = make_user(db)
        fetched = crud.get_user_by_id(db, user.id)
        assert fetched is not None
        assert fetched.id == user.id

    def test_get_user_by_id_not_found(self, db):
        assert crud.get_user_by_id(db, 999_999) is None

    def test_get_user_by_username(self, db):
        user = make_user(db)
        fetched = crud.get_user_by_username(db, "alice")
        assert fetched is not None
        assert fetched.id == user.id

    def test_get_user_by_username_not_found(self, db):
        assert crud.get_user_by_username(db, "ghost") is None

    def test_get_user_by_email(self, db):
        user = make_user(db)
        fetched = crud.get_user_by_email(db, "alice@example.com")
        assert fetched is not None
        assert fetched.id == user.id

    def test_get_user_by_email_not_found(self, db):
        assert crud.get_user_by_email(db, "nobody@example.com") is None


# ===========================================================================
# QUIZ tests
# ===========================================================================

class TestQuizCrud:
    def test_create_quiz(self, db):
        user = make_user(db)
        quiz = make_quiz(db, creator_id=user.id)
        assert quiz.id is not None
        assert quiz.creator_id == user.id

    def test_get_quiz_by_id(self, db):
        user = make_user(db)
        quiz = make_quiz(db, creator_id=user.id)
        fetched = crud.get_quiz_by_id(db, quiz.id)
        assert fetched is not None
        assert fetched.id == quiz.id

    def test_get_quiz_by_id_not_found(self, db):
        assert crud.get_quiz_by_id(db, 999_999) is None

    def test_get_quizzes_by_user_returns_all(self, db):
        user = make_user(db)
        make_quiz(db, creator_id=user.id, title="Q1")
        make_quiz(db, creator_id=user.id, title="Q2")
        quizzes = crud.get_quizzes_by_user(db, user.id)
        assert len(quizzes) == 2

    def test_get_quizzes_by_user_empty(self, db):
        user = make_user(db)
        assert crud.get_quizzes_by_user(db, user.id) == []

    def test_update_quiz_title(self, db):
        user = make_user(db)
        quiz = make_quiz(db, creator_id=user.id)
        updated = crud.update_quiz(db, quiz.id, title="New Title")
        assert updated.title == "New Title"

    def test_update_quiz_publish(self, db):
        user = make_user(db)
        quiz = make_quiz(db, creator_id=user.id)
        updated = crud.update_quiz(db, quiz.id, is_published=True)
        assert updated.is_published is True

    def test_update_quiz_not_found(self, db):
        assert crud.update_quiz(db, 999_999, title="X") is None

    def test_delete_quiz(self, db):
        user = make_user(db)
        quiz = make_quiz(db, creator_id=user.id)
        result = crud.delete_quiz(db, quiz.id)
        assert result is True
        assert crud.get_quiz_by_id(db, quiz.id) is None

    def test_delete_quiz_not_found(self, db):
        assert crud.delete_quiz(db, 999_999) is False


# ===========================================================================
# QUESTION tests
# ===========================================================================

class TestQuestionCrud:
    def test_create_question(self, db):
        user = make_user(db)
        quiz = make_quiz(db, creator_id=user.id)
        question = make_question(db, quiz_id=quiz.id)
        assert question.id is not None
        assert question.quiz_id == quiz.id
        assert question.points == 10

    def test_get_question_by_id(self, db):
        user = make_user(db)
        quiz = make_quiz(db, creator_id=user.id)
        question = make_question(db, quiz_id=quiz.id)
        fetched = crud.get_question_by_id(db, question.id)
        assert fetched is not None
        assert fetched.id == question.id

    def test_get_question_by_id_not_found(self, db):
        assert crud.get_question_by_id(db, 999_999) is None

    def test_get_questions_by_quiz_ordered(self, db):
        user = make_user(db)
        quiz = make_quiz(db, creator_id=user.id)
        make_question(db, quiz_id=quiz.id, content="Q1", order=2)
        make_question(db, quiz_id=quiz.id, content="Q2", order=1)
        questions = crud.get_questions_by_quiz(db, quiz.id)
        assert len(questions) == 2
        assert questions[0].order == 1  # sorted ascending by order

    def test_update_question(self, db):
        user = make_user(db)
        quiz = make_quiz(db, creator_id=user.id)
        question = make_question(db, quiz_id=quiz.id)
        updated = crud.update_question(db, question.id, content="Updated?", points=20)
        assert updated.content == "Updated?"
        assert updated.points == 20

    def test_update_question_not_found(self, db):
        assert crud.update_question(db, 999_999, content="X") is None

    def test_delete_question(self, db):
        user = make_user(db)
        quiz = make_quiz(db, creator_id=user.id)
        question = make_question(db, quiz_id=quiz.id)
        assert crud.delete_question(db, question.id) is True
        assert crud.get_question_by_id(db, question.id) is None

    def test_delete_question_not_found(self, db):
        assert crud.delete_question(db, 999_999) is False


# ===========================================================================
# SESSION tests
# ===========================================================================

class TestSessionCrud:
    def _setup(self, db):
        user = make_user(db)
        quiz = make_quiz(db, creator_id=user.id)
        return quiz, user

    def test_create_session_has_code_and_waiting_status(self, db):
        quiz, user = self._setup(db)
        session = make_session(db, quiz_id=quiz.id, host_id=user.id)
        assert session.id is not None
        assert session.code is not None
        assert len(session.code) == 5
        assert session.status == SessionStatus.WAITING

    def test_get_session_by_code(self, db):
        quiz, user = self._setup(db)
        session = make_session(db, quiz_id=quiz.id, host_id=user.id)
        fetched = crud.get_session_by_code(db, session.code)
        assert fetched is not None
        assert fetched.id == session.id

    def test_get_session_by_code_not_found(self, db):
        assert crud.get_session_by_code(db, "XXXXX") is None

    def test_get_session_by_id(self, db):
        quiz, user = self._setup(db)
        session = make_session(db, quiz_id=quiz.id, host_id=user.id)
        assert crud.get_session_by_id(db, session.id) is not None

    def test_get_session_by_id_not_found(self, db):
        assert crud.get_session_by_id(db, 999_999) is None

    def test_start_session(self, db):
        quiz, user = self._setup(db)
        session = make_session(db, quiz_id=quiz.id, host_id=user.id)
        started = crud.start_session(db, session.id)
        assert started.status == SessionStatus.ACTIVE
        assert started.started_at is not None

    def test_start_session_not_found(self, db):
        assert crud.start_session(db, 999_999) is None

    def test_end_session(self, db):
        quiz, user = self._setup(db)
        session = make_session(db, quiz_id=quiz.id, host_id=user.id)
        ended = crud.end_session(db, session.id)
        assert ended.status == SessionStatus.ENDED
        assert ended.ended_at is not None

    def test_end_session_not_found(self, db):
        assert crud.end_session(db, 999_999) is None

    def test_update_session_question(self, db):
        quiz, user = self._setup(db)
        session = make_session(db, quiz_id=quiz.id, host_id=user.id)
        updated = crud.update_session_question(db, session.id, question_index=3)
        assert updated.current_question_index == 3

    def test_update_session_question_not_found(self, db):
        assert crud.update_session_question(db, 999_999, question_index=0) is None


# ===========================================================================
# PARTICIPANT tests
# ===========================================================================

class TestParticipantCrud:
    def _setup(self, db):
        user = make_user(db)
        quiz = make_quiz(db, creator_id=user.id)
        session = make_session(db, quiz_id=quiz.id, host_id=user.id)
        return session

    def test_create_participant(self, db):
        session = self._setup(db)
        participant = make_participant(db, session_id=session.id)
        assert participant.id is not None
        assert participant.name == "Bob"
        assert participant.total_score == 0

    def test_get_participant_by_id(self, db):
        session = self._setup(db)
        participant = make_participant(db, session_id=session.id)
        fetched = crud.get_participant_by_id(db, participant.id)
        assert fetched is not None
        assert fetched.id == participant.id

    def test_get_participant_by_id_not_found(self, db):
        assert crud.get_participant_by_id(db, 999_999) is None

    def test_get_participants_by_session(self, db):
        session = self._setup(db)
        make_participant(db, session_id=session.id, name="Bob")
        make_participant(db, session_id=session.id, name="Carol")
        participants = crud.get_participants_by_session(db, session.id)
        assert len(participants) == 2

    def test_update_participant_score(self, db):
        session = self._setup(db)
        participant = make_participant(db, session_id=session.id)
        updated = crud.update_participant_score(db, participant.id, points_to_add=50)
        assert updated.total_score == 50
        updated = crud.update_participant_score(db, participant.id, points_to_add=25)
        assert updated.total_score == 75

    def test_update_participant_score_not_found(self, db):
        assert crud.update_participant_score(db, 999_999, points_to_add=10) is None

    def test_get_session_leaderboard_ordered(self, db):
        session = self._setup(db)
        p1 = make_participant(db, session_id=session.id, name="Low")
        p2 = make_participant(db, session_id=session.id, name="High")
        crud.update_participant_score(db, p1.id, points_to_add=10)
        crud.update_participant_score(db, p2.id, points_to_add=100)
        leaderboard = crud.get_session_leaderboard(db, session.id)
        assert leaderboard[0].id == p2.id  # highest score first


# ===========================================================================
# ANSWER tests
# ===========================================================================

class TestAnswerCrud:
    def _setup(self, db):
        user = make_user(db)
        quiz = make_quiz(db, creator_id=user.id)
        question = make_question(db, quiz_id=quiz.id, correct_answer="4", points=10)
        session = make_session(db, quiz_id=quiz.id, host_id=user.id)
        participant = make_participant(db, session_id=session.id)
        return session, participant, question

    def test_submit_correct_answer(self, db):
        session, participant, question = self._setup(db)
        answer = crud.submit_answer(
            db,
            session_id=session.id,
            participant_id=participant.id,
            question_id=question.id,
            answer_text="4",
        )
        assert answer.is_correct is True
        assert answer.score == 10
        updated = crud.get_participant_by_id(db, participant.id)
        assert updated.total_score == 10

    def test_submit_wrong_answer(self, db):
        session, participant, question = self._setup(db)
        answer = crud.submit_answer(
            db,
            session_id=session.id,
            participant_id=participant.id,
            question_id=question.id,
            answer_text="99",
        )
        assert answer.is_correct is False
        assert answer.score == 0
        updated = crud.get_participant_by_id(db, participant.id)
        assert updated.total_score == 0

    def test_submit_answer_case_insensitive(self, db):
        user = make_user(db)
        quiz = make_quiz(db, creator_id=user.id)
        question = make_question(
            db, quiz_id=quiz.id, correct_answer="Yes", points=5,
            question_type=QuestionType.MULTIPLE_CHOICE,
        )
        session = make_session(db, quiz_id=quiz.id, host_id=user.id)
        participant = make_participant(db, session_id=session.id)
        answer = crud.submit_answer(
            db,
            session_id=session.id,
            participant_id=participant.id,
            question_id=question.id,
            answer_text="YES",
        )
        assert answer.is_correct is True

    def test_submit_answer_with_time_taken(self, db):
        session, participant, question = self._setup(db)
        answer = crud.submit_answer(
            db,
            session_id=session.id,
            participant_id=participant.id,
            question_id=question.id,
            answer_text="4",
            time_taken=3.5,
        )
        assert answer.time_taken == pytest.approx(3.5)

    def test_get_answer(self, db):
        session, participant, question = self._setup(db)
        crud.submit_answer(
            db,
            session_id=session.id,
            participant_id=participant.id,
            question_id=question.id,
            answer_text="4",
        )
        fetched = crud.get_answer(db, session.id, participant.id, question.id)
        assert fetched is not None
        assert fetched.answer_text == "4"

    def test_get_answer_not_found(self, db):
        assert crud.get_answer(db, 999_999, 999_999, 999_999) is None

    def test_get_answers_for_question(self, db):
        session, p1, question = self._setup(db)
        p2 = make_participant(db, session_id=session.id, name="Carol")
        crud.submit_answer(db, session.id, p1.id, question.id, "4")
        crud.submit_answer(db, session.id, p2.id, question.id, "3")
        answers = crud.get_answers_for_question(db, session.id, question.id)
        assert len(answers) == 2

    def test_score_answer_updates_participant(self, db):
        session, participant, question = self._setup(db)
        answer = crud.submit_answer(
            db,
            session_id=session.id,
            participant_id=participant.id,
            question_id=question.id,
            answer_text="open ended response",
        )
        assert answer.score == 0

        scored = crud.score_answer(db, answer.id, score=7)
        assert scored.score == 7
        assert scored.is_correct is True

        updated = crud.get_participant_by_id(db, participant.id)
        assert updated.total_score == 7

    def test_score_answer_adjusts_score_diff(self, db):
        """Re-scoring an answer only adds the *difference* to the participant."""
        session, participant, question = self._setup(db)
        answer = crud.submit_answer(db, session.id, participant.id, question.id, "4")
        assert answer.score == 10  # correct, auto-scored

        crud.score_answer(db, answer.id, score=5)
        updated = crud.get_participant_by_id(db, participant.id)
        assert updated.total_score == 5  # 10 + (5 - 10) = 5

    def test_score_answer_not_found(self, db):
        assert crud.score_answer(db, 999_999, score=10) is None

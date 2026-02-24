from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

# TODO: Add composite indices if needed using '__table_args__ = ()'

class QuestionType(str, enum.Enum):
    """Enum for question types"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    OPEN_ENDED = "open_ended"
    SHORT_ANSWER = "short_answer"
    ESTIMATION = "estimation"


class MediaType(str, enum.Enum):
    """Enum for media types"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"


class SessionStatus(str, enum.Enum):
    """Enum for session status"""
    WAITING = "waiting"  # Waiting for participants
    ACTIVE = "active"    # Quiz in progress
    ENDED = "ended"      # Quiz completed


class User(Base):
    """User model - Quiz creators only"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    quizzes = relationship("Quiz", back_populates="creator", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="host", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True))
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Quiz(Base):
    """Quiz model - Collection of questions"""
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan", order_by="Question.order")
    sessions = relationship("Session", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    """Question model - Individual quiz questions"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    order = Column(Integer, nullable=False)  # Question order in quiz
    type = Column(Enum(QuestionType), nullable=False)
    content = Column(Text, nullable=False)  # Question text
    
    # Media fields
    media_url = Column(String(500))  # URL to media file or YouTube link
    media_type = Column(Enum(MediaType))
    
    # Answer configuration (stored as JSON string or separate columns)
    options = Column(Text)  # JSON string for multiple choice options: ["A", "B", "C", "D"]
    correct_answer = Column(Text)  # Correct answer for auto-grading
    
    points = Column(Integer, default=10)  # Points for correct answer
    time_limit = Column(Integer, default=30)  # Time limit in seconds
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")


class Session(Base):
    """Session model - Active quiz session"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    host_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(5), unique=True, nullable=False, index=True)  # Session join code
    status = Column(Enum(SessionStatus), default=SessionStatus.WAITING, nullable=False)
    current_question_index = Column(Integer, default=0)  # Track which question is active
    
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    quiz = relationship("Quiz", back_populates="sessions")
    host = relationship("User", back_populates="sessions")
    participants = relationship("Participant", back_populates="session", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="session", cascade="all, delete-orphan")


class Participant(Base):
    """Participant model - Players in a session"""
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    total_score = Column(Integer, default=0)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("Session", back_populates="participants")
    answers = relationship("Answer", back_populates="participant", cascade="all, delete-orphan")


class Answer(Base):
    """Answer model - Participant answers to questions"""
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    answer_text = Column(Text)  # The actual answer submitted
    is_correct = Column(Boolean)  # For auto-graded questions
    score = Column(Integer, default=0)  # Points awarded
    time_taken = Column(Float)  # Seconds taken to answer
    
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("Session", back_populates="answers")
    participant = relationship("Participant", back_populates="answers")
    question = relationship("Question", back_populates="answers")


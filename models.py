from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# Association tables
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

user_courses = db.Table('user_courses',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
    db.Column('enrolled_date', db.DateTime, default=datetime.utcnow)
)

user_achievements = db.Table('user_achievements',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('achievement_id', db.Integer, db.ForeignKey('achievement.id')),
    db.Column('earned_date', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    profile_image_url = db.Column(db.String(256))
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    # Relationships
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    courses = db.relationship('Course', secondary=user_courses, backref=db.backref('students', lazy='dynamic'))
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy='dynamic')
    forum_posts = db.relationship('ForumPost', backref='author', lazy='dynamic')
    forum_replies = db.relationship('ForumReply', backref='author', lazy='dynamic')
    payments = db.relationship('Payment', backref='user', lazy='dynamic')
    achievements = db.relationship('Achievement', secondary=user_achievements, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_xp(self, amount):
        self.xp += amount
        # Check if user should level up (150 XP per level)
        xp_needed = self.level * 150
        if self.xp >= xp_needed:
            self.level += 1
        return self.level

    def get_rank_name(self):
        ranks = {
            1: "Recruta",
            2: "Marinheiro",
            3: "Cabo",
            4: "3º Sargento",
            5: "2º Sargento",
            6: "1º Sargento",
            7: "Suboficial",
            8: "2º Tenente",
            9: "Capitão",
            10: "Almirante"
        }
        return ranks.get(self.level, "Almirante")

    def get_rank_image(self):
        return f"/static/images/ranks/rank{min(self.level, 10)}.svg"

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def is_admin(self):
        return self.has_role('admin')

    def is_teacher(self):
        return self.has_role('teacher')

    def is_student(self):
        return self.has_role('student')

    def __repr__(self):
        return f'<User {self.username}>'

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Role {self.name}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    thumbnail_url = db.Column(db.String(255))
    price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationships
    author = db.relationship('User', backref=db.backref('created_courses', lazy='dynamic'))
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='course', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Course {self.title}>'

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    video_url = db.Column(db.String(255))
    pdf_path = db.Column(db.String(255))
    order = db.Column(db.Integer, default=0)
    xp_reward = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def __repr__(self):
        return f'<Lesson {self.title}>'

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    time_limit = db.Column(db.Integer)  # in minutes
    passing_score = db.Column(db.Integer, default=70)  # percentage
    xp_reward = db.Column(db.Integer, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy='dynamic')

    def __repr__(self):
        return f'<Quiz {self.title}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))

    # Relationships
    answers = db.relationship('Answer', backref='question', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Question {self.id}>'

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

    def __repr__(self):
        return f'<Answer {self.id}>'

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))

    # Store user answers as JSON string
    user_answers = db.Column(db.Text)  # JSON string of {question_id: answer_id}

    def __repr__(self):
        return f'<QuizAttempt {self.id}>'

    def calculate_score(self):
        """Calculate score as percentage"""
        if not self.user_answers:
            return 0

        import json
        answers = json.loads(self.user_answers)
        total_points = 0
        earned_points = 0

        for question in self.quiz.questions:
            total_points += question.points
            question_id = str(question.id)

            if question_id in answers:
                selected_answer_id = answers[question_id]
                correct_answer = Answer.query.filter_by(
                    question_id=question.id, 
                    is_correct=True
                ).first()

                if correct_answer and str(correct_answer.id) == selected_answer_id:
                    earned_points += question.points

        if total_points == 0:
            return 0

        return (earned_points / total_points) * 100

class ForumCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # Relationships
    forums = db.relationship('Forum', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<ForumCategory {self.name}>'

class Forum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('forum_category.id'))

    # Relationships
    topics = db.relationship('ForumPost', backref='forum', lazy='dynamic')

    def __repr__(self):
        return f'<Forum {self.name}>'

class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_pinned = db.Column(db.Boolean, default=False)
    is_closed = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    forum_id = db.Column(db.Integer, db.ForeignKey('forum.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationships
    replies = db.relationship('ForumReply', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ForumPost {self.title}>'

class ForumReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_official = db.Column(db.Boolean, default=False)  # For teacher/admin answers
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<ForumReply {self.id}>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='BRL')
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    payment_method = db.Column(db.String(20), default='pix')
    transaction_id = db.Column(db.String(255))
    payment_data = db.Column(db.Text)  # JSON string with payment details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    # Relationship
    course = db.relationship('Course')

    def __repr__(self):
        return f'<Payment {self.id}>'

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    badge_image = db.Column(db.String(255))
    xp_reward = db.Column(db.Integer, default=100)

    def __repr__(self):
        return f'<Achievement {self.name}>'

class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'))
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User')
    achievement = db.relationship('Achievement')

    def __repr__(self):
        return f'<UserAchievement {self.id}>'
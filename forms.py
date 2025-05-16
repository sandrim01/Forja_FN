from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, FloatField, IntegerField, HiddenField, RadioField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from models import User

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class RegistrationForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('Nome', validators=[DataRequired()])
    last_name = StringField('Sobrenome', validators=[DataRequired()])
    submit = SubmitField('Registrar')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está em uso. Por favor, escolha outro.')

class ResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar Instruções')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Redefinir Senha')

class CourseForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[DataRequired()])
    thumbnail_url = StringField('URL da Imagem', validators=[Optional()])
    price = FloatField('Preço (R$)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Salvar Curso')

class LessonForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    content = TextAreaField('Conteúdo', validators=[DataRequired()])
    video_url = StringField('URL do Vídeo (YouTube)', validators=[Optional()])
    pdf_file = FileField('Arquivo PDF', validators=[FileAllowed(['pdf'])])
    order = IntegerField('Ordem de Exibição', validators=[DataRequired()])
    xp_reward = IntegerField('Recompensa XP', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Salvar Aula')

class QuizForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[DataRequired()])
    time_limit = IntegerField('Tempo Limite (minutos)', validators=[DataRequired(), NumberRange(min=1)])
    passing_score = IntegerField('Pontuação Mínima (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    xp_reward = IntegerField('Recompensa XP', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Salvar Quiz')

class QuestionForm(FlaskForm):
    text = TextAreaField('Pergunta', validators=[DataRequired()])
    points = IntegerField('Pontos', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Salvar Pergunta')

class AnswerForm(FlaskForm):
    text = TextAreaField('Resposta', validators=[DataRequired()])
    is_correct = BooleanField('Resposta Correta')
    submit = SubmitField('Salvar Resposta')

class QuizAttemptForm(FlaskForm):
    submit = SubmitField('Enviar Respostas')

class ForumPostForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(min=5, max=100)])
    content = TextAreaField('Conteúdo', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Publicar')

class ForumReplyForm(FlaskForm):
    content = TextAreaField('Resposta', validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Responder')

class UserProfileForm(FlaskForm):
    first_name = StringField('Nome', validators=[DataRequired()])
    last_name = StringField('Sobrenome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Atualizar Perfil')

class UserRoleForm(FlaskForm):
    role = SelectField('Papel', choices=[('student', 'Aluno'), ('teacher', 'Professor'), ('admin', 'Administrador')])
    submit = SubmitField('Atualizar Papel')

class PaymentForm(FlaskForm):
    course_id = HiddenField('ID do Curso', validators=[DataRequired()])
    submit = SubmitField('Realizar Pagamento via PIX')

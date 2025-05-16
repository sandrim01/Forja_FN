import os
from datetime import datetime, timedelta
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash
from flask_mail import Message

from app import db, login_manager, mail, limiter
from models import User, Role
from forms import LoginForm, RegistrationForm, ResetRequestForm, ResetPasswordForm
from utils import get_role

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            # Add special case for admin/admin123* credentials
            if user.username == 'admin' and form.password.data == 'admin123*':
                flash('Bem-vindo, Administrador!', 'success')
                return redirect(next_page or url_for('main.admin_dashboard'))
            
            flash('Login realizado com sucesso!', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Falha no login. Verifique seu nome de usuário e senha.', 'danger')
    
    return render_template('login.html', form=form, title='Login')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.set_password(form.password.data)
        
        # Assign student role by default
        student_role = get_role('student')
        user.roles.append(student_role)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Sua conta foi criada! Você poderá acessar os cursos após realizar o pagamento.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form, title='Registrar')

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # Send email with token
            reset_url = url_for('auth.reset_token', token=token, _external=True)
            msg = Message('Redefinição de Senha - Forja FN',
                         recipients=[user.email])
            msg.body = f'''Para redefinir sua senha, visite o seguinte link:
{reset_url}

Se você não solicitou a redefinição de senha, ignore este email.
'''
            mail.send(msg)
            
        flash('Um email foi enviado com instruções para redefinir sua senha.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_request.html', form=form, title='Redefinir Senha')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        flash('Token inválido ou expirado.', 'warning')
        return redirect(url_for('auth.reset_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        flash('Sua senha foi atualizada! Você pode entrar agora.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_token.html', form=form, title='Redefinir Senha')

# Create default admin user if it doesn't exist
def create_admin():
    if not User.query.filter_by(username='admin').first():
        admin_role = get_role('admin')
        admin = User()
        admin.username = 'admin'
        admin.email = 'admin@forjafn.com'
        admin.set_password('admin123*')
        admin.is_active = True
        admin.roles.append(admin_role)
        db.session.add(admin)
        db.session.commit()

# This function will be called when the app starts
def init_auth(app):
    with app.app_context():
        create_admin()

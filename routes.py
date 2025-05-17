from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc

from app import db, limiter
from models import User, Course, Lesson, Quiz, Achievement, ForumPost, Payment
from forms import UserProfileForm
from utils import requires_roles

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get featured courses
    featured_courses = Course.query.limit(3).all()
    
    # Get leaderboard
    leaderboard = User.query.order_by(desc(User.xp)).limit(10).all()
    
    return render_template('index.html', 
                          title='Forja FN - Plataforma de Estudos', 
                          featured_courses=featured_courses,
                          leaderboard=leaderboard)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's enrolled courses
    enrolled_courses = current_user.courses
    
    # Get user's achievements
    achievements = current_user.achievements
    
    # Get recent forum posts
    recent_posts = ForumPost.query.order_by(desc(ForumPost.created_at)).limit(5).all()
    
    # Get leaderboard
    top_users = User.query.order_by(desc(User.xp)).limit(5).all()
    
    # Calculate progress
    next_level_xp = current_user.level * 150
    progress_percentage = min(100, (current_user.xp / next_level_xp) * 100)
    
    return render_template('dashboard.html', 
                          title='Painel do Aluno',
                          enrolled_courses=enrolled_courses,
                          achievements=achievements,
                          recent_posts=recent_posts,
                          top_users=top_users,
                          next_level_xp=next_level_xp,
                          progress_percentage=progress_percentage)

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UserProfileForm()
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Seu perfil foi atualizado com sucesso!', 'success')
        return redirect(url_for('main.profile'))
    
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    
    # Get payment history
    payments = Payment.query.filter_by(user_id=current_user.id).all()
    
    return render_template('profile.html', 
                          title='Meu Perfil',
                          form=form,
                          payments=payments)

@main_bp.route('/courses')
def courses():
    all_courses = Course.query.all()
    return render_template('courses/index.html', 
                          title='Cursos Disponíveis',
                          courses=all_courses)

@main_bp.route('/courses/<int:course_id>')
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if user is enrolled or is admin/teacher
    is_enrolled = False
    can_access = False
    
    if current_user.is_authenticated:
        is_enrolled = course in current_user.courses
        can_access = is_enrolled or current_user.is_admin() or current_user.is_teacher()
    
    return render_template('courses/view.html',
                          title=course.title,
                          course=course,
                          is_enrolled=is_enrolled,
                          can_access=can_access)

@main_bp.route('/courses/<int:course_id>/lesson/<int:lesson_id>')
@login_required
def view_lesson(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Ensure lesson belongs to course
    if lesson.course_id != course.id:
        abort(404)
    
    # Check if user is enrolled or is admin/teacher
    is_enrolled = course in current_user.courses
    can_access = is_enrolled or current_user.is_admin() or current_user.is_teacher()
    
    if not can_access:
        flash('Você precisa estar matriculado neste curso para acessar esta aula.', 'warning')
        return redirect(url_for('main.view_course', course_id=course.id))
    
    # Get lessons for navigation
    lessons = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.order).all()
    
    # Get lesson index for navigation
    current_index = next((i for i, l in enumerate(lessons) if l.id == lesson.id), 0)
    prev_lesson = lessons[current_index - 1] if current_index > 0 else None
    next_lesson = lessons[current_index + 1] if current_index < len(lessons) - 1 else None
    
    # Award XP if first time viewing
    # This would need to track lesson completion in a separate table in a real app
    
    return render_template('courses/lesson.html',
                          title=lesson.title,
                          course=course,
                          lesson=lesson,
                          lessons=lessons,
                          prev_lesson=prev_lesson,
                          next_lesson=next_lesson)

@main_bp.route('/courses/<int:course_id>/quiz/<int:quiz_id>')
@login_required
def view_quiz(course_id, quiz_id):
    course = Course.query.get_or_404(course_id)
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Ensure quiz belongs to course
    if quiz.course_id != course.id:
        abort(404)
    
    # Check if user is enrolled or is admin/teacher
    is_enrolled = course in current_user.courses
    can_access = is_enrolled or current_user.is_admin() or current_user.is_teacher()
    
    if not can_access:
        flash('Você precisa estar matriculado neste curso para acessar este quiz.', 'warning')
        return redirect(url_for('main.view_course', course_id=course.id))
    
    return render_template('courses/quiz.html',
                          title=quiz.title,
                          course=course,
                          quiz=quiz)

@main_bp.route('/leaderboard')
def leaderboard():
    leaders = User.query.order_by(desc(User.xp)).limit(20).all()
    
    return render_template('leaderboard.html',
                          title='Ranking FN',
                          leaders=leaders)

@main_bp.route('/achievements')
@login_required
def achievements():
    # Get all achievements
    all_achievements = Achievement.query.all()
    
    # Get user's achievements
    user_achievements = current_user.achievements
    
    return render_template('achievements.html',
                          title='Conquistas',
                          all_achievements=all_achievements,
                          user_achievements=user_achievements)

# Admin routes
@main_bp.route('/admin')
@login_required
@requires_roles('admin')
def admin_dashboard():
    if not current_user.is_admin():
        abort(403)
    elif request.path == '/':
        return redirect(url_for('main.admin_dashboard'))
        
    # Count users
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_forum_posts = ForumPost.query.count()
    
    # Count payments and calculate total revenue
    completed_payments = Payment.query.filter_by(status='completed').all()
    total_payments = len(completed_payments)
    total_revenue = sum(payment.amount for payment in completed_payments)
    
    # Recent users and payments
    recent_users = User.query.order_by(desc(User.created_at)).limit(10).all()
    recent_payments = Payment.query.order_by(desc(Payment.created_at)).limit(5).all()
    
    return render_template('admin/dashboard.html',
                          title='Painel Administrativo',
                          total_users=total_users,
                          total_courses=total_courses,
                          total_payments=total_payments,
                          total_revenue=total_revenue,
                          total_forum_posts=total_forum_posts,
                          recent_users=recent_users,
                          recent_payments=recent_payments)

@main_bp.route('/admin/users')
@login_required
@requires_roles('admin')
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html',
                          title='Gerenciar Usuários',
                          users=users)

@main_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
@requires_roles('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username != 'admin':
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Cannot delete admin user'})

@main_bp.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@requires_roles('admin')
def toggle_user_status(user_id):
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@login_required
@requires_roles('admin')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.email = data.get('email', user.email)
    user.is_active = data.get('is_active', user.is_active)
    
    db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/admin/users/add', methods=['POST'])
@login_required
@requires_roles('admin')
def add_user():
    try:
        data = request.form
        
        # Create new user
        user = User()
        user.username = data['email'].split('@')[0]  # Use email prefix as username
        user.email = data['email']
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.set_password(data['password'])
        user.is_active = True
        
        # Add student role
        student_role = Role.query.filter_by(name='student').first()
        if student_role:
            user.roles.append(student_role)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@main_bp.route('/admin/courses')
@login_required
@requires_roles('admin')
def admin_courses():
    courses = Course.query.all()
    return render_template('admin/courses.html',
                          title='Gerenciar Cursos',
                          courses=courses)

# Teacher routes
@main_bp.route('/teacher')
@login_required
@requires_roles('teacher')
def teacher_dashboard():
    # Get courses created by this teacher
    teacher_courses = Course.query.filter_by(author_id=current_user.id).all()
    
    return render_template('teacher/dashboard.html',
                          title='Painel do Professor',
                          courses=teacher_courses)

# API endpoints for AJAX calls
@main_bp.route('/api/check_xp')
@login_required
def check_xp():
    """Endpoint to check if user leveled up"""
    return jsonify({
        'level': current_user.level,
        'xp': current_user.xp,
        'rank_name': current_user.get_rank_name(),
        'rank_image': current_user.get_rank_image(),
        'next_level_xp': current_user.level * 150
    })

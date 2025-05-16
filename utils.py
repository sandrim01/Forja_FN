import re
import bleach
from functools import wraps
from flask import abort, render_template
from flask_login import current_user
from werkzeug.security import generate_password_hash
from app import db
from models import Role, User, ForumCategory, Forum

def sanitize_html(content):
    """Sanitize HTML content to prevent XSS attacks"""
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                    'blockquote', 'ul', 'ol', 'li', 'code', 'pre']
    allowed_attrs = {'*': ['class', 'style']}
    
    clean_content = bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )
    
    return clean_content

def requires_roles(*roles):
    """Decorator for views that require specific roles"""
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            for role in roles:
                if current_user.has_role(role):
                    return f(*args, **kwargs)
            
            abort(403)
        return wrapped
    return wrapper

def get_role(name):
    """Get role by name, create if not exists"""
    role = Role.query.filter_by(name=name).first()
    if not role:
        role = Role(name=name)
        db.session.add(role)
        db.session.commit()
    return role

def create_default_roles():
    """Create default roles if they don't exist"""
    roles = ['admin', 'teacher', 'student']
    for role_name in roles:
        get_role(role_name)
    
    db.session.commit()

def create_admin_user():
    """Create admin user if not exists"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@forjafn.com',
            first_name='Admin',
            last_name='User',
            is_active=True
        )
        admin.set_password('admin123*')
        
        # Add admin role
        admin_role = get_role('admin')
        admin.roles.append(admin_role)
        
        db.session.add(admin)
        db.session.commit()

def create_forum_categories():
    """Create default forum categories if they don't exist"""
    categories = [
        {
            'name': 'Dúvidas Técnicas',
            'description': 'Tire suas dúvidas sobre os conteúdos técnicos dos cursos',
            'forums': [
                {'name': 'Matemática', 'description': 'Dúvidas sobre matemática e cálculos'},
                {'name': 'Português', 'description': 'Dúvidas sobre língua portuguesa e redação'},
                {'name': 'Conhecimentos Navais', 'description': 'Dúvidas sobre temas específicos da Marinha'}
            ]
        },
        {
            'name': 'Estratégias de Prova',
            'description': 'Compartilhe e discuta estratégias para as provas',
            'forums': [
                {'name': 'Gerenciamento de Tempo', 'description': 'Como administrar o tempo durante as provas'},
                {'name': 'Técnicas de Estudo', 'description': 'Compartilhe suas técnicas de estudo e memorização'},
                {'name': 'Controle Emocional', 'description': 'Dicas para controlar a ansiedade e o nervosismo'}
            ]
        },
        {
            'name': 'Material Complementar',
            'description': 'Compartilhe materiais complementares que possam ajudar outros alunos',
            'forums': [
                {'name': 'Livros Recomendados', 'description': 'Indicações de livros e materiais de apoio'},
                {'name': 'Links Úteis', 'description': 'Sites e recursos online relevantes'},
                {'name': 'Notícias Militares', 'description': 'Notícias e atualizações relevantes para a carreira militar'}
            ]
        }
    ]
    
    for category_data in categories:
        category = ForumCategory.query.filter_by(name=category_data['name']).first()
        
        if not category:
            category = ForumCategory(
                name=category_data['name'],
                description=category_data['description']
            )
            db.session.add(category)
            db.session.flush()  # Flush to get the ID for relationships
            
            for forum_data in category_data['forums']:
                forum = Forum(
                    name=forum_data['name'],
                    description=forum_data['description'],
                    category_id=category.id
                )
                db.session.add(forum)
    
    db.session.commit()

def handle_403(error):
    """Handle 403 errors"""
    return render_template('errors/403.html', title='Acesso Negado'), 403

def handle_404(error):
    """Handle 404 errors"""
    return render_template('errors/404.html', title='Página não encontrada'), 404

def handle_500(error):
    """Handle 500 errors"""
    return render_template('errors/500.html', title='Erro interno'), 500

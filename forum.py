from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import desc

from app import db, limiter
from models import ForumCategory, Forum, ForumPost, ForumReply
from forms import ForumPostForm, ForumReplyForm
from utils import sanitize_html, requires_roles

forum_bp = Blueprint('forum', __name__)

@forum_bp.route('/')
def index():
    categories = ForumCategory.query.all()
    return render_template('forum/index.html',
                          title='Fórum da Comunidade',
                          categories=categories)

@forum_bp.route('/category/<int:category_id>')
def category(category_id):
    category = ForumCategory.query.get_or_404(category_id)
    forums = Forum.query.filter_by(category_id=category_id).all()
    
    return render_template('forum/category.html',
                          title=category.name,
                          category=category,
                          forums=forums)

@forum_bp.route('/forum/<int:forum_id>')
def view_forum(forum_id):
    forum = Forum.query.get_or_404(forum_id)
    
    # Get posts with pagination
    page = request.args.get('page', 1, type=int)
    posts = ForumPost.query.filter_by(forum_id=forum_id).order_by(
        ForumPost.is_pinned.desc(),
        desc(ForumPost.created_at)
    ).paginate(page=page, per_page=10)
    
    return render_template('forum/forum.html',
                          title=forum.name,
                          forum=forum,
                          posts=posts)

@forum_bp.route('/forum/<int:forum_id>/create', methods=['GET', 'POST'])
@login_required
def create_topic(forum_id):
    forum = Forum.query.get_or_404(forum_id)
    form = ForumPostForm()
    
    if form.validate_on_submit():
        # Sanitize content
        safe_content = sanitize_html(form.content.data)
        
        post = ForumPost(
            title=form.title.data,
            content=safe_content,
            forum_id=forum_id,
            user_id=current_user.id
        )
        
        db.session.add(post)
        db.session.commit()
        
        # Award XP for creating a post
        current_user.add_xp(10)
        db.session.commit()
        
        flash('Tópico criado com sucesso!', 'success')
        return redirect(url_for('forum.view_topic', topic_id=post.id))
    
    return render_template('forum/create_topic.html',
                          title='Criar Novo Tópico',
                          forum=forum,
                          form=form)

@forum_bp.route('/topic/<int:topic_id>', methods=['GET', 'POST'])
def view_topic(topic_id):
    post = ForumPost.query.get_or_404(topic_id)
    
    # Increment view count
    post.view_count += 1
    db.session.commit()
    
    # Reply form
    form = ForumReplyForm()
    
    if current_user.is_authenticated and form.validate_on_submit():
        # Ensure topic is not closed
        if post.is_closed:
            flash('Este tópico está fechado e não aceita novas respostas.', 'warning')
            return redirect(url_for('forum.view_topic', topic_id=topic_id))
        
        # Sanitize content
        safe_content = sanitize_html(form.content.data)
        
        reply = ForumReply(
            content=safe_content,
            post_id=topic_id,
            user_id=current_user.id,
            # Teachers and admins can mark responses as official
            is_official=current_user.is_admin() or current_user.is_teacher()
        )
        
        db.session.add(reply)
        db.session.commit()
        
        # Award XP for replying
        current_user.add_xp(5)
        db.session.commit()
        
        flash('Resposta publicada com sucesso!', 'success')
        return redirect(url_for('forum.view_topic', topic_id=topic_id))
    
    # Get replies with pagination
    page = request.args.get('page', 1, type=int)
    replies = ForumReply.query.filter_by(post_id=topic_id).order_by(
        ForumReply.is_official.desc(),
        ForumReply.created_at
    ).paginate(page=page, per_page=10)
    
    return render_template('forum/topic.html',
                          title=post.title,
                          post=post,
                          replies=replies,
                          form=form)

@forum_bp.route('/topic/<int:topic_id>/pin', methods=['POST'])
@login_required
@requires_roles('admin', 'teacher')
def pin_topic(topic_id):
    post = ForumPost.query.get_or_404(topic_id)
    post.is_pinned = not post.is_pinned
    db.session.commit()
    
    flash(f'Tópico {"fixado" if post.is_pinned else "desafixado"} com sucesso!', 'success')
    return redirect(url_for('forum.view_topic', topic_id=topic_id))

@forum_bp.route('/topic/<int:topic_id>/close', methods=['POST'])
@login_required
@requires_roles('admin', 'teacher')
def close_topic(topic_id):
    post = ForumPost.query.get_or_404(topic_id)
    post.is_closed = not post.is_closed
    db.session.commit()
    
    flash(f'Tópico {"fechado" if post.is_closed else "reaberto"} com sucesso!', 'success')
    return redirect(url_for('forum.view_topic', topic_id=topic_id))

@forum_bp.route('/reply/<int:reply_id>/mark_official', methods=['POST'])
@login_required
@requires_roles('admin', 'teacher')
def mark_official(reply_id):
    reply = ForumReply.query.get_or_404(reply_id)
    reply.is_official = not reply.is_official
    db.session.commit()
    
    flash(f'Resposta {"marcada como oficial" if reply.is_official else "desmarcada como oficial"} com sucesso!', 'success')
    return redirect(url_for('forum.view_topic', topic_id=reply.post_id))

@forum_bp.route('/reply/<int:reply_id>/award_xp', methods=['POST'])
@login_required
@requires_roles('admin', 'teacher')
def award_xp(reply_id):
    reply = ForumReply.query.get_or_404(reply_id)
    
    # Award XP to the reply author for a useful post
    author = reply.author
    author.add_xp(10)
    db.session.commit()
    
    flash(f'10 XP concedido a {author.username} por contribuição útil!', 'success')
    return redirect(url_for('forum.view_topic', topic_id=reply.post_id))

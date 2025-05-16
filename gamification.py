from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import User, Achievement, UserAchievement
from app import db

def check_achievement(user, achievement_name):
    """Check if user has earned an achievement and award it if not"""
    achievement = Achievement.query.filter_by(name=achievement_name).first()
    
    if not achievement:
        return False
    
    if achievement in user.achievements:
        return False
    
    # Award achievement
    user.achievements.append(achievement)
    user.add_xp(achievement.xp_reward)
    db.session.commit()
    
    return True

def check_level_achievements(user):
    """Check and award level-based achievements"""
    level_achievements = {
        5: "Aspirante",
        10: "Almirante"
    }
    
    if user.level in level_achievements and check_achievement(user, level_achievements[user.level]):
        return level_achievements[user.level]
    
    return None

def check_lesson_achievements(user, lessons_completed):
    """Check and award lesson completion achievements"""
    if lessons_completed >= 10 and check_achievement(user, "Dedicado"):
        return "Dedicado"
    
    if lessons_completed >= 50 and check_achievement(user, "Estudioso"):
        return "Estudioso"
    
    return None

def check_quiz_achievements(user, quiz_score, total_quizzes):
    """Check and award quiz-based achievements"""
    if quiz_score == 100 and check_achievement(user, "Excelência"):
        return "Excelência"
    
    if total_quizzes >= 10 and check_achievement(user, "Testado e Aprovado"):
        return "Testado e Aprovado"
    
    return None

def check_forum_achievements(user, post_count, reply_count):
    """Check and award forum participation achievements"""
    if post_count >= 5 and check_achievement(user, "Comunicador"):
        return "Comunicador"
    
    if reply_count >= 20 and check_achievement(user, "Colaborador"):
        return "Colaborador"
    
    return None

def check_course_achievements(user, courses_completed):
    """Check and award course completion achievements"""
    if courses_completed >= 1 and check_achievement(user, "Iniciante"):
        return "Iniciante"
    
    if courses_completed >= 5 and check_achievement(user, "Especialista"):
        return "Especialista"
    
    return None

def update_leaderboard():
    """Return current top 10 users by XP"""
    leaders = User.query.order_by(User.xp.desc()).limit(10).all()
    leaderboard = []
    
    for i, leader in enumerate(leaders):
        leaderboard.append({
            'rank': i+1,
            'username': leader.username,
            'xp': leader.xp,
            'level': leader.level,
            'rank_name': leader.get_rank_name(),
            'rank_image': leader.get_rank_image()
        })
        
    return leaderboard

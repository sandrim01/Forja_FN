import os
import json
import uuid
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify
from flask_login import login_required, current_user

import mercadopago
from app import db, limiter
from models import User, Course, Payment
from forms import PaymentForm

payment_bp = Blueprint('payment', __name__)

# Initialize Mercado Pago SDK
mp = mercadopago.SDK(os.environ.get("MERCADO_PAGO_ACCESS_TOKEN", "TEST-123456789"))

@payment_bp.route('/checkout/<int:course_id>', methods=['GET', 'POST'])
@login_required
def checkout(course_id):
    # Get course
    course = Course.query.get_or_404(course_id)
    
    # Check if user is already enrolled
    if course in current_user.courses:
        flash('Você já está matriculado neste curso.', 'info')
        return redirect(url_for('main.view_course', course_id=course.id))
    
    form = PaymentForm()
    form.course_id.data = course.id
    
    if form.validate_on_submit():
        # Create payment record
        payment = Payment(
            amount=course.price,
            currency='BRL',
            status='pending',
            payment_method='pix',
            user_id=current_user.id,
            course_id=course.id
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Create PIX payment through Mercado Pago
        preference = {
            "transaction_amount": float(course.price),
            "description": f"Inscrição no curso {course.title}",
            "payment_method_id": "pix",
            "payer": {
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
            },
            "external_reference": str(payment.id)
        }
        
        try:
            # In a real app, this would call the Mercado Pago API
            # For demo, we'll create a mock response
            pix_data = {
                "qr_code": "00020126580014br.gov.bcb.pix0136a629532e-7693-4846-b028-f142082d7b3752040000530398654041.005802BR5909Test User6009SAO PAULO62070503***630415A8",
                "qr_code_base64": "iVBORw0KGgoAAAANSUhEUgAABRQAAAUUCAYAAACu5p7oAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAIABJREFUeJzs3XmUlfV9N/7...",
                "in_store_reference": "62070503***",
                "transaction_id": str(uuid.uuid4())
            }
            
            # Update payment with transaction ID
            payment.transaction_id = pix_data['transaction_id']
            payment.payment_data = json.dumps(pix_data)
            db.session.commit()
            
            return render_template('payment/checkout.html',
                                title='Pagamento PIX',
                                course=course,
                                payment=payment,
                                pix_data=pix_data)
        
        except Exception as e:
            db.session.delete(payment)
            db.session.commit()
            flash(f'Erro ao processar pagamento: {str(e)}', 'danger')
            return redirect(url_for('main.view_course', course_id=course.id))
    
    return render_template('payment/checkout.html',
                          title='Checkout',
                          course=course,
                          form=form)

@payment_bp.route('/webhook', methods=['POST'])
@limiter.exempt
def webhook():
    """Webhook for Mercado Pago payment notifications"""
    try:
        data = request.json
        
        if data.get('type') == 'payment' and data.get('action') == 'payment.updated':
            payment_id = data.get('data', {}).get('id')
            
            # Get payment details from Mercado Pago
            # In a real app, this would verify with the Mercado Pago API
            
            # For demo purposes, we'll assume the payment was successful
            # and find the payment by the external_reference
            external_reference = data.get('external_reference')
            
            if external_reference:
                payment = Payment.query.get(external_reference)
                
                if payment and payment.status != 'completed':
                    # Update payment status
                    payment.status = 'completed'
                    payment.updated_at = datetime.utcnow()
                    
                    # Add user to course
                    user = User.query.get(payment.user_id)
                    course = Course.query.get(payment.course_id)
                    
                    if user and course and course not in user.courses:
                        user.courses.append(course)
                        user.is_active = True
                        
                        # Award XP for enrolling in a course
                        user.add_xp(50)
                    
                    db.session.commit()
        
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@payment_bp.route('/success/<int:payment_id>')
@login_required
def payment_success(payment_id):
    # Get payment
    payment = Payment.query.get_or_404(payment_id)
    
    # Ensure payment belongs to current user
    if payment.user_id != current_user.id:
        abort(403)
    
    # For demo purposes, we'll simulate a successful payment
    if payment.status == 'pending':
        payment.status = 'completed'
        payment.updated_at = datetime.utcnow()
        
        # Add user to course if not already enrolled
        course = Course.query.get(payment.course_id)
        if course and course not in current_user.courses:
            current_user.courses.append(course)
            current_user.is_active = True
            
            # Award XP for enrolling in a course
            current_user.add_xp(50)
        
        db.session.commit()
        
        flash('Pagamento confirmado! Você agora tem acesso ao curso.', 'success')
    
    return render_template('payment/success.html',
                          title='Pagamento Confirmado',
                          payment=payment)

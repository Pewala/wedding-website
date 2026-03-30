from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from models import db, RSVP, WeddingInfo
from config import Config
from datetime import datetime
import re

app = Flask(__name__)
app.config.from_object(Config)

# Инициализация базы данных
db.init_app(app)

# Создание таблиц при первом запуске
with app.app_context():
    db.create_all()
    # Добавляем информацию о свадьбе, если её нет
    if not WeddingInfo.query.first():
        wedding_info = WeddingInfo()
        db.session.add(wedding_info)
        db.session.commit()

def validate_phone(phone):
    """Простая валидация российского номера телефона"""
    pattern = r'^(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$'
    return re.match(pattern, phone) is not None

def validate_name(name):
    """Валидация имени (только буквы, пробелы и дефисы)"""
    return len(name.strip()) >= 2 and re.match(r'^[а-яА-ЯёЁa-zA-Z\s\-]+$', name.strip())

@app.route('/')
def index():
    """Главная страница с приглашением"""
    wedding_info = WeddingInfo.query.first()
    return render_template('index.html', wedding_info=wedding_info)

@app.route('/api/rsvp', methods=['POST'])
def rsvp_submit():
    """API для отправки RSVP формы"""
    try:
        data = request.form
        
        # Валидация данных
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        attendance = data.get('attendance', '')
        wishes = data.get('wishes', '').strip()
        
        # Проверка обязательных полей
        if not all([name, phone, attendance]):
            return jsonify({
                'success': False,
                'message': 'Пожалуйста, заполните все обязательные поля'
            }), 400
        
        # Валидация имени
        if not validate_name(name):
            return jsonify({
                'success': False,
                'message': 'Пожалуйста, введите корректное имя (только буквы, пробелы и дефисы)'
            }), 400
        
        # Валидация телефона
        if not validate_phone(phone):
            return jsonify({
                'success': False,
                'message': 'Пожалуйста, введите корректный номер телефона'
            }), 400
        
        # Создание записи в БД
        rsvp = RSVP(
            name=name,
            phone=phone,
            attendance=attendance,
            wishes=wishes
        )
        
        db.session.add(rsvp)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Спасибо! Ваш ответ успешно отправлен.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Произошла ошибка при отправке. Пожалуйста, попробуйте позже.'
        }), 500

@app.route('/api/rsvp/list')
def rsvp_list():
    """API для получения списка RSVP (только для администрирования)"""
    # В реальном проекте здесь должна быть аутентификация
    rsvps = RSVP.query.order_by(RSVP.created_at.desc()).all()
    return jsonify([r.to_dict() for r in rsvps])

@app.route('/api/stats')
def get_stats():
    """API для получения статистики ответов"""
    total = RSVP.query.count()
    coming = RSVP.query.filter_by(attendance='yes').count()
    coming_plus = RSVP.query.filter_by(attendance='plus1').count()
    not_coming = RSVP.query.filter_by(attendance='no').count()
    
    # Примерный подсчет гостей (считаем что plus1 = 2 человека)
    total_guests = coming + (coming_plus * 2)
    
    return jsonify({
        'total_rsvp': total,
        'coming': coming,
        'coming_plus': coming_plus,
        'not_coming': not_coming,
        'total_guests': total_guests
    })

@app.route('/admin')
def admin_panel():
    """Простая админ-панель (в реальном проекте защитить паролем)"""
    # Временная простая админка без аутентификации
    # В продакшене обязательно добавьте проверку пароля!
    rsvps = RSVP.query.order_by(RSVP.created_at.desc()).all()
    stats = {
        'total': len(rsvps),
        'coming': sum(1 for r in rsvps if r.attendance == 'yes'),
        'coming_plus': sum(1 for r in rsvps if r.attendance == 'plus1'),
        'not_coming': sum(1 for r in rsvps if r.attendance == 'no')
    }
    return render_template('admin.html', rsvps=rsvps, stats=stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

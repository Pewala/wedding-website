from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class RSVP(db.Model):
    __tablename__ = 'rsvps'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    attendance = db.Column(db.String(20), nullable=False)
    wishes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'attendance': self.attendance,
            'wishes': self.wishes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class WeddingInfo(db.Model):
    __tablename__ = 'wedding_info'
    
    id = db.Column(db.Integer, primary_key=True)
    bride_name = db.Column(db.String(50), default='Анастасия')
    groom_name = db.Column(db.String(50), default='Илья')
    wedding_date = db.Column(db.String(20), default='2026-07-10')
    wedding_time = db.Column(db.String(10), default='15:00')
    ceremony_place = db.Column(db.String(200), default='Дворец Бракосочетания, ул. Никитская, 96')
    banquet_place = db.Column(db.String(200), default='Кафе "Дружба", пр. Текстильщиков, 92')
    dress_code = db.Column(db.String(200), default='Вечерний, пастельные тона, Black Tie Optional')

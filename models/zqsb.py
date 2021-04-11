# -*- coding: utf-8 -*-
from main import db
import datetime

class Zqsb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512))
    publish_date = db.Column(db.DateTime, default=datetime.datetime.now)
    np = db.Column(db.Integer)
    pdf_url = db.Column(db.String(1024))
    news = db.relationship('ZqsbNews',back_populates='master')
    
    
    
class ZqsbNews(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    
    body = db.Column(db.String(1024))
    
    master_id = db.Column(db.Integer, db.ForeignKey('zqsb.id'))

    master = db.relationship('Zqsb', back_populates='news')
    
    
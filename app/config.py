import os
from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:1326@localhost:5432/sportsbanco'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-forte-aqui'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'uma-chave-secreta-jwt-aqui'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
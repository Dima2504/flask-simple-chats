"""Base config module"""
import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'development'
    DEBUG = True

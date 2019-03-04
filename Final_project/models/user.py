#!/usr/bin/python3
"""
User Class from Models Module
"""
import hashlib
# import os
from flask_login import UserMixin
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from models.base_model import BaseModel, Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float
# STORAGE_TYPE = os.environ.get('HBNB_TYPE_STORAGE')


class User(BaseModel, Base, UserMixin):
    """
        User class handles all application users
    """
    # if STORAGE_TYPE == "db":
    __tablename__ = 'users'
    email = Column(String(128), nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)

    places = relationship('Place', backref='user', cascade='delete')
    reviews = relationship('Review', backref='user', cascade='delete')
    # else:
    #     email = ''
    #     password = ''
    #     first_name = ''
    #     last_name = ''

    def __init__(self, *args, **kwargs):
        """
            instantiates user object
        """
        if kwargs:
            pwd = kwargs.pop('password', None)
            if pwd:
                User.__set_password(self, pwd)
        super().__init__(*args, **kwargs)

    def __set_password(self, pwd):
        """
            custom setter: encrypts password to MD5
        """
        secure = hashlib.md5()
        secure.update(pwd.encode("utf-8"))
        secure_password = secure.hexdigest()
        setattr(self, "password", secure_password)

    def is_authenticated(self):
        return True
    #
    # def get_reset_token(self, expires_sec=1800):
    #     s = Serializer(app.config['SECRET_KEY'], expires_sec)
    #     return s.dumps({'user_id': self.id}).decode('utf-8')

    # @staticmethod
    # def verify_reset_token(token):
    #     s = Serializer(app.config['SECRET_KEY'])
    #     try:
    #         user_id = s.loads(token)['user_id']
    #     except:
    #         return None
    #     return storage.get('User', user_id)

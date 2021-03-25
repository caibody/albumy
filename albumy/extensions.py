# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask_avatars import Avatars
from flask_bootstrap import Bootstrap
from flask_dropzone import Dropzone
from flask_login import LoginManager, AnonymousUserMixin,current_user
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_whooshee import Whooshee
from flask_wtf import CSRFProtect
import sys

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
dropzone = Dropzone()
moment = Moment()
whooshee = Whooshee()
avatars = Avatars()
csrf = CSRFProtect()

# 添加一个获取登陆用户的方法,只要用了flask_login，用户登录就会调用该方法
@login_manager.user_loader
def load_user(user_id):
    # print(sys._getframe().f_code.co_filename)  # 当前文件名，可以通过__file__获得
    # print(sys._getframe(0).f_code.co_name)  # 当前函数名
    # print(sys._getframe(1).f_code.co_name)  # 调用该函数的函数名字，如果没有被调用，则返回<module>
    # print(sys._getframe(0).f_lineno)  # 当前函数的行号
    # print(sys._getframe(1).f_lineno)  # 调用该函数的行号
    print('只要用了flask_login，用户登录就会调用该方法')
    from albumy.models import User
    # User.query.get(int(user_id))是通过主键去查找，得到的是行数据
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
# login_manager.login_message = 'Your custom message'
login_manager.login_message_category = 'warning'

login_manager.refresh_view = 'auth.re_authenticate'
# login_manager.needs_refresh_message = 'Your custom message'
login_manager.needs_refresh_message_category = 'warning'

# 创建一个匿名用户的类型，继承
class Guest(AnonymousUserMixin):
    def can(self, permission_name):
        return False
    @property
    def is_admin(self):
        return False

# 修改匿名用户的属性，添加can()方法和is_admin属性
login_manager.anonymous_user = Guest

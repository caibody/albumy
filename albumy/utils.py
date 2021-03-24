# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import os
import uuid

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

import PIL
from PIL import Image
from flask import current_app, request, url_for, redirect, flash
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from albumy.extensions import db
from albumy.models import User
from albumy.settings import Operations

# expire_in有效时间，单位s，默认3600
def generate_token(user, operation, expire_in=None, **kwargs):
    # s = Serializer(密钥, 有效时间)
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)
    # 要被签名的数据
    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    # 把数据进行签名使用.dumps
    return s.dumps(data)


def validate_token(user, token, operation, new_password=None):
    s = Serializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if operation != data.get('operation') or user.id != data.get('id'):
        return False

    if operation == Operations.CONFIRM:
        user.confirmed = True
    elif operation == Operations.RESET_PASSWORD:
        user.set_password(new_password)
    elif operation == Operations.CHANGE_EMAIL:
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if User.query.filter_by(email=new_email).first() is not None:
            return False
        user.email = new_email
    else:
        return False

    db.session.commit()
    return True


def rename_image(old_filename):
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def resize_image(image, filename, base_width):
    filename, ext = os.path.splitext(filename)
    img = Image.open(image)
    # 如果图片的宽度小于base_width，直接返回图片
    if img.size[0] <= base_width:
        return filename + ext
    #如果图片宽度超了base_width，计算出要缩小的百分比
    w_percent = (base_width / float(img.size[0]))
    # 计算图片高度
    h_size = int((float(img.size[1]) * float(w_percent)))
    # 调整图片大小，抗锯齿处理
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
    # 给新图片命名
    filename += current_app.config['ALBUMY_PHOTO_SUFFIX'][base_width] + ext
    #quality参数： 保存图像的质量，值的范围从1（最差）到95（最佳）。 默认值为75，使用中应尽量避免高于95的值; 100会禁用部分JPEG压缩算法，并导致大文件图像质量几乎没有任何增益。
    img.save(os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'], filename), optimize=True, quality=85)
    return filename


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def redirect_back(default='main.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

from html import escape
import os
import time

import flask
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from .exceptions import MissingDataError, VaildDataError


def escape_data(data: str) -> str:
    return escape(data)


def hashing(data: str) -> str:
    return generate_password_hash(data)


def check_hashing(data: str, hash_data: str) -> bool:
    return check_password_hash(hash_data, data)


def validate_json(json: dict = None, **KT: dict) -> dict:
    if not json:
        raise MissingDataError('the data is not defined')

    for key, value in json.items():
        if key not in KT:
            raise MissingDataError('the key is not defined')
        if not isinstance(value, KT[key]):
            raise VaildDataError('the value is not valid')
    return json


dict_rate_limit = {}


def rate_limit(limit: int = 10, ip: str = None, limit_time: int = 60) -> bool:
    now = time.time()
    if ip not in dict_rate_limit:
        dict_rate_limit[ip] = {'count': 0, 'late_time': now}
    count = dict_rate_limit[ip]['count']
    late_time = dict_rate_limit[ip]['late_time']
    if now - late_time >= limit_time:
        dict_rate_limit[ip] = {'count': 1, 'late_time': now}
        return True
    if count < limit:
        dict_rate_limit[ip] = {'count': count + 1, 'late_time': now}
        return True
    return False


def upload_file(
    key: str,
    directory: str,
    allowed: list = None,
    max_size: int = None,
):
    file = flask.request.files.get(key)

    if not file:
        raise MissingDataError('the file is not defined')

    filename = secure_filename(file.filename)
    if not filename:
        raise MissingDataError('the filename is not defined')

    if allowed:
        extension = filename.rsplit('.', 1)[-1].lower()
        if extension not in [item.lower() for item in allowed]:
            raise VaildDataError('the file type is not allowed')

    if max_size is not None:
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > max_size * 1024 * 1024:
            raise VaildDataError('the file size is too large')

    os.makedirs(directory, exist_ok=True)
    file.save(os.path.join(directory, filename))
    return filename

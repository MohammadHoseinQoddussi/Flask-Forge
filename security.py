from exceptions import MissingDataError , VaildDataError
from html import escape
from werkzeug.security import generate_password_hash, check_password_hash
import time
import os
import flask
from werkzeug.utils import secure_filename
#==============XSS==============
def escape_data(data:str)->str:
    return escape(data)

#==============hashing==============
def hashing(data:str)->str:
    return generate_password_hash(data)

def check_hashing(data:str , hash_data:str)->bool:
    return check_password_hash(hash_data , data)

#==============getting json==============
def validate_json(json:dict=None , **KT:dict)->dict:
    if not json:
        raise MissingDataError('the data is not defined')

    for key , value in json.items():
        if not key in KT:
            raise MissingDataError('the key is not defined')
        elif not isinstance(value , KT[key]):
            raise VaildDataError('the value is not valid')
    return json

#==============rate limit==============
dict_rate_limit = {}
def rate_limit(limit:int=10 , ip:str=None , limit_time:int=60)->bool:
    now = time.time()
    if ip not in dict_rate_limit:
        dict_rate_limit[ip] = {'count': 0, 'late_time': now}
    count , late_time = dict_rate_limit[ip]['count'] , dict_rate_limit[ip]['late_time']
    if now - late_time >= limit_time:
        dict_rate_limit[ip] = {'count': 1, 'late_time': now}
        return True
    elif count < limit:
        dict_rate_limit[ip] = {'count': count + 1, 'late_time': now}
        return True
    return False

#==============file upload==============
'''
    max_size :in mega byte or MB
    key : the key of the file
    directory : the name of folder of uploading the file
    allowed : the allowed file type (png , jpg , jpeg , gif , ...)
'''
def upload_file(
    key: str,
    directory: str,
    allowed: list = None,
    max_size: int = None
):
    file = flask.request.files.get(key)

    if not file:
        raise MissingDataError('the file is not defined')

    filename = secure_filename(file.filename)

    if not filename:
        raise MissingDataError('the filename is not defined')

    #==============check extension==============
    if allowed:
        extension = filename.rsplit('.', 1)[-1].lower()

        if extension not in [item.lower() for item in allowed]:
            raise VaildDataError('the file type is not allowed')

    #==============check size==============
    if max_size is not None:
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        if size > max_size * 1024 * 1024:
            raise VaildDataError('the file size is too large')

    #==============make directory==============
    os.makedirs(directory, exist_ok=True)

    #==============save==============
    file.save(os.path.join(directory, filename))

    return filename
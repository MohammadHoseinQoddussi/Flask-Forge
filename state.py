import flask
import smtplib
from email.message import EmailMessage
from exceptions import MissingDataError , VaildDataError

def make_session(**session_data:dict):
    for key , value in session_data.items():
        flask.session[key] = value

def get_session(key:str)->str:
    return flask.session[key]

def remove_session(key:str)->None:
    flask.session.pop(key , None)

def clear_session()->None:
    flask.session.clear()

def return_session()->dict:
    return flask.session

def check_session(key:str)->bool:
    return (
        key in flask.session
    )

def make_cookie(
    key: str,
    value: str,
    max_age: int = None,
    path: str = None,
    domain: str = None,
    secure: bool = False,
    httponly: bool = False
):
    response = flask.make_response()
    response.set_cookie(
        key,
        value,
        max_age=max_age,
        path=path,
        domain=domain,
        secure=secure,
        httponly=httponly
    )
    return response

def get_cookie(key:str)->str:
    return flask.request.cookies.get(key)

def delete_cookie(key: str):
    response = flask.make_response()
    response.delete_cookie(key)
    return response

def send_email(
        to: str,
        subject: str,
        message: str,
        email: str,
        password: str
    ):
    if not to or not subject or not message or not email or not password:
        raise MissingDataError('the to or subject or message or email or password is not defined')
    if not isinstance(to, str) or not isinstance(subject, str) or not isinstance(message, str) or not isinstance(email, str) or not isinstance(password, str):
        raise VaildDataError('the to or subject or message or email or password is not valid')
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email
    msg['To'] = to
    msg.set_content(message)
    with smtplib.SMTP(host='smtp.gmail.com', port=587) as server:
        server.starttls()
        server.login(email, password)
        server.send_message(msg)
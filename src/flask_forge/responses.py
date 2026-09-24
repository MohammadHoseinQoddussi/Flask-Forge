import os

import flask

from .exceptions import MissingDataError


def redirect(url: str, code: int = 302):
    return flask.redirect(url, code=code)


def json_data(**data: dict):
    if not data:
        raise MissingDataError('the data is not defined')
    return flask.jsonify(data)


def send_from_directory(
    directory: str,
    file_name: str,
    as_attachment: bool = False,
    root_path: str = None,
):
    address_file = os.path.join(root_path, directory) if root_path else directory
    return flask.send_from_directory(
        directory=address_file,
        path=file_name,
        as_attachment=as_attachment,
    )


def url_for(endpoint, **values):
    return flask.url_for(endpoint, **values)


def render(template: str, **context: dict):
    return flask.render_template(template, **context)

import flask


class TestClient:
    def __init__(self, app):
        self.client = app.app.test_client()
        self.app = app.app

    @staticmethod
    def check_type(**DT: dict) -> None:
        for value, expected_type in DT.items():
            if not isinstance(value, expected_type):
                raise TypeError('the type is not valid')

    def get(self, url: str, **setting: dict) -> flask.Response:
        if not isinstance(url, str):
            raise TypeError('the type is not valid')
        return self.client.get(url, **setting)

    def post(self, url: str, **setting: dict) -> flask.Response:
        if not isinstance(url, str):
            raise TypeError('the type is not valid')
        return self.client.post(url, **setting)

    def put(self, url: str, **setting: dict) -> flask.Response:
        if not isinstance(url, str):
            raise TypeError('the type is not valid')
        return self.client.put(url, **setting)

    def delete(self, url: str, **setting: dict) -> flask.Response:
        if not isinstance(url, str):
            raise TypeError('the type is not valid')
        return self.client.delete(url, **setting)

    def set_cookie(self, key: str, value: str, **setting: dict):
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError('the type is not valid')
        return self.client.set_cookie(key, value, **setting)

    def delete_cookie(self, key: str, **setting: dict):
        if not isinstance(key, str):
            raise TypeError('the type is not valid')
        return self.client.delete_cookie(key, **setting)

    def get_cookie(self, key: str, **setting: dict):
        if not isinstance(key, str):
            raise TypeError('the type is not valid')
        return self.client.get_cookie(key, **setting)

    def session_transaction(self, **KV: dict):
        with self.client.session_transaction() as session:
            for key, value in KV.items():
                session[key] = value
        return KV

    def request_context(self, url: str, **setting: dict):
        if not isinstance(url, str):
            raise TypeError('the type is not valid')
        with self.app.test_request_context(url, **setting):
            return flask.request.get_json(silent=True)

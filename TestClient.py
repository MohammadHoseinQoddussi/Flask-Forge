import flask

class TestClient:
    #==============init==============
    #TestClient(app)
    def __init__(self, app):
        self.client = app.app.test_client()
        self.app = app.app

    #==============check type==============
    @staticmethod
    def check_type(**DT:dict)->dict:
        for key , value in DT.items():
            if not isinstance(key , value):
                raise TypeError('the type is not valid')
            
    #==============methods==============
    def get(self , url: str , **setting:dict)->flask.Response:
        self.check_type(**{url:str})
        return self.client.get(url, **setting)

    def post(self , url: str , **setting:dict)->flask.Response:
        self.check_type(**{url:str})
        return self.client.post(url, **setting)

    def put(self , url: str , **setting:dict)->flask.Response:
        self.check_type(**{url:str})
        return self.client.put(url, **setting)

    def delete(self , url: str , **setting:dict)->flask.Response:
        self.check_type(**{url:str})
        return self.client.delete(url, **setting)

    #==============cookies==============
    def set_cookie(self , key:str , value:str , **setting:dict)->flask.Response:
        self.check_type(**{key:str , value:str})
        return self.client.set_cookie(key, value, **setting)

    def delete_cookie(self , key:str , **setting:dict)->flask.Response:
        self.check_type(**{key:str})
        return self.client.delete_cookie(key, **setting)

    def get_cookie(self , key:str , **setting:dict)->flask.Response:
        self.check_type(**{key:str})
        return self.client.get_cookie(key, **setting)

    #==============session==============
    def session_transaction(self , **KV:dict):
        with self.client.session_transaction() as session:
            for key , value in KV.items():
                session[key] = value
            return session
    #==============request context==============
    def request_context(self , url:str , **setting:dict):
        self.check_type(**{url:str})
        request_data = None
        with self.app.test_request_context(url, **setting):
            request_data = flask.request.json
        return request_data

from exceptions import MissingDataError , RequestDataError , RunBarsaFlaskKitError
import requests
import json

#==============request data==============
def request_data(
        method: str = None,
        url: str = None,
        **setting_request: dict
    ) -> dict | str:

        if method and url:
            try:
                match method:
                    case 'GET':
                        return requests.get(
                            url=url,
                            **setting_request
                        ).text

                    case 'POST':
                        return requests.post(
                            url=url,
                            **setting_request
                        ).text

                    case 'PUT':
                        return requests.put(
                            url=url,
                            **setting_request
                        ).text

                    case 'DELETE':
                        return requests.delete(
                            url=url,
                            **setting_request
                        ).text

                    case _:
                        raise RunBarsaFlaskKitError(
                            'the method is not defined'
                        )
            except Exception as error:
                raise RequestDataError(str(error)) from error
        else:
            raise MissingDataError(
                'the method or url is not defined'
            )

def to_json(data:str)->dict:
    return json.loads(data)

def to_text(data:dict)->str:
    return json.dumps(data)
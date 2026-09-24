import pytest

from flask_forge import Forge
from flask_forge.exceptions import MissingDataError


def test_create_forge_app():
    app = Forge("test-app")
    assert app.name == "test-app"
    assert app.app.name == "test-app"
    assert app.app.secret_key


def test_forge_requires_name():
    with pytest.raises(MissingDataError):
        Forge()


def test_route_defaults_to_get():
    app = Forge("route-test", rate_limit_func=lambda **_: True)

    @app.route("/")
    def home(request):
        return "ok"

    response = app.app.test_client().get("/")
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "ok"


def test_route_api_defaults_to_get():
    app = Forge("api-test", rate_limit_func=lambda **_: True)

    @app.route_api("/api")
    def api(request):
        return {"ok": True}

    response = app.app.test_client().get("/api")
    assert response.status_code == 200
    assert response.get_json() == {"ok": True}

from flask_forge import Form


def test_form_required_data_success():
    form = Form({"username": "ali"})
    form.check_data("username")
    assert form.is_valid()


def test_form_required_data_failure():
    form = Form({})
    form.check_data("username")
    assert not form.is_valid()
    assert "username" in form.get_errors()["data_errors"]


def test_form_validate():
    form = Form({"username": "ali", "age": 20})
    valid = form.validate(
        minimum={"string": 2, "number": 1},
        maximum={"string": 20, "number": 120},
        types={"username": str, "age": int},
        datas=("username", "age"),
    )
    assert valid

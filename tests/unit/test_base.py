import pytest
import requests
from requests_mock import Mocker
from nocodb_client import Base 
from const import FAKE_HOST, FAKE_TOKEN

def test_base_list_tables():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/base123/info", json={"version": "1"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/base123/", json={"id": "base123"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/base123/tables", json={
            "list": [
                {"id": "tbl1", "title": "Users"},
                {"id": "tbl2", "title": "Orders"}
            ]
        })

        b = Base("base123", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        tables = b.list_tables()

        assert tables == {"Users": "tbl1", "Orders": "tbl2"}




def test_base_init_calls_info_and_base_and_sets_fields():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/base123/info", json={"version": "1"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/base123/", json={"id": "base123"})
        b = Base("base123", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        assert b.base_id == "base123"


def test_base_list_tables_parsing_to_title_id_map():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/base123/info", json={"version": "1"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/base123/", json={"id": "base123"})
        m.get(
            f"{FAKE_HOST}/api/v2/meta/bases/base123/tables",
            json={"list": [{"id": "tbl1", "title": "Users"}, {"id": "tbl2", "title": "Orders"}]},
        )
        b = Base("base123", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        tables = b.list_tables()
        assert tables == {"Users": "tbl1", "Orders": "tbl2"}


def test_base_list_tables_empty_list():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/baseX/info", json={"version": "1"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/baseX/", json={"id": "baseX"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/baseX/tables", json={"list": []})
        b = Base("baseX", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        assert b.list_tables() == {}


def test_base_list_tables_missing_key_raises_keyerror():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/baseY/info", json={"version": "1"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/baseY/", json={"id": "baseY"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/baseY/tables", json={})
        b = Base("baseY", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        with pytest.raises(KeyError):
            _ = b.list_tables()


def test_create_table_posts_json_and_returns_id():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b/info", json={"version": "1"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b/", json={"id": "b"})
        m.post(f"{FAKE_HOST}/api/v2/meta/bases/b/tables", json={"id": "tbl123"})
        b = Base("b", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        new_id = b.create_table("Users", [{"title": "Name", "uidt": "SingleLineText"}], color="#ff0000")
        assert new_id == "tbl123"
        # Validate posted payload
        posted = m.last_request.json()
        assert posted["table_name"] == "Users"
        assert posted["title"] == "Users"
        assert posted["columns"] == [{"title": "Name", "uidt": "SingleLineText"}]
        assert posted["color"] == "#ff0000"
        # Validate auth header present
        assert m.last_request.headers.get("xc-token") == FAKE_TOKEN


def test_create_table_omits_color_and_still_returns_id():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b2/info", json={"version": "1"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b2/", json={"id": "b2"})
        m.post(f"{FAKE_HOST}/api/v2/meta/bases/b2/tables", json={"id": "tblX"})
        b = Base("b2", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        new_id = b.create_table("Orders", [{"title": "Amount", "uidt": "Number"}])
        assert new_id == "tblX"
        posted = m.last_request.json()
        assert "color" not in posted


def test_create_table_returns_none_when_errors_present():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b3/info", json={"version": "1"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b3/", json={"id": "b3"})
        m.post(f"{FAKE_HOST}/api/v2/meta/bases/b3/tables", json={"errors": [{"message": "bad"}]})
        b = Base("b3", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        assert b.create_table("Bad", [{"title": "X", "uidt": "Y"}]) is None


def test_create_table_returns_none_when_msg_present():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b4/info", json={"version": "1"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b4/", json={"id": "b4"})
        m.post(f"{FAKE_HOST}/api/v2/meta/bases/b4/tables", json={"msg": "Invalid token"})
        b = Base("b4", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        assert b.create_table("Bad2", [{"title": "X", "uidt": "Y"}]) is None



def test_get_table_object_not_found_returns_none():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b6/info", json={"version": "1"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b6/", json={"id": "b6"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b6/tables", json={"list": [{"id": "t1", "title": "Users"}]})
        b = Base("b6", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        assert b.get_table_object("Missing") is None


def test_constructor_reuses_parent_nocodb_session_and_verify_flag():
    # Dummy parent to simulate nocodb object reuse
    import requests
    class Parent:
        def __init__(self):
            self.host = FAKE_HOST
            self.auth_token = FAKE_TOKEN
            self.verify = False
            self.session = requests.Session()
            self.session.headers.update({"accept": "application/json", "xc-token": self.auth_token})
            self.session.verify = self.verify

    parent = Parent()
    with Mocker() as m:
        # Both calls should go through the reused session
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/reuse/info", json={"version": "1"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/reuse/", json={"id": "reuse"})
        b = Base("reuse", nocodb=parent)
        assert b.session is parent.session
        assert b.session.verify is False
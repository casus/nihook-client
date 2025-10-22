from urllib.parse import parse_qs
import pytest
import requests
from requests_mock import Mocker
from nocodb_client import Nocodb  # adjust import path

from const import FAKE_HOST, FAKE_TOKEN

def test_list_bases_parsing():
    nc = Nocodb(FAKE_HOST, FAKE_TOKEN)
    with Mocker() as m:
        m.get(nc._url(""), json={
            "list": [
                {"id": "base1", "title": "Test Base 1"},
                {"id": "base2", "title": "Test Base 2"}
            ]
        })
        bases = nc.list_bases()
        assert bases == {"base1": "Test Base 1", "base2": "Test Base 2"}

def test_create_base_invalid_token():
    nc = Nocodb(FAKE_HOST, "badtoken")
    with Mocker() as m:
        m.post(nc._url(""), json={"msg": "Invalid token"})
        with pytest.raises(Exception, match="Invalid token"):
            nc.create_base("MyBase")


def test_session_verify_flag_true_by_default():
    nc = Nocodb(FAKE_HOST, FAKE_TOKEN)
    assert nc.session.verify is True


def test_session_verify_flag_false_when_disabled():
    nc = Nocodb(FAKE_HOST, FAKE_TOKEN, verify=False)
    assert nc.session.verify is False


def test_list_bases_empty():
    nc = Nocodb(FAKE_HOST, FAKE_TOKEN)
    with Mocker() as m:
        m.get(nc._url(""), json={"list": []})
        bases = nc.list_bases()
        assert bases == {}


def test_list_bases_missing_key_raises_keyerror():
    nc = Nocodb(FAKE_HOST, FAKE_TOKEN)
    with Mocker() as m:
        # Intentionally omit "list" to document current behavior
        m.get(nc._url(""), json={})
        with pytest.raises(KeyError):
            nc.list_bases()


def test_list_bases_ignores_extra_fields():
    nc = Nocodb(FAKE_HOST, FAKE_TOKEN)
    with Mocker() as m:
        m.get(nc._url(""), json={"list": [{"id": "b1", "title": "T1", "extra": "x"}], "other": "y"})
        bases = nc.list_bases()
        assert bases == {"b1": "T1"}


def test_create_base_with_all_fields_form_encoded_and_headers():
    nc = Nocodb(FAKE_HOST, FAKE_TOKEN)

    class DummyEnum:
        name = "PG"

    with Mocker() as m:
        m.post(nc._url(""), json={"id": "created", "title": "T"})
        res = nc.create_base("T", color="#ff0000", description="desc", base_type=DummyEnum)
        assert res["id"] == "created"

        # Inspect the request body and headers
        req = m.last_request
        # Body is form-encoded because create_base uses data=
        body = parse_qs(req.text or "")
        assert body["title"] == ["T"]
        assert body["color"] == ["#ff0000"]
        assert body["description"] == ["desc"]
        assert body["type"] == ["PG"]
        # Session headers should include xc-token
        assert req.headers.get("xc-token") == FAKE_TOKEN


def test_create_base_omits_none_fields():
    nc = Nocodb(FAKE_HOST, FAKE_TOKEN)
    with Mocker() as m:
        m.post(nc._url(""), json={"id": "only-title", "title": "JustTitle"})
        res = nc.create_base("JustTitle")
        assert res["id"] == "only-title"

        req = m.last_request
        body = parse_qs(req.text or "")
        assert body == {"title": ["JustTitle"]}


def test_delete_base_calls_correct_url_and_headers():
    nc = Nocodb(FAKE_HOST, FAKE_TOKEN)
    with Mocker() as m:
        m.delete(nc._url("base123"), json={"ok": True})
        res = nc.delete_base("base123")
        assert res == {"ok": True}
        # Ensure headers carry token when using requests.delete
        assert m.last_request.headers.get("xc-token") == FAKE_TOKEN


def test_get_base_object_not_found_returns_none():
    nc = Nocodb(FAKE_HOST, FAKE_TOKEN)
    with Mocker() as m:
        m.get(nc._url(""), json={"list": [{"id": "b1", "title": "Other"}]})
        obj = nc.get_base_object("Missing")
        assert obj is None











import pytest
import requests
from requests_mock import Mocker
from nihook_client import Table 
from const import FAKE_HOST, FAKE_TOKEN



def test_table_insert():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"count": 0})
        m.post(f"{FAKE_HOST}/api/v2/tables/tbl1/records", json={"id": 42})
        t = Table("tbl1", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        res = t.insert({"field": "value"})
        assert res.json() == {"id": 42}

def test_table_read_table_record():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/42", json={"id": 42, "field": "value"})
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"count": 0})
        t = Table("tbl1", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        res = t.read_table_record(42)
        assert res.get("id") == 42
        assert res.get("field") == "value"


def test_table_init_success_calls_count():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"count": 3})
        t = Table("tbl1", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        # constructor asserts 'count' in response; reaching here implies success
        assert t.tableid == "tbl1"
        assert t.count().get("count") == 3


def test_table_init_fails_when_msg_present():
    with Mocker() as m:
        # Constructor asserts that 'msg' is not in the count response
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"msg": "error"})
        with pytest.raises(AssertionError):
            Table("tbl1", host=FAKE_HOST, auth_token=FAKE_TOKEN)


def test_url_builders_meta_and_data():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"count": 0})
        t = Table("tbl1", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        assert t._meta_url("") == f"{FAKE_HOST}/api/v2/meta/tables/tbl1/"
        assert t._meta_url("columns") == f"{FAKE_HOST}/api/v2/meta/tables/tbl1/columns"
        assert t._data_url("records") == f"{FAKE_HOST}/api/v2/tables/tbl1/records"


def test_read_table_fetches_meta():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"count": 0})
        m.get(f"{FAKE_HOST}/api/v2/meta/tables/tbl1/", json={"id": "tbl1", "base_id": "base1"})
        t = Table("tbl1", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        res = t.read_table()
        assert res == {"id": "tbl1", "base_id": "base1"}


def test_insert_posts_json_and_headers():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"count": 0})
        m.post(f"{FAKE_HOST}/api/v2/tables/tbl1/records", json={"id": 42})
        t = Table("tbl1", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        resp = t.insert({"field": "value"})
        assert resp.json() == {"id": 42}
        assert m.last_request.headers.get("xc-token") == FAKE_TOKEN




def test_read_table_record_by_pk():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"count": 0})
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/42", json={"id": 42, "field": "v"})
        t = Table("tbl1", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        rec = t.read_table_record(42)
        assert rec == {"id": 42, "field": "v"}


def test_count_with_where_param_included():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"count": 0})
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"count": 2})
        t = Table("tbl1", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        res = t.count(where="(field,eq,value)")
        assert res == {"count": 2}
        assert m.last_request.qs.get("where") == ["(field,eq,value)"]


def test_list_includes_expected_query_params_and_excludes_defaults():
    with Mocker() as m:
        # constructor count
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"count": 0})
        # list call
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records", json={"list": [], "pageInfo": {"pageNumber": 1, "isLastPage": True}})
        t = Table("tbl1", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        res = t.list(fields="a,b", sort="-a", where="(a,gt,0)", offset=10, limit=5)
        assert res["list"] == []
        qs = m.last_request.qs
        assert qs["fields"] == ["a,b"]
        assert qs["sort"] == ["-a"]
        assert qs["where"] == ["(a,gt,0)"]
        assert qs["offset"] == ["10"]
        assert qs["limit"] == ["5"]



def test_list_all_records_paginates_until_last_page_and_merges_lists():
    with Mocker() as m:
        # count is called twice: constructor and list_all_records()
        m.get(
            f"{FAKE_HOST}/api/v2/tables/tbl1/records/count",
            [
                {"json": {"count": 0}},  # constructor
                {"json": {"count": 3}},  # list_all_records -> limit
            ],
        )
        # records will be fetched twice: first page, then page=2
        m.get(
            f"{FAKE_HOST}/api/v2/tables/tbl1/records",
            [
                {"json": {"list": [{"id": 1}], "pageInfo": {"pageNumber": 1, "isLastPage": False}}},
                {"json": {"list": [{"id": 2}, {"id": 3}], "pageInfo": {"pageNumber": 2, "isLastPage": True}}},
            ],
        )

        t = Table("tbl1", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        res = t.list_all_records()
        ids = [r["id"] for r in res["list"]]
        assert ids == [1, 2, 3]



def test_delete_without_list_and_with_list_variants():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl2/records/count", json={"count": 0})
        m.delete(f"{FAKE_HOST}/api/v2/tables/tbl2/records", json={"ok": True})
        t = Table("tbl2", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        res = t.delete()
        assert res.get("ok") == True
        assert m.last_request.method == "DELETE"

        # with list body
        m.delete(f"{FAKE_HOST}/api/v2/tables/tbl2/records", json={"deleted": 2})
        res2 = t.delete(list={"ids": [1, 2]})
        assert res2.get("deleted") == 2


def test_create_column_merges_extra_options_and_posts_json():
    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl3/records/count", json={"count": 0})
        m.post(f"{FAKE_HOST}/api/v2/meta/tables/tbl3/columns", json={"id": "col1"})
        t = Table("tbl3", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        res = t.create_column("Status", "SingleLineText", {"default": "New"})
        assert res == {"id": "col1"}
        assert m.last_request.json() == {"title": "Status", "uidt": "SingleLineText", "default": "New"}


def test_link_records_single_and_multiple_with_url_encoding():
    # Prepare metadata used by link/unlink methods
    meta = {
        "id": "tbl1",
        "base_id": "base1",
        "columnsById": {
            "lk1": {"colOptions": {"type": "mm"}}
        }
    }
    with Mocker() as m:
        # constructor count + read_table for link
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"count": 0})
        m.get(f"{FAKE_HOST}/api/v2/meta/tables/tbl1/", json=meta)

        # Single value
        rid = "A/B C"
        encoded_rid = "A%2FB%20C"
        single_url = f"{FAKE_HOST}/api/v1/db/data/noco/base1/tbl1/{encoded_rid}/mm/lk1/99"
        m.post(single_url, json={"ok": True})
        t = Table("tbl1", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        res_single = t.link_records("lk1", rid, refRowPKValue=99)
        assert res_single == {"ok": True}
        assert m.last_request.url == single_url

        # Multiple values
        m.get(f"{FAKE_HOST}/api/v2/meta/tables/tbl1/", json=meta)  # read_table again
        multi_urls = [
            f"{FAKE_HOST}/api/v1/db/data/noco/base1/tbl1/{encoded_rid}/mm/lk1/1",
            f"{FAKE_HOST}/api/v1/db/data/noco/base1/tbl1/{encoded_rid}/mm/lk1/2",
        ]
        for u in multi_urls:
            m.post(u, json={"ok": True})
        res_multi = t.link_records("lk1", rid, refRowPKValues=[1, 2])
        assert res_multi == {"ok": True}
        assert m.last_request.url == multi_urls[-1]


def test_unlink_records_single_and_multiple_with_url_encoding():
    meta = {
        "id": "tbl1",
        "base_id": "base1",
        "columnsById": {
            "lk1": {"colOptions": {"type": "mm"}}
        }
    }
    with Mocker() as m:
        # constructor count + read_table for unlink
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"count": 0})
        m.get(f"{FAKE_HOST}/api/v2/meta/tables/tbl1/", json=meta)

        rid = "A/B C"
        encoded_rid = "A%2FB%20C"
        single_url = f"{FAKE_HOST}/api/v1/db/data/noco/base1/tbl1/{encoded_rid}/mm/lk1/99"
        m.delete(single_url, json={"ok": True})
        t = Table("tbl1", host=FAKE_HOST, auth_token=FAKE_TOKEN)
        res_single = t.unlink_records("lk1", rid, refRowPKValue=99)
        assert res_single == {"ok": True}
        assert m.last_request.url == single_url

        # Multiple values
        m.get(f"{FAKE_HOST}/api/v2/meta/tables/tbl1/", json=meta)  # read_table again
        multi_urls = [
            f"{FAKE_HOST}/api/v1/db/data/noco/base1/tbl1/{encoded_rid}/mm/lk1/1",
            f"{FAKE_HOST}/api/v1/db/data/noco/base1/tbl1/{encoded_rid}/mm/lk1/2",
        ]
        for u in multi_urls:
            m.delete(u, json={"ok": True})
        res_multi = t.unlink_records("lk1", rid, refRowPKValues=[1, 2])
        assert res_multi == {"ok": True}
        assert m.last_request.url == multi_urls[-1]


def test_list_linked_records_fetches_all_when_total_rows_exceeds_first_list():
    with Mocker() as m:
        # constructor count
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"count": 0})
        t = Table("tbl1", host=FAKE_HOST, auth_token=FAKE_TOKEN)

        # First call returns fewer items than totalRows
        first_url = f"{FAKE_HOST}/api/v2/tables/tbl1/links/lk1/records/7"
        second_url = f"{FAKE_HOST}/api/v2/tables/tbl1/links/lk1/records/7?limit=3"
        m.get(first_url, json={"list": [{"id": 1}, {"id": 2}], "pageInfo": {"totalRows": 3}})
        m.get(second_url, json={"list": [{"id": 1}, {"id": 2}, {"id": 3}], "pageInfo": {"totalRows": 3}})
        res = t.list_linked_records("lk1", 7)
        ids = [r["id"] for r in res["list"]]
        assert ids == [1, 2, 3]


def test_constructor_reuses_base_session_and_verify_flag():
    class DummyBase:
        def __init__(self):
            self.host = FAKE_HOST
            self.auth_token = FAKE_TOKEN
            self.verify = False
            import requests
            self.session = requests.Session()
            self.session.headers.update({"accept": "application/json", "xc-token": self.auth_token})
            self.session.verify = self.verify

    with Mocker() as m:
        # The count call will use the provided base.session
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl1/records/count", json={"count": 1})
        base = DummyBase()
        t = Table("tbl1", base=base)
        assert t.session is base.session
        assert t.session.verify is False
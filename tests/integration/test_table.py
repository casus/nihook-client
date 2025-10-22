import os
import pytest
from nocodb_client import Base, Table



ID_COLUMN = {
    "ai": 1,
    "cdf": None,
    "ck": 0,
    "clen": None,
    "column_name": "id",
    "ct": "int(11)",
    "dt": "integer",
    "dtx": "integer",
    "dtxp": "",
    "dtxs": "",
    "np": None,
    "nrqd": 0,
    "ns": 0,
    "pk": 1,
    "rqd": 1,
    "title": "Id",
    "uicn": "",
    "uidt": "ID",
    "uip": "",
    "un": 0
}

@pytest.fixture(scope="module")
def base(nocodb):
    base_title = "IntegrationTestTableBase"
    res = nocodb.create_base(title=base_title)
    base_id = res["id"]
    base_obj = Base(base_id, nocodb=nocodb)
    yield base_obj
    nocodb.delete_base(base_id)

@pytest.fixture(scope="module")
def table(base):
    table_name = "TestTable"
    columns = [
        {"title": "Name", "type": "text"},
        {"title": "Age", "type": "number"},
        ID_COLUMN
    ]
    table_id = base.create_table(name=table_name, columns=columns)
    table_obj = Table(table_id, base=base)
    yield table_obj
    # Cleanup: delete all records and table if needed

def test_read_table(table):
    meta = table.read_table()
    assert isinstance(meta, dict)
    assert "id" in meta

def test_insert_and_list(table):
    data = {"Name": "Alice", "Age": 30}
    res = table.insert(data)
    assert res.status_code == 200
    record = res.json()
    assert "Id" in record
    records = table.list()
    assert "list" in records
    print(records)
    assert any(r.get("Name") == "Alice" for r in records["list"])

def test_count(table):
    count_res = table.count()
    assert isinstance(count_res, dict)
    assert "count" in count_res

def test_read_table_record(table):
    data = {"Name": "Bob", "Age": 25}
    res = table.insert(data)
    record = res.json()
    pk = record["Id"]
    rec = table.read_table_record(pk)
    assert rec.get("Name") == "Bob"
    assert int(rec.get("Age")) == 25

def test_update(table):
    data = {"Name": "Charlie", "Age": 40}
    res = table.insert(data)
    record = res.json()
    pk = int(record["Id"])
    update_res = table.update({**data, "Id": pk, "Age": 41})
    assert "error" not in update_res
    rec = table.read_table_record(pk)
    assert int(rec.get("Age")) == 41

def test_delete(table):
    data = {"Name": "Dave", "Age": 50}
    res = table.insert(data)
    record = res.json()
    pk = int(record["Id"])
    del_res = table.delete({"Id": pk})
    assert "success" in del_res or "error" not in del_res

def test_list_all_records(table):
    res = table.list_all_records()
    assert "list" in res
    assert isinstance(res["list"], list)

def test_create_column(table):
    col_res = table.create_column("Extra", "Text")
    assert "Id" in col_res or "error" not in col_res
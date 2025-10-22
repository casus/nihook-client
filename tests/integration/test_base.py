import pytest
from nocodb_client import Base


@pytest.fixture(scope="module")
def base(nocodb):
    # Create a base for testing
    base_title = "IntegrationTestBase"
    res = nocodb.create_base(title=base_title)
    base_id = res["id"]
    base_obj = Base(base_id, nocodb=nocodb)
    yield base_obj
    nocodb.delete_base(base_id)

def test_get_base_info(base):
    info = base.get_base_info()
    assert isinstance(info, dict)
    assert "RootDB" in info
    assert "PackageVersion" in info

def test_get_base(base):
    meta = base.get_base()
    assert isinstance(meta, dict)
    assert "id" in meta

def test_list_tables_empty(base):
    tables = base.list_tables()
    assert isinstance(tables, dict)
    assert len(tables) == 0

def test_create_and_get_table(base):
    table_name = "TestTable"
    columns = [
        {"title": "Name", "type": "text"},
        {"title": "Age", "type": "number"}
    ]
    table_id = base.create_table(name=table_name, columns=columns)
    assert table_id is not None

    tables = base.list_tables()
    assert table_name in tables
    assert tables[table_name] == table_id

    table_obj = base.get_table_object(table_name)
    assert table_obj is not None
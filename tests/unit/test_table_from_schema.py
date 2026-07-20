import pytest
from requests_mock import Mocker

from nihook_client import NocodbError, ReservedColumnError, SchemaError, UnsupportedTypeError
from nihook_client.table_from_schema import (
    create_new_table_from_schema,
    schema_to_nocodb_definition,
)
from const import FAKE_HOST, FAKE_TOKEN


def test_schema_to_nocodb_definition_prepends_special_columns():
    schema = {"properties": {"my key": {"type": "string"}}}
    columns = schema_to_nocodb_definition("base1", "Table", schema)

    titles = [c['title'] for c in columns]
    assert titles == ["URL", "status", "branch", "my_key"]


def test_missing_type_raises_schema_error_naming_the_key():
    schema = {"properties": {"broken": {"description": "no type here"}}}

    with pytest.raises(SchemaError, match="broken"):
        schema_to_nocodb_definition("base1", "Table", schema)


@pytest.mark.parametrize("reserved", ["URL", "status", "branch"])
def test_reserved_key_raises_reserved_column_error(reserved):
    schema = {"properties": {reserved: {"type": "string"}}}

    with pytest.raises(ReservedColumnError) as excinfo:
        schema_to_nocodb_definition("base1", "Table", schema)

    assert excinfo.value.column_name == reserved
    assert reserved in str(excinfo.value)


def test_unknown_type_raises_unsupported_type_error():
    schema = {"properties": {"weird": {"type": "complex"}}}

    with pytest.raises(UnsupportedTypeError) as excinfo:
        schema_to_nocodb_definition("base1", "Table", schema)

    assert excinfo.value.key == "weird"
    assert excinfo.value.type_name == "complex"


def test_create_new_table_from_schema_reports_nocodb_message():
    schema = {"properties": {"name": {"type": "string"}}}

    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b1/info", json={"version": "1"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b1/", json={"id": "b1"})
        m.post(f"{FAKE_HOST}/api/v2/meta/bases/b1/tables",
               json={"msg": "Duplicate table name", "error": "BAD_REQUEST"})

        with pytest.raises(NocodbError, match="Duplicate table name") as excinfo:
            create_new_table_from_schema(FAKE_HOST, FAKE_TOKEN, True, "b1", "Table", schema)

        assert excinfo.value.response['error'] == "BAD_REQUEST"


def test_create_new_table_from_schema_returns_table_id():
    schema = {"properties": {"name": {"type": "string"}}}

    with Mocker() as m:
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b1/info", json={"version": "1"})
        m.get(f"{FAKE_HOST}/api/v2/meta/bases/b1/", json={"id": "b1"})
        m.post(f"{FAKE_HOST}/api/v2/meta/bases/b1/tables", json={"id": "tbl9"})
        m.get(f"{FAKE_HOST}/api/v2/tables/tbl9/records/count", json={"count": 0})
        m.get(f"{FAKE_HOST}/api/v2/meta/tables/tbl9/", json={"id": "tbl9", "columns": []})

        table_id = create_new_table_from_schema(FAKE_HOST, FAKE_TOKEN, True, "b1", "Table", schema)

    assert table_id == "tbl9"

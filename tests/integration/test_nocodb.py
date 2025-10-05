import pytest

def test_list_bases(nocodb):
    bases = nocodb.list_bases()
    assert isinstance(bases, dict)

def test_create_and_delete_base(nocodb):
    # Create a new base
    base_title = "TestBase"
    res = nocodb.create_base(title=base_title)
    assert "id" in res
    base_id = res["id"]

    # List bases and check the new base exists
    bases = nocodb.list_bases()
    assert base_id in bases
    assert bases[base_id] == base_title

    # Delete the base
    del_res = nocodb.delete_base(base_id)
    assert del_res.get("success") or del_res.get("msg") == "Base deleted successfully"

def test_get_base_object(nocodb):
    # Create a base for testing
    base_title = "TestBaseObj"
    res = nocodb.create_base(title=base_title)
    base_id = res["id"]

    base_obj = nocodb.get_base_object(base_title)
    assert base_obj is not None
    assert hasattr(base_obj, "base_id")
    assert base_obj.base_id == base_id

    # Cleanup
    nocodb.delete_base(base_id)
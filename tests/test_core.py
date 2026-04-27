import pytest
from tool_call_contracts import validate_tool_call, assert_tool_call, ContractError


CONTRACT = {
    "name": "search",
    "arguments": {
        "query": {"type": "string", "required": True},
        "limit": {"type": "int", "enum": [10, 25, 50]},
        "id": {"type": "string", "pattern": r"^[a-z]{3}-\d+$"},
    },
}


def test_valid_call_passes():
    res = validate_tool_call(
        {"name": "search", "arguments": {"query": "python"}},
        CONTRACT,
    )
    assert res.valid is True


def test_wrong_name_fails():
    res = validate_tool_call({"name": "fetch", "arguments": {"query": "x"}}, CONTRACT)
    assert res.valid is False
    assert any("expected tool search" in e for e in res.errors)


def test_missing_required_fails():
    res = validate_tool_call({"name": "search", "arguments": {}}, CONTRACT)
    assert res.valid is False
    assert any("query is required" in e for e in res.errors)


def test_wrong_type_fails():
    res = validate_tool_call(
        {"name": "search", "arguments": {"query": 42}},
        CONTRACT,
    )
    assert res.valid is False
    assert any("query must be string" in e for e in res.errors)


def test_enum_violation_fails():
    res = validate_tool_call(
        {"name": "search", "arguments": {"query": "x", "limit": 99}},
        CONTRACT,
    )
    assert res.valid is False
    assert any("limit must be one of" in e for e in res.errors)


def test_pattern_violation_fails():
    res = validate_tool_call(
        {"name": "search", "arguments": {"query": "x", "id": "BAD"}},
        CONTRACT,
    )
    assert res.valid is False
    assert any("id does not match" in e for e in res.errors)


def test_pattern_match_passes():
    res = validate_tool_call(
        {"name": "search", "arguments": {"query": "x", "id": "abc-123"}},
        CONTRACT,
    )
    assert res.valid is True


def test_assert_raises_on_invalid():
    with pytest.raises(ContractError) as exc:
        assert_tool_call({"name": "fetch", "arguments": {}}, CONTRACT)
    assert exc.value.errors


def test_assert_returns_call_on_valid():
    call = {"name": "search", "arguments": {"query": "x"}}
    assert assert_tool_call(call, CONTRACT) is call

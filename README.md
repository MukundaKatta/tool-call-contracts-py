# tool-call-contracts-py

Validate LLM tool-call payloads with small JSON-like contracts. Pure Python, zero deps. Python port of [`@mukundakatta/tool-call-contracts`](https://www.npmjs.com/package/@mukundakatta/tool-call-contracts).

```bash
pip install tool-call-contracts-py
```

```python
from tool_call_contracts import validate_tool_call, assert_tool_call, ContractError

contract = {
    "name": "search",
    "arguments": {
        "query": {"type": "string", "required": True},
        "limit": {"type": "int", "enum": [10, 25, 50]},
    },
}

res = validate_tool_call({"name": "search", "arguments": {"query": "python"}}, contract)
# ValidationResult(valid=True, errors=[])

assert_tool_call({"name": "fetch", "arguments": {}}, contract)
# raises ContractError: expected tool search, got fetch; query is required
```

Supported rule fields per argument: `type` (`string`/`int`/`float`/`bool`/`list`/`dict`), `required`, `enum`, `pattern` (regex for strings).

## License

MIT

# NocoDB Client

A simple, Python-based wrapper and CLI for the [NocoDB API v2](https://nocodb.com), allowing you to interact with your NocoDB instances programmatically.

## Features

- **Manage Bases:** List, create, and delete bases.
- **Manage Tables:** Create tables from JSON schema, list tables, view table metadata.
- **Data Operations:** Insert, update, delete, and read records.
- **CLI Tools:** Scripts to automate table creation and data ingestion.

## Installation

### From Source

Clone the repository and install using `pip`:

```bash
git clone <repository-url> nihook-client
cd nihook-client
pip install .
```

### For Development

To install development dependencies (like `pytest` and `requests-mock`) along with the package:

```bash
pip install ".[dev]"
```

## Configuration

The client relies on environment variables for connection details. You can set them in your shell or use a `.env` file manager.

| Variable | Description | Default |
|----------|-------------|---------|
| `NOCODB_HOST` | URL of your NocoDB instance | `http://localhost` |
| `NOCODB_TOKEN` | Your NocoDB API Token | `none` |
| `NOCODB_SSL_CERT`| `True`/`False` to enable/disable verification | `True` |

Example:
```bash
export NOCODB_HOST="https://my-nocodb.example.com"
export NOCODB_TOKEN="your-api-token-here"
```

## Usage

### As a Python Library

```python
import os
from nihook_client import Nocodb

# Initialize client
client = Nocodb(
    host=os.getenv("NOCODB_HOST"),
    auth_token=os.getenv("NOCODB_TOKEN")
)

# List all bases
bases = client.list_bases()
print(bases)

# Get a specific base
base = client.get_base_object("My Project")

if base:
    # List tables in the base
    tables = base.list_tables()
    print(tables)
    
    # Get a specific table
    table = base.get_table_object("Employees")
    
    # Read records
    if table:
        records = table.list_records()
        for record in records['list']:
            print(record)
```

### CLI Command

The package installs a `nihook-client` command for checking versions and basic interaction.

```bash
nihook-client -v
```

### Utility Scripts

The package includes several distinct modules that can be run to perform automation tasks.

**1. Create Table from Schema**
Creates a new NocoDB table based on a JSON schema file.

```bash
python3 -m nihook_client.table_from_schema my_schema.json --base <base_id> --name "New Table"
```

**2. Enter Dataset**
Imports data from a JSON file into an existing table.

```bash
python3 -m nihook_client.enter_dataset --file DATASET.json --base <base_id> --table "TableName"
```

## Development

1.  Install in editable mode with dev dependencies:
    ```bash
    pip install -e ".[dev]"
    ```
2.  Run tests:
    ```bash
    pytest
    ```

## Requirements

- Python 3.12+
- `requests`
- `pandas`
- `python-dateutil`
- `jsonschema`

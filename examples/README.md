# CAssIffier Examples

This directory contains example scripts demonstrating various use cases of CAssIffier.

## Available Examples

### 1. basic_usage.py
Demonstrates the most common use case: organizing audio samples from a directory.

```bash
python examples/basic_usage.py /path/to/samples /path/to/output
```

### 2. custom_config.py
Shows how to create and use custom configuration with different settings.

```bash
python examples/custom_config.py
```

This creates a `my_config.json` file that you can use with:

```bash
cassiffier /path/to/samples -o output -c my_config.json
```

### 3. inspect_database.py
Query and inspect the CAssIffier database to see processed files and classifications.

```bash
python examples/inspect_database.py cassiffier.db
```

## Using the Examples

All examples assume you've installed CAssIffier or have it in your Python path. If running from the repository root:

```bash
# Make scripts executable
chmod +x examples/*.py

# Run examples
python examples/basic_usage.py /path/to/samples output
```

## Creating Your Own Scripts

You can use these examples as templates for your own automation scripts. The basic pattern is:

1. Import required modules from `cassiffier`
2. Initialize configuration
3. Create component instances (Database, Scanner, etc.)
4. Process files
5. Clean up (close database)

See `basic_usage.py` for a complete example.

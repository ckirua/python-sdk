# SDK Examples

This directory contains examples demonstrating how to use various components of the Python SDK.

## Running Examples

### Prerequisites
- Python 3.7+
- SDK installed (`make install` from the root directory)
- Virtual environment activated (if using one)

### CNet Examples

#### PGConnectionParameters Example
```bash
cd examples/cnet
python pg_connection.py
```

This example demonstrates:
- Creating PGConnectionParameters objects
- Building PostgreSQL connection URLs
- URL caching optimization
- Different driver configurations

#### Other CNet Examples
```bash
# HTTP client example
python http.py

# ZMQ examples
python zmq_pub_sub.py
python zmq_push_pull.py
python zmq_dealer_router.py
python zmq_task_processor.py
```

### CUUID Examples
```bash
cd examples/cuuid
# Run CUUID examples
```

### CFS Examples
```bash
cd examples/cfs
# Run CFS examples
```

### CTime Examples
```bash
cd examples/ctime
# Run CTime examples
```

## Notes

- Examples assume the SDK is properly installed and importable
- Some examples may require additional dependencies (check individual files)
- Run from the examples directory or ensure proper Python path setup

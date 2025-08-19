#!/usr/bin/env python3
"""
Example demonstrating reading and writing TOML files using the sdk.file_io.toml extension.
"""
import os
from pathlib import Path

from sdk.cfs import read_json, write_json


def print_dict_keys(d, prefix=""):
    """Recursively print dictionary keys with proper indentation."""
    for key, value in d.items():
        if isinstance(value, dict):
            print(f"{prefix}- {key}:")
            print_dict_keys(value, prefix + "  ")
        else:
            print(f"{prefix}- {key}: {value}")


def main():
    # Get paths
    input_path = Path(__file__).parent / "data" / "example.json"
    output_path = input_path.parent / "example_out.json"

    # Read the JSON file
    print(f"\nReading JSON file: {input_path}")
    data = read_json(str(input_path))

    # Display the structure
    print("\nJSON file structure:")
    print_dict_keys(data)

    # Write to new file
    print(f"\nWriting JSON file: {output_path}")
    write_json(str(output_path), data)
    print("Done!")

    # Read and print the output file to verify
    print("\nVerifying output file contents:")
    with open(output_path, "r") as f:
        print(f.read())

    # Delete the output file after verification
    os.remove(output_path)
    print(f"\nDeleted temporary file: {output_path}")


if __name__ == "__main__":
    main()

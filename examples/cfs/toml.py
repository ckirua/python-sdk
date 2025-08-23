#!/usr/bin/env python3
"""
Example demonstrating reading and writing TOML files using the sdk.file_io.toml extension.
"""
import os
from pathlib import Path

from sdk.cfs import read_toml, write_toml


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
    input_path = Path(__file__).parent / "data" / "example.toml"
    output_path = input_path.parent / "example_out.toml"

    # Read the TOML file
    print(f"\nReading TOML file: {input_path}")
    data = read_toml(str(input_path))

    # Display the structure
    print("\nTOML file structure:")
    print_dict_keys(data)

    # Write to new file
    print(f"\nWriting TOML file: {output_path}")
    write_toml(str(output_path), data)
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
from pathlib import Path
from sdk.cfs import extract_zip

if __name__ == "__main__":
    # Path to the sample zip file
    input_path = Path(__file__).parent / "data" / "example.zip"

    # Read the zip file as bytes
    with open(input_path, "rb") as f:
        zip_bytes = f.read()

    # Use extract_zip to extract files from the zip archive
    files = extract_zip(zip_bytes)

    print(f"Files in {input_path}:")
    for file in files:
        print(f"- {file.filename} ({len(file.data)} bytes)")

        # Show the raw list of ints (first 100)
        print(f"  [file.data] Raw ints (first 100): {file.data[:100]}")

        # Preview using file.data (which is a list of ints, not bytes)
        preview_data = file.data[:100]
        try:
            # Convert list of ints to bytes for preview
            preview_data_bytes = bytes(preview_data)
            preview_data_text = preview_data_bytes.decode('utf-8', errors='replace')
            print(f"  [file.data] Preview (ascii): {preview_data_text!r}")
        except Exception:
            preview_data_hex = bytes(preview_data).hex()[:50] + "..." if len(bytes(preview_data).hex()) > 50 else bytes(preview_data).hex()
            print(f"  [file.data] Preview (hex): {preview_data_hex}")

        # Preview using get_data_as_bytes (guaranteed Python bytes)
        file_bytes = file.get_data_as_bytes()
        preview_bytes = file_bytes[:100]
        try:
            preview_bytes_text = preview_bytes.decode('utf-8', errors='replace')
            print(f"  [get_data_as_bytes] Preview (ascii): {preview_bytes_text!r}")
        except Exception:
            preview_bytes_hex = preview_bytes.hex()[:50] + "..." if len(preview_bytes.hex()) > 50 else preview_bytes.hex()
            print(f"  [get_data_as_bytes] Preview (hex): {preview_bytes_hex}")
from sdk.cfs import ListFileReader, ListMMAPFileReader, create_list_reader
from pathlib import Path

if __name__ == "__main__":
    def process_chunk(chunk: list):
        print(chunk)

    data_dir = Path(__file__).parent / "data"

    # Basic usage with a small file
    reader = ListFileReader(str(data_dir / "example.shortlist"))
    lines = reader.read()

    # High-performance for medium-sized files
    reader = ListMMAPFileReader(str(data_dir / "example.mediumlist"))
    lines = reader.read()

    # Auto-selection based on file size (try with mediumlist)
    reader = create_list_reader(str(data_dir / "example.mediumlist"), reader_type="auto")
    lines = reader.read()

    # Advanced options on shortlist
    reader = ListFileReader(
        str(data_dir / "example.shortlist"),
        strip_lines=True,
        skip_empty_lines=True,
        comment_prefix="#",
        encoding="utf-8",
        max_line_length=4096
    )
    print(reader.read()[:5])
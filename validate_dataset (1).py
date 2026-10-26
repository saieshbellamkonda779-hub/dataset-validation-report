validate_dataset.py
import argparse
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", help="Path to the dataset CSV")
    parser.add_argument("--chunksize", type=int, default=250_000)
    args = parser.parse_args()

    total_rows = 0
    missing = {}
    dtypes = {}
    minima = {}
    maxima = {}
    chunk_local_duplicates = 0
    columns = None

    for chunk in pd.read_csv(args.csv_path, chunksize=args.chunksize):
        total_rows += len(chunk)
        if columns is None:
            columns = list(chunk.columns)
        if list(chunk.columns) != columns:
            raise ValueError("Column names/order changed between chunks")

        for col in chunk.columns:
            missing[col] = missing.get(col, 0) + int(chunk[col].isna().sum())
            dtypes.setdefault(col, str(chunk[col].dtype))
            if pd.api.types.is_numeric_dtype(chunk[col]):
                lo, hi = chunk[col].min(), chunk[col].max()
                minima[col] = min(minima.get(col, lo), lo)
                maxima[col] = max(maxima.get(col, hi), hi)

        # Counts exact duplicates inside each chunk only; duplicates across
        # chunk boundaries are not detected by this memory-conscious check.
        chunk_local_duplicates += int(chunk.duplicated().sum())

    print(f"Rows: {total_rows:,}")
    print(f"Columns ({len(columns or [])}): {columns}")
    print("\nData types:")
    for col, dtype in dtypes.items():
        print(f"  {col}: {dtype}")
    print("\nMissing values:")
    for col, count in missing.items():
        print(f"  {col}: {count:,}")
    print(f"\nExact duplicate rows within chunks: {chunk_local_duplicates:,}")
    print("Note: duplicates spanning different chunks are not detected.")
    print("\nNumeric ranges:")
    for col in minima:
        print(f"  {col}: min={minima[col]}, max={maxima[col]}")


if __name__ == "__main__":
    main()

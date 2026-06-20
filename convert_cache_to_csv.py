import json
import csv
import os
import argparse


def convert_json_to_csv(json_file, csv_file, columns_to_keep=None):
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found.")
        return

    print(f"Loading {json_file}...")
    with open(json_file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

    if not data:
        print("JSON file is empty.")
        return

    print("Identifying structure and fields...")
    all_keys = set()
    rows_to_write = []

    # Check first key to determine format
    first_key = next(iter(data))
    first_val = data[first_key]

    # Format 1: followers_cache.json structure (target_user -> { "data": [...] })
    if (
        isinstance(first_val, dict)
        and "data" in first_val
        and isinstance(first_val["data"], list)
    ):
        print("Detected followers_cache format.")
        for target_user, content in data.items():
            followers = content.get("data", [])
            for follower in followers:
                row = {"target_user": target_user}
                row.update(follower)
                rows_to_write.append(row)
                all_keys.update(row.keys())

    # Format 2: users_cache.json structure (username -> { "login": ..., "id": ... })
    else:
        print("Detected users_cache format.")
        for username, details in data.items():
            if isinstance(details, dict):
                row = details
                rows_to_write.append(row)
                all_keys.update(row.keys())
            else:
                print(f"Warning: Unexpected value for key {username}, skipping.")

    if not rows_to_write:
        print("No valid data found to write.")
        return

    # Filter columns if requested
    if columns_to_keep:
        # Filter headers to only those that exist in the data and are requested
        headers = [h for h in columns_to_keep if h in all_keys]
        missing = set(columns_to_keep) - set(headers)
        if missing:
            print(
                f"Warning: The following requested columns were not found in the data: {', '.join(missing)}"
            )
    else:
        # Sort headers for consistency
        headers = sorted(list(all_keys))
        # Move 'target_user' or 'login' to front if they exist
        if "target_user" in headers:
            headers.remove("target_user")
            headers.insert(0, "target_user")
        elif "login" in headers:
            headers.remove("login")
            headers.insert(0, "login")

    print(
        f"Writing {len(rows_to_write)} rows to {csv_file} (Columns: {len(headers)})..."
    )
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows_to_write)

    print(f"Successfully converted {json_file} to {csv_file}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert GitHub analytics JSON caches to CSV."
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="The JSON file to convert (e.g., cache/followers_cache.json)",
    )
    parser.add_argument(
        "--columns",
        "-c",
        help="Comma-separated list of columns to keep (e.g., 'login,name,location')",
    )

    args = parser.parse_args()

    columns = None
    if args.columns:
        columns = [c.strip() for c in args.columns.split(",")]

    if args.input:
        output_file = args.input.replace(".json", ".csv")
        if not output_file.endswith(".csv"):
            output_file += ".csv"
        convert_json_to_csv(args.input, output_file, columns)
    else:
        # Default behavior: convert both known caches if they exist
        for f in ["cache/followers_cache.json", "cache/users_cache.json"]:
            if os.path.exists(f):
                convert_json_to_csv(f, f.replace(".json", ".csv"), columns)
            else:
                print(f"Skipping {f} (not found).")

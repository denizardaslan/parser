import re
import pandas as pd
import os
import glob


def get_file_choice(prompt, file_extensions):
    """Get user's file choice from available files"""
    files = []
    for ext in file_extensions:
        files.extend(glob.glob(f"*.{ext}"))

    if not files:
        print(f"No files found with extensions: {file_extensions}")
        return None

    print(f"\n{prompt}")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")

    while True:
        try:
            choice = int(input("Enter your choice (number): ")) - 1
            if 0 <= choice < len(files):
                return files[choice]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


def parse_config_file(filepath):
    """Parse config .db file and extract parameters"""
    rows = []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("param"):
            parts = line.strip().split("\t")
            if len(parts) < 3:
                i += 1
                continue

            id_ = parts[1]
            name = parts[2]

            # bits and number of locations per value
            i += 1
            if i >= len(lines):
                break
            bits_line = lines[i].strip()
            if not bits_line.startswith("bits"):
                continue
            bits_parts = bits_line.split("\t")
            if len(bits_parts) < 2:
                continue
            num_locations = bits_parts[1]

            # Collect subframe data
            subframes = []
            while i + 1 < len(lines):
                i += 1
                data_line = lines[i].strip()
                if not data_line or not re.match(r"^\d", data_line):
                    i -= 1
                    break
                data_parts = data_line.split("\t")
                if len(data_parts) >= 4:
                    subframe = data_parts[0]
                    word = data_parts[1]
                    lowbit = data_parts[2]
                    highbit = data_parts[3]
                    # Calculate length from highbit and lowbit
                    try:
                        length = int(highbit) - int(lowbit) + 1
                    except ValueError:
                        length = 0

                    subframes.append(
                        {
                            "id": id_,
                            "name": name,
                            "subframe": subframe,
                            "word": word,
                            "lowbit": lowbit,
                            "highbit": highbit,
                            "length": length,
                        }
                    )

            rows.extend(subframes)
        else:
            i += 1

    return rows


def read_lfl_file(filepath):
    """Read LFL document (Excel, CSV, etc.)"""
    try:
        # Try to read based on file extension
        if filepath.endswith(".csv"):
            df = pd.read_csv(filepath)
        elif filepath.endswith((".xls", ".xlsx")):
            df = pd.read_excel(filepath)
        else:
            print(f"Unsupported file format: {filepath}")
            return None

        # Skip first row (header) and get data
        # Column A: id, Column B: word, Column C: lowbit, Column D: length
        lfl_data = []

        for index, row in df.iterrows():
            try:
                # Convert to string and strip whitespace
                id_val = str(row.iloc[0]).strip()
                word_val = str(row.iloc[1]).strip()
                lowbit_val = str(row.iloc[2]).strip()
                length_val = int(row.iloc[3]) if pd.notna(row.iloc[3]) else 0

                # Calculate highbit from lowbit and length
                try:
                    highbit_val = int(lowbit_val) + length_val - 1
                except ValueError:
                    highbit_val = 0

                lfl_data.append(
                    {
                        "id": id_val,
                        "word": word_val,
                        "lowbit": lowbit_val,
                        "highbit": str(highbit_val),
                        "length": length_val,
                    }
                )
            except (IndexError, ValueError) as e:
                print(f"Error processing row {index}: {e}")
                continue

        return lfl_data

    except Exception as e:
        print(f"Error reading LFL file: {e}")
        return None


def compare_parameters(config_data, lfl_data):
    """Compare config and LFL parameters"""
    matches = []
    total_config = len(config_data)
    total_lfl = len(lfl_data)

    print(f"\nComparing parameters...")
    print(f"Config file contains {total_config} parameters")
    print(f"LFL file contains {total_lfl} parameters")

    for config_param in config_data:
        for lfl_param in lfl_data:
            # Check if all fields match
            if (
                config_param["id"] == lfl_param["id"]
                and config_param["word"] == lfl_param["word"]
                and config_param["lowbit"] == lfl_param["lowbit"]
                and config_param["highbit"] == lfl_param["highbit"]
            ):

                matches.append(
                    {
                        "id": config_param["id"],
                        "name": config_param["name"],
                        "word": config_param["word"],
                        "lowbit": config_param["lowbit"],
                        "highbit": config_param["highbit"],
                        "length": config_param["length"],
                    }
                )
                break

    return matches


def generate_report(config_data, lfl_data, matches):
    """Generate comparison report"""
    total_config = len(config_data)
    total_lfl = len(lfl_data)
    total_matches = len(matches)

    if total_config > 0:
        match_rate_config = (total_matches / total_config) * 100
    else:
        match_rate_config = 0

    if total_lfl > 0:
        match_rate_lfl = (total_matches / total_lfl) * 100
    else:
        match_rate_lfl = 0

    print("\n" + "=" * 60)
    print("COMPARISON REPORT")
    print("=" * 60)
    print(f"Total parameters in config file: {total_config}")
    print(f"Total parameters in LFL file: {total_lfl}")
    print(f"Total matching parameters: {total_matches}")
    print(f"Match rate (config perspective): {match_rate_config:.2f}%")
    print(f"Match rate (LFL perspective): {match_rate_lfl:.2f}%")
    print("=" * 60)

    if matches:
        print("\nMATCHING PARAMETERS:")
        print("-" * 80)
        print(
            f"{'ID':<10} {'Name':<20} {'Word':<8} {'LowBit':<8} {'HighBit':<8} {'Length':<8}"
        )
        print("-" * 80)
        for match in matches:
            print(
                f"{match['id']:<10} {match['name']:<20} {match['word']:<8} {match['lowbit']:<8} {match['highbit']:<8} {match['length']:<8}"
            )

    # Save detailed report to Excel
    try:
        # Create detailed comparison DataFrame
        report_data = []

        # Add all config parameters with match status
        for config_param in config_data:
            is_matched = any(
                m["id"] == config_param["id"]
                and m["word"] == config_param["word"]
                and m["lowbit"] == config_param["lowbit"]
                and m["highbit"] == config_param["highbit"]
                for m in matches
            )

            report_data.append(
                {
                    "Source": "Config",
                    "ID": config_param["id"],
                    "Name": config_param["name"],
                    "Word": config_param["word"],
                    "LowBit": config_param["lowbit"],
                    "HighBit": config_param["highbit"],
                    "Length": config_param["length"],
                    "Matched": "Yes" if is_matched else "No",
                }
            )

        # Add LFL parameters that don't have matches
        for lfl_param in lfl_data:
            is_matched = any(
                m["id"] == lfl_param["id"]
                and m["word"] == lfl_param["word"]
                and m["lowbit"] == lfl_param["lowbit"]
                and m["highbit"] == lfl_param["highbit"]
                for m in matches
            )

            if not is_matched:
                report_data.append(
                    {
                        "Source": "LFL",
                        "ID": lfl_param["id"],
                        "Name": "N/A",
                        "Word": lfl_param["word"],
                        "LowBit": lfl_param["lowbit"],
                        "HighBit": lfl_param["highbit"],
                        "Length": lfl_param["length"],
                        "Matched": "No",
                    }
                )

        df_report = pd.DataFrame(report_data)
        df_report.to_excel("comparison_report.xlsx", index=False)
        print(f"\nDetailed report saved to: comparison_report.xlsx")

    except Exception as e:
        print(f"Error saving report: {e}")


def main():
    """Main function"""
    print("Parameter Comparison Tool")
    print("=" * 30)

    # Get config file choice
    config_file = get_file_choice("Choose your config (.db) file:", ["db"])
    if not config_file:
        return

    print(f"Selected config file: {config_file}")

    # Get LFL file choice
    lfl_file = get_file_choice("Choose your LFL document:", ["csv", "xls", "xlsx"])
    if not lfl_file:
        return

    print(f"Selected LFL file: {lfl_file}")

    # Parse config file
    print(f"\nParsing config file: {config_file}")
    config_data = parse_config_file(config_file)
    if not config_data:
        print("No data found in config file.")
        return

    # Read LFL file
    print(f"Reading LFL file: {lfl_file}")
    lfl_data = read_lfl_file(lfl_file)
    if not lfl_data:
        print("No data found in LFL file.")
        return

    # Compare parameters
    matches = compare_parameters(config_data, lfl_data)

    # Generate report
    generate_report(config_data, lfl_data, matches)


if __name__ == "__main__":
    main()

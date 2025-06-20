import re
import pandas as pd

# Dosya yolunu güncelle
filepath = "name.db"

# Excel'e yazılacak veriler
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

        # bits ve number of locations per value
        i += 1
        if i >= len(lines):  # Check bounds
            break
        bits_line = lines[i].strip()
        if not bits_line.startswith("bits"):
            continue
        bits_parts = bits_line.split("\t")
        if len(bits_parts) < 2:  # Check if parts exist
            continue
        num_locations = bits_parts[1]

        # Subframe / Word / Low Bit / High Bit değerlerini topla
        subframes = []
        while i + 1 < len(lines):  # Dynamic subframe collection
            i += 1
            data_line = lines[i].strip()
            if not data_line or not re.match(r"^\d", data_line):
                i -= 1  # Step back if not a data line
                break
            data_parts = data_line.split("\t")
            if len(data_parts) >= 4:
                subframes.append(
                    {
                        "subframe": data_parts[0],
                        "word": data_parts[1],
                        "lowbit": data_parts[2],
                        "highbit": data_parts[3],
                    }
                )

        # type (euct sonrası ilk değer)
        type_val = ""
        while i + 1 < len(lines):  # Better bounds checking
            i += 1
            type_line = lines[i].strip()
            if type_line.startswith("euct"):
                euct_parts = type_line.split("\t")
                if len(euct_parts) > 1:  # Check if value exists
                    type_val = euct_parts[1]
                break

        # row oluştur
        row = {
            "ID": id_,
            "Name": name,
            "Number of Locations per Value": num_locations,
            "Type": type_val,
        }

        # Subframe / Word / Low Bit / High Bit kolonları
        for idx, sub in enumerate(subframes):
            row[f"Subframe{idx+1}"] = sub["subframe"]
            row[f"Word{idx+1}"] = sub["word"]
            row[f"LowBit{idx+1}"] = sub["lowbit"]
            row[f"HighBit{idx+1}"] = sub["highbit"]

        rows.append(row)
    else:
        i += 1

# DataFrame oluştur ve Excel'e kaydet
try:
    df = pd.DataFrame(rows)
    df.to_excel("parsed_output.xlsx", index=False)
    print("Excel dosyası oluşturuldu: parsed_output.xlsx")
except Exception as e:
    print(f"Excel dosyası oluşturulurken hata: {e}")

import pandas as pd
import re

# Excel'den veriyi oku
df = pd.read_excel("your_excel_file.xlsx", sheet_name="Sheet4")

# Konum parse eden fonksiyon
def parse_location(loc):
    if pd.isnull(loc):
        return pd.Series([None, None, None])
    match = re.search(r'Word[:\s]*(\d+)[,\s]*Lowbit[:\s]*(\d+)[,\s]*Highbit[:\s]*(\d+)', loc, re.IGNORECASE)
    if match:
        return pd.Series([int(match.group(1)), int(match.group(2)), int(match.group(3))])
    else:
        return pd.Series([None, None, None])

# LFL konumlarını ayır
df[['LFL_Word', 'LFL_Low', 'LFL_High']] = df['LFL Locations'].apply(parse_location)
df[['DB_Word', 'DB_Low', 'DB_High']] = df['DB Locations'].apply(parse_location)

# LFL ve DB ayrı tablolar gibi düşün
lfl_df = df[['LFL Parameter Name', 'LFL_Word', 'LFL_Low', 'LFL_High']].dropna().drop_duplicates()
db_df = df[['DB Parameter Name', 'DB_Word', 'DB_Low', 'DB_High']].dropna().drop_duplicates()

# Outer join ile konuma göre karşılaştır
merged = pd.merge(
    lfl_df,
    db_df,
    left_on=['LFL_Word', 'LFL_Low', 'LFL_High'],
    right_on=['DB_Word', 'DB_Low', 'DB_High'],
    how='inner'
)

# İsim karşılaştırması (opsiyonel)
merged['Same_Name'] = (
    merged['LFL Parameter Name'].str.strip().str.lower() ==
    merged['DB Parameter Name'].str.strip().str.lower()
)

# Sonuçları kaydet
merged.to_excel("full_location_matches.xlsx", index=False)

# Özet
print(f"Eşleşen kayıt sayısı: {len(merged)}")
print(merged[['LFL Parameter Name', 'DB Parameter Name', 'Same_Name']].head())

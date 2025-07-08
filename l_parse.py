import pandas as pd
import re

# Excel'den veriyi oku
df = pd.read_excel("your_excel_file.xlsx", sheet_name="Sheet4")

# Konum parser fonksiyonu
def parse_location(loc):
    if pd.isnull(loc):
        return pd.Series([None, None, None])
    match = re.search(r'Word[:\s]*(\d+)[,\s]*Lowbit[:\s]*(\d+)[,\s]*Highbit[:\s]*(\d+)', loc, re.IGNORECASE)
    if match:
        return pd.Series([int(match.group(1)), int(match.group(2)), int(match.group(3))])
    else:
        return pd.Series([None, None, None])

# LFL ve DB konum bilgilerini ayır
df[['LFL_Word', 'LFL_Low', 'LFL_High']] = df['LFL Locations'].apply(parse_location)
df[['DB_Word', 'DB_Low', 'DB_High']] = df['DB Locations'].apply(parse_location)

# LFL ve DB taraflarını ayrı tablolar gibi düşün
lfl_df = df[['LFL Parameter Name', 'LFL_Word', 'LFL_Low', 'LFL_High']].dropna().drop_duplicates()
db_df = df[['DB Parameter Name', 'DB_Word', 'DB_Low', 'DB_High']].dropna().drop_duplicates()

# Sadece konuma göre inner join
matches = pd.merge(
    lfl_df,
    db_df,
    left_on=['LFL_Word', 'LFL_Low', 'LFL_High'],
    right_on=['DB_Word', 'DB_Low', 'DB_High'],
    how='inner'
)

# Kolonları sadeleştir
matches = matches[[
    'LFL Parameter Name', 'LFL_Word', 'LFL_Low', 'LFL_High',
    'DB Parameter Name'
]]

# Aynı konumda birden fazla LFL veya DB parametresi olabilir → gruplama doğaldır

# Excel'e kaydet
matches.to_excel("location_based_matches.xlsx", index=False)

print(f"Eşleşen kayıt sayısı: {len(matches)}")
print(matches.head())

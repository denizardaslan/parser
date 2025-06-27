import pandas as pd
import re

# Excel dosyasını oku
df = pd.read_excel("your_excel_file.xlsx", sheet_name="Sheet4")

# Location parser fonksiyonu
def parse_location(loc):
    if pd.isnull(loc):
        return pd.Series([None, None, None])
    match = re.search(r'Word[:\s]*(\d+)[,\s]*Lowbit[:\s]*(\d+)[,\s]*Highbit[:\s]*(\d+)', loc, re.IGNORECASE)
    if match:
        return pd.Series([int(match.group(1)), int(match.group(2)), int(match.group(3))])
    else:
        return pd.Series([None, None, None])

# Lokasyonları ayır
df[['LFL_Word', 'LFL_Low', 'LFL_High']] = df['LFL Locations'].apply(parse_location)
df[['DB_Word', 'DB_Low', 'DB_High']] = df['DB Locations'].apply(parse_location)

# Konum karşılaştırması
df['Same_Position'] = (
    (df['LFL_Word'] == df['DB_Word']) &
    (df['LFL_Low'] == df['DB_Low']) &
    (df['LFL_High'] == df['DB_High'])
)

# İsim karşılaştırması (case-insensitive, strip boşlukları)
df['Same_Name'] = (
    df['LFL Parameter Name'].str.strip().str.lower() ==
    df['DB Parameter Name'].str.strip().str.lower()
)

# Tüm kombinasyonlar için etiket
def status(row):
    if row['Same_Position'] and row['Same_Name']:
        return '✅ Match (Position + Name)'
    elif row['Same_Position']:
        return '🟡 Position Match, Name Mismatch → Check Manually'
    elif row['Same_Name']:
        return '🟠 Name Match, Position Mismatch → Check Location'
    else:
        return '❌ No Match'

df['Comparison_Result'] = df.apply(status, axis=1)

# Sonuçları dışa aktar
df.to_excel("comparison_result.xlsx", index=False)

# Özet
summary = df['Comparison_Result'].value_counts()
print(summary)

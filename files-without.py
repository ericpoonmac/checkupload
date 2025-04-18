import csv
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# Pattern for disallowed prefixes
disallowed_prefixes = re.compile(r'^(00|01|02|03|04|05|x|X)')

# Load the CSV file
input_path = "input.csv"  # Make sure this file is in your current directory
df = pd.read_csv(input_path)

# Collect valid files
filtered_results = []

# Process each row in the CSV
for index, row in df.iterrows():
    ref = row['Ref']
    url = row['URL']

    print(f"\n🔍 Processing Ref {ref}...")

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style"]):
            tag.decompose()

        lines = [line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()]

        found = False
        for line in lines:
            if '.' in line and not disallowed_prefixes.match(line):  # if it's a valid file
                filtered_results.append({'Ref': ref, 'File': line})
                print(f"   📄 {line}")
                found = True

        if not found:
            print("   ❗ No matching files found.")

    except Exception as e:
        print(f"❌ Error processing {ref}: {e}")

# Export results
output_path = "files-upload.csv"
pd.DataFrame(filtered_results).to_csv(output_path, index=False)
print(f"\n✅ Done. Results saved to: {output_path}")

# ✅ Show summary
print(f"\n📦 Total matching files found: {len(filtered_results)}")
print(f"✅ Done. Results saved to: {output_path}")

# Let's assume result_df is your output DataFrame
output = BytesIO()
wb = Workbook()
ws = wb.active

# Convert DataFrame to Excel
for r in dataframe_to_rows(result_df, index=False, header=True):
    ws.append(r)

wb.save(output)
output.seek(0)  # Move pointer back to beginning

# 🎯 Download button
st.download_button(
    label="📥 Download Excel",
    data=output.getvalue(),
    file_name="upload_check_results.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

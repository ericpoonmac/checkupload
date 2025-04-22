import csv
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from collections import defaultdict

# Pattern for disallowed prefixes
disallowed_prefixes = re.compile(r'^(00|01|02|03|04|05|x|X)')

# Load the CSV file
input_path = "input.csv"
df = pd.read_csv(input_path)

# Initialize trackers
total_files_processed = 0
filtered_results = []
results_by_ref = defaultdict(list)

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
            if '.' in line:
                total_files_processed += 1
                if not disallowed_prefixes.match(line):
                    filtered_results.append({'Ref': ref, 'File': line})
                    results_by_ref[ref].append(line)
                    print(f"   📄 {line}")
                    found = True

        if not found:
            print("   ❗ No matching files found.")

    except Exception as e:
        print(f"❌ Error processing {ref}: {e}")

# Export results
output_path = "files-upload.csv"
pd.DataFrame(filtered_results).to_csv(output_path, index=False)

# ✅ Summary
print(f"\n📦 Total files processed: {total_files_processed}")
print(f"✅ Matching files (not starting with 00–05/x/X): {len(filtered_results)}")
print(f"📄 Result saved to: {output_path}")

# ✅ Display result breakdown by Ref
print("\n🧾 Matched Files by Ref:")
if results_by_ref:
    for ref, files in results_by_ref.items():
        print(f"🔸 {ref}:")
        for f in files:
            print(f"   📄 {f}")
else:
    print("❗ No matching files found across all refs.")

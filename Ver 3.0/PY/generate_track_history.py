#!/usr/bin/env python3
import os
import glob
import re
import csv

try:
    import openpyxl
    has_openpyxl = True
except ImportError:
    has_openpyxl = False  # VER 3.0: warned + non-zero exit at end of main()

ROOT = os.environ.get('MAVO_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANDS_DIR = os.path.join(ROOT, 'bands')
CSV_OUT = os.path.join(ROOT, 'MAVOmusic_Track_History.csv')
XLSX_OUT = os.path.join(ROOT, 'MAVOmusic_Track_History.xlsx')

# Set of IDs that have been checked during YouTube Studio screenshot audits
CHECKED_IDS = {
    # Canonical songs audited 0001-0050 (batch complete, through 2026-07-19) + 0053 (Studio-audited 19-07-2026)
    '0001', '0002', '0003', '0004', '0005', '0006', '0007', '0008',
    '0009', '0010', '0011', '0012', '0013', '0014', '0015', '0016',
    '0017', '0018', '0019', '0020', '0021', '0022', '0023', '0024',
    '0025', '0026', '0027', '0028', '0029', '0030', '0031', '0032', '0033', '0034', '0035', '0036', '0037', '0038', '0039', '0040', '0041', '0042', '0043', '0044', '0045', '0046', '0047', '0048', '0049', '0050',
    '0053', # 0054 pair fully audited 20-07-2026 (LF premiere confirmed 19 Jul)
    # A/B algorithm test uploads
    '0051', '0052', '0054', '0055', '0056', '0057', '0058', '0059', '0060', '0061', '0062', '0063', '0064', '0065', # 0055/0056 20-07 + 0057/0058/0059 21-07 + 0060-0064 22-07 + 0065 24-07 realtime/testimony date-synced (own panels pending)
    # Matched alternate cuts audited / date-synced
    '1503', '1707', '0889', '0914', '0705', '1568', '2074', '0192', '0255', '0191', '0426', '0908', '1024', '1072', '2189', '0386', '2063', '1189', '2285', '1451', '2027', '0665', '0943', '2419', '1719',
    '0886', '0887', '0975', '1438', '0376', '1564', '2036', '0375', '1202', '2053', '1398', '2132', '0517', '0187', '0637', '0781', '2374', '0587', '0752', '2307',
    # VER 3.4 - 26-28 Aug 2026 wave audited from the Studio content lists (CO-W01)
    '0093', '0095', '0096', '0099', '0100', '0101', '0102', '0103', '0104', '0111', '0124'
}

TODAY_DATE = '26-07-2026'

# VER 3.4: per-ID check dates for audits filed after the TODAY_DATE era.
# Anything not listed here keeps TODAY_DATE (legacy default); anything missing
# from CHECKED_IDS still shows 'N/A'.
CHECKED_DATES = {
    '0093': '01-11-2026', '0095': '01-11-2026', '0096': '01-11-2026',
    '0099': '01-11-2026', '0100': '01-11-2026', '0101': '01-11-2026',
    '0102': '01-11-2026', '0103': '01-11-2026', '0104': '01-11-2026',
    '0111': '01-11-2026', '0124': '01-11-2026',
}

def title_case_words(text):
    if not text or text.strip() in ['N/A', 'n/a', '']:
        return 'N/A'
    
    def cap_match(m):
        word = m.group(0)
        return word[0].upper() + word[1:]
    
    return re.sub(r'[A-Za-z0-9]+', cap_match, text)

def wrap_5_words(text):
    if not text or text in ['N/A', 'n/a', '']:
        return 'N/A'
    words = text.split()
    chunks = []
    for i in range(0, len(words), 5):
        chunks.append(' '.join(words[i:i+5]))
    return '\n'.join(chunks)

def parse_date_sort_key(date_str):
    if not date_str or date_str == 'N/A':
        return '0000-00-00'
    m = re.match(r'(\d{2})-(\d{2})-(\d{4})', date_str)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    return '0000-00-00'

def main():
    files = sorted(glob.glob(os.path.join(BANDS_DIR, '**', '*.md'), recursive=True))
    rows = []

    for fpath in files:
        parts = fpath.replace(ROOT + os.sep, '').split(os.sep)
        if len(parts) < 5:
            continue
        
        artist_raw = parts[2].replace('_', ' ')
        song_raw = parts[3].replace('_', ' ')
        s_id = parts[4]
        filename = parts[5]
        date_str = filename.replace('.md', '')
        
        with open(fpath, 'r', encoding='utf-8') as fh:
            content = fh.read()
        
        # Split on spaced ' - ' only, so hyphenated artists (American Hi-Fi, Asian Kung-Fu Generation) parse correctly
        h1_m = re.search(r'^\#\s*(.+?)\s+-\s+(.+?)\s*\(', content, re.MULTILINE)
        if h1_m:
            artist_name = h1_m.group(1).strip()
            song_name = h1_m.group(2).strip()
        else:
            artist_name = artist_raw
            song_name = song_raw
            
        # Handles both standard packs ('## 2. SHORTS') and short-only matched cuts ('## 1. SHORTS')
        parts_sec = re.split(r'## [12]\. SHORTS', content, maxsplit=1)
        lf_part = parts_sec[0]
        sf_part = parts_sec[1] if len(parts_sec) > 1 else ''
        
        def extract_field(lab, src):
            pat = r'### ' + re.escape(lab) + r':\s*\n```text\s*\n(.*?)\n```'
            m = re.search(pat, src, re.DOTALL)
            if m:
                val = m.group(1).strip()
                if val and val != 'N/A' and not val.startswith('N/A'):
                    return val
            return 'N/A'
            
        lf_title = extract_field('Title', lf_part)
        sf_title = extract_field('Title', sf_part)
        
        lf_date = date_str if lf_title != 'N/A' else 'N/A'
        sf_date = date_str if sf_title != 'N/A' else 'N/A'
        
        last_checked = (CHECKED_DATES.get(s_id, TODAY_DATE)
                        if s_id in CHECKED_IDS else 'N/A')
        
        # Apply Title Case Capitalization to every word
        band_tc = title_case_words(artist_name)
        song_tc = title_case_words(song_name)
        lf_title_tc = title_case_words(lf_title)
        sf_title_tc = title_case_words(sf_title)
        
        # Apply 5-word line wrapping to titles
        lf_title_wrapped = wrap_5_words(lf_title_tc)
        sf_title_wrapped = wrap_5_words(sf_title_tc)
        
        rows.append({
            'ID': s_id,
            'Last Checked': last_checked,
            'Band': band_tc,
            'Song': song_tc,
            'Uploaded (LF)': lf_date,
            'Title (LF)': lf_title_wrapped,
            'Uploaded (SF)': sf_date,
            'Title (SF)': sf_title_wrapped
        })

    # Sort by uploading date (shorts) in descending order
    rows.sort(key=lambda r: (parse_date_sort_key(r['Uploaded (SF)']), int(r['ID']) if r['ID'].isdigit() else r['ID']), reverse=True)

    fieldnames = [
        'Last Checked',
        'Band',
        'Song',
        'Uploaded (LF)',
        'Title (LF)',
        'Uploaded (SF)',
        'Title (SF)'
    ]

    # Write CSV
    with open(CSV_OUT, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.DictWriter(cf, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Successfully generated CSV: {CSV_OUT} ({len(rows)} records)")

    # Write XLSX
    if has_openpyxl:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Track History"

        # Headers
        ws.append(fieldnames)

        # Style header
        header_fill = openpyxl.styles.PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        header_font = openpyxl.styles.Font(color="FFFFFF", bold=True)
        for col_num in range(1, len(fieldnames) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = openpyxl.styles.Alignment(horizontal="center", vertical="center")

        # Style data rows
        for r in rows:
            ws.append([r[col] for col in fieldnames])

        # Enable text wrapping & vertical top alignment
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = openpyxl.styles.Alignment(wrap_text=True, vertical="top")

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = 0
            for cell in col:
                val = str(cell.value or '')
                lines = val.split('\n')
                line_max = max(len(l) for l in lines) if lines else 0
                if line_max > max_len:
                    max_len = line_max
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 14)

        wb.save(XLSX_OUT)
        print(f"Successfully generated XLSX: {XLSX_OUT}")
    else:
        print("\u274c WARNING: openpyxl is NOT installed -> MAVOmusic_Track_History.xlsx "
              "was NOT regenerated and is now STALE vs the CSV.")
        print("   Mandate #8 requires both sheets in sync. Fix with:")
        print("   pip install -r PY/requirements.txt")
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main() or 0)

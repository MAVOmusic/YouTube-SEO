import os
import re
import collections

ROOT = os.environ.get('MAVO_ROOT') or os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))

# Load Master Shorts Repository
repo_file = os.path.join(ROOT, 'TXT/Master_Shorts_Repository.txt')
if not os.path.exists(repo_file):
    repo_file = os.path.join(ROOT, 'uploads/Master_Shorts_Repository.txt')

with open(repo_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

all_shorts = []
for line in lines:
    line = line.strip()
    if not line or line.startswith('#') or line.startswith('='):
        continue
    m = re.match(r'^(\d{4})\.\s*(.*)', line)
    if m:
        s_id = m.group(1)
        title = m.group(2)
        all_shorts.append((s_id, title))

backlog_shorts = [s for s in all_shorts if int(s[0]) >= 151]

def clean_track_name(name):
    name = re.sub(r'\[📺\]', '', name)
    name = re.sub(r'#\S+', '', name)
    name = name.strip()
    name_norm = name.lower()
    name_norm = re.sub(r'[^\w\s]', '', name_norm)
    name_norm = re.sub(r'\s+', ' ', name_norm).strip()
    return name_norm

track_groups = collections.defaultdict(list)
for s_id, raw_title in backlog_shorts:
    norm = clean_track_name(raw_title)
    track_groups[norm].append((s_id, raw_title))

dup_clusters = {k: v for k, v in track_groups.items() if len(v) > 1}

out_file = os.path.join(ROOT, 'TXT/Backlog_Duplicate_Shorts_Audit_0151_2460.txt')
with open(out_file, 'w', encoding='utf-8') as out:
    out.write("# MAVOmusic (@mavomusicyt) - BACKLOG SHORTS DUPLICATION AUDIT (0151 to 2460)\n")
    out.write(f"# Total Backlog Shorts Examined: {len(backlog_shorts)}\n")
    out.write(f"# Total Multi-Upload Duplicate Tracks Found in 0151+: {len(dup_clusters)}\n\n")
    out.write("="*90 + "\n")
    out.write("FULL DUPLICATE CLUSTERS BEYOND CANONICAL FOLDERS LIST (SORTED BY UPLOAD COUNT)\n")
    out.write("="*90 + "\n\n")

    for norm, cluster in sorted(dup_clusters.items(), key=lambda item: len(item[1]), reverse=True):
        track_display = cluster[0][1]
        ids_list = [f"[{c[0]}]" for c in cluster]
        out.write(f"Track: {track_display} ({len(cluster)} uploads)\n")
        out.write(f"  Shorts IDs: {', '.join(ids_list)}\n\n")

print(f"Audit report generated: {out_file} ({len(dup_clusters)} clusters)")

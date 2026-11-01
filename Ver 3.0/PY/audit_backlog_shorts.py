#!/usr/bin/env python3
import re
import os
import glob
import collections

ROOT = os.environ.get('MAVO_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAVO_FOLDERS = {
    "0001": (["0001"], "Squeeze - Cool for Cats"),
    "0002": (["0002"], "Foo Fighters - Run"),
    "0003": (["0003"], "Huey Lewis and the News - The Power of Love"),
    "0004": (["0004"], "Rick Springfield - Jessie's Girl"),
    "0005": (["0005"], "Bummrraa - Butt Ugly Playroom"),
    "0006": (["0006"], "Gary Wright - Dream Weaver"),
    "0007": (["0007", "1503"], "Rage Against The Machine - Bulls On Parade"),
    "0008": (["0008", "2285"], "9mm Parabellum Bullet - Sacrifice"),
    "0009": (["0009"], "The Strokes - Juicebox"),
    "0010": (["0010"], "BrokeNCYDE - Band Tee"),
    "0011": (["0011"], "The Strokes - Last Nite"),
    "0012": (["0012", "1451"], "Alexisonfire - No Transitory"),
    "0013": (["0013", "2027"], "Joe Satriani - Satch Boogie"),
    "0014": (["0014", "0665", "0943", "2419"], "System Of A Down - Hypnotize"),
    "0015": (["0015"], "The Police - Roxanne"),
    "0016": (["0016", "1719"], "The Dear Hunter - Stuck On A Wire Out On A Fence"),
    "0017": (["0017", "0887"], "Alice Cooper - No More Mr. Nice Guy"),
    "0018": (["0018"], "Queen - Killer Queen"),
    "0019": (["0019", "0886", "0887"], "Bush - Machinehead"), # MAVO screenshot labeled 0887; actual match is 0886
    "0020": (["0020"], "Scott Walker - The Old Man's Back Again"),
    "0021": (["0021", "0975", "1438"], "Anouk - Good God"),
    "0022": (["0022"], "The Clash - Guns Of Brixton"),
    "0023": (["0023"], "The Clash - Should I Stay Or Should I Go"),
    "0024": (["0024", "0376", "1564"], "American Authors - Best Day Of My Life"),
    "0025": (["0025"], "50 Cent - In Da Club"),
    "0026": (["0026"], "Asian Kung-Fu Generation - After Dark"),
    "0027": (["0027", "2036"], "Gold Motel - Brand New Kind Of Blue"),
    "0028": (["0028", "0375", "1202"], "American Hi-Fi - Flavor Of The Weak"),
    "0029": (["0029"], "The Blues Brothers - Soul Man"),
    "0030": (["0030"], "Rise Against - The Good Left Undone"),
    "0031": (["0031", "2053"], "Queen - We Are The Champions"),
    "0032": (["0032"], "Fall Out Boy - Dance, Dance"),
    "0033": (["0033"], "Seth Chapla - Carol Of The Bells"),
    "0034": (["0034"], "Apocalyptica - Life Burns!"),
    "0035": (["0035", "1398"], "Screaming Females - Rotten Apple"),
    "0036": (["0036"], "The Temptations - My Girl"),
    "0037": (["0037", "2132"], "A Change Of Pace - Weekend Warriors"),
    "0038": (["0038"], "Bush - Comedown"),
    "0039": (["0039", "0517"], "Pat Benatar - Hit Me With Your Best Shot"),
    "0040": (["0040"], "Led Zeppelin - Black Dog"),
    "0041": (["0041"], "Maroon 5 - Harder To Breathe"),
    "0042": (["0042"], "Blink-182 - All The Small Things"),
    "0043": (["0043"], "Atreyu - Falling Down"),
    "0044": (["0044", "0587", "0752", "2307"], "04 Limited Sazabys - Galapagos"),
    "0045": (["0045"], "Fang Island - Chompers"),
    "0046": (["0046"], "Blink-182 - Dammit"),
    "0047": (["0047", "1707"], "AFI - Totalimmortal"),
    "0048": (["0048", "0889"], "The Kinks - You Really Got Me"),
    "0049": (["0049"], "Slipknot - Killpop"),
    "0050": (["0050", "0914"], "(Hed) P.E. - Bartender"),
    "0051": (["0051"], "Pendulum Feat. In Flames - Self VS. Self"),
    "0052": (["0052"], "Billie Eilish - Bad Guy"),
    "0053": (["0053", "0187", "0637", "0781", "2374"], "Pendulum - 9,000 Miles"),
    "0054": (["0054"], "The Dandy Warhols - Bohemian Like You"),
    "0055": (["0055", "0705", "1568"], "Attila - Pizza"),
    "0056": (["0056", "2074"], "Autopilot Off - The 12th Day"),
    "0057": (["0057"], "Temple Of The Dog - Hunger Strike"),
    "0058": (["0058", "0192", "0255"], "BrokeNCYDE - 2 Drunk 2 Drive"),
    "0059": (["0059", "0191"], "Coheed And Cambria - A Favor House Atlantic"),
    "0060": (["0060", "0426", "0908", "1024", "1072", "2189"], "Avenged Sevenfold - A Little Piece Of Heaven"),
    "0061": (["0061", "0386", "2063"], "Rammstein - Adieu"),
    "0062": (["0062"], "The Boomtown Rats - I Don't Like Mondays"),
    "0063": (["0063", "1189"], "Rammstein - Adios"),
    "0064": (["0064"], "The Mamas & The Papas - Monday, Monday"),
    "0065": (["0065"], "Happy Mondays - Step On"),
    "0066": (["0066"], "The Bangles - Manic Monday"),
    "0067": (["0067"], "Pratt & McClain - Happy Days"),
    "0068": (["0068"], "The Allman Brothers Band - Stormy Monday"),
    "0069": (["0069"], "Coldrampage - Spoon"),
    "0070": (["0070", "0673", "0782", "2427"], "Rammstein - Amerika"),
    "0071": (["0071"], "Rammstein - Alter Mann"),
    "0072": (["0072", "0650", "2438"], "Rammstein - Hilf Mir"),
    "0073": (["0073", "0553", "0919", "2438"], "Rammstein - Amour"),
    "0074": (["0074", "0180", "0258"], "Pegboard Nerds - Heaven Let Us Down"),
    "0075": (["0075"], "Rammstein - Angst"),
    "0076": (["0076"], "Cream - Those Were The Days"),
    "0077": (["0077"], "T. Rex - 20th Century Boy"),
    "0078": (["0078"], "Tommy Tutone - 867-5309/Jenny"),
    "0079": (["0079", "2381"], "All Time Low Feat. Vic Fuentes - A Love Like War"),
    "0080": (["0080"], "Paramore - Misery Business"),
    "0081": (["0081"], "Avril Lavigne - Complicated"),
    "0082": (["0082", "0184"], "Jawbreaker - Accident Prone"),
    "0083": (["0083"], "Rammstein - Ein Lied"),
    "0084": (["0084"], "Kreator - Enemy Of God"),
    "0085": (["0085"], "Rogue x Stonebank x Slippy - Unity"),
    "0086": (["0086", "0590", "0809", "2314"], "Die Antwoord - Enter The Ninja"),
    "0087": (["0087", "0697", "1362", "1442", "2391", "2461"], "System Of A Down - Lonely Day"),
    "0088": (["0088", "1991"], "\"Weird Al\" Yankovic - Amish Paradise"),
    "0089": (["0089", "0197", "2050"], "Scorpions - Wind Of Change"),
    "0090": (["0090", "1512"], "Lostprophets - Last Train Home"),
    "0091": (["0091", "1146", "1822"], "Avril Lavigne - How Does It Feel"),
    "0092": (["0092", "0862", "1160"], "Silverstein - My Heroine"),
    "0093": (["0093", "1180"], "Johnny Cash - Personal Jesus"),
    "0094": (["0094", "1040", "1573"], "Paramore - All I Wanted"),
    "0095": (["0095", "0615", "0698"], "Rammstein - Du Hast"),
    "0096": (["0096", "0523", "2239"], "Linkin Park - Lying From You"),
    "0097": (["0097", "2094"], "Korn - Twisted Transistor"),
    "0098": (["0098", "0678", "0936", "2437"], "Billy Talent - Red Flag"),
    "0099": (["0099", "0387", "2146"], "Nirvana - The Man Who Sold The World"),
    "0100": (["0100", "0666", "1164", "2420"], "My Chemical Romance - Dead!"),
    "0101": (["0101", "0560", "1008", "2269"], "Paramore - Decode"),
    "0102": (["0102", "1109"], "Green Day - 21 Guns"),
    "0103": (["0103", "0620", "1070", "2345"], "Linkin Park - Numb"),
    "0104": (["0104", "0285", "1293", "2128"], "Ado - Usseewa"),
    "0105": (["0105", "1162", "1286", "1646"], "Muse - Time Is Running Out"),
    "0106": (["0106", "0460", "0894", "2333"], "Tom Misch - Disco Yes"),
    "0107": (["0107"], "Blink-182 - All The Small Things"),
    "0108": (["0108", "1185"], "My Chemical Romance - I Don't Love You"),
    "0109": (["0109", "1273", "1712"], "Bullet For My Valentine - Tears Don't Fall"),
    "0110": (["0110", "0390", "2147"], "HIM (His Infernal Majesty) - Wings Of A Butterfly"),
    "0111": (["0111", "0428", "2193"], "System Of A Down - Toxicity"),
    "0112": (["0112", "2376"], "Red Hot Chili Peppers - Soul To Squeeze"),
    "0113": (["0113", "0418", "0757", "2180"], "Pendulum - Fasten Your Seatbelt"),
    "0114": (["0114", "0388", "2022"], "Megadeth - Sweating Bullets"),
    "0115": (["0115"], "Electric Callboy - We Got The Moves"),
    "0116": (["0116", "2236"], "BABYMETAL Feat. Electric Callboy - RATATATA"),
    "0117": (["0117"], "Bury Your Dead - Magnolia"),
    "0118": (["0118", "1626"], "Coal Chamber - Sway"),
    "0119": (["0119"], "Coal Chamber - Fiend"),
    "0120": (["0120", "0372", "1791"], "Burzum - Autumn Leaves"),
    "0121": (["0121"], "DevilDriver - Sail"),
    "0122": (["0122", "0421", "2184"], "Rise Against - Savior"),
    "0123": (["0123", "0500"], "The Offspring - Gone Away"),
    "0124": (["0124", "0407", "1381", "2169"], "Arctic Monkeys - Do I Wanna Know?"),
    "0125": (["0125"], "Depresszió - Lásd (Azt Amit Neked Szántak)"),
    "0126": (["0126"], "Judas Priest - Electric Eye"),
    "0127": (["0127", "0658", "1085", "2411"], "+44 (Plus 44) - Chapter XIII"),
    "0128": (["0128", "0437", "1175", "2202"], "Metallica - Nothing Else Matters"),
    "0129": (["0129", "1163"], "Marilyn Manson - Coma White"),
    "0130": (["0130", "0680", "0702", "2441"], "Motionless In White - Another Life"),
    "0131": (["0131", "0204", "0900", "2387"], "Radiohead - Paranoid Android"),
    "0132": (["0132", "0799"], "La Bouche - Be My Lover"),
    "0133": (["0133", "1224", "1419"], "Michael Jackson - Billie Jean"),
    "0134": (["0134", "2059"], "Eminem - Rap God"),
    "0135": (["0135", "0605", "2328"], "Amon Amarth - Raise Your Horns"),
    "0136": (["0136"], "Korpiklaani - Rauta"),
    "0137": (["0137"], "Moonsorrow - Pakanajuhla"),
    "0138": (["0138"], "Amon Amarth - Fate Of Norns"),
    "0139": (["0139"], "Our Last Night - Fate"),
    "0140": (["0140", "0588", "1022", "2308"], "Avenged Sevenfold - Bat Country"),
    "0141": (["0141", "1258", "1414"], "The Used - All That I've Got"),
    "0142": (["0142", "2190"], "The Amity Affliction - Don't Lean On Me"),
    "0143": (["0143"], "Slipknot - Danger - Keep Away"),
    "0144": (["0144", "1251"], "Finntroll - Slaget Vid Blodsalv"),
    "0145": (["0145"], "Mastodon - Blood And Thunder"),
    "0146": (["0146"], "Wind Rose - Diggy Diggy Hole"),
    "0147": (["0147"], "Suicide Silence - Unanswered"),
    "0148": (["0148"], "Mudvayne - Dig"),
    "0149": (["0149"], "Slipknot - People=Shit"),
    "0150": (["0150"], "Infected Mushroom - Send Me An Angel")
}

def clean_track_name(name):
    # Strip studio noise like [📺], #shorts, hashtags, etc.
    name = re.sub(r'\[📺\]', '', name)
    name = re.sub(r'#\S+', '', name)
    name = name.strip()
    # Normalize punctuation/quotes
    name_norm = name.lower()
    name_norm = re.sub(r'[^\w\s]', '', name_norm)
    name_norm = re.sub(r'\s+', ' ', name_norm).strip()
    return name_norm

def main():
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

    # Separate 0001-0150 and 0151-2460
    canonical_map = {}
    for cid, (ids, name) in MAVO_FOLDERS.items():
        norm = clean_track_name(name)
        canonical_map[norm] = (cid, ids, name)

    backlog_shorts = [s for s in all_shorts if int(s[0]) >= 151]

    print(f"Total Backlog Shorts (0151+): {len(backlog_shorts)}")

    # 1. Check if any 0151+ Short matches 0001-0150 canonical tracks BUT is missing from MAVO's folder list!
    missing_from_folders = []
    already_in_folders = []

    # 2. Group all duplicates within the 0151+ backlog itself!
    backlog_track_groups = collections.defaultdict(list)

    for s_id, raw_title in backlog_shorts:
        norm = clean_track_name(raw_title)
        backlog_track_groups[norm].append((s_id, raw_title))

        # Check against 0001-0150 canonicals
        if norm in canonical_map:
            cid, folder_ids, name = canonical_map[norm]
            if s_id not in folder_ids:
                missing_from_folders.append((s_id, raw_title, cid, name))
            else:
                already_in_folders.append((s_id, cid))

    print("\n" + "="*80)
    print("AUDIT FINDINGS 1: SHORTS FROM 0151+ MATCHING CANONICAL TRACKS (0001-0150)")
    print("="*80)
    if missing_from_folders:
        print(f"Found {len(missing_from_folders)} Shorts in 0151+ matching 0001-0150 that were NOT listed in folder names:")
        for s_id, raw_t, cid, cname in missing_from_folders:
            print(f"  Short ID [{s_id}] ({raw_t}) --> Matches Canonical [{cid}] ({cname})")
    else:
        print("✓ All Shorts in 0151+ that match 0001-0150 are ALREADY recorded in MAVO's folder list!")

    print("\n" + "="*80)
    print("AUDIT FINDINGS 2: DUPLICATE SHORTS WITHIN THE 0151+ BACKLOG ITSELF")
    print("="*80)
    
    dup_backlog_clusters = {k: v for k, v in backlog_track_groups.items() if len(v) > 1}
    print(f"Total Duplicate Groups found in 0151+ Backlog: {len(dup_backlog_clusters)}")
    
    for norm, cluster in sorted(dup_backlog_clusters.items(), key=lambda item: len(item[1]), reverse=True):
        track_display = cluster[0][1]
        ids_list = [c[0] for c in cluster]
        print(f"\nTrack: {track_display} ({len(cluster)} uploads in 0151+)")
        print(f"  Shorts IDs: {', '.join(ids_list)}")

if __name__ == '__main__':
    main()

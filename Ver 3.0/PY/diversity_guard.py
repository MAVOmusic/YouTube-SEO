#!/usr/bin/env python3
"""
MAVOmusic DIVERSITY GUARD v1.2 (Section 21 enforcement)
==========================================================
Hard gate against YouTube 'mass-produced / inauthentic content' classification.
Runs AFTER verify.py (which checks opener/first-word uniqueness). This guard checks
the things YouTube's repetition detector actually measures:

  1. Boilerplate sentences  - any sentence (>=25 chars) used in > MAX_SENT_REUSE packages
  2. Boilerplate lines      - any full line (>=34 chars, non-tag, non-header) reused > MAX_LINE_REUSE
  3. Gear-line byte-clones  - identical gear/footer lines > MAX_GEAR_REUSE
  4. Description similarity - same skeleton (artist/song-blanked) used > MAX_SKEL_REUSE
  5. Link policy            - Shorts desc/pins: ZERO urls. LF desc: <=3 urls, allowlist only
  6. Pin policy             - ZERO urls in any pinned comment
  7. Technique policy       - Section 20: no slap/thumb; no pick-technique terms
                              (idioms 'pick one/your pick/picked up' and 'pickup' whitelisted)
  8. Tag box policy         - <=450 chars; 3-5 base tags (<=8 w/ golden); artist+song identity;
                              `rocksmith bass` on SF; no noise/bare/dupes; <=1 genre-lane tag
  9. Tracking-ID leaks      - folder ID (NNNN) must not appear in public-facing fields
 10. Retired phrases        - registry of banned stock sentences from the 2026-07-19 audit

Exit code 0 = PASS. Exit code 1 = FAIL (with printed violation list).
"""
import glob, os, re, collections, sys

ROOT = os.environ.get('MAVO_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = sorted(glob.glob(ROOT + '/bands/**/*.md', recursive=True))

MAX_SENT_REUSE = 4      # a sentence may appear in at most 4 packages
MAX_LINE_REUSE = 4      # full-line reuse cap (tags lines follow golden-sync rule and are exempt)
MAX_GEAR_REUSE = 1      # gear/footer lines must be byte-unique
MAX_SKEL_REUSE = 2      # description skeleton (A/S-blanked) may appear at most twice
MAX_LF_URLS = 3
ALLOWED = ('kick.com', 'twitch.tv', 'discord.gg')

# Retired stock phrases (2026-07-19 purge, VER 1.56). Never use again, even re-ordered.
RETIRED = [
    'Getting that exact pocket and dynamic feel to sound right on the Epiphone Thunderbird',
    'Let me know how you think the low end sits in the mix',
    'We tackle everything from classic 60s walking lines to modern metal breakdowns live every single day',
    'If you love seeing how iconic rock and metal riffs translate to physical bass strings, hit subscribe',
    'That Epiphone Thunderbird delivers such a thick, satisfying foundation for this classic track',
    'the incredible bass pocket of',
    'straight into the heart of',
    'such an enduring', 'Is it the rhythm section or the vocals',
    'I pushed the Thunderbird hard on this one',
    'has always been a standout', 'Share your first impression of this song below',
    'The full performance is pinned up top',
    'Check out the full linked video above and leave your challenge below',
    'Full track is one click up above',
    'Tap the full playthrough link above and tell me',
    'is an absolute masterclass. What is your go-to',
    'If you had to pick one', 'Quick question for the bass fam',
    'blaze.stream', 'club.com/mavomusic', 'tiktok.com/@mavomusictt',
]

PICK_IDIOMS = re.compile(
    r"(pick(ed)? up a bass|picked up the bass|pick one|your pick|my pick|'s pick|viewer pick|every pick|"
    r"pick a side|pick your|could'?ve picked|fan.?s pick|pick for|pick of|picked as|pick between)", re.I)
PICK_TERMS = re.compile(r'\b(pick|picks|picked|picking|pick-bass|downpick\w*|pickwork|pick-work)\b(?!ups?\b)', re.I)
PROHIBITED = re.compile(r'\b(slap|slapping|slapper|slapped|thumb-slapp?\w*|slam[- ]?thumb\w*)\b', re.I)
THUMB_TECH = re.compile(r'\b(thumb|thumbs)\b', re.I)
THUMB_OK = re.compile(r'(thumbnail)', re.I)

def get_fields(content):
    # v1.2: single-section "Matched Short" packages use "## 1. SHORTS VIDEO SEO PACK" only -
    # their ONE Tags Box is a SHORTS box for policy purposes (mandatory `rocksmith bass` etc.).
    if '## 1. SHORTS VIDEO SEO PACK' in content and '## 2. SHORTS' not in content:
        lf, sf = '', content
    else:
        lf, sf = (content.split('## 2. SHORTS', 1) + [''])[:2]
    def ex(sec, lab):
        m = re.search(r'### ' + re.escape(lab) + r':\s*\n```text\s*\n(.*?)\n```', sec, re.DOTALL)
        return m.group(1).strip() if m else ''
    return dict(lf_title=ex(lf,'Title'), lf_desc=ex(lf,'Description'), lf_tags=ex(lf,'Tags Box'),
                lf_pin=ex(lf,'Pinned Comment'), sf_title=ex(sf,'Title'), sf_desc=ex(sf,'Description'),
                sf_tags=ex(sf,'Tags Box'), sf_pin=ex(sf,'Pinned Comment'))

def sentences(t):
    t = re.sub(r'\s+', ' ', t)
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', t) if len(s.strip()) >= 25]

def main():
    errors, warnings = [], []

    sent_map = collections.defaultdict(set)
    line_map = collections.defaultdict(set)
    gear_map = collections.defaultdict(set)
    skel_lf = collections.defaultdict(set)
    skel_sf = collections.defaultdict(set)

    for fp in FILES:
        rel = os.path.relpath(fp, ROOT)
        parts = rel.split(os.sep)
        id_ = parts[-2]
        artist = parts[2].replace('_', ' ') if len(parts) == 6 else ''
        song = parts[3].replace('_', ' ') if len(parts) == 6 else ''
        content = open(fp, encoding='utf-8').read()
        F = get_fields(content)
        public = [F['lf_title'], F['lf_desc'], F['lf_tags'], F['lf_pin'],
                  F['sf_title'], F['sf_desc'], F['sf_tags'], F['sf_pin']]
        public_txt = '\n'.join(x for x in public if x and not x.startswith('N/A'))

        # 1. sentence reuse
        for s in sentences((F['lf_desc'] or '') + ' ' + (F['sf_desc'] or '') + ' ' + (F['lf_pin'] or '') + ' ' + (F['sf_pin'] or '')):
            sent_map[s].add(id_)

        # 2. full-line boilerplate (exempt tag-box lines & hash tails - golden-sync rule)
        in_tags = False
        for line in content.split('\n'):
            ls = line.strip()
            if ls.startswith('### Tags Box'):
                in_tags = True
            elif ls.startswith('###'):
                in_tags = False
            if in_tags or ls.startswith(('#', '```', '---', '**', '(This')) or len(ls) < 34:
                continue
            if '#BassCover' in ls or '#shorts' in ls:
                continue
            line_map[ls].add(id_)

        # 3. gear lines
        for line in content.split('\n'):
            ls = line.strip()
            if (ls.startswith(('🎸', '🎮')) and 'Thunderbird' in ls) or (ls.startswith('🎸') and 'Rocksmith' in ls):
                gear_map[ls].add(id_)

        # 4. description skeletons (blank out artist/song tokens)
        def skel(t):
            t = t.lower()
            for w in set(re.findall(r'[a-z0-9]+', artist.lower() + ' ' + song.lower())):
                if len(w) > 2:
                    t = re.sub(r'\b' + re.escape(w) + r'\b', '<X>', t)
            return re.sub(r'\s+', ' ', t).strip()
        if F['lf_desc'] and not F['lf_desc'].startswith('N/A'):
            skel_lf[skel(F['lf_desc'])].add(id_)
        if F['sf_desc'] and not F['sf_desc'].startswith('N/A'):
            skel_sf[skel(F['sf_desc'])].add(id_)

        # 5/6. link policy
        for name, val in (('SF desc', F['sf_desc']), ('SF pin', F['sf_pin']),
                          ('LF pin', F['lf_pin'])):
            if val and re.search(r'https?://', val):
                errors.append(f'LINK POLICY: {rel} - URL found in {name}')
        lf_urls = re.findall(r'https?://[^\s)]+', F['lf_desc'] or '')
        if len(lf_urls) > MAX_LF_URLS:
            errors.append(f'LINK POLICY: {rel} - {len(lf_urls)} LF urls (> {MAX_LF_URLS})')
        # v4.13: the same URL must never appear twice in one description. Two asks can
        # share one link ("request a song, or boost the server") but must not print it
        # twice - it reads as a broken template and wastes a line of the CTA.
        _seen = {}
        for _u in lf_urls:
            _k = _u.rstrip('/').lower()
            _seen[_k] = _seen.get(_k, 0) + 1
        for _k, _n in _seen.items():
            if _n > 1:
                errors.append(f'LINK POLICY: {rel} - duplicate LF url repeated {_n}x ({_k})')
        for u in lf_urls:
            if not any(a in u for a in ALLOWED):
                errors.append(f'LINK POLICY: {rel} - non-allowlist LF url {u}')

        # 7. technique policy
        for mm in PROHIBITED.finditer(public_txt):
            errors.append(f'SECTION 20: {rel} - prohibited percussive term: {mm.group(0)!r}')
        for mm in THUMB_TECH.finditer(public_txt):
            if not THUMB_OK.search(public_txt[max(0, mm.start()-10):mm.end()+10]):
                errors.append(f'SECTION 20: {rel} - prohibited "thumb" technique reference')
        for mm in PICK_TERMS.finditer(public_txt):
            seg = public_txt[max(0, mm.start()-40):mm.end()+40]
            if PICK_IDIOMS.search(seg):
                continue
            errors.append(f'SECTION 20: {rel} - pick-technique term: ...{seg.strip()}...')

        # 8. tag policy (comparison normalizes accents + punctuation, mirroring YouTube search)
        import unicodedata
        def norm(s):
            s = unicodedata.normalize('NFKD', s.lower())
            s = ''.join(ch for ch in s if not unicodedata.combining(ch))
            s = s.replace("'", '').replace('’', '')  # fold contractions: don't -> dont
            return re.sub(r'\s+', ' ', re.sub(r"[^a-z0-9]+", ' ', s)).strip()
        for tagfield, val in (('LF tags', F['lf_tags']), ('SF tags', F['sf_tags'])):
            if not val or val.startswith('N/A'):
                continue
            if len(val) > 450:
                errors.append(f'TAG POLICY: {rel} - {tagfield} {len(val)} chars (>450)')
            tags = [t.strip().lower() for t in val.split(',') if t.strip()]
            joined = norm(' '.join(tags))
            art_tok = [w for w in norm(artist).split() if len(w) > 1]
            song_tok = [w for w in norm(song).split() if len(w) > 3]
            if art_tok and not any(any(a in norm(t) for a in art_tok) for t in tags):
                warnings.append(f'TAG POLICY: {rel} - {tagfield} lacks artist-identity tag')
            if song_tok and not all(w in joined for w in song_tok):
                warnings.append(f'TAG POLICY: {rel} - {tagfield} lacks song-identity coverage')
            # v1.57 tag mandates: 3-5 base tags (golden back-ports may extend to <=8),
            # mandatory `rocksmith bass` on every Shorts box, banned bare generics +
            # noise/farm registry, no intra-box dupes, max 1 genre-lane tag.
            if len(tags) < 3:
                errors.append(f'TAG POLICY: {rel} - {tagfield} {len(tags)} tags (<3 floor; need artist+song+platform identity)')
            if len(tags) > 8:
                errors.append(f'TAG POLICY: {rel} - {tagfield} {len(tags)} tags (>8 ceiling; golden back-ports allowed 3-8)')
            if tagfield == 'SF tags' and 'rocksmith bass' not in joined:
                errors.append(f'TAG POLICY: {rel} - SF tags missing mandatory `rocksmith bass` (rule 11)')
            normed = [norm(t) for t in tags]
            if len(set(normed)) != len(normed):
                errors.append(f'TAG POLICY: {rel} - {tagfield} has intra-box duplicate (normalized)')
            BARE_GEN = {'rocksmith', 'rocksmith 2014'}
            NOISE = {'cover bass','flamenco guitar tutorial','seiji igusa bass','among us','chick fil a',
                     'mukesh ambani','kobore','787-10 ana','dekho kaise','bhoot ki video','funny video',
                     'cartoon cartoon cartoon cartoon','bass tabs for popular songs','head and munky','arti',
                     'aspinall vs gane','brian may guitar','beatbox','blue prince','sophia buttons','ally law',
                     'ken smith bass','9000 miles bass cover','slopsmith','slopsmith bass'}
            for t in tags:
                tn = t.strip().lower()
                if tn in BARE_GEN:
                    errors.append(f'TAG POLICY: {rel} - {tagfield} bare generic tag {t!r} (use `rocksmith bass` / `rocksmith 2014 bass`)')
                if tn in NOISE:
                    errors.append(f'TAG POLICY: {rel} - {tagfield} rejected-noise tag {t!r}')
            # genre-lane cap: max 1 pure-genre tag per box. GOLDEN registry (analytics-proven,
            # see v1.57 tag audit) and identity tags are exempt.
            GOLDEN = {norm(x) for x in (
                'flavor of the week|flavour of the week|american hi fi flavor of the week|flavor of the week bass|'
                'flavour of the week american hi fi|flavor of the weak bass|all small things|all small things bass|'
                'chomper|chomper bass cover|rotten apple bass|rocksmith eb drop db|screaming females rotten apple bass|'
                '04 limited sazabys|04 limited sazabys live|04 limited sazabys bass|fight so dirty but you love so sweet|'
                'galapagos bass|we are the champion|we are the champions|we are the champions bass|'
                'we are the champions cover|rocksmith queen|killer queen bass|berserk bass|berserk sacrifice|'
                'kick drop bass|roulette bass|tim commerford bass|shavo odadjian bass|john deacon bass|'
                'gareth mcgrillen bass|soad hypnotize|soad hypnotize bass|soad bass cover|mavo music original|'
                'rocksmith original song').split('|')}
            GENRE_WORDS = {'rock','metal','punk','pop','dnb','hardcore','metalcore','grunge','emo','ska','reggae',
                           'funk','soul','blues','jazz','country','indie','alternative','thrash','djent','crunkcore',
                           'electropop','synthpop','synthwave','synth','ndh','rap','glam','prog','progressive',
                           'psychedelic','stoner','doom','sludge','acoustic','classical','electronic','electro',
                           'dance','techno','house','trance','dubstep','shoegaze','britpop','cello','proto',
                           'atmospheric','melodic','heavy','hardcore','emo','screamo','pop-punk','nu-metal','j-rock'}
            art_t = {w for w in norm(artist).split() if len(w) > 1}
            song_t = {w for w in norm(song).split() if len(w) > 3}
            def is_genre(tag):
                tn = norm(tag)
                if tn in GOLDEN or tn in ('rocksmith bass','rocksmith 2014 bass','rocksmith shorts'):
                    return False
                tt = set(tn.split())
                if (tt & art_t) or (tt & song_t):
                    return False
                return bool(tt & GENRE_WORDS)
            ngenre = sum(1 for t in tags if is_genre(t))
            if ngenre > 1:
                warnings.append(f'TAG POLICY: {rel} - {tagfield} {ngenre} genre-lane tags (>1 cap)')

        # 9. tracking-ID leak (own folder ID in public text)
        if re.search(r'\b' + re.escape(id_) + r'\b', public_txt):
            errors.append(f'ID LEAK: {rel} - folder ID {id_} appears in public-facing text')

        # 10. retired phrases
        low = public_txt.lower()
        for phrase in RETIRED:
            if phrase.lower() in low:
                errors.append(f'RETIRED PHRASE: {rel} - {phrase[:70]!r}')

    # corpus-level checks
    for s, ids in sorted(sent_map.items(), key=lambda kv: -len(kv[1])):
        if len(ids) > MAX_SENT_REUSE:
            errors.append(f'BOILERPLATE SENTENCE x{len(ids)} [{sorted(ids)[:6]}...]: {s[:110]!r}')
    for l, ids in sorted(line_map.items(), key=lambda kv: -len(kv[1])):
        if len(ids) > MAX_LINE_REUSE:
            errors.append(f'BOILERPLATE LINE x{len(ids)} [{sorted(ids)[:6]}...]: {l[:110]!r}')
    for g, ids in sorted(gear_map.items(), key=lambda kv: -len(kv[1])):
        if len(ids) > MAX_GEAR_REUSE:
            errors.append(f'GEAR CLONE x{len(ids)} [{sorted(ids)}]: {g[:110]!r}')
    for s, ids in sorted(skel_lf.items(), key=lambda kv: -len(kv[1])):
        if len(ids) > MAX_SKEL_REUSE:
            errors.append(f'LF DESC SKELETON x{len(ids)} [{sorted(ids)[:8]}]: {s[:110]!r}')
    for s, ids in sorted(skel_sf.items(), key=lambda kv: -len(kv[1])):
        if len(ids) > MAX_SKEL_REUSE:
            errors.append(f'SF DESC SKELETON x{len(ids)} [{sorted(ids)[:8]}]: {s[:110]!r}')

    print('=' * 56)
    print('MAVOmusic DIVERSITY GUARD v1.2 (Section 21 gate)')
    print('=' * 56)
    print(f'Packages scanned : {len(FILES)}')
    print(f'Violations (FAIL): {len(errors)}')
    print(f'Warnings         : {len(warnings)}')
    if errors:
        print('\n--- VIOLATIONS ---')
        for e in errors:
            print('  ❌', e)
    if warnings:
        print('\n--- WARNINGS ---')
        for w in warnings[:40]:
            print('  ⚠️ ', w)
        if len(warnings) > 40:
            print(f'  ⚠️  ... {len(warnings)-40} more')
    if not errors:
        print('\n✅ PASS: no mass-production / inauthentic-content signals detected.')
    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())

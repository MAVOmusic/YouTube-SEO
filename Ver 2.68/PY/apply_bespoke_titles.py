#!/usr/bin/env python3
import os
import glob
import re

ROOT = '/home/user'
BANDS_DIR = os.path.join(ROOT, 'bands')

BESPOKE_TITLES = {
    "0054": ("Zia McCabe's driving 2000s garage-rock indie bass groove!", "Indie garage-rock bass drive on 'Bohemian Like You'! #shorts #bass"),
    "0055": ("Devouring the heaviest, most chaotic metalcore breakdown about pizza!", "Feasting on the heaviest metalcore breakdown ever written about pizza! #shorts #bass"),
    "0056": ("2004 skate-punk basslines like Autopilot Off's 'The 12th Day' are pure nostalgia!", "Driving early-2000s skate punk pick-bass sprint! #shorts #bass"),
    "0057": ("Jeff Ament's soulful 1991 grunge bassline on 'Hunger Strike'!", "Jeff Ament's legendary 1991 grunge bass tone! #shorts #bass"),
    "0058": ("Adding a live Thunderbird bassline over 2008 crunkcore synth 808s!", "Crunkcore synth 808s paired with real distorted bass guitar! #shorts #bass"),
    "0059": ("Michael Todd's catchy prog-pop bass hook on 'A Favor House Atlantic'!", "2003 prog-punk bassline that sticks in your head for days! #shorts #bass"),
    "0060": ("Johnny Christ's theatrical bass work on 'A Little Piece Of Heaven' is wild!", "Orchestral metal madness on Avenged Sevenfold's darkest track! #shorts #bass"),
    "0061": ("Oliver Riedel's crushing Drop-C industrial metal bass weight on 'Adieu'!", "Crushing German industrial metal Drop-C low end! #shorts #bass"),
    "0062": ("Pete Briquette's melodic new wave bass runs on 'I Don'T Like Mondays'!", "1979 UK new wave melodic bass runs on a Thunderbird! #shorts #bass"),
    "0063": ("Heavy industrial guitar riffing backed by Oliver Riedel's relentless bass pulse!", "Industrial metal pick-bass aggression on Rammstein's 'Adios'! #shorts #bass"),
    "0064": ("Joe Osborn's studio Wrecking Crew 1966 sunshine pop bassline!", "Wrecking Crew 1966 sunshine pop bass masterclass! #shorts #bass"),
    "0065": ("Paul Ryder's Madchester funk-house bassline is an absolute dancefloor classic!", "90s UK Madchester funk bass groove that refuses to quit! #shorts #bass"),
    "0066": ("Prince-written 80s pop-rock basslines played with crisp pick attack!", "Bright 1986 pop-rock bass drive written by Prince! #shorts #bass"),
    "0067": ("Classic 1970s TV theme walking basslines played with vintage feel!", "Vintage 70s walking pop-rock bassline from 'Happy Days'! #shorts #bass"),
    "0068": ("Berry Oakley's legendary fluid 12-bar blues-rock bass walking lines!", "Masterclass in 12-bar blues-rock walking bass lines! #shorts #bass"),
    "0069": ("Slapping through this underground indie-rock gem with heavy groove!", "Underground indie bass riff with serious slap punch! #shorts #bass"),
    "0070": ("Stomping through Oliver Riedel's heavy satirical industrial metal groove!", "Stomping 2004 industrial metal bass punch on 'Amerika'! #shorts #bass"),
    "0071": ("Oliver Riedel's atmospheric, heavy 90s industrial bass pulse on 'Alter Mann'!", "Deep 90s German industrial metal bass foundation! #shorts #bass"),
    "0072": ("Brooding, heavy industrial metal basslines off Rosenrot!", "Dark industrial metal pick-bass drive on 'Hilf Mir'! #shorts #bass"),
    "0073": ("Dark, romantic industrial metal low-end dynamics on Rammstein's 'Amour'!", "Brooding industrial love-metal bass depth on a Thunderbird! #shorts #bass"),
    "0074": ("Translating dubstep/electronic rock bass drops to physical strings!", "When electronic EDM dubstep bass drops meet real bass guitar! #shorts #bass"),
    "0075": ("The heaviest ultra-low Drop-tuning bass assault in modern Rammstein history!", "Modern ultra-heavy Drop-tuning metal power from Rammstein! #shorts #bass"),
    "0076": ("Jack Bruce's revolutionary 1968 psych-rock bass improvisations!", "Jack Bruce's wild 60s blues-rock bass wizardry! #shorts #bass"),
    "0077": ("Steve Currie's swaggering 1973 glam-rock bass riff on '20th Century Boy'!", "1973 glam-rock swaggering bass riff from T. Rex! #shorts #bass"),
    "0078": ("Jon Kribs's driving 1981 power-pop bass engine on '867-5309/Jenny'!", "Driving 1981 power-pop bass pulse on a Thunderbird! #shorts #bass"),
    "0079": ("This 2013 pop-punk anthem has a surprisingly driving low-end core!", "High-octane pop-punk bass energy on 'A Love Like War'! #shorts #bass"),
    "0080": ("The unstoppable 2007 pop-punk pick-bass attack on 'Misery Business'!", "Pure 2007 pop-punk pick-bass energy from Paramore! #shorts #bass"),
    "0081": ("The low-end pulse that held 2002 pop-punk radio together!", "Nostalgic 2000s pop-punk bass drive on 'Complicated'! #shorts #bass"),
    "0082": ("90s emo pioneer Jawbreaker built this masterpiece around deep bass dynamics!", "Deep 90s emo-punk basslines that built a genre! #shorts #bass"),
    "0083": ("Subtle, delicate low-end acoustic support on Rammstein's ambient closer!", "Subtle ambient low-end warmth from Rammstein! #shorts #bass"),
    "0084": ("Christian Giesler's thrash metal precision picking on Kreator's 'Enemy Of God'!", "190 BPM German thrash metal pick-bass intensity! #shorts #bass"),
    "0085": ("High-speed Monstercat gaming electro-rock basslines on four strings!", "EDM gaming electro-rock bass drops on physical strings! #shorts #bass"),
    "0086": ("Translating South African zef rave synth-bass to physical strings!", "Rave synth 808s translated directly to a bass guitar! #shorts #bass"),
    "0087": ("Shavo Odadjian's emotional Drop-C bass foundation on 'Lonely Day'!", "Shavo's haunting Drop-C low-end support on 'Lonely Day'! #shorts #bass"),
    "0088": ("Steve Jay's deep 1996 hip-hop bass groove parodying 'Gangsta's Paradise'!", "Heavy 90s hip-hop bass groove on 'Amish Paradise'! #shorts #bass"),
    "0089": ("Francis Buchholz's smooth, anthemic rock bassline on 'Wind Of Change'!", "The iconic 1990 rock ballad low-end foundation! #shorts #bass"),
    "0090": ("Driving early-2000s melodic rock basslines on the Thunderbird!", "2004 alt-rock bass drive with huge melodic hooks! #shorts #bass"),
    "0091": ("Deep emotional alternative-rock bass dynamics on Avril Lavigne's 'How Does It Feel'!", "Brooding 2000s alt-rock low-end depth on bass! #shorts #bass"),
    "0092": ("Bill Hamilton's driving post-hardcore pick-bass on 2005's 'My Heroine'!", "Peak 2005 post-hardcore pick-bass drive from Silverstein! #shorts #bass"),
    "0093": ("Adapting Depeche Mode's electronic riff through Johnny Cash's dark acoustic drive!", "Dark acoustic blues-rock low end on Johnny Cash's cover! #shorts #bass"),
    "0094": ("Jeremy Davis's heavy alternative rock bass dynamics on Paramore's 'All I Wanted'!", "Brooding alt-rock low-end surge on Paramore's biggest crescendo! #shorts #bass"),
    "0095": ("Oliver Riedel's iconic 1997 industrial metal bass punch on 'Du Hast'!", "The most recognizable industrial metal bassline in history! #shorts #bass"),
    "0096": ("Phoenix's heavy Drop-D riff on 'Lying From You' is pure Meteora power!", "Nu-metal Drop D riffage on Linkin Park's 'Lying From You'! #shorts #bass"),
    "0097": ("Fieldy's signature slap-clank tone on 'Twisted Transistor' defined 2000s nu-metal!", "Fieldy's iconic low-tuned Korn slap bass tone! #shorts #bass"),
    "0098": ("Jon Gallant's relentless post-hardcore picking on 'Red Flag' is a forearm killer!", "170 BPM Canadian post-hardcore pick-bass sprint! #shorts #bass"),
    "0099": ("Krist Novoselic's fluid, melodic bass runs on MTV Unplugged in New York!", "Krist Novoselic's legendary acoustic bass performance! #shorts #bass"),
    "0100": ("Matt Cortez & Mikey Way's theatrical punk-rock bass drive on 'Dead!'!", "High-speed 2006 theatrical punk bass drive from MCR! #shorts #bass"),
    "0101": ("Jeremy Davis's driving Drop-D bass hook on Twilight's anthem 'Decode'!", "The iconic 2008 Drop-D alt-rock bass drive on 'Decode'! #shorts #bass"),
    "0102": ("Mike Dirnt's emotional bass melody on '21 Guns' is secretly the lead voice!", "When Mike Dirnt's low-end carries the entire chorus! #shorts #bass"),
    "0103": ("The iconic 2003 alt-rock bass foundation on Linkin Park's 'Numb'!", "Nostalgic 2000s low-end power on Linkin Park's biggest hit! #shorts #bass"),
    "0104": ("Ado's 'Usseewa' has one of the most aggressive J-pop basslines ever written!", "Insanely fast J-pop bass attack on Ado's 'Usseewa'! #shorts #bass"),
    "0105": ("Chris Wolstenholme's filthy, fuzz-drenched bass synth effect on 'Time Is Running Out'!", "The ultimate fuzz-synth bass distortion tone from Muse! #shorts #bass"),
    "0106": ("Tom Misch's ultra-funky modern disco-house bassline on 'Disco Yes'!", "Ultra-funky modern disco bass fingerstyle workout! #shorts #bass"),
    "0107": ("Driving through the ultimate 1999 skate-punk anthem!", "Unstoppable 1999 pop-punk bass energy! #shorts #bass"),
    "0108": ("Mikey Way's emotional, ballad basslines on The Black Parade!", "Brooding 2000s rock ballad bass foundation from MCR! #shorts #bass"),
    "0109": ("Jason James's metalcore bass drive on 'Tears Don'T Fall' is pure 2000s emo!", "The 2005 metalcore anthem that defined an entire generation! #shorts #bass"),
    "0110": ("Mige's brooding love-metal bass tone on 'Wings Of A Butterfly'!", "Dark Finnish love-metal bass hook from 2005! #shorts #bass"),
    "0111": ("Shavo Odadjian's wild, syncopated Drop-C bass assault on 'Toxicity'!", "Nu-metal Drop-C bass chaos on System Of A Down's 'Toxicity'! #shorts #bass"),
    "0112": ("Flea's sublime 1993 melodic funk-rock bass masterpiece on 'Soul To Squeeze'!", "Flea's most soul-stirring melodic bassline ever recorded! #shorts #bass"),
    "0113": ("Gareth McGrillen's 174 BPM drum & bass synth lines played live on bass!", "174 BPM drum and bass electronic energy on four strings! #shorts #bass"),
    "0114": ("David Ellefson's snarky, technical thrash basslines on 'Sweating Bullets'!", "David Ellefson's technical thrash metal bass drive! #shorts #bass"),
    "0115": ("German electronic metalcore with the bounciest bass drops of the decade!", "Wild electro-metal bass party energy from Electric Callboy! #shorts #bass"),
    "0116": ("Kawaii metal meets German electro-core — the ultimate low-end collision!", "When Japanese metal core collides with German rave bass drops! #shorts #bass"),
    "0117": ("Crushing 2004 heavy hardcore beatdown riffs on four strings!", "Maximum low-tuned hardcore mosh pit bass power! #shorts #bass"),
    "0118": ("Loco nu-metal bouncing basslines from the peak 1997 mosh era!", "Loco bounce and heavy nu-metal clank on bass! #shorts #bass"),
    "0119": ("Nadja Peulen's industrial nu-metal groove on Coal Chamber's 'Fiend'!", "Spooky late-90s nu-metal bass clank on full display! #shorts #bass"),
    "0120": ("Atmospheric black metal ambient low-end textures on bass!", "Brooding atmospheric black metal low-end isolation! #shorts #bass"),
    "0121": ("Turning AWOLNATION's electronic hit into a heavy metal destruction test!", "Groove metal cover of 'Sail' with crushing low-end drive! #shorts #bass"),
    "0122": ("Joe Principe's blistering 185 BPM punk-rock pick-bass stamina test on 'Savior'!", "185 BPM punk rock pick-bass stamina challenge! #shorts #bass"),
    "0123": ("Greg K.'s driving punk-rock bass foundation on 1997's 'Gone Away'!", "Melodic 90s punk-rock pick-bass drive on 'Gone Away'! #shorts #bass"),
    "0124": ("That dark, fuzz-drenched 'Do I Wanna Know?' riff is peak 2010s indie!", "The ultimate dark fuzz-bass groove from Arctic Monkeys! #shorts #bass"),
    "0125": ("Hungarian metal heavyweights Depresszió deliver an absolute headbanger!", "Heavy Hungarian metal bass power on Depresszió's anthem! #shorts #bass"),
    "0126": ("Ian Hill's galloping heavy metal engine on 'Electric Eye' is pure power!", "1982 British heavy metal galloping bass masterclass! #shorts #bass"),
    "0127": ("Mark Hoppus's melancholic +44 bassline hits so different on a Thunderbird!", "Unlocking Mark Hoppus's post-Blink +44 bass tone! #shorts #bass"),
    "0128": ("Jason Newsted's subtle, supporting bass foundation on 'Nothing Else Matters'!", "The subtle low-end magic of Metallica's legendary ballad! #shorts #bass"),
    "0129": ("Twiggy Ramirez's dark, atmospheric bass tone on 'Coma White'!", "Industrial glam-rock bass depth on Marilyn Manson's classic! #shorts #bass"),
    "0130": ("Modern gothic metalcore bass dynamics on Motionless In White's 'Another Life'!", "Modern gothic metal low-end weight and huge choruses! #shorts #bass"),
    "0131": ("Colin Greenwood's genius, unpredictable bass counterpoint on 'Paranoid Android'!", "Colin Greenwood's 90s alt-rock bass masterclass on Radiohead! #shorts #bass"),
    "0132": ("Translating 90s eurodance synth-bass bangers to a physical Thunderbird!", "90s eurodance club synth-bass played live on bass guitar! #shorts #bass"),
    "0133": ("Louis Johnson's immortal 1982 funk-pop bassline on 'Billie Jean'!", "The most famous bassline in pop music history! #shorts #bass"),
    "0134": ("Attempting the world's fastest rap song synth-bassline on four strings!", "Can a bass guitar keep up with Eminem's 'Rap God' tempo? #shorts #bass"),
    "0135": ("Stomping through the ultimate Viking metal drinking anthem on bass!", "Heavy Viking metal bass drive on 'Raise Your Horns'! #shorts #bass"),
    "0136": ("Finnish folk metal accordion and fiddle melodies on a heavy bass!", "Folk metal party bass drive on Korpiklaani's 'Rauta'! #shorts #bass"),
    "0137": ("Epic pagan folk metal galloping low-end power from Finland!", "Finnish pagan metal bass battle charge on a Thunderbird! #shorts #bass"),
    "0138": ("Thunderous melodic death metal bass weight on Amon Amarth's 'Fate Of Norns'!", "Deep Viking metal bass rumble on a Thunderbird! #shorts #bass"),
    "0139": ("Post-hardcore bass drive and heavy breakdown drops on 'Fate'!", "Post-hardcore low-end power and heavy mosh drops! #shorts #bass"),
    "0140": ("Johnny Christ's fast walking-metal bass fills on 'Bat Country' are unreal!", "Wild dual-guitar metal classic with insane bass fills! #shorts #bass"),
    "0141": ("Jeph Howard's melodic 2004 post-hardcore bassline on 'All That I'Ve Got'!", "2004 post-hardcore bass hook from The Used! #shorts #bass"),
    "0142": ("Ahren Stringer's emotional post-hardcore bass drive on 'Don'T Lean On Me'!", "Australian post-hardcore low-end depth on 'Don'T Lean On Me'! #shorts #bass"),
    "0143": ("Alessandro 'V-Man' Venturella's dark, atmospheric ambient metal bass tones!", "Atmospheric gothic metal bass depth on Slipknot's ambient track! #shorts #bass"),
    "0144": ("Folk metal humppa accordion riffs translated to heavy pick-bass!", "Finnish folk metal bass speed run on a Thunderbird! #shorts #bass"),
    "0145": ("Troy Sanders's ferocious sludge-prog bass riffing on 'Blood And Thunder'!", "Sludge metal heavy low-end fury on Mastodon's mosh anthem! #shorts #bass"),
    "0146": ("Cristiano Bertocchi's heavy dwarf power metal bass anthem!", "Stomping dwarf power metal bass drive on 'Diggy Diggy Hole'! #shorts #bass"),
    "0147": ("Dan Kenny's extreme deathcore pick-bass speed on 'Unanswered'!", "190 BPM deathcore pick-bass assault on 'Unanswered'! #shorts #bass"),
    "0148": ("Ryan Martinie's finger-style slap technique on 'Dig' is an impossible bass benchmark!", "Ryan Martinie's legendary 'BRBR DENG' slap-bass masterclass! #shorts #bass"),
    "0149": ("Paul Gray's lowest, most brutal Drop-B metal bass assault on 'People=Shit'!", "Drop-B extreme metal bass destruction from Paul Gray! #shorts #bass"),
    "0150": ("Psytrance synth bass speed runs on physical Thunderbird strings!", "When electronic psytrance basslines meet real metal strings! #shorts #bass")
}

def replace_title_in_section(section_text, new_title):
    pattern = r'(### Title:\s*\n```text\s*\n)(.*?)(?=\n```)'
    m = re.search(pattern, section_text, flags=re.DOTALL)
    if m:
        start, end = m.span(2)
        return section_text[:start] + new_title + section_text[end:]
    return section_text

def fix_file(fpath):
    s_id = os.path.basename(os.path.dirname(fpath))
    if s_id not in BESPOKE_TITLES:
        return False

    lf_new_title, sf_new_title = BESPOKE_TITLES[s_id]

    with open(fpath, 'r', encoding='utf-8') as fh:
        text = fh.read()

    parts = text.split('## 2. SHORTS')
    lf_part = parts[0]
    sf_part = parts[1] if len(parts) > 1 else ''

    lf_part = replace_title_in_section(lf_part, lf_new_title)
    if sf_part:
        sf_part = replace_title_in_section(sf_part, sf_new_title)

    new_content = lf_part + '## 2. SHORTS' + sf_part

    with open(fpath, 'w', encoding='utf-8') as fh:
        fh.write(new_content)

    return True

def main():
    files = sorted(glob.glob(os.path.join(BANDS_DIR, '**', '*.md'), recursive=True))
    updated_count = 0
    for f in files:
        if fix_file(f):
            updated_count += 1
            print(f"Updated titles for ID {os.path.basename(os.path.dirname(f))}: {f}")

    print(f"\nTotal files updated with bespoke titles: {updated_count}")

if __name__ == '__main__':
    main()

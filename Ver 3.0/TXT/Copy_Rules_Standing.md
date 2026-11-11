# Standing copy rules, consolidated 2026-11-11

Written after three user corrections in one day. These rules bind every title, description, tag set and creator comment from here on. If a package breaks one, it is not delivered.

## Titles

1. Never open a title with "[Song] on bass". That starter is banned in both formats.
2. A long form and its Short never share an opening. The first three words of the two titles must differ, and so must the sentence skeleton.
3. No two titles in a batch share their first three words. Titles are checked as a set before delivery, not one at a time.
4. Vary where the song sits: opening, middle or end. Vary the device: chart fact, album fact, date, question, musician angle, story angle.
5. No plain "Band - Song", no possessive opener ("Band's Song is..."), no "[Song] is [Band]".
6. Never call a normal long form a play along in the title. Play along is a format label for the dedicated play-along uploads only. The same applies inside long form descriptions: say bass performance or playthrough.
7. The song title appears once in the title.
7c. Scope-by-song rule, added 2026-11-11 after Paramore Misery Business was missed a second way: LF 0643 and Short 2390 had copy files and were variants of a song in scope (LF 0674 and Short 2421 were in the recent batches), but the workbook's variant matching only knew the LF 0001-0010 song list, so older variants of newer songs fell out. Scope is decided per song, never per file: once a song is in scope (LF 0001-0010, an upload from 6 November 2026 onward, or a recent batch), every version of that song ever uploaded goes into the workbook and is audited side by side. The builder now works in two passes to enforce this, and its missing-copy guard uses the same per-song scope.
7b. Completeness rule, added 2026-11-11 after Motionless In White Masterpiece was missed: LF 0119 and Shorts 0147 and 1864 had Studio screenshots and upload markers but no _03 - Copy.md, so a builder that only reads copy files silently skipped them. Scope is never defined by which copy files happen to exist. The builder now scans uploaded folders in scope and reports any folder with screenshots or an upload marker but no copy file as a problem. Do not miss songs we have done: every variant of a song in scope goes in the workbook, or the audit fails.
7a. Same-song rule, added 2026-11-11 after LF 0178, SF 0205 and SF 1923 were caught: one version of a song may start with the song name, but every other version of that same song must not. All variants of a song are compared side by side, and their titles, description first lines and comment first lines must each start with a different word. A starter shared by the whole variant set is a fault even when each individual package looks fine on its own. The workbook builder checks this per song group.

## Descriptions

8. Never open a description with the title, with the song title, or with the title's opening words. Open on an album, date, chart, studio or story fact, and let the title and tags carry the song name.
9. The song title appears once in a description. Pointer lines and later paragraphs refer to "this track", "the whole song", "the complete performance".
10. Every Short description carries a block pointing at the attached full recording as the related video. Its wording is written fresh for that video and never reused, and it does not restate the song title.
11. No Short is ever described as trimmed, cut down, lifted or pulled from the long form, and never as a separate recording or separate take. One performance is captured horizontally and vertically at the same moment.
12. Kick first, then Twitch, then Discord, one URL each, each line worded differently from the last batch.
13. No stated upload duration that is not known. No artist or song named in genre playlist descriptions. No em dashes, en dashes, curly quotes or ellipses.

## Creator comments (pinned or posted)

14. Every video gets a creator fact, trivia or question comment, even when a viewer or artist comment is already pinned. A preserved pin is never edited, unpinned or replaced; the creator comment goes beneath it.
15. Rotate the format: multiple choice quiz, trivia statement, did-you-know fact, true or false, chart fact, sales fact, producer fact, opinion question. Never label every comment a quiz, and never use the word Quiz on two comments in a row.
16. Never open two comments in a batch with the same emoji. The opening emoji is part of the format and rotates with it.
17. On a Short, the comment opens with the related video pointer, in its own wording and with its own emoji, then the trivia, fact or question.
18. The comment must not mirror the description's opening move. Quiz answers are kept out of the description.

## Before anything is delivered

19. Run the checks, every time, against the workbook, not from memory: rebuild Ver 3.0/TXT/Copy_Workbook_0001_0010_And_New_Uploads.xlsx with Ver 3.0/PY/build_copy_workbook.py and read its Audit sheet. It must show zero problems before anything is delivered. It compares title, description and comment starters across every row, checks SF comments open with a unique related video pointer and unique opening emoji, checks SF descriptions carry Kick, Twitch and Discord CTAs, and rejects play along long form titles and song-on-bass openers. Then five-word overlap, then verify.sh.
20. Deliver paste-ready blocks, then open a pull request and merge it, and confirm the merge with gh pr view.

## Where this is registered

- This file is the consolidated list.
- Ver 3.0/TXT/Copy_Shape_Register.txt carries the title and description rules.
- Ver 3.0/TXT/Creator_Comment_Rule.md carries rules 14 to 18.
- Ver 3.0/TXT/Short_Full_Recording_Rule.md carries rules 10, 11 and 17.
- Ver 3.0/TXT/Historical_Quiz_Questions_And_Answers.md logs every comment format used, so rotation can be checked.

Workbook order rule, set by the user 2026-11-11 and replacing the earlier bottom-of-workbook note: new edits and uploads are never scattered through the copy workbook, and a song's rows are never split across the file. The main body keeps its existing order; every newly edited or newly uploaded song moves as one complete group to the bottom of the file, all of that song's long forms first in ascending order, then all of its Shorts in ascending order, with the older LF and SF versions of the same song moved down alongside the new ones (the Sabaton and Avril older versions sitting near the top while the new pairs sat at the bottom is the fault this rule exists to prevent). build_copy_workbook.py enforces this through its EDITED_GROUPS list, which is appended in delivery order on every delivery. Separately: uploads were paused on 11 November 2026 after four pairs; the queue restarts at 02:00 on 12 November with +44 Chapter XIII (LF 0733 / Short 2480), then Exodus Toxic Waltz (LF 0734 / Short 2481) at 05:00, and every following upload pushed into the following time slots in the same order, recorded in Upload_Plan_11_November_Onwards.md.

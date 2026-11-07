#!/bin/bash
# MAVOmusic Workspace Verification Script — pre-ship gate with catalogue consistency (VER 3.0)
# Portable: runs from anywhere; the workspace root is this script's own folder.
#   bash verify.sh          -> full gate, exit 1 on any violation
#
# Tier 1: PY/verify.py           (uniqueness, folder paths, lettering, tidy root)
# Tier 2: PY/diversity_guard.py  (Section 21 anti-repetition / tag / link / §20)
# Catalogue: PY/check_song_catalogues.py (row/folder/saved-title consistency)

cd "$(dirname "$(readlink -f "$0")")" || exit 1

echo "========================================="
echo "MAVOmusic Workspace Verification (VER 3.0)"
echo "========================================="
echo ""

python3 PY/verify.py
VERIFY_RC=$?

echo ""
echo "========================================="
echo "Section 21 Diversity Guard (Anti-Repetition Gate)"
echo "========================================="
echo ""

python3 PY/diversity_guard.py
GUARD_RC=$?

echo ""
echo "========================================="
echo "Chronological song catalogues"
echo "========================================="
python3 PY/check_song_catalogues.py
CATALOGUE_RC=$?

echo ""
echo "========================================="
echo "GATE SUMMARY"
echo "========================================="

if [ $VERIFY_RC -ne 0 ]; then
    echo "❌ TIER 1 verify.py FAILED (see violations above)."
else
    echo "✓ TIER 1 verify.py passed."
fi

if [ $GUARD_RC -ne 0 ]; then
    echo "❌ TIER 2 diversity_guard.py FAILED (see violations above)."
else
    echo "✓ TIER 2 diversity_guard.py passed."
fi

if [ $CATALOGUE_RC -ne 0 ]; then
    echo "❌ Catalogue consistency check FAILED (see errors above)."
else
    echo "✓ Catalogue consistency check passed."
fi

echo ""
if [ $VERIFY_RC -ne 0 ] || [ $GUARD_RC -ne 0 ] || [ $CATALOGUE_RC -ne 0 ]; then
    echo "❌ OVERALL FAIL — resolve all reported errors before shipping."
    exit 1
fi
echo "Bands corpus checks passed. This does NOT verify long-form copy or factual accuracy."
echo "For long-form releases, follow TXT/Long_Form_Release_Gate.txt and run PY/long_form_gate.py --check with each video ID."
exit 0

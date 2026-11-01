#!/bin/bash
# MAVOmusic Workspace Verification Script
# Run from /home/user

cd /home/user

echo "========================================="
echo "MAVOmusic Workspace Verification"
echo "========================================="
echo ""

python3 PY/verify.py

echo ""
echo "========================================="
echo "Section 21 Diversity Guard (Anti-Repetition Gate)"
echo "========================================="
echo ""

python3 PY/diversity_guard.py
GUARD_RC=$?

echo ""
echo "========================================="
echo "Section 11 Compliance Check"
echo "========================================="
echo ""

# Check for .py files in root
if ls *.py 1>/dev/null 2>&1; then
    echo "❌ FAIL: .py files found in root directory"
    ls *.py
else
    echo "✓ No .py files in root directory"
fi

# Check for images in root
if ls *.jpg *.jpeg *.png 1>/dev/null 2>&1; then
    echo "❌ FAIL: Image files found in root directory"
    ls *.jpg *.jpeg *.png 2>/dev/null
else
    echo "✓ No image files in root directory"
fi

echo ""
if [ $GUARD_RC -ne 0 ]; then
    echo "❌ OVERALL FAIL: diversity_guard.py reported violations (see Section 21 gate above)."
    exit 1
fi
echo "Verification complete! ALL GATES GREEN ✓"
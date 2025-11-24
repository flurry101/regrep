#!/bin/bash
# Run this script to see all the features in action

set -e
GREP="./grep.sh"
DEMO_DIR="./demo"

echo "======================================"
echo "Grep Implementation Demo"
echo "======================================"
echo ""

# Feature 1: Basic pattern matching
echo "1. BASIC PATTERN MATCHING"
echo "   Command: $GREP -E 'cherry' demo/simple.txt"
echo "   Result:"
$GREP -E "cherry" $DEMO_DIR/simple.txt || true
echo ""

# Feature 2: Match word characters
echo "2. WORD CHARACTERS (\\w - alphanumeric + underscore)"
echo "   Command: echo 'hello_world' | $GREP -E '\\w+'"
echo "   Result:"
echo "hello_world" | $GREP -E "\w+" || true
echo ""

# Feature 3: Match digits
echo "3. DIGITS (\\d - match numbers)"
echo "   Command: grep 'I have 5 apples' demo/numbers.txt"
echo "   Result:"
$GREP -E "5" $DEMO_DIR/numbers.txt || true
echo "" 

# Feature 4: Character classes
echo "4. CHARACTER CLASSES [abc] - match a, b, or c"
echo "   Command: $GREP -E '[aeiou]' demo/simple.txt (lines with vowels)"
echo "   Result:"
$GREP -E "[aeiou]" $DEMO_DIR/simple.txt | head -3 || true
echo ""

# Feature 5: Negated character classes
echo "5. NEGATED CHARACTER CLASSES [^abc]"
echo "   Command: echo 'apple' | $GREP -E '[^xyz]'"
echo "   Result:"
echo "apple" | $GREP -E "[^xyz]" || true
echo ""

# Feature 6: Anchors - start of line
echo "6. ANCHORS - START OF LINE (^)"
echo "   Command: $GREP -E '^start' demo/patterns.txt"
echo "   Result:"
$GREP -E "^start" $DEMO_DIR/patterns.txt || true
echo ""

# Feature 7: Anchors - end of line
echo "7. ANCHORS - END OF LINE ($)"
echo "   Command: $GREP -E 'end\$' demo/patterns.txt"
echo "   Result:"
$GREP -E "end$" $DEMO_DIR/patterns.txt || true
echo ""

# Feature 8: Dot - any character
echo "8. DOT (.) - MATCH ANY CHARACTER"
echo "   Command: echo 'cat' | $GREP -E 'c.t'"
echo "   Result:"
echo "cat" | $GREP -E "c.t" || true
echo ""

# Feature 9: Plus quantifier
echo "9. PLUS QUANTIFIER (+) - ONE OR MORE"
echo "   Command: echo 'numbers 123' | $GREP -E '\\d+'"
echo "   Result:"
echo "numbers 123" | $GREP -E "\d+" || true
echo ""

# Feature 10: Question mark quantifier
echo "10. QUESTION MARK (?) - ZERO OR ONE"
echo "    Command: $GREP -E 'colou?r' demo/patterns.txt"
echo "    Result:"
$GREP -E "colou?r" $DEMO_DIR/patterns.txt || true
echo ""

# Feature 11: Groups/Alternation
echo "11. GROUPS & ALTERNATION (pattern1|pattern2)"
echo "    Command: $GREP -E '(TODO|BUG)' demo/nested/todo.txt"
echo "    Result:"
$GREP -E "(TODO|BUG)" $DEMO_DIR/nested/todo.txt || true
echo ""

# Feature 12: Capture groups with backreferences
echo "12. CAPTURE GROUPS WITH BACKREFERENCES"
echo "    Command: $GREP -E '(\\w+) \\1' demo/words.txt (repeated words)"
echo "    Result:"
$GREP -E "(\w+) \1" $DEMO_DIR/words.txt || true
echo ""

# Feature 13: Multiple files
echo "13. SEARCH MULTIPLE FILES"
echo "    Command: $GREP -E 'TODO' demo/nested/todo.txt demo/nested/code.txt"
echo "    Result:"
$GREP -E "TODO" $DEMO_DIR/nested/todo.txt || true
echo ""

# Feature 14: Recursive directory search
echo "14. RECURSIVE DIRECTORY SEARCH (-r)"
echo "    Command: $GREP -r -E 'TODO' demo/"
echo "    Result:"
$GREP -r -E "TODO" $DEMO_DIR/ || true
echo ""

echo "======================================"
echo "Demo Complete!"
echo "======================================"

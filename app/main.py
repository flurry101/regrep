import sys
import os

# import pyparsing - available if you need it!  
# import lark - available if you need it!

debug = False
capture_groups = {} 
capture_group_counter = 0
match_found_in_file = False

def reset_matcher_state():
    global capture_groups
    global capture_group_counter
    capture_groups = {}
    capture_group_counter = 0

def save_matcher_state():
    return (capture_groups.copy(), capture_group_counter)

def restore_matcher_state(snapshot):
    global capture_groups
    global capture_group_counter
    capture_groups = snapshot[0].copy()
    capture_group_counter = snapshot[1]


def has_top_level_bar(regexp: str):
    depth = 0
    for ch in regexp:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "|" and depth == 0:
            return True
    return False


def split_top_level_alternatives(pattern: str):
    parts = []
    current = []
    depth = 0
    for char in pattern:
        if char == "(":
            depth += 1
            current.append(char)
        elif char == ")":
            depth -= 1
            current.append(char)
        elif depth == 0 and char == "|":
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    parts.append("".join(current))
    return parts



def match(regexp: str, text: str):
    """Match a regular expression pattern against a text string.
    This function implements regex pattern matching with support for alternation (|),
    anchors (^ and $), and various regex features through match_at_position().
    Args:
        regexp (str): The regular expression pattern to match against
        text (str): The input text to search in
    Returns:
        bool: True if the pattern matches the text, False otherwise
    The function handles several cases:
    - Alternation with | operator by splitting and trying each alternative
    - Start of string anchor ^ 
    - End of string anchor $
    - Unanchored patterns by trying matches at each position
    Global state:
        debug: If True, prints debug information about the matching process
        Relies on reset_matcher_state() to clear matcher state between attempts
    """
    global debug
    if debug:
        print(f"Text: {text} ({len(text)}), Regexp: {regexp} ({len(regexp)})")
    if "|" in regexp and has_top_level_bar(regexp):
        try:
            x, y = find_alternation_bounds(regexp)
            parts = regexp[x:y].split("|")
            for part in parts:
                reset_matcher_state()
                new_regexp = regexp[:x] + part + regexp[y:]
                if regexp.startswith("^") and regexp.endswith("$"):
                    inner = new_regexp[1:-1]
                    if match_at_position(inner, text, require_full=True):
                        return True
                else:
                    if match(new_regexp, text):
                        return True
            return False
        except Exception:
            parts = regexp.split("|")
            for part in parts:
                reset_matcher_state()
                if regexp.startswith("^") and regexp.endswith("$"):
                    inner = part[1:-1] if part.startswith("^") and part.endswith("$") else part
                    if match_at_position(inner, text, require_full=True):
                        return True
                else:
                    if match(part, text):
                        return True
            return False

    if regexp.startswith("^") and regexp.endswith("$"):
        inner = regexp[1:-1]
        return match_at_position(inner, text, require_full=True)

    elif regexp.startswith("^"):
        return match_at_position(regexp[1:], text, require_full=False)
    else:
        for i in range(len(text) + 1):
            reset_matcher_state()
            if match_at_position(regexp, text[i:], require_full=False):
                return True
        return False

def find_alternation_bounds(text: str):
    ''''Find the bounds of alternation patterns in a regex string.
    This function finds the starting and ending indices of alternation patterns 
    enclosed in parentheses, such as in "(cat|dog)". It returns the index after
    the opening parenthesis and the index of the closing parenthesis.
    Args:
        text (str): The input string containing alternation pattern(s)
    Returns:
        tuple: A tuple containing:
            - int: Index after the first opening parenthesis
            - int: Index of the last closing parenthesis
    Example:
        >>> find_alternation_bounds("(cat|dog)")
        (1, 8)
        >>> find_alternation_bounds("(a|b|c)")
        (1, 6)      
    Returns index of (first brac + 1) and last brac . If text is "(cat|dog)", it returns idx of c and )
    ''' 
    x = text.find("|")
    split_count = text.count("|")
    last_bar_idx = text.rfind("|")
    last_brac_idx = text.rfind(")", last_bar_idx)
    first_bar_idx = text.find("|")
    first_brac_idx = text.rfind("(", 0, first_bar_idx)
    return first_brac_idx + 1, last_brac_idx

def match_at_position(regexp: str, text: str, require_full: bool=False):
    """Matches a regular expression pattern against text at a specific position.
    This function implements regex pattern matching with support for:
    - Empty patterns
    - End of string anchor ($)
    - Escaped tokens with + quantifier (e.g. \\d+)
    - Normal chars or dot with + quantifier
    - Negated character classes [^abc] with optional +
    - Character classes [abc] with optional +
    - Escaped patterns (\\d, \\w etc)
    - Standard patterns (literal chars and dot)
    Args:
        regexp (str): The regular expression pattern to match
        text (str): The text to match against
        require_full (bool, optional): If True, requires the entire text to match. 
                                     Defaults to False.
    Returns:
        bool: True if pattern matches at current position, False otherwise
    Global Variables:
        debug (bool): If True, prints debug information during matching
    Examples:
        >>> match_at_position('a+', 'aaa')
        True
        >>> match_at_position('\\d+', '123abc') 
        True
        >>> match_at_position('[abc]+', 'cab123')
        True
        >>> match_at_position('[^0-9]+', 'abc123')
        True
    """
    global debug
    # Require_full=True consume entire text
    if debug:
        print(f"reg: '{regexp}', text: '{text}', require_full: {require_full}")
    if regexp == "":
        return (text == "") if require_full else True
    if regexp == "$" and text == "":
        return True
    # Escaped token with +  (e.g. \d+)
    if len(regexp) > 2 and regexp[0] == "\\" and regexp[2] == "+":
        if not text:
            return False
        i = 0
        while i < len(text) and match_escaped_pattern(regexp[:2], text[i:], require_full=False):
            i += 1
        for j in range(i, 0, -1):
            if match_at_position(regexp[3:], text[j:], require_full=require_full):
                return True
        return False
    # Normal character or dot with +
    elif len(regexp) > 1 and regexp[1] == "+":
        if not text:
            return False
        i = 0
        while i < len(text) and match_standard_pattern(regexp[:1], text[i:], require_full=False):
            i += 1
        for j in range(i, 0, -1):
            if match_at_position(regexp[2:], text[j:], require_full=require_full):
                return True
        return False
    
    elif regexp.startswith("[^"):
        end_idx = regexp.find("]")
        if end_idx == -1:
            return False
        char_class = regexp[2:end_idx]
        if end_idx + 1 < len(regexp) and regexp[end_idx + 1] == "+":
            count = 0
            for i in range(len(text)):
                if text[i] not in char_class:
                    count += 1
                else:
                    break            
            if debug:
                print(count, "count")
            if count == 0:
                return False
            return match_at_position(regexp[end_idx + 2:], text[count:], require_full=require_full)

        if text and text[0] not in char_class:
            return match_at_position(regexp[end_idx + 1:], text[1:], require_full=require_full)
        else:
            return False
    
    elif regexp.startswith("["):
        end_idx = regexp.find("]")
        if end_idx == -1:
            return False
        char_class = regexp[1:end_idx]
        if end_idx + 1 < len(regexp) and regexp[end_idx + 1] == "+":
            count = 0
            for i in range(len(text)):
                if text[i] in char_class:
                    count += 1
                else:
                    break
            if debug:
                print(count, "count")
            if count == 0:
                return False

            return match_at_position(regexp[end_idx + 2:], text[count:], require_full=require_full)
        if text and text[0] in char_class:
            return match_at_position(regexp[end_idx + 1:], text[1:], require_full=require_full)
        else:
            return False
    elif regexp.startswith("\\"):
        return match_escaped_pattern(regexp, text, require_full=require_full)
    elif regexp:
        return match_standard_pattern(regexp, text, require_full=require_full)
    return False

        
def match_standard_pattern(regexp:str, text:str, require_full:bool=False):
    """
    Match a standard regular expression pattern against input text.
    This function implements core regex pattern matching functionality, supporting:
    - Literal character matching
    - Dot (.) wildcard matching
    - Optional character matching (?)
    - Capturing groups with alternatives (|)
    Args:
        regexp (str): The regular expression pattern to match
        text (str): The input text to match against
        require_full (bool, optional): If True, requires the entire text to match. Defaults to False.
    Returns:
        bool: True if pattern matches, False otherwise
    Global Variables Used:
        debug: Controls debug output printing
        capture_group_counter: Tracks current capture group number
        capture_groups: Dictionary storing captured text for each group
    Examples:
        >>> match_standard_pattern("a.c", "abc")
        True
        >>> match_standard_pattern("a?b", "b")
        True
        >>> match_standard_pattern("(ab|cd)", "ab")
        True
    """
    global debug
    global capture_group_counter
    global capture_groups
    if debug:
        print("pr norm")
    if not regexp:
        return False   
    if regexp[0] == ".":
        if text:
            return match_at_position(regexp[1:], text[1:], require_full=require_full)
        return False
    elif len(regexp) > 1 and regexp[0].isalpha() and regexp[1] == "?":
        if text and regexp[0] == text[0]:
            if debug:
                print(1)
            return match_at_position(regexp[2:], text[1:], require_full=require_full)
        else:
            if debug:
                print(2)
            return match_at_position(regexp[2:], text, require_full=require_full)
    elif text and regexp[0] == "(":
        snapshot = save_matcher_state()
        prev_capture_counter = snapshot[1]
        group_number = prev_capture_counter + 1
        # greedy capture
        end_idx_of_group = -1
        count = 0
        for i in range(len(regexp)):
            if regexp[i] == "(":
                count += 1
            if regexp[i] == ")":
                count -= 1
            if count == 0:
                end_idx_of_group = i
                break
        if end_idx_of_group == -1:
            return False
        group_content = regexp[1:end_idx_of_group]
        alternatives = split_top_level_alternatives(group_content)  
        for alt in alternatives:
            for j in range(len(text), -1, -1):
                restore_matcher_state(snapshot)
                capture_group_counter = group_number
                if not match_at_position(alt, text[:j], require_full=True):
                    continue
                captured_text = text[:j]
                capture_groups[group_number] = captured_text

                remaining_regexp = regexp[end_idx_of_group + 1:]
                remaining_text = text[j:]

                if match_at_position(remaining_regexp, remaining_text, require_full=require_full):
                    return True
                else:
                    restore_matcher_state(snapshot)
        restore_matcher_state(snapshot)
        return False    
    elif text and regexp:
        if text[0] == regexp[0]:
            return match_at_position(regexp[1:], text[1:], require_full=require_full)
        else:
            return 
    else:
        return False


def match_escaped_pattern(regexp: str, text: str, require_full: bool=False):
    """
    Match text against escaped patterns in regular expressions.
    This function handles special escaped sequences in regular expressions:
    - \\d : Matches any digit character
    - \\N : Matches the content of the Nth capture group
    - \\w : Matches any word character (alphanumeric or underscore)
    Args:
        regexp (str): The regular expression pattern containing escaped sequences
        text (str): The text to match against
        require_full (bool, optional): If True, requires the entire text to match. Defaults to False.
    Returns:
        bool: True if the pattern matches at the current position, False otherwise
    Notes:
        - Uses global variables capture_groups and capture_group_counter
        - Recursively calls match_at_position for remaining pattern matching
    """
    global capture_groups
    global capture_group_counter

    if not regexp:
        return False
    if regexp.startswith("\\d") and text:
        x = text[0].isdigit()
        if x:
            return match_at_position(regexp[2:], text[1:], require_full=require_full)
        else:
            return False
    elif regexp.startswith("\\") and len(regexp) > 1 and regexp[1].isdigit() and text:
        digit = int(regexp[1])
        if digit in capture_groups:
            list_text = capture_groups[digit]
            if text.startswith(list_text):
                return match_at_position(regexp[2:], text[len(list_text):], require_full=require_full)
            else:
                return False
        else:
            return False
    elif regexp.startswith("\\w") and text:
        x = text[0].isalnum() or text[0] == "_"
        if x:
            return match_at_position(regexp[2:], text[1:], require_full=require_full)
        else:
            return False
    return False

def len_consumed(regexp, text):
    max_len = -1
    for i in range(len(text) + 1):
        if match_at_position(regexp, text[:i], require_full=False) and text[i:] == "":
            max_len = i
    return max_len

def search_directory_recursive(dir, regexp=""):
    """
    Recursively searches through directories and files for pattern matches.
    This function traverses through a directory structure and searches for text patterns
    in files using regular expressions. When a match is found, it prints the file path
    and the matching line content.
    Args:
        dir (str): The directory path to start the search from
        regexp (str, optional): Regular expression pattern to match against. Defaults to "".
    Global Variables:
        match_found_in_file (bool): Indicates if any matches were found in the files
    Returns:
        None: Results are printed to stdout
    Example:
        search_directory_recursive("/home/user/documents", r".*error.*")
    """
    global match_found_in_file
    full_dir_path = dir
    for filename in sorted(os.listdir(full_dir_path)):
        full_path = os.path.join(full_dir_path, filename)
        if os.path.isdir(full_path):
            search_directory_recursive(full_path, regexp)
        else:
            with open(full_path, 'r', errors='ignore') as file:
                for line in file:
                    content = line.rstrip('\r\n')
                    if match(regexp, content):
                        match_found_in_file = True
                        print(f"{full_path}:{content}")

def main():
    global match_found_in_file
    if len(sys.argv) < 3:
        print("Usage: program -E pattern [file...]")
        exit(1)

    if sys.argv[1] == "-r":
        if len(sys.argv) < 5 or sys.argv[2] != "-E":
            print("Usage: program -r -E pattern directory/")
            exit(1)
        regexp = sys.argv[3]
        dir = sys.argv[4]
        if not dir.endswith("/"):
            exit(1)
        search_directory_recursive(dir=dir, regexp=regexp)
        if match_found_in_file:
            exit(0)
        exit(1)
    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)
    regexp = sys.argv[2]
    #handle stdin if no files provided
    if len(sys.argv) == 3:
        text = sys.stdin.read()
        if match(regexp, text.rstrip('\n')):
            exit(0)
        exit(1)
    
    #handle file input
    if len(sys.argv) == 4:
        found = False
        with open(sys.argv[3], 'r') as file:
            for line in file:
                if match(regexp, line.rstrip('\n')):
                    found = True
                    print(line, end="")
        exit(0 if found else 1)
    
    #handle multiple files!!!
    if len(sys.argv) > 4:
        found = False
        for filepath in sys.argv[3:]:
            with open(filepath, 'r') as file:
                for line in file:
                    if match(regexp, line.rstrip('\n')):
                        found = True
                        print(f"{filepath}:{line}", end="")
        exit(0 if found else 1)
if __name__ == "__main__":
    main()
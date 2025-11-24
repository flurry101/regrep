# yet another grep implementation

## what's this

just your friendly neighborhood grep implementation in python. it's like regular grep, but with a fresh coat of paint and maybe a few quirks. perfect for when you want to search through files and pretend you're a developer from the 70s.

## try the demo
To see all features in action:
```bash
chmod +x try-it
./try-it.sh
```

## before you dive in

you'll need:
- Python 3.8+ 

## getting started

1. get the code:
```bash
git clone [your-repo-url]
cd grep
```

2. make it executable (yes, chmod +x):
```bash
chmod +x grep.sh
```

3. that's it! no fancy build process, no 500MB of node_modules, just pure python simplicity

## the stuff it can do

- finds text patterns
- understands regex character classes (`\d` for digits, `\w` for words, etc)
- handles quantifiers (`+`, `?`)
- does start/end matching (`^` and `$` - the anchors of regex)
- groups things together with `()` and can do alternation with groups. `(pattern) +` , `(pattern1!pattern2)`
- remembers what it captured (back-references)
- digs through directories recursively too!

## how to use it

search a file:
```bash
./grep.sh -E "whatever" file.txt
```

search multiple files (because one is never enough):
```bash
./grep.sh -E "pattern" file1.txt file2.txt
```

pipe some text through it:
```bash
cat pascal.txt | ./your_program.sh -E "triangle"
echo "does this work?" | ./grep.sh -E "work"
```

recursive search an entire directory:
```bash
./grep.sh -r -E "whoops" ./my_entire_project/
```

## examples

find numbers:
```bash
./grep.sh -E "\d+" numbers.txt
```

find all your TODO comments:
```bash
./grep.sh -r -E "TODO" ./src/
```

match repeated words (like "the the"):
```bash
./grep.sh -E "(the)\1" essay.txt
```

find email-like patterns
```bash
./grep.sh -E "\w+@\w+" contacts.txt
```

## when things go wrong (or ...right)

- exit code 0: "found it!" 🎉
- exit code 1: "nope" 🤷🏻‍♀️ (sorry!)

## contributing

found a bug? want to add a feature? know how to make it faster or better? pull requests welcome.
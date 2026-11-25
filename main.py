#!/usr/bin/env python3
"""One-Line Office Jokes: a single standup joke, at most 200 characters.

The entry lives in a small config mapping; a class owns the gate and the
file round-trip. Python standard library only.
"""

import getopt
import os
import re
import sys
import tempfile

CONFIG = {
    "text": 'Monday standup is fourteen people taking turns saying "no blockers" while visibly, gloriously blocked.',
    "max_chars": 200,
}

SINGLE_LINE = re.compile(r"^[^\r\n]+$")


class Entry:
    def __init__(self, config):
        self.text = config["text"]
        self.limit = config["max_chars"]

    def gate(self):
        if not SINGLE_LINE.match(self.text):
            raise ValueError("entry must be exactly one non-empty line")
        if len(self.text) >= self.limit:
            raise ValueError(f"entry is {len(self.text)} chars, limit under {self.limit}")
        if self.text.strip() != self.text:
            raise ValueError("entry has stray surrounding whitespace")

    def destination(self):
        return os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "."), "entry.txt")

    def write(self, path):
        self.gate()
        folder = os.path.dirname(os.path.abspath(path))
        os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as out:
            out.write(self.text + "\n")
        self.verify(path)

    def verify(self, path):
        with open(path, "rb") as raw:
            blob = raw.read()
        if blob != (self.text + "\n").encode("utf-8"):
            raise ValueError("entry.txt bytes differ from the entry line")
        if blob.endswith(b"\n\n"):
            raise ValueError("entry.txt must end with exactly one newline")
        self.gate()
        return blob

    def check(self, path):
        if not os.path.exists(path):
            raise ValueError(f"no file at {path}")
        blob = self.verify(path)
        print(f"check OK: {path} valid, {len(self.text)} chars, {len(blob)} bytes")

    def self_test(self):
        self.gate()
        with tempfile.TemporaryDirectory() as yard:
            probe = os.path.join(yard, "entry.txt")
            self.write(probe)
            self.check(probe)
        print(f"self-test OK: 1 line, {len(self.text)} chars")


def usage():
    print("usage: main.py [--self-test | --check]")
    return 2


def main(argv):
    try:
        opts, _rest = getopt.getopt(argv, "", ["self-test", "check", "help"])
    except getopt.GetoptError as err:
        print(err, file=sys.stderr)
        return usage()
    entry = Entry(CONFIG)
    names = {name.lstrip("-") for name, _value in opts}
    if "help" in names:
        return usage()
    if "self-test" in names:
        entry.self_test()
    elif "check" in names:
        entry.check(entry.destination())
    else:
        entry.write(entry.destination())
        print(f"wrote {entry.destination()} ({len(entry.text)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

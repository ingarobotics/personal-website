#!/usr/bin/env python3
"""Bake content.js edits permanently into the HTML files.

Usage:
    python3 bake.py            # apply edits into the .html files
    python3 bake.py --dry-run  # show what would change, write nothing

After baking, the HTML files contain your edited text directly, so the
edit tooling (editor.js / content.js) is no longer needed to display it.
Review changes with `git diff` before committing.
"""
import os, sys, json
from html.parser import HTMLParser

CONTENT_FILE = 'content.js'
PREFIX = 'window.CONTENT = '
VOID = {'meta', 'link', 'hr', 'br', 'img', 'input', 'area',
        'base', 'col', 'embed', 'source', 'track', 'wbr'}
EDITABLE = {'h2', 'p', 'li'}


def read_content():
    with open(CONTENT_FILE) as f:
        text = f.read().strip()
    return json.loads(text[len(PREFIX):].rstrip(';').strip())


class EditableFinder(HTMLParser):
    """Finds the same elements editor.js getEditables() selects, in order:
    .content-block h2, .content-block p, .content-block li:not(.post-item)
    Records (inner_start, inner_end) char offsets for each."""

    def __init__(self, raw):
        super().__init__(convert_charrefs=False)
        self.raw = raw
        # line -> absolute char offset
        self.line_off = [0]
        for line in raw.splitlines(keepends=True):
            self.line_off.append(self.line_off[-1] + len(line))
        self.stack = []            # [(tag, is_content_block)] of open elements
        self.capturing = None      # tag name currently being captured
        self.cap_depth = 0
        self.cap_start = 0
        self.spans = []            # list of (start, end) inner ranges, in order

    def _abs(self):
        ln, col = self.getpos()
        return self.line_off[ln - 1] + col

    @staticmethod
    def _has_class(attrs, name):
        for k, v in attrs:
            if k == 'class' and v and name in v.split():
                return True
        return False

    def _inside_cb(self):
        return any(is_cb for _, is_cb in self.stack)

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        inside_cb = self._inside_cb()
        self.stack.append((tag, self._has_class(attrs, 'content-block')))

        if self.capturing:
            if tag == self.capturing:
                self.cap_depth += 1
            return

        if (inside_cb and tag in EDITABLE
                and not (tag == 'li' and self._has_class(attrs, 'post-item'))):
            lt = self._abs()
            gt = self.raw.index('>', lt)
            self.capturing = tag
            self.cap_depth = 1
            self.cap_start = gt + 1

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.capturing and tag == self.capturing:
            self.cap_depth -= 1
            if self.cap_depth == 0:
                self.spans.append((self.cap_start, self._abs()))
                self.capturing = None
        # pop the matching open element
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def find_spans(raw):
    f = EditableFinder(raw)
    f.feed(raw)
    return f.spans


def bake_file(page, edits, dry_run):
    if not os.path.exists(page):
        print(f'  skip {page} (file not found)')
        return 0
    with open(page) as fh:
        raw = fh.read()
    spans = find_spans(raw)
    repls = []
    for idx_str, new_html in edits.items():
        i = int(idx_str)
        if i >= len(spans):
            print(f'  warn {page}: index {i} out of range (has {len(spans)})')
            continue
        s, e = spans[i]
        if raw[s:e] != new_html:
            repls.append((s, e, new_html))
    if not repls:
        print(f'  {page}: nothing to change')
        return 0
    for s, e, new_html in sorted(repls, reverse=True):
        raw = raw[:s] + new_html + raw[e:]
    if dry_run:
        print(f'  {page}: would update {len(repls)} element(s)')
    else:
        with open(page, 'w') as fh:
            fh.write(raw)
        print(f'  {page}: updated {len(repls)} element(s)')
    return len(repls)


def main():
    dry = '--dry-run' in sys.argv
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        os.chdir(sys.argv[1])
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    content = read_content()
    if not content:
        print('content.js is empty — nothing to bake.')
        return
    total = 0
    print(('DRY RUN — ' if dry else '') + 'Baking edits:')
    for page, edits in content.items():
        total += bake_file(os.path.basename(page), edits, dry)
    if dry:
        print(f'\n{total} element(s) would change. Re-run without --dry-run to apply.')
    else:
        print(f'\nDone — {total} element(s) baked. Review with: git diff')
        print('You can now clear content.js (echo "window.CONTENT = {};" > content.js)')


if __name__ == '__main__':
    main()

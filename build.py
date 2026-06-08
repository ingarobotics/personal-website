#!/usr/bin/env python3
"""Run after adding/editing posts: python3 build.py"""
import os, json, re

POSTS_DIR = 'posts'

def parse_frontmatter(content):
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        return {}, content
    fm = {}
    for line in match.group(1).splitlines():
        if ':' in line:
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip()
    return fm, content[match.end():]

posts = []
for fname in sorted(os.listdir(POSTS_DIR)):
    if not fname.endswith('.md'):
        continue
    slug = fname[:-3]
    with open(os.path.join(POSTS_DIR, fname)) as f:
        fm, body = parse_frontmatter(f.read())
    posts.append({
        'title': fm.get('title', slug),
        'date':  fm.get('date', ''),
        'slug':  slug,
        'markdown': body.strip(),
    })

posts.sort(key=lambda p: p['date'], reverse=True)

with open('posts-data.js', 'w') as f:
    f.write('window.POSTS = ' + json.dumps(posts, indent=2) + ';\n')

print(f'Built {len(posts)} post(s) → posts-data.js')

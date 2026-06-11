#!/usr/bin/env python3
"""Run after adding/editing posts: python3 build.py

Generates:
  posts-data.js   — window.POSTS array with title/date/slug/markdown
  <slug>.html     — one static page per post, slug = .md filename stem
                    URL: /<slug>   (via vercel cleanUrls + serve.py fallback)
"""
import os, json, re

POSTS_DIR = 'posts'
TEMPLATE  = 'post.html'

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


# --- 1. Read all posts ---
posts = []
for fname in sorted(os.listdir(POSTS_DIR)):
    if not fname.endswith('.md'):
        continue
    slug = fname[:-3]
    with open(os.path.join(POSTS_DIR, fname)) as f:
        fm, body = parse_frontmatter(f.read())
    posts.append({
        'title':    fm.get('title', slug),
        'date':     fm.get('date', ''),
        'slug':     slug,
        'markdown': body.strip(),
    })

posts.sort(key=lambda p: p['date'], reverse=True)

# --- 2. Write posts-data.js ---
with open('posts-data.js', 'w') as f:
    f.write('window.POSTS = ' + json.dumps(posts, indent=2) + ';\n')

# --- 3. Generate one <slug>.html per post from the post.html template ---
with open(TEMPLATE) as f:
    template = f.read()

# Cleanup: remove any per-slug files in root that no longer correspond to a post
current_slugs = {p['slug'] for p in posts}
RESERVED = {'index.html', 'writing.html', 'bookshelf.html', 'post.html'}
for fname in os.listdir('.'):
    if not fname.endswith('.html') or fname in RESERVED:
        continue
    stem = fname[:-5]
    # Heuristic: a file at root with stem matching no current post AND containing the renderer marker is a stale generated page
    if stem not in current_slugs:
        try:
            with open(fname) as fh:
                if 'window.POST_SLUG' in fh.read():
                    os.remove(fname)
        except Exception:
            pass

# Write current per-post pages: inject `window.POST_SLUG = "<slug>"` before posts-data.js
for p in posts:
    page_html = template.replace(
        '<script src="posts-data.js"></script>',
        f'<script>window.POST_SLUG = "{p["slug"]}";</script>\n  <script src="posts-data.js"></script>',
        1,
    )
    with open(f"{p['slug']}.html", 'w') as f:
        f.write(page_html)

print(f"Built {len(posts)} post(s):")
print(f"  posts-data.js")
for p in posts:
    print(f"  {p['slug']}.html   →   /{p['slug']}")

#!/usr/bin/env python3
"""Write the latest Substack posts into the "Writing" block of index.html.

Runs daily in GitHub Actions (.github/workflows/writing.yml) and can be run by hand:

    python3 scripts/update_writing.py
    python3 scripts/update_writing.py --feed https://other.substack.com/feed --file /tmp/index.html

Standard library only. The page is rewritten only between the two markers below, and only
when the feed was read successfully and contains posts: a Substack outage or an empty feed
leaves the live list as it is.
"""
import argparse, html, re, sys, urllib.request
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree

PUBLICATION = "https://robertnmackenzie.substack.com"
SHOW = 3
START, END = "<!-- writing:start -->", "<!-- writing:end -->"


def fetch_posts(feed_url):
    req = urllib.request.Request(feed_url, headers={"User-Agent": "mackenzie-advisory.ch writing list"})
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ElementTree.fromstring(r.read())
    posts = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title or not link:
            continue
        try:
            date = parsedate_to_datetime(item.findtext("pubDate") or "")
        except (TypeError, ValueError):
            continue
        posts.append({"title": title, "link": link, "date": date,
                      "subtitle": (item.findtext("description") or "").strip()})
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def render(posts):
    rows = []
    for p in posts[:SHOW]:
        meta = p["date"].strftime("%-d %B %Y")
        sub = p["subtitle"]
        if len(sub) > 150:
            sub = sub[:150].rsplit(" ", 1)[0].rstrip(",;:.") + "…"
        if sub:
            meta += f" &middot; {html.escape(sub)}"
        rows.append(
            f'        <li><span class="mark"></span><a href="{html.escape(p["link"])}" target="_blank" rel="noopener">'
            f'{html.escape(p["title"])}</a><span class="w-meta">{meta}</span></li>')
    return "\n".join([
        START,
        '    <hr class="rule">',
        "",
        '    <section class="pad" id="writing">',
        '      <p class="label"><span class="mark"></span>Writing</p>',
        '      <ul class="eng writing">',
        *rows,
        "      </ul>",
        '      <p class="writing-links">'
        f'<a href="{PUBLICATION}/archive" target="_blank" rel="noopener">All articles</a>'
        f'<a href="{PUBLICATION}/subscribe" target="_blank" rel="noopener">Subscribe</a></p>',
        "    </section>",
        "",
        "    " + END,
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feed", default=f"{PUBLICATION}/feed")
    ap.add_argument("--file", default=str(Path(__file__).resolve().parent.parent / "index.html"))
    a = ap.parse_args()

    page = Path(a.file).read_text(encoding="utf-8")
    block = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not block.search(page):
        sys.exit(f"Markers {START} … {END} not found in {a.file}")

    try:
        posts = fetch_posts(a.feed)
    except Exception as e:  # network, HTTP or XML error: keep the page as it is
        print(f"Feed not readable ({e}); page unchanged.")
        return
    if not posts:
        print("Feed has no posts; page unchanged.")
        return

    new = block.sub(lambda _: render(posts), page, count=1)
    if new == page:
        print("Writing list already up to date.")
        return
    Path(a.file).write_text(new, encoding="utf-8")
    print("Writing list updated: " + " | ".join(p["title"] for p in posts[:SHOW]))


if __name__ == "__main__":
    main()

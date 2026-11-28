#!/usr/bin/env python3
"""Write the Substack posts into the "Insights" block of index.html.

Runs daily in GitHub Actions (.github/workflows/insights.yml) and can be run by hand:

    python3 scripts/update_insights.py
    python3 scripts/update_insights.py --feed https://other.substack.com/feed --file /tmp/index.html

The three newest posts are listed; the rest sit behind a "Show all" toggle (<details>, so it
works without JavaScript). LinkedIn figures come from data/engagement.json, keyed by Substack
slug, because LinkedIn cannot be read by the daily job.

Standard library only. The page is rewritten only between the two markers below, and only
when the feed was read successfully and contains posts: a Substack outage or an empty feed
leaves the live list as it is.
"""
import argparse, html, json, re, sys, urllib.request
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree

PUBLICATION = "https://robertnmackenzie.substack.com"
SHOW = 3
START, END = "<!-- insights:start -->", "<!-- insights:end -->"
ROOT = Path(__file__).resolve().parent.parent


def fetch_posts(feed_url):
    req = urllib.request.Request(feed_url, headers={"User-Agent": "mackenzie-advisory.ch insights list"})
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
        # Substack's feed sometimes encodes entities twice (&amp;#8217;): decode until stable
        clean = lambda s: (lambda u: u if u == s else clean(u))(html.unescape(s))
        posts.append({"title": clean(title), "link": link, "date": date,
                      "subtitle": clean((item.findtext("description") or "").strip())})
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def short(n):
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def stats_line(stats):
    if not stats:
        return ""
    parts = [f"{short(stats['impressions'])} impressions"] if stats.get("impressions") else []
    parts += [f"{stats[k]} {k}" for k in ("reactions", "comments") if stats.get(k)]
    return f'<span class="w-stats">{" &middot; ".join(parts)} on LinkedIn</span>' if parts else ""


def row(p, engagement):
    sub = p["subtitle"]
    if len(sub) > 150:
        sub = sub[:150].rsplit(" ", 1)[0].rstrip(",;:.") + "…"
    meta = p["date"].strftime("%-d %B %Y") + (f" &middot; {html.escape(sub)}" if sub else "")
    slug = p["link"].rstrip("/").rsplit("/", 1)[-1]
    return (f'        <li><span class="mark"></span><div><a href="{html.escape(p["link"])}" target="_blank" rel="noopener">'
            f'{html.escape(p["title"])}</a><span class="w-meta">{meta}</span>{stats_line(engagement.get(slug))}</div></li>')


def render(posts, engagement):
    lines = [START,
             '    <hr class="rule">',
             "",
             '    <section class="pad" id="insights">',
             '      <p class="label"><span class="mark"></span>Insights</p>',
             '      <p class="insights-links">'
             f'<a href="{PUBLICATION}/archive" target="_blank" rel="noopener">All articles on Substack</a>'
             f'<a href="{PUBLICATION}/subscribe" target="_blank" rel="noopener">Subscribe</a></p>',
             '      <ul class="eng insights">',
             *[row(p, engagement) for p in posts[:SHOW]],
             "      </ul>"]
    if len(posts) > SHOW:
        lines += ['      <details class="more">',
                  '        <summary><span class="when-closed">Show all articles</span>'
                  '<span class="when-open">Show fewer</span></summary>',
                  '        <ul class="eng insights">',
                  *[row(p, engagement) for p in posts[SHOW:]],
                  "        </ul>",
                  "      </details>"]
    lines += ["    </section>",
              "",
              "    " + END]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feed", default=f"{PUBLICATION}/feed")
    ap.add_argument("--file", default=str(ROOT / "index.html"))
    ap.add_argument("--engagement", default=str(ROOT / "data/engagement.json"))
    a = ap.parse_args()

    page = Path(a.file).read_text(encoding="utf-8")
    block = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not block.search(page):
        sys.exit(f"Markers {START} … {END} not found in {a.file}")
    try:
        engagement = json.loads(Path(a.engagement).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        engagement = {}

    try:
        posts = fetch_posts(a.feed)
    except Exception as e:  # network, HTTP or XML error: keep the page as it is
        print(f"Feed not readable ({e}); page unchanged.")
        return
    if not posts:
        print("Feed has no posts; page unchanged.")
        return

    new = block.sub(lambda _: render(posts, engagement), page, count=1)
    if new == page:
        print("Insights list already up to date.")
        return
    Path(a.file).write_text(new, encoding="utf-8")
    print(f"Insights list updated: {len(posts)} posts, newest: {posts[0]['title']}")


if __name__ == "__main__":
    main()

# MacKenzie Executive Advisory — website

Static one-page site. No build step: `index.html` plus `img/`.

Live at **https://mackenzie-advisory.ch** (and `www.`). HTTPS enforced.

## Editing
Everything lives in `index.html` — CSS at the top, content below. Colours and type are
CSS custom properties on `:root`; `--accent` / `--block-accent` control the green.

## Images
| File | Where it appears |
|---|---|
| `m-robot.jpg`, `m-panel.jpg`, `m-stage.jpg`, `m-davos.jpg` | hero mosaic |
| `headshot.jpg` | About |
| `show-*.jpg` (+ `-1200` versions) | full-width band: slideshow of recent engagements and appearances |
| `band-teaching.jpg` | not used since the slideshow (kept; was the single band photo) |
| `logo-horizontal*.svg`, `monogram.svg` | header, footer, favicon |

Originals: `../Media/photos/events/` and `../Media/photos/portraits/`. Logo masters: `../Media/`.

### Slideshow
One `<img>` per photo inside `.show-frame` in `index.html`; the first one carries `class="on"`.
Each line sets its crop focus (`style="--pos:50% 40%"`, horizontal then vertical) and its
caption (`data-cap`). Indicators and pause button are built by the script at the bottom of
the page. Timing: 7 s per photo (`--dwell` on `.band figure`), 1.8 s crossfade.

| Slide image | Original in `../Media/photos/events/` |
|---|---|
| `show-davos-2026` | `2026.01 World Economic Forum - Robotics, Physical AI Roundtable AI House.png` (badges already removed) |
| `show-summit-2026` | `2026.11 Machine Intelligence Summit - Moderator 02.jpg` |
| `show-lab-2026` | `2026.11 Nio Robotics - Advisor 02.jpg` |
| `show-ceibs-2026` | `2026.06 CEIBS - Robotics & Executive Thinking.JPG` |
| `show-keynote-2026` | `2026.03 Robotics on the Rise - Keynote (Bild-4).jpg` |
| `show-pingpong-2026` | `2026.06 - Playing against a ping pong robot.png` |
| `show-stuttgart-2026` | `2026.02 CEIBS Stuttgart - Global Executive MBA 01.jpeg` |
| `show-reinvent-2023` | `2023.11 AWS reInvent - Speaking 01 (IMG-20231128-WA0014).jpg` |

To add a photo: export a large version (2000–2400 px wide, or the original width if smaller)
and a 1200 px version, JPEG quality ~75, **without metadata** — phone photos carry GPS
coordinates. Then copy an existing `<img>` line and adjust `--pos` until the person is framed
at both desktop and phone widths.

## Deploy
Push to `main` on `github.com/robert-n-mackenzie/mackenzie-advisory-website`
(public repo — GitHub Pages requires public on the free plan). Pages rebuilds
automatically, usually within a minute.

The `CNAME` file at the repo root holds the bare domain. Do not delete it —
GitHub rewrites it from Settings → Pages → Custom domain, and without it the
site 404s on the custom domain.

## How the domain is wired — read before touching DNS

Registrar and DNS: **Infomaniak**. Site: **GitHub Pages**. Mail: **Infomaniak**.
All three coexist in one DNS zone that Infomaniak hosts. Nameservers were
deliberately NOT delegated elsewhere.

Infomaniak Manager → Domain → mackenzie-advisory.ch → **«Change the DNS zone»**
(this is the record editor, despite the name).

| Purpose | Records |
|---|---|
| Site, apex | 4 × A → `185.199.108.153`, `.109.153`, `.110.153`, `.111.153` |
| Site, apex, IPv6 | 4 × AAAA → `2606:50c0:8000::153` … `8003::153` |
| Site, www | CNAME `www` → `robert-n-mackenzie.github.io.` |
| Mail | MX → `mta-gw.infomaniak.ch` (prio 5), SPF TXT, DKIM TXT, DMARC TXT, 6 × SRV, `autoconfig` + `autodiscover` CNAME |

**Never use «Modify DNS servers».** That delegates the whole zone away and takes
the mailbox with it. DNSSEC is enabled, which makes a botched nameserver change
fail closed — the domain would resolve nowhere at all.

Deleting or editing a web A/AAAA record cannot affect mail. The two are
independent record sets.

## Domain and mailbox facts
- Registered 18.09.2026, expires 18.09.2027, **auto-renewal ON**, DNSSEC ON.
- Holder: Robert MacKenzie personally (an Einzelfirma cannot hold a domain).
  Organisation field carries the firm name.
- Registry contact is a **non-domain address** (hotmail) on purpose: renewal and
  recovery mail must still arrive when the domain itself is broken. Do not
  change it to `robert@mackenzie-advisory.ch`.
- Mailbox `robert@mackenzie-advisory.ch` is Infomaniak's free **Starter** tier —
  one address on the own domain, free as long as the domain is paid. A *second*
  address (e.g. `info@`) means paying for kSuite Standard; check whether an
  alias on Starter suffices before buying one.
- Infomaniak invoices for the domain/mail live in the parent folder — business
  expense, hand to the Treuhänder with the year-end figures.

## Insights section (Substack)
Header menu (Services · About · Insights · Contact) jumps to the section ids on the page.
The block between `<!-- insights:start -->` and `<!-- insights:end -->` in `index.html` is generated:
`scripts/update_insights.py` reads https://robertnmackenzie.substack.com/feed, lists the three newest
posts and puts the rest behind a "Show all" toggle (`<details>`, works without JavaScript). Under each
article it shows LinkedIn figures from `data/engagement.json` (keyed by Substack slug; refreshed by hand
from LinkedIn post analytics, last 28.11.2026). An unreachable or empty feed leaves the page unchanged.
Run it by hand with `python3 scripts/update_insights.py`, then commit and push.

`.github/workflows/insights.yml` (local, **not yet on GitHub**) runs the script daily at 06:00 UTC and
commits only on change. The push token in `../.secrets/` has no "workflow" permission, so this file
must be added through the GitHub web UI or after granting the token Workflows: read/write.

## Not in this repo
`../.secrets/github.token` — the push credential. Never commit it.

The macOS Keychain also holds a GitHub login for this account, but it has **no write access**
to this repo (push fails with 403). Push with the token instead, read from the file and never
echoed:

```
git -c http.postBuffer=157286400 -c http.version=HTTP/1.1 -c credential.helper= -c credential.helper='!f(){ echo username=x-access-token; printf "password=%s\n" "$(tr -d "[:space:]" < ../.secrets/github.token)"; }; f' push origin main
```

The two `http.*` settings matter for pushes with new photos: without them a push of a few MB
fails with "the remote end hung up unexpectedly" and nothing arrives on GitHub.

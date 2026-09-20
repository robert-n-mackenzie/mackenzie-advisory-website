# MacKenzie Executive Advisory — website

Static one-page site. No build step: `index.html` plus `img/`.

## Editing
Everything lives in `index.html` — CSS at the top, content below. Colours and type are
CSS custom properties on `:root`; `--accent` / `--block-accent` control the green.

## Images
| File | Where it appears |
|---|---|
| `m-robot.jpg`, `m-panel.jpg`, `m-stage.jpg`, `m-davos.jpg` | hero mosaic |
| `headshot.jpg` | About |
| `band-teaching.jpg` | full-width band |
| `logo-horizontal*.svg`, `monogram.svg` | header, footer, favicon |

Originals: `../Media/photos/`. Logo masters: `../Media/`.

## Deploy
Push to `main`. Host (Cloudflare Pages or GitHub Pages) rebuilds automatically.
For a custom domain on GitHub Pages, add a `CNAME` file containing the bare domain.

## Not in this repo
`../.secrets/github.token` — the push credential. Never commit it.

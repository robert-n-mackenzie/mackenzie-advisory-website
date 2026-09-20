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
| `band-teaching.jpg` | full-width band |
| `logo-horizontal*.svg`, `monogram.svg` | header, footer, favicon |

Originals: `../Media/photos/`. Logo masters: `../Media/`.

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

## Not in this repo
`../.secrets/github.token` — the push credential. Never commit it.

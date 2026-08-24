# Mentec Business Advisory — Redesign

A static, multi-page redesign concept for [mentec.com.au](https://www.mentec.com.au/):
refreshed brand styling (same logo mark and blue/grey palette as the current
site, sharpened), a mega nav, and dedicated pages for Services, Approach,
Case Studies, Clients, About, Insights and Contact.

## Status: live

Prepped for the real domain: `BASE_URL` is `https://www.mentec.com.au/`,
`NOINDEX` is off, `robots.txt` allows crawling, and a `CNAME` file
(`www.mentec.com.au`) is committed for GitHub Pages' custom domain
feature. DNS/hosting still needs pointing at this GitHub Pages deploy for
the domain to actually resolve here — see "Going live for real" below.

Content notes:
- The five clients on the Clients / Case Studies pages (Siric Architects,
  BuyersCircle, Excitation, COAX, BrandMarkets) and the contact details in
  the footer are pulled from the live site.
- Testimonials are real, attributed quotes (Lance Eerhard/BuyersCircle,
  Daniel Siric/Siric Architects, Joel/COAX), used with their written
  approval. No fabricated quotes are attributed to anyone on this site.

## Structure

Plain HTML/CSS/JS, no build step required to serve it. Clean URLs: every
page but home is its own directory with an `index.html` inside it, so
nothing is ever linked with a `.html` extension:

```
index.html                     home — /
services/index.html            /services/
approach/index.html            /approach/
case-studies/index.html        /case-studies/
clients/index.html             /clients/
about/index.html               /about/
insights/index.html            /insights/
contact/index.html             /contact/
assets/style.css                shared styles (light + dark mode)
assets/site.js                  mega nav, mobile menu, scroll-reveal, chart
assets/favicon.*                 generated from the logo mark
```

## Editing content

Don't hand-edit the generated `index.html` files directly. Edit
`tools/build.py` (page copy, the `CLIENTS`/`TESTIMONIALS` lists, contact
details, meta titles/descriptions) and regenerate:

```bash
python3 tools/build.py
```

Every internal link in the templates is written as a plain slug (e.g.
`href="services.html"`) — `write()` rewrites those into the correct
`../`-relative clean-URL path for wherever that page actually lives on
disk, in one place (`rewrite_links()`). You never need to hand-write a
relative path when adding content.

To preview locally:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Going live for real

1. ~~Set `BASE_URL` in `tools/build.py` to the real domain and set
   `NOINDEX = False`, then rerun the build.~~ Done.
2. ~~Remove the `Disallow: /` from `robots.txt`.~~ Done.
3. Point `www.mentec.com.au`'s DNS (a CNAME record) at
   `breezyconsulting.github.io`, and in the GitHub repo's Settings → Pages,
   confirm the custom domain is `www.mentec.com.au` and enable "Enforce
   HTTPS" once DNS has propagated (GitHub provisions the certificate
   automatically once it can verify the CNAME). Set up 301 redirects from
   any old indexed Wix URLs if their paths differ, and redirect the bare
   `mentec.com.au` apex to `www.mentec.com.au` at the registrar/DNS level.

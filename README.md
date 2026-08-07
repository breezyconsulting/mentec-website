# Mentec Business Advisory — Redesign

A static, multi-page redesign concept for [mentec.com.au](https://www.mentec.com.au/):
refreshed brand styling (same logo mark and blue/grey palette as the current
site, sharpened), a mega nav, and dedicated pages for Services, Approach,
Case Studies, Clients, About, Insights and Contact.

## Status: staging preview

This is **not** the live site. It's deployed separately (GitHub Pages) so it
can be reviewed before anything touches the real domain. `robots.txt`
disallows all crawling and every page carries a `noindex` meta tag, so it
won't compete with the real mentec.com.au in search results while it's
being reviewed.

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

When this is ready to replace the live site:
1. Set `BASE_URL` in `tools/build.py` to the real domain and set
   `NOINDEX = False`, then rerun the build.
2. Remove the `Disallow: /` from `robots.txt`.
3. Point the real domain's DNS/hosting at this build (or copy these files
   into the existing host), and set up 301 redirects from any old indexed
   Wix URLs if their paths differ.

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
- Testimonials are placeholder copy, clearly marked "Sample — replace with
  real quote." No fabricated quotes are presented as genuine anywhere on
  the site.

## Structure

Plain HTML/CSS/JS, no build step required to serve it:

```
index.html, services.html, approach.html, case-studies.html,
clients.html, about.html, insights.html, contact.html
assets/style.css      shared styles (light + dark mode)
assets/site.js        mega nav, mobile menu, scroll-reveal
assets/favicon.*       generated from the logo mark
```

## Editing content

Don't hand-edit the eight `.html` files directly — they're generated. Edit
`tools/build.py` (page copy, the `CLIENTS` list, contact details, meta
titles/descriptions) and regenerate:

```bash
python3 tools/build.py
```

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
4. Swap the placeholder testimonials for real client quotes.

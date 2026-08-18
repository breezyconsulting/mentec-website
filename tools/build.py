#!/usr/bin/env python3
"""Static site generator for the Mentec Business Advisory redesign.
Run: python3 tools/build.py
Regenerates the .html files in the repo root from the templates below.
Kept in the repo so future content edits don't require hand-editing eight
files with duplicated nav/footer markup.
"""
import os, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://breezyconsulting.github.io/mentec-website/"  # replaced by deploy.sh once the Pages URL is known
NOINDEX = True  # staging deploy — flip to False (and drop robots.txt disallow) at real go-live

SITE_NAME = "Mentec Business Advisory"
ADDRESS = "Suite 6.01, 7 Maitland Pl, Norwest NSW 2153"
EMAIL = "info@mentec.com.au"
PHONE = "+61 414 674 353"
PHONE_TEL = "+61414674353"
LINKEDIN_URL = "https://au.linkedin.com/in/joe-siric-1985532"

CLIENTS = [
    {
        "id": "siric-architects",
        "name": "Siric Architects",
        "category": "Architecture — Premium Residential, Industrial & Commercial",
        "summary": "Founded by Daniel to provide premium architectural services, specialising in professional offices and premium residential developments.",
        "engagement": "With the engagement of Mentec, targeted business development activity was shifted to focus on commercial projects, which were more profitable and efficient.",
        "result": "This new focus on commercial clients has seen 80% of revenue now derived from that sector, in turn allowing the Siric team to grow.",
        "stat_value": "80%",
        "stat_label": "of revenue now from commercial projects",
        "featured": True,
        "logo": None,  # pending — real Siric Architects mark not supplied yet
    },
    {
        "id": "buyerscircle",
        "name": "BuyersCircle Pty Ltd",
        "category": "Social e-commerce Platform & Retailer",
        "summary": "Established to target the online e-commerce market, utilising in-house developed platform systems. The business strategy needed to be strengthened and acquisition methods needed to be coordinated, and the leadership needed direction.",
        "engagement": "With a need for change, Mentec formulated a business plan to target the wholesale sector as a simpler variant of the SaaS product.",
        "result": "This led to new funding models and a more attractive investment proposition.",
        "stat_value": None, "stat_label": None,
        "featured": False,
        "logo": "buyerscircle.png",
    },
    {
        "id": "excitation",
        "name": "Excitation Pty Ltd",
        "category": "Agile Online Marketing Agency",
        "summary": "Driven by data-supported results. Although the brand and product is strong, Excitation needed to bring in business skills to elevate its operations and business development.",
        "engagement": "Mentec introduced resourcing based on an understanding of small-to-medium enterprise business pillars, stabilising the business and setting it up for success. Through a rebuild, Mentec is currently working on the required Operational and Financial pillars.",
        "result": "Core people introduced to drive methodology and structured practices.",
        "stat_value": None, "stat_label": None,
        "featured": False,
        "logo": "excitation.png",
    },
    {
        "id": "coax",
        "name": "Coax AU Pty Ltd",
        "category": "Simplified Business Communications",
        "summary": "Coax was born out of the belief that communication for your business should be as simple as possible.",
        "engagement": "Working with Mentec, through strategic planning and financial management, Coax has been able to offer targeted, tailored help for the startup small business.",
        "result": "Faster conversations, which in turn lead to more sales and stronger relationships.",
        "stat_value": None, "stat_label": None,
        "featured": False,
        "logo": "coax.png",
    },
    {
        "id": "brandmarkets",
        "name": "BrandMarkets",
        "category": "E-commerce Platform Retailer",
        "summary": "Established to deliver a wide range of brand name, designer, and high quality products across categories such as homewares, fashion, accessories and beauty.",
        "engagement": "Engagement in progress.",
        "result": "",
        "stat_value": None, "stat_label": None,
        "featured": False,
        "logo": "brandmarkets.png",
    },
]

# Real clients, quoted with their written approval to use this wording.
TESTIMONIALS = [
    {
        "quote": "Within the first quarter we finally had reporting we could hand to our bank without scrambling. That alone changed how we made decisions.",
        "name": "Lance Eerhard", "title": "CEO", "company": "BuyersCircle",
    },
    {
        "quote": "Every other advisor we spoke to sold a strategy document. Mentec was the only one still in the building three months later.",
        "name": "Daniel Siric", "title": "Director", "company": "Siric Architects",
    },
    {
        "quote": "Having someone with equity in the outcome changes the conversation. It stopped feeling like billable hours and started feeling like a partner.",
        "name": "Joel Fuller", "title": "CEO/Co Founder", "company": "COAX",
    },
]

def testimonials_grid():
    cards = ""
    for t in TESTIMONIALS:
        cards += f"""      <div class="testi-card">
        <blockquote>&ldquo;{t['quote']}&rdquo;</blockquote>
        <div class="testi-who"><strong>{t['name']}</strong><span>{t['title']}, {t['company']}</span></div>
      </div>
"""
    return cards

PAGES = ["home","services","approach","case-studies","clients","about","insights","contact",
         "digital-strategy-execution","ecommerce-strategy-execution","customer-experience-design",
         "equity-retainer"]
# Clean URLs, arbitrary nesting: SLUG_DIR is the single source of truth for where a
# page lives on disk ("." = site root). Every page but home is a directory with an
# index.html inside it, so nothing is ever linked with a ".html" extension. The three
# service sub-pages nest one level deeper, under services/; equity-retainer nests
# under approach/.
SLUG_DIR = {
    "home": ".",
    "services": "services", "approach": "approach", "case-studies": "case-studies",
    "clients": "clients", "about": "about", "insights": "insights", "contact": "contact",
    "digital-strategy-execution": "services/digital-strategy-execution",
    "ecommerce-strategy-execution": "services/ecommerce-strategy-execution",
    "customer-experience-design": "services/customer-experience-design",
    "equity-retainer": "approach/equity-retainer",
}
SLUG_TO_FILE = {slug: (d + "/index.html" if d != "." else "index.html") for slug, d in SLUG_DIR.items()}
TITLES = {
    "home": "Virtual CFO Services Sydney | Mentec Business Advisory",
    "services": "Virtual CFO & Business Advisory Services | Mentec Business Advisory",
    "approach": "Our Approach | Strategise, Plan, Execute — Mentec Business Advisory",
    "case-studies": "Case Studies | Real Partner Results — Mentec Business Advisory",
    "clients": "Clients | Who We Partner With — Mentec Business Advisory",
    "about": "About | Joe Siric, Virtual CFO & Founder — Mentec Business Advisory",
    "insights": "Insights | Virtual CFO & Business Advisory Articles — Mentec",
    "contact": "Contact | Book a Virtual CFO Introductory Call — Mentec, Sydney",
    "digital-strategy-execution": "Digital Strategy & Execution — Mentec Business Advisory",
    "ecommerce-strategy-execution": "Ecommerce Strategy & Execution — Mentec Business Advisory",
    "customer-experience-design": "Customer & User Experience Design — Mentec Business Advisory",
    "equity-retainer": "Equity & Retainer | How the Trade-Off Works — Mentec Business Advisory",
}
DESCRIPTIONS = {
    "home": "Virtual CFO leadership and an equity-aligned partnership for ambitious Sydney and Australia-wide SMEs — 30+ years of senior CFO experience, from strategy through to hands-on execution.",
    "services": "CFO leadership (virtual/fractional), strategic planning, financial management and execution — six services for SMEs, tailored per partner. Based in Sydney, working Australia-wide.",
    "approach": "Why Mentec takes an equity position instead of billing by the hour, and how a partnership moves from strategy to a delivered, working plan.",
    "case-studies": "How Mentec's partnership model has worked in practice for Siric Architects, BuyersCircle, Excitation, COAX and BrandMarkets.",
    "clients": "Who Mentec partners with, the sectors we work in, and the SME businesses we've worked alongside.",
    "about": "Founder Joe Siric spent his career as a CFO before founding Mentec — providing the kind of senior leadership known as a virtual or fractional CFO, structured as a partnership.",
    "insights": "Field notes on virtual CFO leadership, financial management, enterprise value and strategic planning for Australian SME owners.",
    "contact": "Book a 15-minute introductory call with Mentec Business Advisory in Norwest, Sydney — or reach us directly by phone or email.",
    "digital-strategy-execution": "Digital transformation roadmaps and hands-on execution, led by a team with senior digital leadership experience across private and public companies.",
    "ecommerce-strategy-execution": "Ecommerce channel strategy, unit economics and execution support, grounded in senior ecommerce leadership across private and public companies.",
    "customer-experience-design": "Customer and user experience design tied to commercial outcomes, led by a team with senior CX/UX leadership across private and public companies.",
    "equity-retainer": "Taking an equity position is optional. When a partner takes one, the retainer is reduced; without it, the retainer is higher. How the trade-off works.",
}

COMPANY_PAGES = {"approach", "case-studies", "clients", "about", "equity-retainer"}
SERVICES_PAGES = {"services", "digital-strategy-execution", "ecommerce-strategy-execution", "customer-experience-design"}

def nav_html(active):
    def cls(slug):
        return "navbtn current" if slug == active else "navbtn"
    services_cls = "navbtn current" if active in SERVICES_PAGES else "navbtn"
    company_cls = "navbtn current" if active in COMPANY_PAGES else "navbtn"
    return f"""<header class="site">
  <div class="wrap nav">
    <a href="index.html" class="wordmark">
      <svg width="30" height="30" viewBox="0 0 40 40" aria-hidden="true">
        <polygon points="12,5 18,5 9,35 3,35" fill="var(--steel)"></polygon>
        <polygon points="22,5 28,5 34,35 28,35 22,17 16,35 10,35" fill="var(--steel)"></polygon>
      </svg>
      <span class="wtext"><b>MENTEC</b><span>Business Advisory</span></span>
    </a>

    <nav class="navmid" id="desktopNav">
      <div class="navitem" data-group="services">
        <button class="{services_cls}" aria-expanded="false">Services <span class="caret">&#9662;</span></button>
        <div class="mega" id="mega-services">
          <div class="mega-links">
            <a class="mega-link" href="services.html"><span class="code">01</span><span class="name">CFO Services</span><span class="desc">CFO leadership, strategy, execution &mdash; the full range.</span></a>
            <a class="mega-link" href="digital-strategy-execution.html"><span class="code">02</span><span class="name">Digital Strategy &amp; Execution</span><span class="desc">A digital operating model that gets used.</span></a>
            <a class="mega-link" href="ecommerce-strategy-execution.html"><span class="code">03</span><span class="name">Ecommerce Strategy &amp; Execution</span><span class="desc">Channel growth built on unit economics.</span></a>
            <a class="mega-link" href="customer-experience-design.html"><span class="code">04</span><span class="name">Customer &amp; UX Design</span><span class="desc">Experience work tied to commercial outcomes.</span></a>
          </div>
          <div class="mega-promo">
            <div>
              <span class="eyebrow">Not sure where to start</span>
              <p>&ldquo;Most partners start with one problem. The engagement usually grows from there.&rdquo;</p>
            </div>
            <a href="contact.html" class="btn btn-ghost" style="align-self:flex-start;">Book a call</a>
          </div>
        </div>
      </div>
      <div class="navitem" data-group="company">
        <button class="{company_cls}" aria-expanded="false">Company <span class="caret">&#9662;</span></button>
        <div class="mega" id="mega-company">
          <div class="mega-links">
            <a class="mega-link" href="approach.html"><span class="code">01</span><span class="name">Approach</span><span class="desc">How the partnership actually works.</span></a>
            <a class="mega-link" href="case-studies.html"><span class="code">02</span><span class="name">Case Studies</span><span class="desc">Results from real engagements.</span></a>
            <a class="mega-link" href="clients.html"><span class="code">03</span><span class="name">Clients</span><span class="desc">Who we partner with, and why.</span></a>
            <a class="mega-link" href="about.html"><span class="code">04</span><span class="name">About</span><span class="desc">The founder story and the pillars.</span></a>
            <a class="mega-link" href="equity-retainer.html"><span class="code">05</span><span class="name">Equity &amp; Retainer</span><span class="desc">How the two halves of the model trade off.</span></a>
          </div>
          <div class="mega-promo">
            <div>
              <span class="eyebrow">Founder-led</span>
              <p>&ldquo;30+ years as a CFO, now structured as a partnership rather than an invoice.&rdquo;</p>
            </div>
            <a href="about.html" class="btn btn-ghost" style="align-self:flex-start;">Meet Joe Siric</a>
          </div>
        </div>
      </div>
      <a href="insights.html" class="{cls('insights')}">Insights</a>
      <a href="contact.html" class="{cls('contact')}">Contact</a>
    </nav>

    <div class="navcta">
      <a href="contact.html" class="btn btn-primary">Book a call</a>
      <button class="menu-toggle" id="mobileToggle" aria-label="Menu" aria-expanded="false">&#9776;</button>
    </div>
  </div>
  <div class="wrap mobile-panel" id="mobilePanel">
    <div class="mobile-group-label">Services</div>
    <a href="services.html">CFO Services</a>
    <a href="digital-strategy-execution.html">Digital Strategy &amp; Execution</a>
    <a href="ecommerce-strategy-execution.html">Ecommerce Strategy &amp; Execution</a>
    <a href="customer-experience-design.html">Customer &amp; UX Design</a>
    <div class="mobile-group-label">Company</div>
    <a href="approach.html">Approach</a>
    <a href="case-studies.html">Case Studies</a>
    <a href="clients.html">Clients</a>
    <a href="about.html">About</a>
    <a href="equity-retainer.html">Equity &amp; Retainer</a>
    <div class="mobile-group-label">More</div>
    <a href="insights.html">Insights</a>
    <a href="contact.html">Contact</a>
  </div>
</header>"""

def footer_html():
    return f"""<footer>
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a href="index.html" class="wordmark">
          <svg width="26" height="26" viewBox="0 0 40 40" aria-hidden="true"><polygon points="12,5 18,5 9,35 3,35" fill="var(--steel)"></polygon><polygon points="22,5 28,5 34,35 28,35 22,17 16,35 10,35" fill="var(--steel)"></polygon></svg>
          <span class="wtext"><b>MENTEC</b><span>Business Advisory</span></span>
        </a>
        <p style="margin-top:16px; font-size:14.5px; max-width:32ch;">CFO-calibre strategy, planning and execution for ambitious SME businesses across Australia.</p>
        <div class="foot-contact">
          <a href="https://maps.google.com/?q={ADDRESS.replace(' ', '+')}" target="_blank" rel="noopener">{ADDRESS}</a>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
          <a href="tel:{PHONE_TEL}">{PHONE}</a>
        </div>
      </div>
      <div>
        <h5>Services</h5>
        <ul>
          <li><a href="services.html#cfo">CFO Leadership</a></li>
          <li><a href="services.html#str">Strategic Planning</a></li>
          <li><a href="services.html#fin">Financial Management</a></li>
          <li><a href="services.html#exe">Execution &amp; Delivery</a></li>
          <li><a href="services.html#val">Enterprise Value &amp; Growth</a></li>
          <li><a href="services.html#dd">Due Diligence &amp; Risk</a></li>
          <li><a href="digital-strategy-execution.html">Digital Strategy &amp; Execution</a></li>
          <li><a href="ecommerce-strategy-execution.html">Ecommerce Strategy &amp; Execution</a></li>
          <li><a href="customer-experience-design.html">Customer &amp; UX Design</a></li>
        </ul>
      </div>
      <div>
        <h5>Company</h5>
        <ul>
          <li><a href="approach.html">Approach</a></li>
          <li><a href="equity-retainer.html">Equity &amp; Retainer</a></li>
          <li><a href="case-studies.html">Case Studies</a></li>
          <li><a href="clients.html">Clients</a></li>
          <li><a href="about.html">About</a></li>
        </ul>
      </div>
      <div>
        <h5>More</h5>
        <ul>
          <li><a href="insights.html">Insights</a></li>
          <li><a href="contact.html">Contact</a></li>
          <li><a href="{LINKEDIN_URL}" target="_blank" rel="noopener">LinkedIn</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span>&copy; 2026 Mentec Business Advisory</span>
    </div>
  </div>
</footer>"""

HEAD_EXTRA = {
    "home": """
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "name": "Mentec Business Advisory",
    "alternateName": "Mentec Virtual CFO Services",
    "description": "Virtual CFO leadership, strategy, planning and execution for ambitious SME businesses, delivered through an equity-aligned partnership model.",
    "email": "info@mentec.com.au",
    "telephone": "+61414674353",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "Suite 6.01, 7 Maitland Pl",
      "addressLocality": "Norwest",
      "addressRegion": "NSW",
      "postalCode": "2153",
      "addressCountry": "AU"
    },
    "founder": { "@type": "Person", "name": "Joe Siric" },
    "areaServed": ["Norwest NSW", "Hills District NSW", "Sydney", "New South Wales", "Australia"],
    "knowsAbout": ["Virtual CFO Services", "Fractional CFO Services", "CFO Leadership", "Strategic Planning", "Financial Management", "Enterprise Value Growth"]
  }
  </script>"""
}

def head(slug):
    title = TITLES[slug]
    desc = DESCRIPTIONS[slug]
    url = f"{BASE_URL}{'' if slug=='home' else SLUG_DIR[slug]+'/'}"
    robots = '<meta name="robots" content="noindex,nofollow">\n  ' if NOINDEX else ''
    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
{robots}<meta property="og:type" content="website">
<meta property="og:site_name" content="Mentec Business Advisory">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="assets/favicon-16.png">
<link rel="shortcut icon" href="assets/favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="assets/apple-touch-icon.png">
<link rel="stylesheet" href="assets/style.css">{HEAD_EXTRA.get(slug,"")}
</head>
<body>
"""

FOOT = """
<script src="assets/site.js"></script>
</body>
</html>
"""

def page(slug, breadcrumb_label, h1, dek, body, parent=None):
    """parent, if given, is (label, slug) for a page nested under another
    (e.g. a services/ sub-page): renders "Home / Services / {breadcrumb_label}"."""
    out = head(slug)
    out += nav_html(slug)
    if slug != "home":
        crumb = '<a href="index.html">Home</a>'
        if parent:
            crumb += f' / <a href="{parent[1]}.html">{parent[0]}</a>'
        crumb += f' / {breadcrumb_label}'
        out += f"""
<div class="pagehead">
  <div class="wrap">
    <div class="breadcrumb">{crumb}</div>
    <span class="eyebrow">{breadcrumb_label}</span>
    <h1>{h1}</h1>
    <p class="dek">{dek}</p>
  </div>
</div>
"""
    out += body
    out += footer_html()
    out += FOOT
    return out

SUBPAGE_SLUGS = [s for s in PAGES if s != "home"]
# Longest-slug-first so e.g. "digital-strategy-execution" (which contains no
# shorter slug as a substring here, but this keeps the rule generally safe)
# never gets shadowed by a shorter match.
SUBPAGE_SLUGS.sort(key=len, reverse=True)

def rewrite_links(html, slug):
    """Every page is generated writing plain 'services.html' / 'assets/x' style
    references, regardless of where it actually ends up on disk. This is the
    single place that turns those into real clean-URL, ../-relative paths for
    wherever this page and its target actually live (SLUG_DIR), so templates
    never need to hand-compute a relative path themselves — including for the
    services/ sub-pages, which sit one level deeper than everything else."""
    cur_dir = SLUG_DIR[slug]
    def rel(target_dir):
        r = os.path.relpath(target_dir, start=cur_dir)
        return "" if r == "." else r.replace(os.sep, "/") + "/"
    root_prefix = rel(".")  # e.g. "" for home, "../" one level deep, "../../" two levels deep
    # assets/ lives at the root, and the literal strings below already include
    # "assets/" themselves, so they only need the prefix to reach the root.
    html = html.replace('href="assets/', f'href="{root_prefix}assets/')
    html = html.replace('src="assets/', f'src="{root_prefix}assets/')
    html = html.replace('href="index.html"', f'href="{root_prefix or "./"}"')
    for s in SUBPAGE_SLUGS:
        target_href = rel(SLUG_DIR[s])
        def _sub(m, target_href=target_href):
            frag = m.group(1) or ""
            # self-link with no fragment (e.g. this page's own entry in a nav
            # list): target_href is "" here, so fall back to "./" rather than
            # emitting a bare href="".
            return f'href="{target_href or ("./" if not frag else "")}{frag}"'
        html = re.sub(rf'href="{re.escape(s)}\.html(#[a-zA-Z0-9_-]+)?"', _sub, html)
    return html

def write(slug, content):
    content = rewrite_links(content, slug)
    path = os.path.join(ROOT, SLUG_TO_FILE[slug])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print("wrote", SLUG_TO_FILE[slug])

def countup_span(value_str, extra_class=""):
    """<span> that renders the real final value (no-JS / crawlers see it as-is);
    site.js animates 0 -> value on scroll-reveal for JS users."""
    m = re.match(r'^([\d.]+)(.*)$', value_str.strip())
    num, suffix = (m.group(1), m.group(2)) if m else (value_str, "")
    cls = ("big tabular" + (" " + extra_class if extra_class else "")).strip()
    return f'<span class="{cls}" data-countup="{num}" data-suffix="{suffix}">{value_str}</span>'

def mini_cta(prompt, button_label="Book an introductory call", sub=""):
    """A slim, unobtrusive between-sections CTA -- deliberately not another
    full-width colour band like .final-cta, so the page doesn't read as a
    string of blue banners."""
    sub_html = f'<span class="mini-cta-sub">{sub}</span>' if sub else ""
    return f"""
<section class="mini-cta">
  <div class="wrap" data-reveal>
    <p>{prompt}{sub_html}</p>
    <a href="contact.html" class="btn btn-primary">{button_label}</a>
  </div>
</section>
"""

# ---------------------------------------------------------------- HOME -----
# Intrinsic pixel dimensions of the real logo files, so the <img> reserves
# the right aspect ratio (height is fixed by CSS; width follows from this).
LOGO_DIMS = {
    "buyerscircle.png": (310, 128),
    "excitation.png": (288, 88),
    "coax.png": (244, 244),
    "brandmarkets.png": (284, 128),
}

def client_chip_row():
    rows = []
    for c in CLIENTS:
        if c.get("logo"):
            w, h = LOGO_DIMS[c["logo"]]
            inner = f'<img src="assets/logos/{c["logo"]}" alt="{c["name"]}" width="{w}" height="{h}" loading="lazy" class="logo-{c["id"]}">'
        else:
            inner = c["name"]
        rows.append(f'        <a href="clients.html#{c["id"]}" class="logo-chip">{inner}</a>')
    return "\n".join(rows)

# ---- Impact chart: indexed Revenue / Profit / Operating Cost over a typical
# 12-month engagement. Dummy/illustrative data — never presented as a real
# client's figures (labelled as such on the chart itself).
CHART_MONTHS = list(range(13))
CHART_SERIES = [
    {"id": "revenue", "label": "Revenue (indexed)", "role": "series-1", "fill": True,
     "values": [100,104,109,113,119,124,129,133,137,141,145,148,152]},
    {"id": "profit", "label": "Profit (indexed)", "role": "series-2", "fill": True,
     "values": [100,103,108,118,128,136,144,151,157,163,168,172,176]},
    {"id": "cost", "label": "Operating cost (indexed)", "role": "series-3", "fill": False,
     "values": [100,99,97,94,92,90,88,87,86,85,84,83,82]},
]
CHART_VW, CHART_VH = 720, 300
CHART_X0, CHART_X1 = 12, 630
CHART_Y0, CHART_Y1 = 26, 244  # y0 = top (max value), y1 = bottom (min value)
CHART_YMIN, CHART_YMAX = 76, 182

def _cx(i):
    return CHART_X0 + (i / (len(CHART_MONTHS) - 1)) * (CHART_X1 - CHART_X0)

def _cy(v):
    t = (v - CHART_YMIN) / (CHART_YMAX - CHART_YMIN)
    return CHART_Y1 - t * (CHART_Y1 - CHART_Y0)

def _smooth_path_d(values):
    """Catmull-Rom -> cubic Bezier through every real data point (tension 1/6,
    the standard conversion) -- a curved line rather than straight segments,
    without inventing values the data doesn't support."""
    pts = [(_cx(i), _cy(v)) for i, v in enumerate(values)]
    n = len(pts)
    if n < 3:
        return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    d = f"M{pts[0][0]:.2f},{pts[0][1]:.2f} "
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else pts[i + 1]
        c1x, c1y = p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6
        c2x, c2y = p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6
        d += f"C{c1x:.2f},{c1y:.2f} {c2x:.2f},{c2y:.2f} {p2[0]:.2f},{p2[1]:.2f} "
    return d.strip()

def _smooth_area_d(values, baseline_y):
    line_d = _smooth_path_d(values)
    x_last, x_first = _cx(len(values) - 1), _cx(0)
    return f"{line_d} L{x_last:.2f},{baseline_y:.2f} L{x_first:.2f},{baseline_y:.2f} Z"

def sales_chart_svg():
    baseline_y = _cy(100)
    gridlines = "\n".join(
        f'      <line x1="{CHART_X0}" y1="{_cy(v):.1f}" x2="{CHART_X1}" y2="{_cy(v):.1f}" class="chart-grid"/>'
        for v in (80, 100, 130, 160)
    )
    x_labels = "\n".join(
        f'      <text x="{_cx(m):.1f}" y="{CHART_Y1 + 22}" class="chart-axis-label" text-anchor="middle">M{m}</text>'
        for m in (0, 3, 6, 9, 12)
    )
    defs = "\n".join(
        f"""      <linearGradient id="chart-grad-{s['id']}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" class="chart-grad-stop-start" data-series="{s['id']}"/>
        <stop offset="100%" class="chart-grad-stop-end" data-series="{s['id']}"/>
      </linearGradient>
      <clipPath id="chart-clip-{s['id']}"><rect class="chart-clip-rect" data-series="{s['id']}" x="{CHART_X0}" y="0" width="0" height="{CHART_VH}"/></clipPath>"""
        for s in CHART_SERIES if s["fill"]
    )
    areas, lines, end_labels, dots, pings, tips = "", "", "", "", "", ""
    for s in CHART_SERIES:
        if s["fill"]:
            areas += f'      <path d="{_smooth_area_d(s["values"], baseline_y)}" class="chart-area" data-series="{s["id"]}" fill="url(#chart-grad-{s["id"]})" stroke="none" clip-path="url(#chart-clip-{s["id"]})"/>\n'
        d = _smooth_path_d(s["values"])
        lines += f'      <path d="{d}" class="chart-line" data-series="{s["id"]}" fill="none"/>\n'
        first_v, last_v = s["values"][0], s["values"][-1]
        pct = (last_v / first_v - 1) * 100
        pct_str = f"{'+' if pct >= 0 else ''}{pct:.0f}%"
        sx, sy = _cx(0), _cy(first_v)
        ex, ey = _cx(12), _cy(last_v)
        dots += f'      <circle cx="{ex:.1f}" cy="{ey:.1f}" r="3.5" class="chart-dot" data-series="{s["id"]}"/>\n'
        pings += f'      <circle cx="{ex:.1f}" cy="{ey:.1f}" r="3.5" class="chart-ping" data-series="{s["id"]}"/>\n'
        tips += f'      <circle cx="{sx:.1f}" cy="{sy:.1f}" r="4.5" class="chart-tip" data-series="{s["id"]}"/>\n'
        end_labels += (
            f'      <g class="chart-endlabel" data-series="{s["id"]}" transform="translate({ex+10:.1f},{ey:.1f})">'
            f'<text class="chart-endlabel-pct" data-countup-pct="{pct:.0f}" dy="-4">{pct_str}</text>'
            f'</g>\n'
        )
    legend = "\n".join(
        f'      <button type="button" class="chart-legend-item" data-series="{s["id"]}" aria-pressed="false">'
        f'<i class="chart-swatch" data-series="{s["id"]}"></i>{s["label"]}</button>'
        for s in CHART_SERIES
    )
    table_rows = "\n".join(
        "        <tr><td>Month {}</td>{}</tr>".format(
            m, "".join(f"<td>{s['values'][m]}</td>" for s in CHART_SERIES)
        )
        for m in CHART_MONTHS
    )
    table_head = "".join(f"<th>{s['label']}</th>" for s in CHART_SERIES)
    chart_payload = json.dumps({
        "months": CHART_MONTHS,
        "series": [{"id": s["id"], "label": s["label"], "values": s["values"]} for s in CHART_SERIES],
        "x0": CHART_X0, "x1": CHART_X1, "ymin": CHART_YMIN, "ymax": CHART_YMAX,
        "y0": CHART_Y0, "y1": CHART_Y1, "vw": CHART_VW, "vh": CHART_VH,
    })

    return f"""
    <div class="chart-card" data-reveal>
      <div class="chart-head">
        <div>
          <span class="eyebrow">Illustrative &mdash; dummy data</span>
          <h3>What tends to happen to the numbers.</h3>
          <p>A typical shape for a 12-month partnership, indexed to 100 at the start. Not a specific client's figures &mdash; see the <a href="case-studies.html" class="inline-link">real case studies</a> for actual results.</p>
        </div>
        <div class="chart-legend">
{legend}
        </div>
      </div>
      <div class="chart-svg-wrap">
        <svg viewBox="0 0 {CHART_VW} {CHART_VH}" class="chart-svg" role="img" aria-label="Indexed revenue, profit and operating cost over a 12-month illustrative engagement" data-chart='{chart_payload}'>
          <defs>
{defs}
          </defs>
          <line x1="{CHART_X0}" y1="{baseline_y:.1f}" x2="{CHART_X1}" y2="{baseline_y:.1f}" class="chart-baseline"/>
          <text x="{CHART_X0}" y="{baseline_y - 8:.1f}" class="chart-axis-label">Start</text>
{gridlines}
{x_labels}
{areas}{lines}{dots}{pings}{end_labels}{tips}
          <line x1="-100" y1="{CHART_Y0}" x2="-100" y2="{CHART_Y1}" class="chart-crosshair"/>
          <circle r="4" class="chart-hover-dot" data-series="revenue" style="opacity:0"/>
          <circle r="4" class="chart-hover-dot" data-series="profit" style="opacity:0"/>
          <circle r="4" class="chart-hover-dot" data-series="cost" style="opacity:0"/>
        </svg>
        <div class="chart-tooltip" hidden></div>
      </div>
      <details class="chart-table-toggle">
        <summary>View as a data table</summary>
        <div class="table-wrap">
          <table class="compare chart-table">
            <thead><tr><th>Month</th>{table_head}</tr></thead>
            <tbody>
{table_rows}
            </tbody>
          </table>
        </div>
      </details>
    </div>
"""

# ---- Business Pillars diagram: redesigned from the original site's teal
# clip-art gears-and-arrows graphic. Same three real pillars and their
# original wording, drawn as a clean node-and-connector diagram in the
# site's own steel-blue / hairline / mono-numeral system instead.
PILLARS = [
    {"n": "01", "name": "Differentiate",
     "desc": "“Be very good at what you are good at.” Know your product or service, and have a genuine differentiator."},
    {"n": "02", "name": "Operate",
     "desc": "Operate the business efficiently and effectively."},
    {"n": "03", "name": "Protect",
     "desc": "Protect the business structurally and financially."},
]
_PN_X = [110, 360, 610]
_PN_Y = 55
_PN_R = 27

def pillars_diagram_svg():
    nodes = ""
    flow_arrows = ""
    for i, (p, x) in enumerate(zip(PILLARS, _PN_X)):
        nodes += (
            f'    <circle cx="{x}" cy="{_PN_Y}" r="{_PN_R}" class="pd-node"/>\n'
            f'    <text x="{x}" y="{_PN_Y}" class="pd-node-n tabular" text-anchor="middle" dy="6">{p["n"]}</text>\n'
        )
    for x1, x2 in zip(_PN_X, _PN_X[1:]):
        mx = (x1 + x2) / 2
        flow_arrows += (
            f'    <line x1="{x1+_PN_R+6}" y1="{_PN_Y}" x2="{x2-_PN_R-14}" y2="{_PN_Y}" class="pd-flow"/>\n'
            f'    <path d="M{mx-2},{_PN_Y-6} L{mx+7},{_PN_Y} L{mx-2},{_PN_Y+6}" class="pd-flow-head"/>\n'
        )
    loop_y = _PN_Y + 78
    loop_d = (
        f"M{_PN_X[0]},{_PN_Y+_PN_R+8} "
        f"C{_PN_X[0]-40},{loop_y} {_PN_X[-1]+40},{loop_y} {_PN_X[-1]},{_PN_Y+_PN_R+8}"
    )
    return f"""
    <div class="pillars-diagram" data-reveal>
      <svg viewBox="0 0 720 165" class="pd-svg" role="img" aria-label="Three business pillars: Differentiate, Operate, Protect, reinforcing each other in a continuous cycle">
{nodes}{flow_arrows}
        <path d="{loop_d}" class="pd-loop" fill="none" marker-end="url(#pd-arrow)"/>
        <defs>
          <marker id="pd-arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse">
            <path d="M0,0 L8,4 L0,8 Z" class="pd-loop-head"/>
          </marker>
        </defs>
      </svg>
      <div class="pd-cards">
{"".join(f'''        <div class="pd-card">
          <span class="pd-card-n">{p["n"]}</span>
          <h4>{p["name"]}</h4>
          <p>{p["desc"]}</p>
        </div>
''' for p in PILLARS)}      </div>
    </div>
"""

# ---- Equity/retainer trade-off bar chart. Illustrative index only, no real
# dollar figures (Mentec's actual terms are set per partnership) -- reuses
# the site's existing generic [data-reveal] and [data-countup] behaviour,
# so it needs no bespoke JS.
EQ_BARS = [
    {"id": "no-equity", "label": "No equity stake", "sub": "Standalone advisory fee", "value": 100},
    {"id": "with-equity", "label": "With equity stake", "sub": "Reduced to reflect the equity position", "value": 55},
]
_EQ_X = [110, 300]
_EQ_BAR_W = 90
_EQ_BASE_Y = 210
_EQ_MAX_H = 150

def equity_retainer_chart():
    delta = round((EQ_BARS[1]["value"] / EQ_BARS[0]["value"] - 1) * 100)
    bars = ""
    for b, x in zip(EQ_BARS, _EQ_X):
        h = _EQ_MAX_H * (b["value"] / 100)
        y = _EQ_BASE_Y - h
        bars += f"""      <g>
        <rect x="{x}" y="{y:.1f}" width="{_EQ_BAR_W}" height="{h:.1f}" class="eq-bar" data-series="{b['id']}"/>
        <text x="{x + _EQ_BAR_W/2}" y="{y - 14:.1f}" text-anchor="middle" class="eq-bar-value tabular" data-countup="{b['value']}">{b['value']}</text>
        <text x="{x + _EQ_BAR_W/2}" y="{_EQ_BASE_Y + 26}" text-anchor="middle" class="eq-bar-label">{b['label']}</text>
        <text x="{x + _EQ_BAR_W/2}" y="{_EQ_BASE_Y + 44}" text-anchor="middle" class="eq-bar-sub">{b['sub']}</text>
      </g>
"""
    return f"""
    <div class="eq-chart-card" data-reveal>
      <div class="eq-chart-head">
        <span class="eyebrow">Illustrative &mdash; not a fixed rate card</span>
        <p>The exact reduction is agreed per partnership, but the direction always holds: more equity, less cash retainer.</p>
      </div>
      <svg viewBox="0 0 410 280" class="eq-svg" role="img" aria-label="Illustrative comparison: retainer level with no equity stake versus with an equity stake, showing the retainer is lower when equity is taken">
        <line x1="60" y1="{_EQ_BASE_Y}" x2="380" y2="{_EQ_BASE_Y}" class="eq-baseline"/>
{bars}        <g class="eq-delta">
          <path d="M{_EQ_X[0]+_EQ_BAR_W+14},{_EQ_BASE_Y - _EQ_MAX_H*(EQ_BARS[0]['value']/100) + 8:.1f} L{_EQ_X[1]-14},{_EQ_BASE_Y - _EQ_MAX_H*(EQ_BARS[1]['value']/100) + 8:.1f}" class="eq-delta-line" marker-end="url(#eq-arrow)"/>
          <text x="{(_EQ_X[0]+_EQ_BAR_W+_EQ_X[1])/2}" y="{_EQ_BASE_Y - _EQ_MAX_H*(EQ_BARS[0]['value']/100) - 6:.1f}" text-anchor="middle" class="eq-delta-label">{delta}%</text>
        </g>
        <defs>
          <marker id="eq-arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse">
            <path d="M0,0 L8,4 L0,8 Z" class="eq-delta-head"/>
          </marker>
        </defs>
      </svg>
    </div>
"""

home_body = f"""
<section class="hero wrap">
  <div class="hero-grid">
    <div>
      <span class="eyebrow">Corporate &middot; Business &middot; Operations Advisory</span>
      <h1 data-reveal>CFO-calibre leadership for businesses ready to <em>outgrow themselves.</em></h1>
      <p class="lede">Mentec provides virtual CFO leadership for ambitious Sydney and Australia-wide SMEs &mdash; pairing 30+ years of senior CFO experience with a partnership most advisors won't offer: an equity position alongside a reduced retainer, so our incentive is your enterprise value, not billable hours. We don't hand over a strategy and leave. We stay and execute it with you.</p>
      <div class="hero-ctas">
        <a href="contact.html" class="btn btn-primary">Book an introductory call</a>
        <a href="approach.html" class="btn btn-ghost">See how we work</a>
      </div>
    </div>
    <div class="ledger-card" data-reveal>
      <div class="ledger-head"><span class="eyebrow" style="margin:0;">On the ledger</span></div>
      <div class="ledger-row"><span class="k">Senior CFO experience</span><span class="v tabular">30+ yrs</span></div>
      <div class="ledger-row"><span class="k">How we're paid</span><span class="v" style="font-size:15px;">Equity<a href="equity-retainer.html" class="inline-link" title="Equity is optional — see how it trades off against the retainer">*</a> + retainer</span></div>
      <div class="ledger-row"><span class="k">Where advice ends</span><span class="v" style="font-size:15px;">It doesn't &mdash; we execute</span></div>
      <div class="ledger-row"><span class="k">Who it's for</span><span class="v" style="font-size:15px;">SME, strong model</span></div>
    </div>
  </div>
</section>

<section class="logos-section">
  <div class="wrap">
    <p class="logos-label"><span class="eyebrow" style="margin-bottom:4px;">Partnering with ambitious SME operators</span></p>
    <div class="logos-row">
{client_chip_row()}
    </div>
  </div>
</section>

<section class="wrap" data-reveal>
  <div class="section-head">
    <span class="eyebrow">Approach</span>
    <h2>Strategy, planned properly &mdash; and then actually delivered.</h2>
    <p>Most advisory firms stop at the recommendation. Mentec is built around the part that comes after it. <a href="approach.html" class="inline-link">Read the full approach &rarr;</a></p>
  </div>
  <div class="card-grid-3">
    <div class="tile"><span class="tag">01 &mdash; Strategise</span><h3>Understand the business</h3><p>Where enterprise value is genuinely being created, and where it's quietly leaking.</p></div>
    <div class="tile"><span class="tag">02 &mdash; Plan</span><h3>Build a plan with owners</h3><p>Strategy becomes a sequenced, deliverable project plan. Not a slide deck.</p></div>
    <div class="tile"><span class="tag">03 &mdash; Execute</span><h3>Work inside the business</h3><p>We stay and drive delivery until results show up in the numbers.</p></div>
  </div>
  <div class="callout">
    <p>&ldquo;Most advisors hand you a strategy and leave. We take a position in your business &mdash; so staying to execute it is in our own interest too.&rdquo;</p>
    <a href="contact.html" class="btn btn-primary">Talk about your business</a>
  </div>
</section>

<section class="section-alt">
  <div class="wrap" data-reveal>
    <div class="section-head">
      <span class="eyebrow">Services</span>
      <h2>Six ways we get involved.</h2>
      <p><a href="services.html" class="inline-link">See the full services page &rarr;</a></p>
    </div>
    <div class="card-grid-3">
      <div class="tile"><span class="tag">CFO</span><h3>CFO Leadership</h3><p>Board packs, lender reporting, a senior voice at the table.</p></div>
      <div class="tile"><span class="tag">STR</span><h3>Strategic Planning</h3><p>A plan built around your specific commercial model.</p></div>
      <div class="tile"><span class="tag">FIN</span><h3>Financial Management</h3><p>Systems that keep growth from outrunning cash.</p></div>
      <div class="tile"><span class="tag">EXE</span><h3>Execution &amp; Delivery</h3><p>We work inside the business to drive the plan home.</p></div>
      <div class="tile"><span class="tag">VAL</span><h3>Enterprise Value</h3><p>The moves that raise what the business is worth.</p></div>
      <div class="tile"><span class="tag">DD</span><h3>Due Diligence &amp; Risk</h3><p>Risk flagged early, before it's expensive.</p></div>
    </div>
  </div>
</section>

{mini_cta("&ldquo;Doing the work brilliantly and running the business behind it are two different skills.&rdquo;", sub="Mentec exists for the gap between the two.")}
<section class="wrap" data-reveal>
  <div class="section-head">
    <span class="eyebrow">Additional Services</span>
    <h2>Growth needs more than the numbers.</h2>
    <p>Financial rigour sets the ceiling. The following three push a business toward it &mdash; led by people who've held senior roles in each, across private and publicly listed companies.</p>
  </div>
  <div class="card-grid-3">
    <div class="tile"><h3>Digital Strategy &amp; Execution</h3><p>A digital operating model built for the business you have, then delivered.</p><a class="more" href="digital-strategy-execution.html">Explore this service &rarr;</a></div>
    <div class="tile"><h3>Ecommerce Strategy &amp; Execution</h3><p>Channel strategy and unit economics that hold together commercially.</p><a class="more" href="ecommerce-strategy-execution.html">Explore this service &rarr;</a></div>
    <div class="tile"><h3>Customer &amp; UX Design</h3><p>Experience work judged by what it moves in the business.</p><a class="more" href="customer-experience-design.html">Explore this service &rarr;</a></div>
  </div>
</section>

{mini_cta("Growth, digital, ecommerce or experience — most engagements start with one problem and grow from there.")}
<section class="wrap">
  <div class="section-head" data-reveal>
    <span class="eyebrow">Impact</span>
    <h2>Where the value equation actually moves.</h2>
  </div>
  {sales_chart_svg()}
</section>

<section class="wrap" data-reveal>
  <div class="section-head">
    <span class="eyebrow">Results</span>
    <h2>What the partnership model looks like in practice.</h2>
    <p><a href="case-studies.html" class="inline-link">Read all five case studies &rarr;</a></p>
  </div>
  <div class="case-card">
    <div class="case-body">
      <span class="eyebrow">Case study &mdash; Architecture &amp; Property</span>
      <h3>Siric Architects</h3>
      <p>A premium residential, industrial and commercial architecture practice. With Mentec engaged, targeted business development was redirected toward commercial work &mdash; more profitable and a better fit for the practice's strengths.</p>
    </div>
    <div class="case-stat">
      {countup_span("80%")}
      <span class="cap">of revenue now derived from commercial projects</span>
    </div>
  </div>
  <div style="margin-top:24px;">
    <a href="case-studies.html#siric-architects" class="btn btn-ghost">Read the full Siric Architects case study &rarr;</a>
  </div>
</section>

<section class="section-alt" data-reveal>
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">In their words</span>
      <h2>What partners say once the plan is actually running.</h2>
      <p><a href="clients.html" class="inline-link">See clients &amp; more testimonials &rarr;</a></p>
    </div>
    <div class="testi-grid">
{testimonials_grid()}    </div>
  </div>
</section>

{mini_cta("If it's a fit, the first call is 15 minutes.", "Book yours")}
<section class="wrap" data-reveal>
  <div class="about-grid">
    <div>
      <span class="eyebrow">About Mentec</span>
      <h2 style="margin-top:16px; font-size:clamp(24px,3vw,32px);">Built by a CFO, for businesses a full-time CFO hasn't reached yet.</h2>
      <p style="margin-top:18px; font-size:16px;">Before founding Mentec, Joe Siric spent his career as CFO across a number of corporations, providing strategic and financial leadership at the executive table. Mentec was established to give ambitious SMEs that same calibre of leadership &mdash; structured as a partnership, not another consulting invoice.</p>
      <p style="margin-top:24px;"><a href="about.html" class="inline-link" style="font-family:ui-monospace,monospace; font-size:13px; letter-spacing:0.04em;">Read the full story &amp; business pillars &rarr;</a></p>
    </div>
    <div class="founder-card">
      <div class="initials">JS</div>
      <h3 style="font-size:19px;">Joe Siric</h3>
      <p style="font-size:14.5px; margin-top:6px;">Founder, Mentec Business Advisory</p>
      <ul class="credential-list">
        <li>Member, Australian Society of Certified Professional Accountants</li>
        <li>30+ years' experience in senior CFO roles</li>
        <li>Focus: SME businesses with a strong, unique commercial model</li>
      </ul>
    </div>
  </div>
</section>

<section class="section-alt" data-reveal>
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Insights</span>
      <h2>Field notes on running the finance function properly.</h2>
      <p><a href="insights.html" class="inline-link">Browse all insights &rarr;</a></p>
    </div>
    <div class="insights-grid">
      <div class="insight-card"><span class="cat">Enterprise value</span><h4>Five moves that raise what your business is worth &mdash; not just what it earns</h4><p>Why profit and enterprise value diverge, and where to look first.</p></div>
      <div class="insight-card"><span class="cat">Cash &amp; reporting</span><h4>The lender-ready report most SMEs don't have until it's too late</h4><p>What board- and bank-grade reporting actually requires.</p></div>
      <div class="insight-card"><span class="cat">Partnership model</span><h4>Why an equity-aligned advisor behaves differently to an hourly one</h4><p>The incentive problem at the heart of most consulting engagements.</p></div>
    </div>
  </div>
</section>

<section class="final-cta">
  <div class="wrap">
    <span class="eyebrow">Start here</span>
    <h2>Ready for leadership that stays until the plan is delivered?</h2>
    <div class="hero-ctas">
      <a href="contact.html" class="btn btn-primary" style="background:#F3F8FB; color:var(--steel-deep);">Book an introductory call</a>
      <a href="services.html" class="btn btn-ghost">Review the services</a>
    </div>
  </div>
</section>
"""
write("home", head("home") + nav_html("home") + home_body + footer_html() + FOOT)

# ------------------------------------------------------------ SERVICES -----
SERVICES_FAQ = [
    ("Is Mentec a virtual CFO service?",
     "Yes &mdash; Mentec provides the same calibre of senior financial leadership as a virtual or fractional CFO, structured as an equity-aligned partnership rather than a straightforward hourly rate or fixed retainer."),
    ("What's the difference between a virtual CFO and a fractional CFO?",
     "In Australia the terms are largely used interchangeably to describe senior, part-time CFO-level leadership. Mentec's model goes a step further: alongside that leadership, we take a position in the business and stay to help execute the plan, not just advise on it."),
    ("Do you only work with businesses in Sydney?",
     "Mentec is based in Norwest, in Sydney's Hills District, and partners with SME businesses Australia-wide."),
    ("What size or stage of business is this for?",
     "SME businesses with an innovative or unique offering and a strong, proven commercial model already generating revenue &mdash; not early-stage ideas still finding a model."),
    ("How is Mentec paid?",
     "Through an equity position in the partner business alongside a retainer that's substantially lower than a standalone consulting fee. See the <a href=\"approach.html\" class=\"inline-link\">Approach page</a> for the full detail."),
    ("Do you only advise, or do you actually get involved?",
     "Both. Mentec builds the plan, then works inside the business to drive delivery &mdash; reporting, cash discipline, and the commercial decisions that determine whether the plan actually happens."),
]

def services_faq_html():
    items = ""
    for q, a in SERVICES_FAQ:
        items += f"""    <details class="faq-item">
      <summary>{q}</summary>
      <div class="a"><p>{a}</p></div>
    </details>
"""
    return items

def _faq_plain(html_text):
    """Strip markup/entities for FAQPage schema text (kept in sync with the
    visible SERVICES_FAQ copy above, not hand-duplicated)."""
    t = re.sub(r'<[^>]+>', '', html_text)
    return t.replace('&mdash;', '—').replace('&amp;', '&')

HEAD_EXTRA["services"] = """
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
""" + ",\n".join(
    "      {\"@type\": \"Question\", \"name\": " + json.dumps(q) +
    ", \"acceptedAnswer\": {\"@type\": \"Answer\", \"text\": " + json.dumps(_faq_plain(a)) + "}}"
    for q, a in SERVICES_FAQ
) + """
    ]
  }
  </script>"""

services_body = f"""
<section class="wrap">
  <div class="service-block" data-reveal id="cfo">
    <div class="svc-head"><span class="svc-code-big">CFO &mdash; 01</span><h3>CFO Leadership</h3><span class="best-for">Best for: businesses making real decisions without a finance voice in the room</span></div>
    <div>
      <p class="desc">On-call, senior financial leadership without carrying a full-time seat &mdash; the role sometimes called a virtual CFO or fractional CFO. Mentec's version comes with an equity-aligned partnership, not just an hourly rate. A member of the Australian Society of Certified Professional Accountants with 30+ years of experience, sitting at the table when it matters.</p>
      <ul class="incl-list">
        <li>Board packs and management reporting on a regular cadence</li>
        <li>Lender and investor-ready reporting when capital conversations start</li>
        <li>Cash flow forecasting and KPI dashboards</li>
        <li>A senior financial voice in commercial decisions as they're being made, not after</li>
      </ul>
    </div>
  </div>

  <div class="service-block" data-reveal id="str">
    <div class="svc-head"><span class="svc-code-big">STR &mdash; 02</span><h3>Strategic Planning</h3><span class="best-for">Best for: a strong business without a clear, sequenced plan to scale it</span></div>
    <div>
      <p class="desc">A corporate strategy built around your specific commercial model &mdash; not a generic template &mdash; then translated into a plan the business can actually deliver.</p>
      <ul class="incl-list">
        <li>Initial due diligence and review of current processes and documents</li>
        <li>A high-level program agreed with all parties before work begins</li>
        <li>Translation of strategy into simple, deliverable project plans</li>
        <li>Clear alignment on what "success" needs to mean for this business</li>
      </ul>
    </div>
  </div>

  <div class="service-block" data-reveal id="fin">
    <div class="svc-head"><span class="svc-code-big">FIN &mdash; 03</span><h3>Financial Management</h3><span class="best-for">Best for: businesses where growth is starting to outrun cash discipline</span></div>
    <div>
      <p class="desc">Financial analysis and systems that optimise how the business's resources are deployed, so ambition doesn't outpace the numbers behind it.</p>
      <ul class="incl-list">
        <li>Resource allocation and margin analysis by project or business line</li>
        <li>Cash flow management and working capital discipline</li>
        <li>Financial systems and reporting cadence set up to scale with the business</li>
        <li>Ongoing financial development toward a more resilient base</li>
      </ul>
    </div>
  </div>

  <div class="service-block" data-reveal id="exe">
    <div class="svc-head"><span class="svc-code-big">EXE &mdash; 04</span><h3>Execution &amp; Delivery</h3><span class="best-for">Best for: businesses that already have a plan sitting on a shelf</span></div>
    <div>
      <p class="desc">The part most advisory firms skip. Mentec works inside the business to drive delivery of the plan &mdash; not just recommend it.</p>
      <ul class="incl-list">
        <li>Working within the business to drive delivery of the agreed plan</li>
        <li>Progress reporting to all parties on a regular rhythm</li>
        <li>Course-correction as real conditions test the plan</li>
        <li>Accountability that doesn't end when the strategy document is signed off</li>
      </ul>
    </div>
  </div>

  <div class="service-block" data-reveal id="val">
    <div class="svc-head"><span class="svc-code-big">VAL &mdash; 05</span><h3>Enterprise Value &amp; Growth</h3><span class="best-for">Best for: owners thinking about what the business is actually worth</span></div>
    <div>
      <p class="desc">Identifying and sequencing the moves that increase what the business is worth &mdash; not just what it earns this year.</p>
      <ul class="incl-list">
        <li>A read on where enterprise value is being created or quietly lost</li>
        <li>Prioritisation of growth moves by value impact, not just revenue</li>
        <li>Positioning the business for a future raise, sale, or succession, if relevant</li>
        <li>Learning from present and past experience to set a repeatable blueprint</li>
      </ul>
    </div>
  </div>

  <div class="service-block" data-reveal id="dd">
    <div class="svc-head"><span class="svc-code-big">DD &mdash; 06</span><h3>Due Diligence &amp; Risk</h3><span class="best-for">Best for: businesses about to take on a partner, lender, or major commitment</span></div>
    <div>
      <p class="desc">Initial due diligence, process and document review, with risk flagged early &mdash; before it becomes an expensive surprise.</p>
      <ul class="incl-list">
        <li>Document and process review across the business</li>
        <li>Risk identification ahead of a funding, partnership, or growth decision</li>
        <li>Plain-language findings, not a compliance report nobody reads</li>
        <li>A clear view of what needs fixing before it's someone else's discovery</li>
        <li>For digital-first and ecommerce businesses, a review of tech stack, channel economics and customer data health alongside the financials</li>
      </ul>
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="wrap" data-reveal>
    <div class="section-head">
      <span class="eyebrow">Specialist capabilities</span>
      <h2>Where growth needs more than the numbers.</h2>
      <p>Strategy and financial discipline set the ceiling. These three bring the commercial, digital and experience work that actually pushes a business toward it &mdash; led by people who've held senior roles in each, across private and publicly listed companies.</p>
    </div>
    <div class="card-grid-3">
      <div class="tile">
        <span class="tag">Specialist</span>
        <h3>Digital Strategy &amp; Execution</h3>
        <p>A digital operating model built for the business you actually have, then delivered rather than handed over.</p>
        <a class="more" href="digital-strategy-execution.html">Explore this service &rarr;</a>
      </div>
      <div class="tile">
        <span class="tag">Specialist</span>
        <h3>Ecommerce Strategy &amp; Execution</h3>
        <p>Channel strategy and unit economics that hold together commercially, not just traffic and conversion tactics.</p>
        <a class="more" href="ecommerce-strategy-execution.html">Explore this service &rarr;</a>
      </div>
      <div class="tile">
        <span class="tag">Specialist</span>
        <h3>Customer &amp; UX Design</h3>
        <p>Experience work judged by what it moves in the business, not just how it looks.</p>
        <a class="more" href="customer-experience-design.html">Explore this service &rarr;</a>
      </div>
    </div>
  </div>
</section>

<section class="wrap" data-reveal>
  <div class="section-head">
    <span class="eyebrow">FAQ</span>
    <h2>Questions worth asking before you engage anyone.</h2>
  </div>
  <div class="faq-list">
{services_faq_html()}  </div>
</section>

<section class="final-cta">
  <div class="wrap">
    <span class="eyebrow">Next step</span>
    <h2>Not sure which of these you need first?</h2>
    <div class="hero-ctas">
      <a href="contact.html" class="btn btn-primary" style="background:#F3F8FB; color:var(--steel-deep);">Book an introductory call</a>
      <a href="approach.html" class="btn btn-ghost">See how engagements start</a>
    </div>
  </div>
</section>
"""
write("services", page("services", "Services",
    "Every engagement is tailored. This is the full range we draw from.",
    "Mentec doesn't sell a fixed package. Each partner gets a program of works assembled from these six areas &mdash; starting wherever the business actually needs it.",
    services_body))

# ---------------------------------------------------- SERVICE SUB-PAGES -----
CREDIBILITY_LINE = "This capability is led by people who have held senior positions inside some of Australia's largest companies &mdash; including Dan Murphy's, Woolworths, Pernod Ricard and leading advertising agencies &mdash; driving real change, from the rollout of major initiatives through to growth in profit and revenue, for both private and publicly listed companies."

def service_subpage_cta(label):
    return f"""
<section class="final-cta">
  <div class="wrap">
    <span class="eyebrow">Next step</span>
    <h2>{label}</h2>
    <div class="hero-ctas">
      <a href="contact.html" class="btn btn-primary" style="background:#F3F8FB; color:var(--steel-deep);">Book an introductory call</a>
      <a href="services.html" class="btn btn-ghost">See all services</a>
    </div>
  </div>
</section>
"""

digital_strategy_body = f"""
<section class="wrap" data-reveal>
  <div class="section-head">
    <span class="eyebrow">What this covers</span>
    <h2>A digital operating model, not a roadmap slide.</h2>
    <p>Most digital strategy work stops at a workshop and a deck. This is built the way the rest of Mentec's model is: a plan, then the work of actually running the business through it.</p>
  </div>
  <ul class="incl-list">
    <li>Digital maturity assessment across systems, data and ways of working</li>
    <li>A technology and platform roadmap sequenced against the commercial plan, not a wish list</li>
    <li>Digital operating model design: who owns what, how decisions get made, how progress is measured</li>
    <li>Hands-on execution support through the build and rollout, not just the recommendation</li>
  </ul>
  <div class="callout">
    <p>&ldquo;{CREDIBILITY_LINE}&rdquo;</p>
  </div>
</section>

<section class="section-alt">
  <div class="wrap" data-reveal>
    <div class="section-head">
      <span class="eyebrow">Part of the same model</span>
      <h2 style="font-size:24px;">Not a report. A partnership.</h2>
      <p>Like every Mentec engagement, this isn't handed off as a document. It's built into the same equity-aligned partnership as the rest of the work &mdash; so the incentive is the business's enterprise value, not billable hours. <a href="approach.html" class="inline-link">See how the partnership model works &rarr;</a></p>
    </div>
  </div>
</section>
"""
write("digital-strategy-execution", page(
    "digital-strategy-execution", "Digital Strategy &amp; Execution",
    "A digital operating model that actually gets used.",
    "Strategy without a digital operating model to run it through stalls at the workshop. This is where the digital side of the business gets built to match the ambition of the rest of it.",
    digital_strategy_body + service_subpage_cta("Ready to build a digital operating model that gets used?"),
    parent=("Services", "services"),
))

ecommerce_strategy_body = f"""
<section class="wrap" data-reveal>
  <div class="section-head">
    <span class="eyebrow">What this covers</span>
    <h2>Channel growth that holds together commercially.</h2>
    <p>Channel growth that doesn't hold together commercially isn't growth &mdash; it's deferred risk. This service keeps strategy and unit economics in the same room.</p>
  </div>
  <ul class="incl-list">
    <li>Channel and marketplace strategy sequenced by margin and capacity, not just opportunity size</li>
    <li>Unit economics and contribution margin by channel, product and cohort</li>
    <li>Conversion, retention and lifetime value roadmap tied to the financial plan</li>
    <li>Integration with cash flow and reporting, so growth doesn't outrun working capital</li>
    <li>Retail media investment and joint business planning with major retail partners &mdash; spend that's tied to a return, not a line item</li>
  </ul>
  <div class="callout">
    <p>&ldquo;{CREDIBILITY_LINE}&rdquo;</p>
  </div>
</section>

<section class="section-alt">
  <div class="wrap" data-reveal>
    <div class="section-head">
      <span class="eyebrow">Proof, not theory</span>
      <h2 style="font-size:24px;">Done inside real ecommerce businesses.</h2>
      <p>Mentec's partners include <a href="case-studies.html#buyerscircle" class="inline-link">BuyersCircle</a>, a social e-commerce platform where this work reshaped the funding model and investment proposition, and <a href="case-studies.html#brandmarkets" class="inline-link">BrandMarkets</a>, a multi-category ecommerce retailer. <a href="case-studies.html" class="inline-link">Read the case studies &rarr;</a></p>
    </div>
  </div>
</section>
"""
write("ecommerce-strategy-execution", page(
    "ecommerce-strategy-execution", "Ecommerce Strategy &amp; Execution",
    "Ecommerce strategy built on unit economics, not just traffic.",
    "Channel growth that doesn't hold together commercially isn't growth &mdash; it's deferred risk. This service keeps the two in the same room.",
    ecommerce_strategy_body + service_subpage_cta("Ready to make the channel strategy hold together commercially?"),
    parent=("Services", "services"),
))

cx_design_body = f"""
<section class="wrap" data-reveal>
  <div class="section-head">
    <span class="eyebrow">What this covers</span>
    <h2>Experience work judged by what it moves.</h2>
    <p>Good UX is a commercial lever, not a finishing touch. This service ties experience work directly to the metrics that matter to the business.</p>
  </div>
  <ul class="incl-list">
    <li>Experience and usability audit across the core customer journey</li>
    <li>Journey mapping tied to commercial drop-off points, not just friction</li>
    <li>UX and service design roadmap, sequenced by expected impact</li>
    <li>A measurement framework linking experience changes to revenue, retention and conversion</li>
    <li>Customer data and loyalty program design, connected to retention and lifetime-value economics &mdash; not run as a marketing side-project</li>
  </ul>
  <div class="callout">
    <p>&ldquo;{CREDIBILITY_LINE}&rdquo;</p>
  </div>
</section>

<section class="section-alt">
  <div class="wrap" data-reveal>
    <div class="section-head">
      <span class="eyebrow">Part of the same model</span>
      <h2 style="font-size:24px;">Design tied to the numbers, not separate from them.</h2>
      <p>Experience recommendations are prioritised the same way the rest of a Mentec plan is &mdash; by expected commercial impact, sequenced into a plan Mentec stays to help deliver. <a href="approach.html" class="inline-link">See how the partnership model works &rarr;</a></p>
    </div>
  </div>
</section>
"""
write("customer-experience-design", page(
    "customer-experience-design", "Customer &amp; UX Design",
    "Customer and user experience design, tied to commercial outcomes.",
    "Experience work judged by what it moves in the business, not just how it looks.",
    cx_design_body + service_subpage_cta("Ready to tie experience work to the numbers?"),
    parent=("Services", "services"),
))

# ------------------------------------------------------------ APPROACH -----
approach_body = """
<section class="wrap" data-reveal>
  <div class="section-head">
    <span class="eyebrow">Why it's different</span>
    <h2>The incentive most consultants don't share with you.</h2>
    <p>In exchange for its services, Mentec takes a position in the partner business alongside a substantially more affordable retainer than a standalone consulting fee. That single structural choice changes almost everything else about how the relationship runs. The equity position itself is optional &mdash; <a href="equity-retainer.html" class="inline-link">see how it trades off against the retainer &rarr;</a></p>
  </div>
  <div class="table-wrap">
    <table class="compare">
      <thead><tr><th></th><th>Traditional consultant</th><th>Mentec partnership</th></tr></thead>
      <tbody>
        <tr><td>How they're paid</td><td>Hourly or fixed fee, regardless of outcome</td><td class="yes">Equity position + reduced retainer</td></tr>
        <tr><td>What they deliver</td><td>A strategy document or slide deck</td><td class="yes">A strategy, a plan, and hands-on delivery</td></tr>
        <tr><td>Where they sit</td><td>Outside the business, engagement by engagement</td><td class="yes">Inside the business, through delivery</td></tr>
        <tr><td>What happens after sign-off</td><td>The engagement typically ends</td><td class="yes">The work continues &mdash; this is where value is created</td></tr>
        <tr><td>Their incentive</td><td>The next engagement</td><td class="yes">The enterprise value of your business</td></tr>
      </tbody>
    </table>
  </div>
</section>

<section class="section-alt">
  <div class="wrap" data-reveal>
    <div class="section-head">
      <span class="eyebrow">The mechanism</span>
      <h2>Strategise. Plan. Execute.</h2>
    </div>
    <div class="card-grid-3">
      <div class="tile">
        <span class="tag">01 &mdash; Strategise</span>
        <h3>Understand the business</h3>
        <p>We start inside the numbers and the model &mdash; where enterprise value is genuinely being created, and where it's quietly leaking. This stage asks questions and reviews real processes and documents, not assumptions carried in from another industry.</p>
      </div>
      <div class="tile">
        <span class="tag">02 &mdash; Plan</span>
        <h3>Build a plan with owners</h3>
        <p>Strategy becomes a sequenced, deliverable project plan &mdash; with owners, milestones and financial targets attached. High-level thinking gets broken into simple project plans someone can actually run.</p>
      </div>
      <div class="tile">
        <span class="tag">03 &mdash; Execute</span>
        <h3>Work inside the business</h3>
        <p>Mentec stays and drives delivery &mdash; reporting, cash discipline, the commercial calls &mdash; until results show up in the numbers, not just the plan.</p>
      </div>
    </div>
  </div>
</section>

<section class="wrap" data-reveal>
  <div class="section-head">
    <span class="eyebrow">Our process</span>
    <h2>How a partnership actually starts.</h2>
  </div>
  <div class="process-list">
    <div class="process-item"><span class="num tabular">1</span><div><h4>Introductory meeting</h4><p>We align on what matters to each party and what "success" needs to mean here.</p></div></div>
    <div class="process-item"><span class="num tabular">2</span><div><h4>Engagement proposal</h4><p>A high-level program is presented and agreed by all parties before any work begins.</p></div></div>
    <div class="process-item"><span class="num tabular">3</span><div><h4>Discovery</h4><p>We ask questions and review the real processes and documents &mdash; not assumptions.</p></div></div>
    <div class="process-item"><span class="num tabular">4</span><div><h4>Due diligence</h4><p>Initial due diligence pressure-tests the plan before it's locked in.</p></div></div>
    <div class="process-item"><span class="num tabular">5</span><div><h4>Planning</h4><p>The high-level plan is translated into simple, deliverable project plans.</p></div></div>
    <div class="process-item"><span class="num tabular">6</span><div><h4>Delivery &amp; reporting</h4><p>Progress is reported to all parties, and Mentec works inside the business to drive delivery.</p></div></div>
  </div>
</section>

<section class="final-cta">
  <div class="wrap">
    <span class="eyebrow">Start here</span>
    <h2>See what this looks like for your business.</h2>
    <div class="hero-ctas"><a href="contact.html" class="btn btn-primary" style="background:#F3F8FB; color:var(--steel-deep);">Book an introductory call</a></div>
  </div>
</section>
"""
write("approach", page("approach", "Approach",
    "Advice you can act on &mdash; because we act on it with you.",
    "Most advisory relationships end at the recommendation. Ours is structured so that ending there would work against us too.",
    approach_body))

# --------------------------------------------------------- EQUITY/RETAINER --
EQUITY_RETAINER_FAQ = [
    ("Is an equity position required to work with Mentec?",
     "No. It's optional. Some partners prefer to keep it a straightforward cash arrangement, and that's a completely workable version of the same engagement."),
    ("So what actually changes if I take it?",
     "The retainer. Taking an equity position lowers the cash retainer, because part of Mentec's return is then tied to the enterprise value we help build &mdash; not just the monthly fee."),
    ("What if I don't want to give up equity?",
     "Then the retainer is set higher, structured as a standalone advisory fee. No equity changes hands, and the scope of work &mdash; strategy, planning, execution &mdash; doesn't change either way."),
    ("How is the split actually decided?",
     "Case by case, during the proposal stage, based on the business and what's being asked of the engagement. There's no fixed formula published here because there isn't one in practice."),
]

def equity_retainer_faq_html():
    items = ""
    for q, a in EQUITY_RETAINER_FAQ:
        items += f"""    <details class="faq-item">
      <summary>{q}</summary>
      <div class="a"><p>{a}</p></div>
    </details>
"""
    return items

equity_retainer_body = f"""
<section class="wrap" data-reveal>
  <div class="section-head">
    <span class="eyebrow">How it works</span>
    <h2>One lever, two settings.</h2>
    <p>Every Mentec engagement is paid for through the same two components &mdash; a retainer, and optionally, an equity position. Only the balance between them changes.</p>
  </div>
  <ul class="incl-list">
    <li>Take an equity position, and the cash retainer is reduced &mdash; Mentec's return is then partly tied to the enterprise value we help build</li>
    <li>Skip the equity position, and the retainer is set higher, structured as a standalone advisory fee</li>
    <li>The scope of work is identical either way: CFO leadership, strategy, planning and hands-on execution</li>
    <li>The split is agreed once, during the proposal stage &mdash; not renegotiated engagement to engagement</li>
  </ul>
</section>

<section class="section-alt">
  <div class="wrap" data-reveal>
    <div class="section-head">
      <span class="eyebrow">The trade-off</span>
      <h2 style="font-size:24px;">More equity, less cash. Less equity, more cash.</h2>
    </div>
    {equity_retainer_chart()}
  </div>
</section>

<section class="wrap" data-reveal>
  <div class="section-head">
    <span class="eyebrow">FAQ</span>
    <h2 style="font-size:24px;">The questions this usually raises.</h2>
  </div>
  <div class="faq-list">
{equity_retainer_faq_html()}  </div>
</section>

<section class="final-cta">
  <div class="wrap">
    <span class="eyebrow">Start here</span>
    <h2>Talk through which setting fits your business.</h2>
    <div class="hero-ctas"><a href="contact.html" class="btn btn-primary" style="background:#F3F8FB; color:var(--steel-deep);">Book an introductory call</a></div>
  </div>
</section>
"""
write("equity-retainer", page(
    "equity-retainer", "Equity &amp; Retainer",
    "How the equity and retainer actually trade off.",
    "The equity position is optional. It exists to lower what you pay in cash &mdash; not as a requirement to work with Mentec.",
    equity_retainer_body, parent=("Approach", "approach"),
))

# --------------------------------------------------------- CASE STUDIES ----
featured = next(c for c in CLIENTS if c["featured"])
others = [c for c in CLIENTS if not c["featured"]]

case_html = f"""
<section class="wrap">
  <div class="case-card" data-reveal id="{featured['id']}">
    <div class="case-body">
      <span class="eyebrow">{featured['category']}</span>
      <h3>{featured['name']}</h3>
      <span class="lbl">The business</span>
      <p>{featured['summary']}</p>
      <span class="lbl">The approach</span>
      <p>{featured['engagement']}</p>
      <span class="lbl">The result</span>
      <p>{featured['result']}</p>
    </div>
    <div class="case-stat">
      {countup_span(featured['stat_value'])}
      <span class="cap">{featured['stat_label']}</span>
    </div>
  </div>

  <div class="section-head" style="margin-top:64px;">
    <span class="eyebrow">More partnerships</span>
    <h2>Different businesses, the same model.</h2>
  </div>
  <div class="sample-case-grid">
"""
for c in others:
    case_html += f"""    <div class="sample-case" data-reveal id="{c['id']}">
      <span class="eyebrow">{c['category']}</span>
      <h4>{c['name']}</h4>
      <p>{c['summary']}</p>
      <p style="margin-top:10px;"><strong style="color:var(--ink);">With Mentec:</strong> {c['engagement']} {c['result']}</p>
    </div>
"""
case_html += """    <div class="sample-case" data-reveal id="dan-murphys-beaten-board">
      <span class="eyebrow">Retail &mdash; UX, Motion &amp; Development, National Rollout</span>
      <h4>Dan Murphy&rsquo;s &mdash; Beaten Board</h4>
      <p>Every day, Dan Murphy&rsquo;s staff tore pages from competitor catalogues and pinned them to a corkboard stamped &ldquo;BEATEN&rdquo; &mdash; proof of the retailer&rsquo;s price promise, done entirely by hand, store by store.</p>
      <p style="margin-top:10px;"><strong style="color:var(--ink);">From our expert team:</strong> An API-driven, animated real-time catalogue in a dynamic layout, able to feature any of Dan Murphy&rsquo;s 50,000+ products &mdash; designed and rolled out across every Dan Murphy&rsquo;s store nationwide, replacing the manual process and letting prices update on the hour.</p>
    </div>
  </div>
</section>

<section class="final-cta">
  <div class="wrap">
    <span class="eyebrow">Be the next one</span>
    <h2>Ready to build a result worth writing up?</h2>
    <div class="hero-ctas"><a href="contact.html" class="btn btn-primary" style="background:#F3F8FB; color:var(--steel-deep);">Book an introductory call</a></div>
  </div>
</section>
"""
write("case-studies", page("case-studies", "Case Studies",
    "What the partnership model looks like from inside real businesses.",
    "Five engagements, five different starting points &mdash; architecture, e-commerce, marketing, communications and retail.",
    case_html))

# ---------------------------------------------------------------- CLIENTS --
client_cards = ""
for c in CLIENTS:
    client_cards += f"""      <div class="tile" data-reveal id="{c['id']}">
        <span class="tag">{c['category']}</span>
        <h3>{c['name']}</h3>
        <p>{c['summary']}</p>
        <a class="more" href="case-studies.html#{c['id']}">Read the full story &rarr;</a>
      </div>
"""

clients_body = f"""
<section class="wrap" data-reveal>
  <div class="section-head">
    <span class="eyebrow">Fit</span>
    <h2>Mentec partners typically have:</h2>
  </div>
  <ul class="profile-list">
    <li>An innovative or genuinely unique idea, product or service</li>
    <li>A strong, proven commercial model already generating revenue</li>
    <li>SME scale &mdash; established enough to have real financial complexity, not yet large enough to justify a full-time CFO</li>
    <li>A continued drive to grow, not just maintain</li>
  </ul>
  <div class="section-head" style="margin-top:48px;">
    <span class="eyebrow">Sectors</span>
    <h2 style="font-size:22px;">Where our current partners sit.</h2>
  </div>
  <div class="industries-row">
    <span class="industry-chip">Architecture &amp; Design</span>
    <span class="industry-chip">E-commerce &amp; Retail</span>
    <span class="industry-chip">Marketing &amp; Media</span>
    <span class="industry-chip">Technology &amp; Communications</span>
  </div>
</section>

<section class="section-alt">
  <div class="wrap" data-reveal>
    <div class="section-head"><span class="eyebrow">Partners</span><h2>Current and past engagements.</h2></div>
    <div class="card-grid-3">
{client_cards}    </div>
  </div>
</section>

<section class="wrap" data-reveal>
  <div class="section-head"><span class="eyebrow">In their words</span><h2>What partners say once the plan is actually running.</h2></div>
  <div class="testi-grid">
{testimonials_grid()}  </div>
</section>

<section class="final-cta">
  <div class="wrap">
    <span class="eyebrow">Start here</span>
    <h2>Think you're a fit? Let's find out together.</h2>
    <div class="hero-ctas"><a href="contact.html" class="btn btn-primary" style="background:#F3F8FB; color:var(--steel-deep);">Book an introductory call</a></div>
  </div>
</section>
"""
write("clients", page("clients", "Clients",
    "Who we partner with, and why we're selective about it.",
    "Mentec's model only works when both sides are genuinely aligned. That starts with taking on the right partners in the first place.",
    clients_body))

# ------------------------------------------------------------------ ABOUT --
about_body = f"""
<section class="wrap" data-reveal>
  <div class="about-grid">
    <div>
      <span class="eyebrow">Our story</span>
      <h2 style="margin-top:16px; font-size:clamp(24px,3vw,32px);">Why Mentec exists.</h2>
      <p style="margin-top:20px; font-size:16px;">Before founding Mentec, Joe Siric spent his career as CFO across a number of corporations, providing strategic and professional finance leadership at the executive table. That work made one thing clear: strong business relationships, not just strong numbers, are what set the foundation for lasting success.</p>
      <p style="margin-top:16px; font-size:16px;">Mentec Business Advisory was established to give small to medium-sized enterprises with an innovative or distinctive idea access to that same calibre of strategic leadership and financial rigour &mdash; the kind of senior support often described as a virtual CFO or fractional CFO &mdash; structured as a genuine partnership, not another consulting invoice.</p>
      <p style="margin-top:16px; font-size:16px;">Mentec creates a tailored strategy for each partner, then stays inside the business to help deliver it &mdash; learning from what's worked and what hasn't, so the blueprint fits the business in front of us rather than a template pulled off the shelf.</p>
    </div>
    <div class="founder-card">
      <img class="founder-photo" src="assets/people/joe-siric.jpg" alt="Joe Siric, Founder of Mentec Business Advisory" width="88" height="88" loading="lazy">
      <div class="founder-name-row">
        <h3 style="font-size:19px;">Joe Siric</h3>
        <a class="founder-linkedin" href="{LINKEDIN_URL}" target="_blank" rel="noopener" aria-label="Joe Siric on LinkedIn"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.45 20.45h-3.55v-5.57c0-1.33-.02-3.03-1.85-3.03-1.86 0-2.14 1.45-2.14 2.94v5.66H9.36V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.38-1.85 3.61 0 4.28 2.38 4.28 5.47v6.27zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45z"></path></svg></a>
      </div>
      <p style="font-size:14.5px; margin-top:6px;">Founder, Mentec Business Advisory</p>
      <ul class="credential-list">
        <li>Member, Australian Society of Certified Professional Accountants</li>
        <li>30+ years' experience in senior CFO roles</li>
        <li>Focus: SME businesses with a strong, unique commercial model</li>
      </ul>
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="wrap" data-reveal>
    <div class="section-head"><span class="eyebrow">Business pillars</span><h2>What Mentec looks at in every business.</h2><p>Being excellent at the work and being excellent at running a business aren't the same skill. These are the three pillars Mentec looks at in every partner &mdash; each one reinforcing the other two.</p></div>
    {pillars_diagram_svg()}
  </div>
</section>

<section class="final-cta">
  <div class="wrap">
    <span class="eyebrow">Start here</span>
    <h2>Talk to Joe about your business.</h2>
    <div class="hero-ctas"><a href="contact.html" class="btn btn-primary" style="background:#F3F8FB; color:var(--steel-deep);">Book an introductory call</a></div>
  </div>
</section>
"""
write("about", page("about", "About",
    "Built by a CFO, for businesses a full-time CFO hasn't reached yet.",
    "The story, the founder, and the pillars the partnership model is built on.",
    about_body))

# --------------------------------------------------------------- INSIGHTS --
INSIGHTS = [
    {
        "id": "five-moves-that-raise-enterprise-value",
        "category": "Enterprise value",
        "title": "Five moves that raise what your business is worth &mdash; not just what it earns",
        "dek": "Why profit and enterprise value diverge, and where to look first.",
        "body": """
<p>Two businesses can post the same annual profit and be worth wildly different amounts to a buyer, a lender or an investor. Profit measures what the business made last year. Enterprise value measures how confident someone else is that it'll keep making money &mdash; predictably, without the current owner in the room &mdash; for years after they sign. That gap is where most of the real work sits.</p>
<p>Here are five of the levers that move it.</p>
<h3>1. Recurring revenue over one-off wins</h3>
<p>A dollar of contracted, repeatable revenue is worth more than a dollar won fresh each quarter, because it's a dollar someone else can underwrite. Retainers, subscriptions, service contracts and renewal-heavy customer bases all compress risk for a buyer. If most of the top line resets to zero every January, that's usually the first thing to fix.</p>
<h3>2. Reduce key-person risk</h3>
<p>If the business stops functioning the week the founder takes leave, that's a discount on the valuation, not a compliment to the founder. Documented processes, a genuine second layer of leadership and customer relationships that don't run through one mobile number all reduce the risk premium a buyer prices in.</p>
<h3>3. Clean, defensible financials</h3>
<p>Numbers that hold up under diligence &mdash; consistent revenue recognition, a clear split between one-off and recurring income, no ambiguity between the owner's personal expenses and the business's &mdash; move faster through a sale process and attract fewer price chips along the way. Messy books don't just cost time; they cost trust, and trust is priced.</p>
<h3>4. Diversify the customer base</h3>
<p>A business where one client is 40% of revenue is one contract renewal away from a very different valuation. Spreading concentration risk across more accounts, or building switching costs into the ones you have, is slower work than winning a single big client &mdash; but it's the work a valuation actually rewards.</p>
<h3>5. A credible growth plan, not just a growth story</h3>
<p>Buyers and lenders discount a pitch. They pay for a plan &mdash; one with a market sized properly, a resourced path to execute it, and a track record of hitting what was previously forecast. The gap between "we think we could grow 30%" and "here's the plan, the hires and the 18 months of results that support it" is most of the multiple.</p>
<p>None of these five are quick fixes, and none of them show up on this year's P&amp;L. That's exactly why they tend to get put off &mdash; and why the businesses that start early are the ones with real options when the time comes to sell, raise, or simply stop worrying about what happens if the owner gets hit by a bus.</p>
""",
    },
    {
        "id": "lender-ready-reporting",
        "category": "Cash & reporting",
        "title": "The lender-ready report most SMEs don't have until it's too late",
        "dek": "What board- and bank-grade reporting actually requires.",
        "body": """
<p>Most SME reporting is built to answer one question: did we make money last month? Lender-ready reporting has to answer a harder one: will this business still be able to service its obligations in six months, under a plausible worse case &mdash; and can you prove it before we ask?</p>
<p>The gap between those two usually isn't accuracy. Most owners can tell you last month's number was right. It's structure, forward visibility and consistency over time &mdash; the three things a lender or a board actually needs and a monthly P&amp;L doesn't provide on its own.</p>
<h3>What's usually missing</h3>
<p>A rolling cash flow forecast, updated monthly rather than built from scratch under pressure when the bank asks for one. Covenant headroom tracked against the actual facility terms, not just "we're pretty sure we're fine." Working capital detail &mdash; debtor days, creditor days, stock turn &mdash; broken out rather than buried in a single balance sheet line. And management accounts that are internally consistent month to month, so a reader can trust a trend rather than re-verifying every figure from scratch.</p>
<h3>What bank-grade reporting includes</h3>
<p>A rolling 13-week cash flow for short-term visibility, and a 12&ndash;24 month forecast for the medium term. A covenant summary showing where the business actually sits against each facility condition, not just whether repayments have been made. A variance commentary that explains the gap between forecast and actual in plain language &mdash; because an unexplained variance reads as a red flag whether or not it should. And reporting that's produced on a predictable schedule, not assembled in a hurry the week a lender asks for it.</p>
<h3>Why this matters before you need it</h3>
<p>The businesses that get the best terms &mdash; on a new facility, an extension, or a covenant reset during a rough quarter &mdash; are the ones that can hand over this pack without a scramble. It signals the business is being run properly, and it puts the owner in a negotiating position instead of a defensive one. Building it after the lender asks is possible, but it's expensive, stressful, and it's happening at the exact moment you have the least leverage to insist on good terms.</p>
""",
    },
    {
        "id": "why-equity-aligned-advisors-behave-differently",
        "category": "Partnership model",
        "title": "Why an equity-aligned advisor behaves differently to an hourly one",
        "dek": "The incentive problem at the heart of most consulting engagements.",
        "body": """
<p>Most advisory relationships are billed by the hour, the day, or the project. On paper that looks like a fair exchange &mdash; time for money. In practice it creates a quiet incentive problem: the advisor gets paid whether or not the recommendation actually works, and gets paid more the longer the engagement runs. Neither of those incentives is aligned with the thing the business owner actually wants, which is a result.</p>
<p>An equity-aligned model changes the mechanics. When part of the advisor's compensation is a stake in the business rather than an invoice, the advisor's own return depends on the business genuinely becoming more valuable &mdash; not on the number of workshops run or slides produced.</p>
<h3>What actually changes in practice</h3>
<p>It changes what gets recommended. An hourly advisor has no particular reason to avoid a longer, more elaborate program of work; an equity-aligned one has a direct reason to recommend the shortest path to a real result, because that's what moves their own return. It changes who stays in the room. Handing over a strategy document and moving to the next client is a reasonable business model when you're paid by the deliverable; it's a bad one when your own upside depends on that strategy actually landing. And it changes what gets said. Telling a client an idea won't work is easier when the advisor's income doesn't depend on that client saying yes to the next phase of work.</p>
<h3>Where it doesn't fit</h3>
<p>This model isn't right for every engagement or every business. It requires genuine alignment on where the business is headed, a level of trust that takes longer to establish up front, and a business the advisor is actually willing to take a position in &mdash; which means selectivity on both sides. It's a partnership model, not a faster way to buy the same hours.</p>
<p>For the businesses it does fit, the difference shows up less in what gets proposed and more in what happens after the proposal &mdash; whether the advisor is still in the building three months later, working through the same problem the business is.</p>
""",
    },
    {
        "id": "strategy-document-vs-deliverable-plan",
        "category": "Strategy",
        "title": "The difference between a strategy document and a deliverable plan",
        "dek": "Turning a workshop's worth of ideas into owners, milestones and targets.",
        "body": """
<p>Most strategy documents are correct. That's rarely the problem. The problem is that a document full of good ideas and a plan that actually gets executed are two different artefacts, built to different standards &mdash; and most engagements stop at the first one.</p>
<p>A strategy document answers "what should we do." It's usually organised around themes: grow this segment, fix that cost base, enter this channel. It's genuinely useful thinking. It's also, on its own, almost impossible to execute, because nothing in it says who is responsible, by when, with what resources, or how anyone will know it's on track.</p>
<h3>What a deliverable plan adds</h3>
<p>An owner for every initiative &mdash; a named person accountable for it, not "the leadership team." A sequence, because most businesses can't run six strategic initiatives at once with the team they have, and pretending otherwise is how nothing finishes. Milestones with dates attached, specific enough that it's obvious within a month whether something is on track or quietly slipping. A resourced budget, so the plan reflects what the business can actually fund rather than what would be ideal in an unconstrained world. And a review cadence &mdash; a standing point where progress against the plan gets checked against reality, not just referenced in passing at the next strategy day.</p>
<h3>Why this is where most engagements actually fail</h3>
<p>Turning themes into a sequenced, resourced, owned plan is less interesting work than the strategy session that produced the themes in the first place, and it's usually where an external advisor's involvement ends &mdash; right at the point the hard part begins. The strategy gets filed, the business goes back to its existing rhythm, and six months later the same themes get raised again, sounding a little more urgent each time.</p>
<p>The fix isn't a better strategy document. It's treating the plan as the deliverable, and staying involved long enough to see it actually run.</p>
""",
    },
    {
        "id": "virtual-cfo-vs-fractional-cfo",
        "category": "Virtual CFO",
        "title": "Virtual CFO vs fractional CFO: same job, different word?",
        "dek": "What the terms actually mean in Australia, and where Mentec's model differs from both.",
        "body": """
<p>"Virtual CFO" and "fractional CFO" get used almost interchangeably in the Australian market, and in most cases that's a fair way to treat them &mdash; both describe senior CFO-level leadership delivered on a part-time or as-needed basis, rather than a full-time in-house hire.</p>
<p>Where a distinction gets drawn, it's usually this: "fractional" emphasises the time-slice &mdash; a portion of a CFO's week, allocated across a small number of clients, often with a fairly fixed weekly or monthly commitment. "Virtual" emphasises the delivery model &mdash; the CFO isn't in the office full-time and much of the relationship runs remotely, but the scope of the role can flex more with what the business actually needs in a given month.</p>
<h3>Why the label matters less than the scope</h3>
<p>In practice, the more useful questions aren't about the term at all. What's actually in scope &mdash; is this board-pack-and-lender-reporting only, or does it extend to strategy and execution? What's the seniority behind it &mdash; genuine CFO-level experience, or a bookkeeper wearing a CFO title? What's the cadence &mdash; a few fixed hours a month, or genuine availability when something urgent comes up? And critically, how is the advisor incentivised &mdash; paid regardless of outcome, or with something riding on the business actually doing well?</p>
<h3>Where Mentec's model sits</h3>
<p>Mentec offers virtual CFO leadership, but structured differently to most fractional or virtual arrangements: alongside a reduced retainer, Mentec takes an equity position in the partner business. That changes the incentive from "deliver the agreed hours" to "the business needs to actually get more valuable" &mdash; and it's why the engagement doesn't stop at strategy. The same team that builds the plan stays to help execute it, inside the business, until the results show up in the numbers.</p>
<p>Whichever term a firm uses, the label is a poor way to evaluate the offer. Scope, seniority, availability and incentive are what actually determine whether the arrangement behaves like a genuine finance partner or a part-time consultant with a CFO title.</p>
""",
    },
    {
        "id": "virtual-cfo-vs-accountant",
        "category": "Virtual CFO",
        "title": "Virtual CFO vs accountant: what founders get wrong",
        "dek": "Compliance and strategy are different jobs. Most SMEs only have one of them covered.",
        "body": """
<p>Almost every SME has an accountant. Very few have a CFO, virtual or otherwise &mdash; and a lot of founders don't realise the gap exists until something forces the question: a lender asks for a forecast nobody's built, a board member asks where enterprise value is actually being created, or growth stalls and it's unclear why.</p>
<p>The confusion is understandable, because both roles deal in numbers. But they're built to do different jobs.</p>
<h3>What an accountant is engaged to do</h3>
<p>Tax compliance, statutory reporting, BAS lodgements, historical bookkeeping &mdash; the record of what already happened, prepared accurately and on time, to meet obligations to the ATO and other regulators. This work is essential, it's specialised, and a good accountant is genuinely hard to replace. It's also, almost by definition, backward-looking: it tells you what the business did, not what it should do next.</p>
<h3>What's typically missing</h3>
<p>Forward-looking financial leadership &mdash; cash flow forecasting, scenario planning, pricing and margin strategy, capital structure decisions. Board- and investor-grade judgement on where the business should be investing, and where it's quietly leaking value. And execution: turning a financial view of the business into decisions that actually get made and followed through, not just reported on after the fact.</p>
<h3>Where the two fit together</h3>
<p>A virtual CFO isn't a replacement for the accountant &mdash; the compliance work still needs to happen, and still needs a specialist. The value of a virtual CFO is everything the compliance relationship was never built to cover: sitting at the table for the decisions that shape where the business is headed, not just recording where it's been. The businesses that get this right usually keep both relationships running in parallel, each doing the job it's actually suited for.</p>
<p>The mistake isn't hiring an accountant. It's assuming that relationship was ever meant to cover strategic financial leadership too &mdash; and only finding out otherwise at the exact moment it would have mattered most.</p>
""",
    },
]

for _i, _art in enumerate(INSIGHTS):
    PAGES.append(_art["id"])
    SLUG_DIR[_art["id"]] = f"insights/{_art['id']}"
    TITLES[_art["id"]] = f"{re.sub('<[^<]+?>', '', _art['title'])} | Mentec Insights"
    DESCRIPTIONS[_art["id"]] = _art["dek"]
SLUG_TO_FILE = {slug: (d + "/index.html" if d != "." else "index.html") for slug, d in SLUG_DIR.items()}
SUBPAGE_SLUGS = [s for s in PAGES if s != "home"]
SUBPAGE_SLUGS.sort(key=len, reverse=True)

def insight_cards_html(exclude_id=None, limit=None):
    cards = []
    for art in INSIGHTS:
        if art["id"] == exclude_id:
            continue
        cards.append(f'    <a class="insight-card" data-reveal href="{art["id"]}.html"><span class="cat">{art["category"]}</span><h4>{art["title"]}</h4><p>{art["dek"]}</p></a>')
        if limit and len(cards) >= limit:
            break
    return "\n".join(cards)

insights_body = f"""
<section class="wrap insights-section" data-reveal>
  <div class="insights-grid">
{insight_cards_html()}
  </div>
</section>

<section class="final-cta">
  <div class="wrap">
    <span class="eyebrow">Talk it through</span>
    <h2>Have a specific question? Skip the article.</h2>
    <div class="hero-ctas"><a href="contact.html" class="btn btn-primary" style="background:#F3F8FB; color:var(--steel-deep);">Book an introductory call</a></div>
  </div>
</section>
"""
write("insights", page("insights", "Insights",
    "Field notes on running the finance function properly.",
    "A content pillar for search visibility, and a way to show CFO-level thinking before the first call.",
    insights_body))

for art in INSIGHTS:
    article_body = f"""
<section class="wrap" data-reveal>
  <div class="article-body">
    {art['body'].strip()}
  </div>
  {mini_cta("Want this applied to your business specifically, not in the abstract?", button_label="Book an introductory call")}
</section>

<section class="wrap" data-reveal style="margin-top:24px;">
  <div class="section-head" style="margin-bottom:24px;">
    <span class="eyebrow">More insights</span>
    <h2 style="font-size:22px;">Related reading.</h2>
  </div>
  <div class="insights-grid">
{insight_cards_html(exclude_id=art['id'], limit=3)}
  </div>
</section>
"""
    write(art["id"], page(art["id"], art["category"], art["title"], art["dek"],
        article_body, parent=("Insights", "insights")))

# ---------------------------------------------------------------- CONTACT --
contact_body = f"""
<section class="wrap" data-reveal>
  <div class="time-picker" id="timePicker">
    <div class="section-head" style="margin-bottom:0;">
      <span class="eyebrow">Pick a time</span>
      <h2 style="font-size:22px;">See a slot that works? Request it directly.</h2>
      <p style="font-size:14.5px; color:var(--text-soft); margin-top:8px;">Weekdays, 9am&ndash;5pm. Picking a time drafts an email requesting that slot &mdash; Joe confirms it by reply, it isn't an automatic booking.</p>
    </div>
    <div class="tp-days" id="tpDays" style="margin-top:24px;"></div>
    <div class="tp-slots" id="tpSlots"></div>
    <div class="tp-footer">
      <span class="tp-selected" id="tpSelected">No time selected yet.</span>
      <a href="#" id="tpRequestBtn" class="btn btn-primary tp-request-btn tp-disabled" aria-disabled="true">Request this time</a>
    </div>
  </div>
</section>

<section class="wrap" data-reveal>
  <div class="contact-grid">
    <div>
      <span class="eyebrow">Enquire</span>
      <h2 style="margin-top:14px; font-size:24px;">Tell us about the business.</h2>
      <p style="margin-top:12px; font-size:14.5px; color:var(--text-soft);">Opens in your email client, addressed straight to Mentec.</p>
      <form style="margin-top:24px;" action="mailto:{EMAIL}" method="post" enctype="text/plain">
        <div class="field"><label for="fname">Name</label><input id="fname" name="Name" type="text" placeholder="Jordan Blake" required></div>
        <div class="field"><label for="fcompany">Company</label><input id="fcompany" name="Company" type="text" placeholder="Business name"></div>
        <div class="field"><label for="femail">Email</label><input id="femail" name="Email" type="email" placeholder="you@company.com.au" required></div>
        <div class="field"><label for="fmsg">What's going on?</label><textarea id="fmsg" name="Message" rows="4" placeholder="A line or two on where the business is stuck."></textarea></div>
        <button type="submit" class="btn btn-primary">Request an introductory call</button>
      </form>
    </div>
    <div>
      <span class="eyebrow">What happens next</span>
      <div class="process-list" style="margin-top:14px;">
        <div class="process-item"><span class="num tabular">1</span><div><h4>Introductory call</h4><p>15 minutes to align on what matters and whether it's a fit &mdash; no obligation.</p></div></div>
        <div class="process-item"><span class="num tabular">2</span><div><h4>Engagement proposal</h4><p>If it's a fit, a high-level program is proposed and agreed by all parties.</p></div></div>
        <div class="process-item"><span class="num tabular">3</span><div><h4>Discovery begins</h4><p>Mentec starts understanding the business properly &mdash; before any plan is written.</p></div></div>
      </div>
    </div>
  </div>
</section>
"""
write("contact", page("contact", "Contact",
    "Start with a 15-minute introductory call.",
    "No pitch deck required. We'll talk about the business, where it's stuck, and whether Mentec's model is actually a fit &mdash; based in Norwest, Sydney, working with SME partners Australia-wide.",
    contact_body))

print("done: all pages")

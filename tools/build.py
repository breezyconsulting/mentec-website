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
EMAIL = "joe.siric@mentec.com.au"
PHONE = "+61 414 674 353"
PHONE_TEL = "+61414674353"

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
        "name": "Joel", "title": "Director", "company": "COAX",
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
         "digital-strategy-execution","ecommerce-strategy-execution","customer-experience-design"]
# Clean URLs, arbitrary nesting: SLUG_DIR is the single source of truth for where a
# page lives on disk ("." = site root). Every page but home is a directory with an
# index.html inside it, so nothing is ever linked with a ".html" extension. The three
# new service sub-pages nest one level deeper, under services/.
SLUG_DIR = {
    "home": ".",
    "services": "services", "approach": "approach", "case-studies": "case-studies",
    "clients": "clients", "about": "about", "insights": "insights", "contact": "contact",
    "digital-strategy-execution": "services/digital-strategy-execution",
    "ecommerce-strategy-execution": "services/ecommerce-strategy-execution",
    "customer-experience-design": "services/customer-experience-design",
}
SLUG_TO_FILE = {slug: (d + "/index.html" if d != "." else "index.html") for slug, d in SLUG_DIR.items()}
TITLES = {
    "home": "Mentec Business Advisory | CFO-Calibre Leadership for Growing SMEs",
    "services": "Services | CFO Leadership, Strategy & Execution — Mentec Business Advisory",
    "approach": "Our Approach | Strategise, Plan, Execute — Mentec Business Advisory",
    "case-studies": "Case Studies | Real Partner Results — Mentec Business Advisory",
    "clients": "Clients | Who We Partner With — Mentec Business Advisory",
    "about": "About | Joe Siric & the Mentec Story — Mentec Business Advisory",
    "insights": "Insights | CFO & Business Advisory Articles — Mentec Business Advisory",
    "contact": "Contact | Book an Introductory Call — Mentec Business Advisory",
    "digital-strategy-execution": "Digital Strategy & Execution — Mentec Business Advisory",
    "ecommerce-strategy-execution": "Ecommerce Strategy & Execution — Mentec Business Advisory",
    "customer-experience-design": "Customer & User Experience Design — Mentec Business Advisory",
}
DESCRIPTIONS = {
    "home": "Mentec pairs 30+ years of senior CFO experience with an equity-aligned partnership model for ambitious Australian SMEs — strategy, planning and hands-on execution.",
    "services": "CFO Leadership, Strategic Planning, Financial Management, Execution & Delivery, Enterprise Value & Growth, and Due Diligence — six services, tailored per partner.",
    "approach": "Why Mentec takes an equity position instead of billing by the hour, and how a partnership moves from strategy to a delivered, working plan.",
    "case-studies": "How Mentec's partnership model has worked in practice for Siric Architects, BuyersCircle, Excitation, COAX and BrandMarkets.",
    "clients": "Who Mentec partners with, the sectors we work in, and the SME businesses we've worked alongside.",
    "about": "Founder Joe Siric spent his career as a CFO before founding Mentec Business Advisory. The story, credentials and pillars behind the partnership model.",
    "insights": "Field notes on CFO-level financial management, enterprise value and strategic planning for SME business owners.",
    "contact": "Book a 20-minute introductory call with Mentec Business Advisory, or reach us directly by phone or email.",
    "digital-strategy-execution": "Digital transformation roadmaps and hands-on execution, led by a team with senior digital leadership experience across private and public companies.",
    "ecommerce-strategy-execution": "Ecommerce channel strategy, unit economics and execution support, grounded in senior ecommerce leadership across private and public companies.",
    "customer-experience-design": "Customer and user experience design tied to commercial outcomes, led by a team with senior CX/UX leadership across private and public companies.",
}

COMPANY_PAGES = {"approach", "case-studies", "clients", "about"}

def nav_html(active):
    def cls(slug):
        return "navbtn current" if slug == active else "navbtn"
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
      <a href="services.html" class="{cls('services')}">Services</a>
      <div class="navitem" data-group="company">
        <button class="{company_cls}" aria-expanded="false">Company <span class="caret">&#9662;</span></button>
        <div class="mega" id="mega-company">
          <div class="mega-links">
            <a class="mega-link" href="approach.html"><span class="code">01</span><span class="name">Approach</span><span class="desc">How the partnership actually works.</span></a>
            <a class="mega-link" href="case-studies.html"><span class="code">02</span><span class="name">Case Studies</span><span class="desc">Results from real engagements.</span></a>
            <a class="mega-link" href="clients.html"><span class="code">03</span><span class="name">Clients</span><span class="desc">Who we partner with, and why.</span></a>
            <a class="mega-link" href="about.html"><span class="code">04</span><span class="name">About</span><span class="desc">The founder story and the pillars.</span></a>
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
    <a href="services.html">Services</a>
    <div class="mobile-group-label">Company</div>
    <a href="approach.html">Approach</a>
    <a href="case-studies.html">Case Studies</a>
    <a href="clients.html">Clients</a>
    <a href="about.html">About</a>
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
          <li><a href="https://www.linkedin.com" target="_blank" rel="noopener">LinkedIn</a></li>
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
    "description": "CFO-calibre strategy, planning and execution for ambitious SME businesses, delivered through an equity-aligned partnership model.",
    "email": "joe.siric@mentec.com.au",
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
    "areaServed": "AU"
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

# ---------------------------------------------------------------- HOME -----
def client_chip_row():
    return "\n".join(
        f'        <a href="clients.html#{c["id"]}" class="logo-chip">{c["name"]}</a>'
        for c in CLIENTS
    )

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
      </linearGradient>"""
        for s in CHART_SERIES if s["fill"]
    )
    areas, lines, end_labels, dots, pings = "", "", "", "", ""
    for s in CHART_SERIES:
        if s["fill"]:
            areas += f'      <path d="{_smooth_area_d(s["values"], baseline_y)}" class="chart-area" data-series="{s["id"]}" fill="url(#chart-grad-{s["id"]})" stroke="none"/>\n'
        d = _smooth_path_d(s["values"])
        lines += f'      <path d="{d}" class="chart-line" data-series="{s["id"]}" fill="none"/>\n'
        first_v, last_v = s["values"][0], s["values"][-1]
        pct = (last_v / first_v - 1) * 100
        pct_str = f"{'+' if pct >= 0 else ''}{pct:.0f}%"
        ex, ey = _cx(12), _cy(last_v)
        dots += f'      <circle cx="{ex:.1f}" cy="{ey:.1f}" r="3.5" class="chart-dot" data-series="{s["id"]}"/>\n'
        pings += f'      <circle cx="{ex:.1f}" cy="{ey:.1f}" r="3.5" class="chart-ping" data-series="{s["id"]}"/>\n'
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
{areas}{lines}{dots}{pings}{end_labels}
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

home_body = f"""
<section class="hero wrap">
  <div class="hero-grid">
    <div>
      <span class="eyebrow">Corporate &middot; Business &middot; Operations Advisory</span>
      <h1 data-reveal>CFO-calibre leadership for businesses ready to <em>outgrow themselves.</em></h1>
      <p class="lede">Mentec pairs 30+ years of senior CFO experience with a partnership most advisors won't offer: an equity position alongside a reduced retainer, so our incentive is your enterprise value &mdash; not billable hours. We don't hand over a strategy and leave. We stay and execute it with you.</p>
      <div class="hero-ctas">
        <a href="contact.html" class="btn btn-primary">Book an introductory call</a>
        <a href="approach.html" class="btn btn-ghost">See how we work</a>
      </div>
    </div>
    <div class="ledger-card" data-reveal>
      <div class="ledger-head"><span class="eyebrow" style="margin:0;">On the ledger</span></div>
      <div class="ledger-row"><span class="k">Senior CFO experience</span><span class="v tabular">30+ yrs</span></div>
      <div class="ledger-row"><span class="k">How we're paid</span><span class="v" style="font-size:15px;">Equity + retainer</span></div>
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
services_body = """
<section class="wrap">
  <div class="service-block" data-reveal id="cfo">
    <div class="svc-head"><span class="svc-code-big">CFO &mdash; 01</span><h3>CFO Leadership</h3><span class="best-for">Best for: businesses making real decisions without a finance voice in the room</span></div>
    <div>
      <p class="desc">On-call, senior financial leadership without carrying a full-time seat. A member of the Australian Society of Certified Professional Accountants with 30+ years of experience, sitting at the table when it matters.</p>
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
CREDIBILITY_LINE = "This capability is led by people who have held senior positions across multiple sectors, delivering real growth for both private and publicly listed companies &mdash; judgment that's been tested against real P&amp;Ls, not just frameworks."

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
    <p>In exchange for its services, Mentec takes a position in the partner business alongside a substantially more affordable retainer than a standalone consulting fee. That single structural choice changes almost everything else about how the relationship runs.</p>
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
case_html += """  </div>
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
about_body = """
<section class="wrap" data-reveal>
  <div class="about-grid">
    <div>
      <span class="eyebrow">Our story</span>
      <h2 style="margin-top:16px; font-size:clamp(24px,3vw,32px);">Why Mentec exists.</h2>
      <p style="margin-top:20px; font-size:16px;">Before founding Mentec, Joe Siric spent his career as CFO across a number of corporations, providing strategic and professional finance leadership at the executive table. That work made one thing clear: strong business relationships, not just strong numbers, are what set the foundation for lasting success.</p>
      <p style="margin-top:16px; font-size:16px;">Mentec Business Advisory was established to give small to medium-sized enterprises with an innovative or distinctive idea access to that same calibre of strategic leadership and financial rigour &mdash; structured as a genuine partnership, not another consulting invoice.</p>
      <p style="margin-top:16px; font-size:16px;">Mentec creates a tailored strategy for each partner, then stays inside the business to help deliver it &mdash; learning from what's worked and what hasn't, so the blueprint fits the business in front of us rather than a template pulled off the shelf.</p>
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

<section class="section-alt">
  <div class="wrap" data-reveal>
    <div class="section-head"><span class="eyebrow">Business pillars</span><h2>What the partnership model is built on.</h2></div>
    <div class="pillar-grid">
      <div class="pillar"><span class="n">i</span><h4>Partnership Alignment</h4><p>Equity + retainer, so our incentive is your enterprise value.</p></div>
      <div class="pillar"><span class="n">ii</span><h4>Strategic Clarity</h4><p>A plan built for this business, not a template.</p></div>
      <div class="pillar"><span class="n">iii</span><h4>Financial Discipline</h4><p>Reporting and cash management that scale with growth.</p></div>
      <div class="pillar"><span class="n">iv</span><h4>Delivery</h4><p>We stay inside the business until the plan is real.</p></div>
    </div>
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
insights_body = """
<section class="wrap insights-section" data-reveal>
  <div class="insights-grid">
    <div class="insight-card"><span class="cat">Enterprise value</span><h4>Five moves that raise what your business is worth &mdash; not just what it earns</h4><p>Why profit and enterprise value diverge, and where to look first.</p></div>
    <div class="insight-card"><span class="cat">Cash &amp; reporting</span><h4>The lender-ready report most SMEs don't have until it's too late</h4><p>What board- and bank-grade reporting actually requires.</p></div>
    <div class="insight-card"><span class="cat">Partnership model</span><h4>Why an equity-aligned advisor behaves differently to an hourly one</h4><p>The incentive problem at the heart of most consulting engagements.</p></div>
    <div class="insight-card"><span class="cat">Strategy</span><h4>The difference between a strategy document and a deliverable plan</h4><p>Turning a workshop's worth of ideas into owners, milestones and targets.</p></div>
    <div class="insight-card"><span class="cat">Due diligence</span><h4>What a due diligence review catches that founders usually miss</h4><p>Common blind spots before a raise, sale or major partnership.</p></div>
    <div class="insight-card"><span class="cat">Growth</span><h4>When a business has outgrown a bookkeeper but not yet earned a CFO</h4><p>The access gap this whole firm exists to close.</p></div>
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

# ---------------------------------------------------------------- CONTACT --
contact_body = f"""
<section class="wrap" data-reveal>
  <div class="contact-grid">
    <div>
      <span class="eyebrow">Enquire</span>
      <h2 style="margin-top:14px; font-size:24px;">Tell us about the business.</h2>
      <p style="margin-top:12px; font-size:14.5px; color:var(--text-soft);">Opens in your email client, addressed to Joe directly.</p>
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
        <div class="process-item"><span class="num tabular">1</span><div><h4>Introductory call</h4><p>20 minutes to align on what matters and whether it's a fit &mdash; no obligation.</p></div></div>
        <div class="process-item"><span class="num tabular">2</span><div><h4>Engagement proposal</h4><p>If it's a fit, a high-level program is proposed and agreed by all parties.</p></div></div>
        <div class="process-item"><span class="num tabular">3</span><div><h4>Discovery begins</h4><p>Mentec starts understanding the business properly &mdash; before any plan is written.</p></div></div>
      </div>
    </div>
  </div>
</section>
"""
write("contact", page("contact", "Contact",
    "Start with a 20-minute introductory call.",
    "No pitch deck required. We'll talk about the business, where it's stuck, and whether Mentec's model is actually a fit.",
    contact_body))

print("done: all pages")

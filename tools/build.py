#!/usr/bin/env python3
"""Static site generator for the Mentec Business Advisory redesign.
Run: python3 tools/build.py
Regenerates the .html files in the repo root from the templates below.
Kept in the repo so future content edits don't require hand-editing eight
files with duplicated nav/footer markup.
"""
import os, re

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
        "category": "Social e-commerce Platform Developer & Retailer",
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
        "name": "COAX AU PTY LTD",
        "category": "Simplified Business Communications",
        "summary": "Coax was born out of the belief that communication for your business should be as simple as possible.",
        "engagement": "Working with Mentec, through strategic planning and financial management, COAX has been able to offer targeted, tailored help for the startup small business.",
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

PAGES = ["home","services","approach","case-studies","clients","about","insights","contact"]
SLUG_TO_FILE = {
    "home":"index.html","services":"services.html","approach":"approach.html",
    "case-studies":"case-studies.html","clients":"clients.html","about":"about.html",
    "insights":"insights.html","contact":"contact.html",
}
TITLES = {
    "home": "Mentec Business Advisory | CFO-Calibre Leadership for Growing SMEs",
    "services": "Services | CFO Leadership, Strategy & Execution — Mentec Business Advisory",
    "approach": "Our Approach | Strategise, Plan, Execute — Mentec Business Advisory",
    "case-studies": "Case Studies | Real Partner Results — Mentec Business Advisory",
    "clients": "Clients | Who We Partner With — Mentec Business Advisory",
    "about": "About | Joe Siric & the Mentec Story — Mentec Business Advisory",
    "insights": "Insights | CFO & Business Advisory Articles — Mentec Business Advisory",
    "contact": "Contact | Book an Introductory Call — Mentec Business Advisory",
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
    file = SLUG_TO_FILE[slug]
    url = f"{BASE_URL}{'' if slug=='home' else file}"
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
<link rel="stylesheet" href="assets/style.css">
<script defer src="https://cdn.vercel-insights.com/v1/script.js"></script>{HEAD_EXTRA.get(slug,"")}
</head>
<body>
"""

FOOT = """
<script src="assets/site.js"></script>
</body>
</html>
"""

def page(slug, breadcrumb_label, h1, dek, body):
    out = head(slug)
    out += nav_html(slug)
    out += f"""
<div class="pagehead">
  <div class="wrap">
    <div class="breadcrumb"><a href="index.html">Home</a> / {breadcrumb_label}</div>
    <span class="eyebrow">{breadcrumb_label}</span>
    <h1>{h1}</h1>
    <p class="dek">{dek}</p>
  </div>
</div>
""" if slug != "home" else ""
    out += body
    out += footer_html()
    out += FOOT
    return out

def write(slug, content):
    path = os.path.join(ROOT, SLUG_TO_FILE[slug])
    with open(path, "w") as f:
        f.write(content)
    print("wrote", SLUG_TO_FILE[slug])

# ---------------------------------------------------------------- HOME -----
def client_chip_row():
    return "\n".join(
        f'        <a href="clients.html#{c["id"]}" class="logo-chip">{c["name"]}</a>'
        for c in CLIENTS
    )

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
      <span class="big tabular">80%</span>
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
      <div class="testi-card">
        <span class="sample-tag">Sample &mdash; replace with real quote</span>
        <blockquote>&ldquo;Within the first quarter we finally had reporting we could hand to our bank without scrambling. That alone changed how we made decisions.&rdquo;</blockquote>
        <div class="testi-who"><strong>Founder / Managing Director</strong><span>Client name, company &mdash; pending</span></div>
      </div>
      <div class="testi-card">
        <span class="sample-tag">Sample &mdash; replace with real quote</span>
        <blockquote>&ldquo;Every other advisor we spoke to sold a strategy document. Mentec was the only one still in the building three months later.&rdquo;</blockquote>
        <div class="testi-who"><strong>Managing Director</strong><span>Client name, company &mdash; pending</span></div>
      </div>
      <div class="testi-card">
        <span class="sample-tag">Sample &mdash; replace with real quote</span>
        <blockquote>&ldquo;Having someone with equity in the outcome changes the conversation. It stopped feeling like billable hours and started feeling like a partner.&rdquo;</blockquote>
        <div class="testi-who"><strong>Founder</strong><span>Client name, company &mdash; pending</span></div>
      </div>
    </div>
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
      <span class="big tabular">{featured['stat_value']}</span>
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
    <div class="testi-card">
      <span class="sample-tag">Sample &mdash; replace with real quote</span>
      <blockquote>&ldquo;Within the first quarter we finally had reporting we could hand to our bank without scrambling. That alone changed how we made decisions.&rdquo;</blockquote>
      <div class="testi-who"><strong>Founder / Managing Director</strong><span>Client name, company &mdash; pending</span></div>
    </div>
    <div class="testi-card">
      <span class="sample-tag">Sample &mdash; replace with real quote</span>
      <blockquote>&ldquo;Every other advisor we spoke to sold a strategy document. Mentec was the only one still in the building three months later.&rdquo;</blockquote>
      <div class="testi-who"><strong>Managing Director</strong><span>Client name, company &mdash; pending</span></div>
    </div>
    <div class="testi-card">
      <span class="sample-tag">Sample &mdash; replace with real quote</span>
      <blockquote>&ldquo;Having someone with equity in the outcome changes the conversation. It stopped feeling like billable hours and started feeling like a partner.&rdquo;</blockquote>
      <div class="testi-who"><strong>Founder</strong><span>Client name, company &mdash; pending</span></div>
    </div>
  </div>
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
      <div class="contact-detail">
        <p><strong style="color:var(--ink);">Mentec Business Advisory</strong><br>Corporate &middot; Business &middot; Operations Advisory</p>
        <ul class="foot-contact" style="margin-top:16px; list-style:none;">
          <li><a href="https://maps.google.com/?q={ADDRESS.replace(' ', '+')}" target="_blank" rel="noopener">{ADDRESS}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li><a href="tel:{PHONE_TEL}">{PHONE}</a></li>
        </ul>
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

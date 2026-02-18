"""ExecSignals — HTML template generators.

Generates: <head>, nav, footer, and full page wrapper.
Pattern: Aligned with Fieldwork framework (Pariter Media standard).
"""

import json
from nav_config import (
    SITE_NAME, DOMAIN, CSS_VERSION, THEME_COLOR, THEME_COLOR_LIGHT,
    JS_VERSION, NAV_LINKS, NAV_CTA_TEXT, NAV_CTA_HREF,
    FOOTER_LINKS, FOOTER_ENTITY, GA4_ID,
)

YEAR = "2026"


def get_html_head(title, description, canonical_path="/", og_image=None, schemas=None, noindex=False):
    """Generate the full <head> section.

    Head order (Fieldwork standard):
    charset → viewport → title → description → canonical → robots →
    favicons → manifest → theme-color → OG → Twitter → JSON-LD →
    fonts → CSS
    """
    og_image = og_image or f"https://{DOMAIN}/assets/social-preview.png"
    canonical = f"https://{DOMAIN}{canonical_path}"

    schema_block = ""
    if schemas:
        schema_json = json.dumps(schemas, indent=4)
        schema_block = f"""
    <!-- JSON-LD -->
    <script type="application/ld+json">
    {schema_json}
    </script>"""

    robots_meta = '    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">'
    if noindex:
        robots_meta = '    <meta name="robots" content="noindex, nofollow">'

    # GA4 block — omit if placeholder ID
    ga4_block = ""
    if GA4_ID and not GA4_ID.startswith("G-XXXX"):
        ga4_block = f"""
    <!-- GA4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA4_ID}');
    </script>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{canonical}">
{robots_meta}

    <!-- Favicon -->
    <link rel="icon" href="/assets/svg/icon-inverted.svg" type="image/svg+xml">
    <link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">
    <link rel="icon" href="/assets/favicon-32x32.png" sizes="32x32" type="image/png">
    <link rel="icon" href="/assets/favicon-16x16.png" sizes="16x16" type="image/png">
    <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">
    <meta name="theme-color" content="{THEME_COLOR}" media="(prefers-color-scheme: dark)">
    <meta name="theme-color" content="{THEME_COLOR_LIGHT}" media="(prefers-color-scheme: light)">
    <meta name="msapplication-TileColor" content="{THEME_COLOR}">

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta property="og:image" content="{og_image}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:locale" content="en_US">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{og_image}">
{schema_block}

    <!-- Fonts (non-blocking: preload + media=print swap + noscript fallback) -->
    <link rel="preload" href="/assets/fonts/plus-jakarta-sans-latin-400.woff2"
          as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="/assets/fonts/fonts.css"
          media="print" onload="this.media='all'">
    <noscript><link rel="stylesheet" href="/assets/fonts/fonts.css"></noscript>

    <!-- CSS -->
    <link rel="stylesheet" href="/css/styles.css?v={CSS_VERSION}">
{ga4_block}
</head>"""


def get_nav_html(active_page="home"):
    """Generate the sticky header with nav."""
    links = ""
    for link in NAV_LINKS:
        links += f'            <a href="{link["href"]}">{link["label"]}</a>\n'

    return f"""
<header class="site-header">
    <div class="header-inner">
        <a href="/" class="site-logo">Exec<span>Signals</span></a>
        <nav class="nav">
{links}            <a href="{NAV_CTA_HREF}" class="nav-cta">{NAV_CTA_TEXT}</a>
        </nav>
        <button class="menu-toggle" aria-label="Toggle menu">
            <span class="menu-toggle-bar"></span>
            <span class="menu-toggle-bar"></span>
            <span class="menu-toggle-bar"></span>
        </button>
    </div>
</header>"""


def get_footer_html():
    """Generate the footer with script tag at bottom of body (Fieldwork pattern)."""
    links = ""
    for link in FOOTER_LINKS:
        links += f'            <a href="{link["href"]}">{link["label"]}</a>\n'

    return f"""
<footer class="site-footer">
    <div class="footer-content">
        <div class="footer-browse">
            Browse: <a href="/roles/">Roles</a> &middot; <a href="/cities/">Cities</a> &middot; <a href="/industries/">Industries</a>
        </div>
        <span>&copy; {YEAR} {SITE_NAME}. A product of {FOOTER_ENTITY}</span>
        <div class="footer-links">
{links}        </div>
    </div>
</footer>

<script src="/js/main.js?v={JS_VERSION}"></script>
</body>
</html>"""


def get_page_wrapper(title, description, canonical_path, body_html, schemas=None, noindex=False):
    """Combine head + nav + body + footer into a complete page."""
    head = get_html_head(title, description, canonical_path, schemas=schemas, noindex=noindex)
    nav = get_nav_html()
    footer = get_footer_html()

    return f"""{head}
<body>
{nav}
{body_html}
{footer}"""

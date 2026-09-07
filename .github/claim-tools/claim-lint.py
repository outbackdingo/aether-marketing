#!/usr/bin/env python3
"""claim-lint — check marketing copy and live pages against the claim ledger.

The GlacierAI site carried claims its own validation audit had withdrawn three
days earlier, and nothing caught it. This does.

    claim-lint.py FILE...                 # lint drafts
    claim-lint.py --url https://...       # lint a live page
    claim-lint.py --all                   # drafts + both production sites
    claim-lint.py --quiet                 # only output on failure (for cron)

Exit 0 clean, 1 findings, 2 could not run. Stdlib only, so it runs in CI.
"""

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "claims.json")

PROD = [
    "https://optimcloud.com/glacier",
    "https://optimcloud.com/",
    "https://aether-io.com/",
]

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")

RED, YEL, GRN, DIM, OFF = "\033[31m", "\033[33m", "\033[32m", "\033[2m", "\033[0m"
if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
    RED = YEL = GRN = DIM = OFF = ""


def strip_html(raw):
    """Visible text only. Scripts and style blocks go first: Next.js inlines its
    RSC payload into a <script>, which would otherwise double every match."""
    raw = re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(text))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def near(text, pos, pattern, window):
    """Is `pattern` within `window` characters either side of pos?"""
    lo, hi = max(0, pos - window), min(len(text), pos + window)
    return re.search(pattern, text[lo:hi]) is not None


def excerpt(text, pos, span=70):
    lo, hi = max(0, pos - span), min(len(text), pos + span)
    return "…" + text[lo:hi].strip() + "…"


def check(name, text, ledger, exempt):
    findings = []

    def add(sev, cid, msg, where):
        findings.append((sev, cid, msg, where))

    for rule in ledger["red"]:
        if rule["id"] in exempt:
            continue
        for m in re.finditer(rule["pattern"], text):
            ok = rule.get("allow_if_near")
            if ok and near(text, m.start(), ok, 300):
                continue
            add("RED", rule["id"], rule["why"], excerpt(text, m.start()))

    for rule in ledger["amber"]:
        if rule["id"] in exempt:
            continue
        for m in re.finditer(rule["pattern"], text):
            if near(text, m.start(), rule["requires"], rule.get("window", 200)):
                continue
            add("AMBER", rule["id"],
                rule["why"] + " — qualifier missing nearby",
                excerpt(text, m.start()))

    # Figures are a whitelist, not a completeness check. Prose does not have to
    # restate every fact, so "this passage omits 6.5" is noise. "This passage
    # states a distance that is on no measured record" is signal.
    for rule in ledger["figures"]:
        if rule["id"] in exempt:
            continue
        if not re.search(rule["context"], text):
            continue
        allowed = set(rule["allowed"])
        seen = set()
        for m in re.finditer(rule["extract"], text):
            got = m.group(1)
            if got in allowed or got in seen:
                continue
            # Only distances attached to a validated event are claims about a
            # measurement. Design figures elsewhere on the page are not.
            if "near" in rule and not near(text, m.start(), rule["near"],
                                           rule.get("near_window", 170)):
                continue
            seen.add(got)
            add("FIGURE", rule["id"],
                "%s km is not on the measured record — %s" % (got, rule["why"]),
                excerpt(text, m.start()))

    parts = ledger["required_parts"]
    for role, part in parts.items():
        if role.startswith("_"):
            continue
        # Catch near-misses: right family, wrong number. The stem is the part's
        # leading alphabetic run (ATECC608A -> ATECC), which is what makes
        # ATECC508A visible; a fixed-width prefix missed it.
        alpha = re.match(r"[A-Za-z]+", part).group(0)
        stem = re.escape(alpha if len(alpha) >= 3 else part[:4])
        for m in re.finditer(stem + r"[A-Za-z0-9-]*", text):
            if m.group(0) != part:
                add("PART", role,
                    "reads %s, canonical is %s" % (m.group(0), part),
                    excerpt(text, m.start()))

    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="files to lint")
    ap.add_argument("--url", action="append", default=[], help="live page to lint")
    ap.add_argument("--all", action="store_true",
                    help="lint every draft in the posts dir plus production")
    ap.add_argument("--quiet", action="store_true", help="silent unless findings")
    args = ap.parse_args()

    try:
        ledger = json.load(open(LEDGER))
    except Exception as e:
        print("cannot read ledger %s: %s" % (LEDGER, e), file=sys.stderr)
        return 2

    targets = []
    paths, urls = list(args.paths), list(args.url)

    if args.all:
        posts = os.path.dirname(HERE)
        paths += sorted(os.path.join(posts, f) for f in os.listdir(posts)
                        if f.endswith((".md", ".txt")))
        urls += PROD

    for p in paths:
        try:
            body = open(p, encoding="utf-8").read()
        except Exception as e:
            print("cannot read %s: %s" % (p, e), file=sys.stderr)
            return 2
        # CI lints built HTML from disk. Without stripping, "&lt;60s" never
        # matches "<60s" and a pattern spanning a tag boundary is invisible —
        # the check would pass for the wrong reason, which is worse than no
        # check at all.
        if p.lower().endswith((".html", ".htm")) or "<html" in body[:2048].lower():
            body = strip_html(body)
        targets.append((os.path.basename(p), body))

    for u in urls:
        try:
            targets.append((u, strip_html(fetch(u))))
        except urllib.error.URLError as e:
            print("cannot fetch %s: %s" % (u, e), file=sys.stderr)
            return 2

    if not targets:
        ap.print_help()
        return 2

    exempt_files = set(ledger.get("exempt", []))
    total = 0
    out = []

    for name, text in targets:
        # A file that documents the prohibitions is not violating them.
        exempt_rules = set()
        if os.path.basename(name) in exempt_files:
            exempt_rules = {r["id"] for r in ledger["red"]} | \
                           {r["id"] for r in ledger["amber"]}

        findings = check(name, text, ledger, exempt_rules)
        total += len(findings)
        if findings:
            out.append("%s%s%s" % (RED, name, OFF))
            for sev, cid, msg, where in findings:
                col = RED if sev in ("RED", "FIGURE", "PART") else YEL
                out.append("  %s%-6s%s %-22s %s" % (col, sev, OFF, cid, msg))
                out.append("         %s%s%s" % (DIM, where, OFF))
        elif not args.quiet:
            out.append("%s✓%s %s" % (GRN, OFF, name))

    if total or not args.quiet:
        print("\n".join(out))
        print("\n%d target(s), %s%d finding(s)%s" %
              (len(targets), RED if total else GRN, total, OFF))

    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())

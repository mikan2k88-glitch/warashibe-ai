from flask import Blueprint, Response

privacy_bp = Blueprint("privacy_policy", __name__)

@privacy_bp.get("/privacy")
def privacy_policy():
    html = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Warashibe AI Dropshipping Privacy Policy</title></head><body>
<h1>Warashibe AI Dropshipping Privacy Policy</h1>
<p>Effective: October 15, 2026. Contact: <a href="mailto:warashibeai@gmail.com">warashibeai@gmail.com</a>.</p>
<h2>Data and purposes</h2><p>With your authorization, we use the eBay sell.account.readonly scope to retrieve seller account policies, including return terms. We also analyze marketplace listings, supplier quotes, and shipping costs to evaluate research opportunities. We do not use this connection to place orders, post listings or process payments.</p>
<h2>Tokens and retention</h2><p>The current authorization callback exchanges a code for a temporary access token and uses the token for one read-only account policy request. It does not intentionally persist OAuth access or refresh tokens. Research observations and service logs may be retained for analysis and troubleshooting; infrastructure providers may separately retain technical logs.</p>
<h2>Providers</h2><p>eBay supplies account authorization and policy data; CJdropshipping supplies product information. Render hosts this app; GitHub supports its development; Supabase may store research observations. We do not sell account information.</p>
<h2>Security and your choices</h2><p>HTTPS is used for authorization. You may decline or revoke eBay authorization. To request access, correction, or deletion of information held by the app, contact <a href="mailto:warashibeai@gmail.com">warashibeai@gmail.com</a>. Requests are reviewed subject to applicable law and retention obligations.</p>
<h2>International transfers and changes</h2><p>Providers may process information in other countries. We will update this page when our practices change.</p>
</body></html>"""
    return Response(html, mimetype="text/html", headers={"Cache-Control": "public, max-age=300"})

"""
Verification test for modular frontend assets, CSS selectors, and endpoints.
"""
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_frontend_root():
    res = client.get("/")
    assert res.status_code == 200
    assert "<!DOCTYPE html>" in res.text
    assert "/css/main.css" in res.text
    assert "/js/app.js" in res.text
    assert res.headers.get("cache-control") == "no-cache, no-store, must-revalidate"
    # Verify markup elements
    assert 'class="logo-badge">G</div>' in res.text
    assert 'class="nav-bar">' in res.text
    assert 'class="nav-btn' in res.text

def test_css_assets_and_selectors():
    css_files = ["main.css", "dashboard.css", "incidents.css", "studio.css"]
    for css_file in css_files:
        res = client.get(f"/css/{css_file}")
        assert res.status_code == 200, f"CSS {css_file} returned {res.status_code}"
        assert len(res.text) > 100

    main_css = client.get("/css/main.css").text
    # Header logo flex alignment
    assert ".header-left" in main_css
    assert ".logo-badge" in main_css
    assert "background: #059669" in main_css
    # Nav bar buttons styling
    assert "button.nav-btn" in main_css or ".nav-btn" in main_css
    assert "border-bottom: 3px solid #059669" in main_css

def test_js_assets():
    js_files = [
        "config.js",
        "api.js",
        "components/kpiCards.js",
        "components/charts.js",
        "components/incidentsTable.js",
        "components/liveStudio.js",
        "components/insights.js",
        "components/testAi.js",
        "app.js"
    ]
    for js_file in js_files:
        res = client.get(f"/js/{js_file}")
        assert res.status_code == 200, f"JS {js_file} returned {res.status_code}"
        assert len(res.text) > 100

    api_js = client.get("/js/api.js").text
    assert "data.incidents" in api_js

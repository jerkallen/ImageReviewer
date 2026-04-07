from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
STYLE_CSS = ROOT / "static" / "css" / "style.css"
INDEX_HTML = ROOT / "templates" / "index.html"


def test_homepage_brand_acronym_is_emphasized_in_page_title():
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = STYLE_CSS.read_text(encoding="utf-8")

    assert '<h1 class="page-title"><span class="page-title-brand">UAES</span>无锡厂视觉图片二次确认</h1>' in html

    page_title_block = re.search(
        r"\.header\s+\.page-title\s*\{[^}]*font-weight:\s*([0-9]+);",
        css,
        re.S,
    )
    brand_block = re.search(
        r"\.header\s+\.page-title-brand\s*\{[^}]*font-weight:\s*([0-9]+);",
        css,
        re.S,
    )

    assert page_title_block and page_title_block.group(1) == "600"
    assert brand_block and brand_block.group(1) == "800"

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
STYLE_CSS = ROOT / "static" / "css" / "style.css"
MAIN_JS = ROOT / "static" / "js" / "main.js"
INDEX_HTML = ROOT / "templates" / "index.html"
TEMPLATE_FILES = [
    ROOT / "templates" / "history.html",
    ROOT / "templates" / "review.html",
    ROOT / "templates" / "settings.html",
]


def test_global_css_defines_new_theme_palette_and_font_stack():
    css = STYLE_CSS.read_text(encoding="utf-8")

    for marker in [
        "--theme-bg: #171d23;",
        "--theme-accent: #687f92;",
        "--theme-ok: #6f9586;",
        "--theme-nok: #c9735a;",
        "--theme-bg: #eceff1;",
        "--theme-text: #2f3a43;",
        "font-family: 'Bahnschrift', 'Segoe UI', 'Microsoft YaHei', sans-serif;",
    ]:
        assert marker in css

    for old_marker in [
        "#14100b",
        "#221a13",
        "#c9843d",
        "#dda464",
        "#8f5721",
    ]:
        assert old_marker not in css


def test_inline_styled_pages_apply_theme_override_block():
    for template_file in TEMPLATE_FILES:
        html = template_file.read_text(encoding="utf-8")

        assert "/* Theme overrides */" in html
        assert "var(--theme-accent)" in html
        assert "var(--theme-panel-strong)" in html

        for old_marker in [
            "rgba(201, 132, 61",
            "#fff8ef",
            "#fffaf4",
        ]:
            assert old_marker not in html


def test_button_text_sizes_are_bumped_without_layout_rework():
    css = STYLE_CSS.read_text(encoding="utf-8")
    settings_html = (ROOT / "templates" / "settings.html").read_text(encoding="utf-8")

    btn_block = re.search(r"\.btn\s*\{[^}]*font-size:\s*([0-9.]+rem);", css, re.S)
    btn_small_block = re.search(r"\.btn-small\s*\{[^}]*font-size:\s*([0-9.]+rem);", css, re.S)
    settings_button_block = re.search(
        r"\.btn-save,\s*\.btn-reset,\s*\.btn-test\s*\{[^}]*font-size:\s*([0-9.]+rem);",
        settings_html,
        re.S,
    )

    assert btn_block and btn_block.group(1) == "1.08rem"
    assert btn_small_block and btn_small_block.group(1) == "0.92rem"
    assert settings_button_block and settings_button_block.group(1) == "1.08rem"


def test_homepage_primary_image_area_is_larger():
    css = STYLE_CSS.read_text(encoding="utf-8")

    image_container_block = re.search(
        r"\.image-container\s*\{[^}]*min-height:\s*([0-9]+px);[^}]*max-height:\s*calc\(100vh - ([0-9]+px)\);",
        css,
        re.S,
    )
    main_image_block = re.search(
        r"\.main-image\s*\{[^}]*max-height:\s*calc\(100vh - ([0-9]+px)\);",
        css,
        re.S,
    )

    assert image_container_block and image_container_block.group(1) == "460px"
    assert image_container_block and image_container_block.group(2) == "320px"
    assert main_image_block and main_image_block.group(1) == "320px"


def test_homepage_has_image_fit_mode_control_with_default_mode():
    html = INDEX_HTML.read_text(encoding="utf-8")
    js = MAIN_JS.read_text(encoding="utf-8")

    assert 'id="image-fit-mode-controls"' in html
    assert 'id="image-fit-fit-window"' in html
    assert 'id="image-fit-prioritize-height"' in html
    assert 'data-image-fit-mode="fit-window"' in html

    options_section_index = html.index('<div class="options-section">')
    control_index = html.index('id="image-fit-mode-controls"')
    aside_end_index = html.index('</aside>')
    main_area_index = html.index('<main class="image-area"')

    assert options_section_index < control_index < aside_end_index
    assert control_index < main_area_index

    assert "const IMAGE_FIT_MODE_STORAGE_KEY = 'imageFitMode';" in js
    assert "const DEFAULT_IMAGE_FIT_MODE = 'fit-window';" in js


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


def test_homepage_image_fit_mode_is_persisted_in_local_storage():
    js = MAIN_JS.read_text(encoding="utf-8")

    assert "localStorage.getItem(IMAGE_FIT_MODE_STORAGE_KEY)" in js
    assert "localStorage.setItem(IMAGE_FIT_MODE_STORAGE_KEY, mode);" in js


def test_homepage_image_fit_modes_define_distinct_css_strategies():
    css = STYLE_CSS.read_text(encoding="utf-8")

    fit_window_block = re.search(
        r'\.image-area\[data-image-fit-mode="fit-window"\]\s*\{[^}]*--image-frame-offset:\s*([0-9]+px);',
        css,
        re.S,
    )
    prioritize_height_block = re.search(
        r'\.image-area\[data-image-fit-mode="prioritize-height"\]\s*\{[^}]*--image-frame-offset:\s*([0-9]+px);[^}]*--image-min-height:\s*([0-9]+px);',
        css,
        re.S,
    )

    assert fit_window_block and fit_window_block.group(1) == "320px"
    assert prioritize_height_block and prioritize_height_block.group(1) != "320px"
    assert prioritize_height_block and prioritize_height_block.group(2) != "460px"


def test_theme_toggle_is_docked_to_page_top_right_corner_and_scrolls_with_page():
    css = STYLE_CSS.read_text(encoding="utf-8")
    js = MAIN_JS.read_text(encoding="utf-8")

    theme_toggle_block = re.search(
        r"\.theme-toggle\s*\{[^}]*position:\s*absolute;[^}]*top:\s*0;[^}]*right:\s*0;[^}]*border-radius:\s*0\s+0\s+0\s+([0-9]+px);",
        css,
        re.S,
    )

    assert "const themeHost = document.querySelector('.container') || document.body;" in js
    assert "themeHost.appendChild(toggle);" in js
    assert theme_toggle_block and theme_toggle_block.group(1) == "12px"

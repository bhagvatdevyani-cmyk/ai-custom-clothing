
import io
import zipfile
from html import escape

import cairosvg
import streamlit as st

# ==========================================================
# AI-ASSISTED CUSTOM CLOTHING SYSTEM
# Recommendations + responsive images + pattern prototype
# ==========================================================

st.set_page_config(
    page_title="AI-Assisted Custom Clothing System",
    page_icon="🧵",
    layout="wide",
)

st.markdown("""
<style>
.block-container {
    max-width: 1600px;
    padding: 1.5rem 2rem;
}
.hero {
    padding: 25px;
    border-radius: 18px;
    background: linear-gradient(120deg, #f8e5ef, #eee7fa);
    margin-bottom: 20px;
}
.hero h1 { color: #492b40; }
.hero p { color: #654b60; }

/* Responsive inspiration images */
[data-testid="stImage"] img {
    display: block;
    width: 100%;
    max-width: 100%;
    height: auto;
    object-fit: contain;
    border-radius: 12px;
}

/* Responsive layout on smaller screens */
@media (max-width: 700px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>

<div class="hero">
    <h1>🧵 AI-Assisted Custom Clothing System</h1>
    <p>Explore fashion recommendations, visual inspiration,
    and measurement-based garment pattern drafting.</p>
</div>
""", unsafe_allow_html=True)


# ==========================================================
# CLOTHING CATALOGUE
# ==========================================================

GARMENTS = {
    "Straight Kurti": {
        "styles": ["Minimal", "Traditional", "Indo-western",
                   "Office wear", "Casual"],
        "occasions": ["College", "Office", "Everyday",
                      "Festive", "Casual outing"],
        "fabrics": ["Cotton", "Rayon", "Linen", "Viscose"],
        "colors": ["Pastel pink", "Black", "White", "Blue",
                   "Earth tones", "Jewel tones"],
        "image": "https://images.unsplash.com/photo-1583391733956-6c78276477e3?auto=format&fit=crop&w=900&q=85",
        "description": "A versatile, straight silhouette for daily wear.",
        "tip": "Try cotton, a contrast placket, side slits, or subtle embroidery.",
    },
    "A-Line Kurti": {
        "styles": ["Traditional", "Indo-western", "Casual", "Festive"],
        "occasions": ["College", "Casual outing", "Festive", "Everyday"],
        "fabrics": ["Cotton", "Rayon", "Viscose", "Chanderi"],
        "colors": ["Pastel pink", "Blue", "White", "Earth tones"],
        "image": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=900&q=85",
        "description": "A gently flared silhouette with comfortable movement.",
        "tip": "Try a printed yoke, a narrow border, or a flowing fabric.",
    },
    "Tunics": {
        "styles": ["Minimal", "Office wear", "Casual", "Indo-western"],
        "occasions": ["College", "Office", "Travel", "Everyday"],
        "fabrics": ["Cotton", "Linen", "Rayon", "Viscose"],
        "colors": ["White", "Black", "Blue", "Earth tones"],
        "image": "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=900&q=85",
        "description": "Easy separates for jeans, trousers, or palazzos.",
        "tip": "Explore curved hems, mandarin collars, and small side slits.",
    },
    "Tops": {
        "styles": ["Minimal", "Trendy", "Casual", "Office wear",
                   "Indo-western"],
        "occasions": ["College", "Office", "Casual outing",
                      "Party", "Travel"],
        "fabrics": ["Cotton", "Linen", "Satin", "Rayon"],
        "colors": ["White", "Black", "Pastel pink", "Blue"],
        "image": "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?auto=format&fit=crop&w=900&q=85",
        "description": "Wardrobe essentials for skirts, jeans, and tailored pants.",
        "tip": "Balance a relaxed top with a clean silhouette on the bottom.",
    },
    "Blouse": {
        "styles": ["Traditional", "Festive", "Minimal", "Statement"],
        "occasions": ["Festive", "Wedding guest", "Family function"],
        "fabrics": ["Cotton", "Silk blend", "Raw silk", "Satin"],
        "colors": ["Jewel tones", "Black", "Gold", "Pastel pink"],
        "image": "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?auto=format&fit=crop&w=900&q=85",
        "description": "A styling piece for sarees and ethnic ensembles.",
        "tip": "Check armhole comfort and closure placement before embellishing.",
    },
    "Dress": {
        "styles": ["Minimal", "Romantic", "Trendy", "Classic", "Festive"],
        "occasions": ["Casual outing", "Party", "Wedding guest", "Travel"],
        "fabrics": ["Cotton", "Linen", "Rayon", "Satin", "Viscose"],
        "colors": ["Pastel pink", "Black", "White", "Blue", "Jewel tones"],
        "image": "https://images.unsplash.com/photo-1539008835657-9e8e9680c956?auto=format&fit=crop&w=900&q=85",
        "description": "A one-piece option adaptable to different occasions.",
        "tip": "Test the bust, waist, hip, and hem balance with a toile.",
    },
    "Skirt": {
        "styles": ["Classic", "Minimal", "Indo-western", "Festive"],
        "occasions": ["College", "Casual outing", "Festive", "Party"],
        "fabrics": ["Cotton", "Rayon", "Linen", "Satin", "Silk blend"],
        "colors": ["Black", "White", "Pastel pink", "Blue", "Earth tones"],
        "image": "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?auto=format&fit=crop&w=900&q=85",
        "description": "A versatile separate for shirts, fitted tops, and blouses.",
        "tip": "Check waist finish, hip ease, and walking room.",
    },
    "Palazzo Pants": {
        "styles": ["Minimal", "Indo-western", "Casual", "Office wear"],
        "occasions": ["College", "Office", "Travel", "Festive"],
        "fabrics": ["Cotton", "Rayon", "Linen", "Viscose"],
        "colors": ["Black", "White", "Blue", "Earth tones"],
        "image": "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=900&q=85",
        "description": "Wide-leg trousers with an airy, flowing silhouette.",
        "tip": "Check crotch depth, stride comfort, and finished length.",
    },
}


# ==========================================================
# STYLE PREFERENCES
# ==========================================================

st.sidebar.header("Your style preferences")

occasion = st.sidebar.selectbox(
    "Occasion",
    ["College", "Office", "Casual outing", "Travel", "Festive",
     "Party", "Wedding guest", "Everyday", "Family function"],
)

style = st.sidebar.selectbox(
    "Preferred style",
    ["Any", "Minimal", "Traditional", "Indo-western", "Office wear",
     "Casual", "Trendy", "Classic", "Romantic", "Statement", "Festive"],
)

fabric = st.sidebar.selectbox(
    "Preferred fabric",
    ["Any", "Cotton", "Rayon", "Linen", "Viscose", "Satin",
     "Silk blend", "Raw silk", "Chanderi"],
)

color = st.sidebar.selectbox(
    "Preferred colour",
    ["Any", "Pastel pink", "Black", "White", "Blue",
     "Earth tones", "Jewel tones", "Gold"],
)

budget = st.sidebar.selectbox(
    "Budget",
    ["Budget-friendly", "Mid-range", "Premium"],
)

sleeves = st.sidebar.selectbox(
    "Sleeve preference",
    ["Any", "Sleeveless", "Short sleeve",
     "Three-quarter sleeve", "Full sleeve"],
)

fit = st.sidebar.selectbox(
    "Fit preference",
    ["Any", "Relaxed", "Regular", "Fitted"],
)


# ==========================================================
# RECOMMENDATION ENGINE
# Rule-based scoring, not a trained AI model
# ==========================================================

def rank_garments():
    results = []

    for name, item in GARMENTS.items():
        score = 0

        if occasion in item["occasions"]:
            score += 3

        if style != "Any" and style in item["styles"]:
            score += 2

        if fabric != "Any" and fabric in item["fabrics"]:
            score += 2

        if color != "Any" and color in item["colors"]:
            score += 1

        if fit == "Relaxed" and name in [
            "Tunics", "Dress", "Palazzo Pants", "A-Line Kurti"
        ]:
            score += 1

        if fit == "Fitted" and name in [
            "Tops", "Blouse", "Straight Kurti"
        ]:
            score += 1

        if sleeves == "Sleeveless" and name in [
            "Tops", "Dress", "Blouse"
        ]:
            score += 1

        if sleeves == "Full sleeve" and name in [
            "Straight Kurti", "A-Line Kurti", "Tunics"
        ]:
            score += 1

        # Budget is retained as a user preference.
        # No verified garment prices are available, so it does
        # not fabricate prices or affect the score.

        results.append((score, name, item))

    return sorted(results, key=lambda x: (-x[0], x[1]))


# ==========================================================
# APP TABS
# ==========================================================

recommendation_tab, pattern_tab, info_tab = st.tabs([
    "✨ Clothing Recommendations & Images",
    "📐 Custom Pattern Generator",
    "ℹ️ About the System",
])


# ==========================================================
# CLOTHING RECOMMENDATIONS + IMAGES
# ==========================================================

with recommendation_tab:
    st.subheader("Your personalised clothing suggestions")

    st.write(
        f"Explore outfit ideas for **{occasion}**, "
        f"with **{style.lower()}** styling and "
        f"**{color.lower()}** colour preferences."
    )

    ranked = rank_garments()

    for start in range(0, len(ranked), 3):
        columns = st.columns(3)

        for column, (score, name, item) in zip(
            columns, ranked[start:start + 3]
        ):
            with column:
                st.markdown(f"### {name}")

                # Responsive display:
                # image fits its column and preserves aspect ratio.
                st.image(
                    item["image"],
                    caption=f"Visual inspiration: {name}",
                    use_container_width=True,
                )

                st.write(item["description"])
                st.write(f"**Design idea:** {item['tip']}")

                if score >= 6:
                    st.success("Strong preference match")
                elif score >= 3:
                    st.info("Possible match")
                else:
                    st.caption("Alternative style to explore")

                with st.expander("Fabric, colour & occasion details"):
                    st.write("**Suitable fabrics:** " + ", ".join(item["fabrics"]))
                    st.write("**Colour ideas:** " + ", ".join(item["colors"]))
                    st.write("**Occasions:** " + ", ".join(item["occasions"]))

    st.caption(
        "Images are external visual references and require internet access. "
        "Replace these URLs with your own licensed garment photographs "
        "or approved image sources when deploying the application."
    )


# ==========================================================
# STRAIGHT KURTI SVG DRAFT
# EDUCATIONAL PROTOTYPE — NOT FIT-VALIDATED
# ==========================================================

def create_kurti_svg(m, ease, seam, hem):
    """
    Creates a simplified front/back half-block illustration.

    Units in the SVG are millimetres; entered body measurements
    are centimetres.

    IMPORTANT: This is not a professionally validated pattern.
    It is a simplified prototype for demonstrating the workflow.
    """

    for label, value in m.items():
        if value <= 0:
            raise ValueError(f"{label} must be greater than zero.")

    if m["Neck width"] >= m["Shoulder"]:
        raise ValueError("Neck width must be smaller than shoulder.")

    if m["Armhole depth"] >= m["Kurti length"]:
        raise ValueError("Armhole depth must be less than kurti length.")

    if m["Front neck depth"] >= m["Kurti length"]:
        raise ValueError("Front neck depth must be less than kurti length.")

    if m["Back neck depth"] >= m["Kurti length"]:
        raise ValueError("Back neck depth must be less than kurti length.")

    # Quarter body measurements plus ease.
    chest = (m["Bust"] + ease) / 4
    waist = (m["Waist"] + ease) / 4
    hip = (m["Hip"] + ease) / 4

    # Simplified geometry. This does NOT calculate a proper
    # armhole curve, shoulder slope, or seam-offset contour.
    piece_width_cm = max(chest, waist, hip) + seam + 2
    piece_height_cm = m["Kurti length"] + hem + seam + 2

    scale = 10.0  # 1 cm = 10 mm
    width = piece_width_cm * scale
    height = piece_height_cm * scale
    gap = 30 * scale

    total_width = width * 2 + gap
    total_height = height + 100

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{total_width}mm" height="{total_height}mm" '
        f'viewBox="0 0 {total_width} {total_height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>'
        'text{font-family:Arial,sans-serif;fill:#222}'
        '.outline{fill:#fff8fc;stroke:#9d3267;stroke-width:0.7}'
        '.detail{fill:none;stroke:#222;stroke-width:0.5}'
        '.grain{stroke:#28754a;stroke-width:0.8}'
        '.dash{stroke-dasharray:4 3}'
        '</style>',
    ]

    for index, front in enumerate([True, False]):
        offset_x = index * (width + gap)

        neck_depth = (
            m["Front neck depth"] if front
            else m["Back neck depth"]
        )

        # Coordinates in mm
        x0 = offset_x
        x_neck = offset_x + (m["Neck width"] / 2 + seam) * scale
        x_shoulder = offset_x + (
            m["Shoulder"] / 2 + seam
        ) * scale

        x_chest = offset_x + (chest + seam) * scale
        x_waist = offset_x + (waist + seam) * scale
        x_hip = offset_x + (hip + seam) * scale
        x_side = max(x_chest, x_waist, x_hip)

        y_top = seam * scale
        y_neck = (neck_depth + seam) * scale
        y_shoulder = (m["Shoulder"] / 2 + seam) * scale
        y_arm = (m["Armhole depth"] + seam) * scale
        y_waist = (m["Kurti length"] * 0.42 + seam) * scale
        y_hip = (m["Kurti length"] * 0.62 + seam) * scale
        y_hem = (m["Kurti length"] + hem + seam) * scale

        outline = (
            f"M {x0} {y_top} "
            f"L {x_neck} {y_top} "
            f"Q {x_shoulder * 0.85 + offset_x * 0.15} {y_top} "
            f"{x_shoulder} {y_shoulder} "
            f"L {x_chest} {y_arm} "
            f"L {x_waist} {y_waist} "
            f"L {x_hip} {y_hip} "
            f"L {x_side} {y_hem} "
            f"L {x0} {y_hem} Z"
        )

        neck = (
            f"M {x0} {y_top} "
            f"Q {x0 + 1} {y_top} {x_neck} {y_neck}"
        )

        label = "FRONT HALF BLOCK" if front else "BACK HALF BLOCK"

        parts.append(f'<path class="outline" d="{outline}"/>')
        parts.append(f'<path class="detail" d="{neck}"/>')

        # Centre/fold line
        parts.append(
            f'<line class="detail dash" x1="{x0}" y1="{y_top}" '
            f'x2="{x0}" y2="{y_hem}"/>'
        )

        # Grainline
        grain_x = offset_x + x_side * 0.45
        grain_y1 = y_hem * 0.30
        grain_y2 = y_hem * 0.72

        parts.append(
            f'<line class="grain" x1="{grain_x}" y1="{grain_y1}" '
            f'x2="{grain_x}" y2="{grain_y2}"/>'
        )

        # Notch at approximate armhole level
        parts.append(
            f'<line class="detail" x1="{x_chest - 2}" y1="{y_arm}" '
            f'x2="{x_chest + 2}" y2="{y_arm}"/>'
        )

        # Labels are kept outside the cutting outline.
        parts.append(
            f'<text x="{offset_x + 5}" y="{y_hem + 18}" '
            f'font-size="5">{escape(label)}</text>'
        )
        parts.append(
            f'<text x="{offset_x + 5}" y="{y_hem + 28}" '
            f'font-size="3.5">Simplified half-block / verify fold</text>'
        )
        parts.append(
            f'<text x="{offset_x + 5}" y="{y_hem + 38}" '
            f'font-size="3.5">Seam: {seam:g} cm | Hem: {hem:g} cm</text>'
        )

    # 50 mm calibration square
    square_x = 10
    square_y = total_height - 65

    parts.append(
        f'<rect x="{square_x}" y="{square_y}" width="50" height="50" '
        f'fill="none" stroke="#111" stroke-width="0.7"/>'
    )
    parts.append(
        f'<text x="{square_x}" y="{square_y - 5}" font-size="4">'
        'Calibration square: 5 cm × 5 cm</text>'
    )
    parts.append(
        f'<text x="10" y="{total_height - 8}" font-size="3.5">'
        'UNVALIDATED EDUCATIONAL PROTOTYPE — make and fit a toile first.'
        '</text>'
    )
    parts.append("</svg>")

    return "".join(parts)


# ==========================================================
# PATTERN GENERATOR INTERFACE
# ==========================================================

with pattern_tab:
    st.subheader("Straight Kurti — custom measurement prototype")

    st.warning(
        "This pattern is an unvalidated prototype. It is not a "
        "production-ready garment block and does not guarantee fit. "
        "The current simplified geometry does not include a properly "
        "drafted armhole, sleeve, darts, placket, facing, or verified "
        "seam-offset curves. Make a toile and validate the fit first."
    )

    st.write("Enter body measurements in centimetres.")

    with st.form("kurti_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            bust = st.number_input(
                "Bust (cm)", 50.0, 180.0, 90.0, step=0.5
            )
            waist = st.number_input(
                "Waist (cm)", 45.0, 170.0, 76.0, step=0.5
            )
            hip = st.number_input(
                "Hip (cm)", 50.0, 190.0, 96.0, step=0.5
            )

        with col2:
            shoulder = st.number_input(
                "Shoulder (cm)", 25.0, 60.0, 36.0, step=0.5
            )
            armhole = st.number_input(
                "Armhole depth (cm)", 12.0, 45.0, 21.0, step=0.5
            )
            length = st.number_input(
                "Kurti length (cm)", 35.0, 160.0, 100.0, step=0.5
            )

        with col3:
            neck_width = st.number_input(
                "Neck width (cm)", 5.0, 25.0, 8.0, step=0.5
            )
            front_neck = st.number_input(
                "Front neck depth (cm)", 3.0, 35.0, 12.0, step=0.5
            )
            back_neck = st.number_input(
                "Back neck depth (cm)", 1.0, 20.0, 3.0, step=0.5
            )

        col4, col5, col6 = st.columns(3)

        with col4:
            ease = st.number_input(
                "Added ease (cm)", 0.0, 20.0, 6.0, step=0.5
            )

        with col5:
            seam = st.number_input(
                "Seam allowance (cm)", 0.0, 3.0, 1.0, step=0.5
            )

        with col6:
            hem = st.number_input(
                "Hem allowance (cm)", 0.0, 8.0, 3.0, step=0.5
            )

        generate = st.form_submit_button(
            "Generate prototype pattern",
            type="primary",
        )

    if generate:
        measurements = {
            "Bust": bust,
            "Waist": waist,
            "Hip": hip,
            "Shoulder": shoulder,
            "Armhole depth": armhole,
            "Kurti length": length,
            "Neck width": neck_width,
            "Front neck depth": front_neck,
            "Back neck depth": back_neck,
        }

        try:
            svg_string = create_kurti_svg(
                measurements, ease, seam, hem
            )

            st.session_state["kurti_svg"] = svg_string

            st.success(
                "Prototype created. Review the drawing and limitations below."
            )

        except ValueError as error:
            st.error(str(error))

    if "kurti_svg" in st.session_state:
        svg_string = st.session_state["kurti_svg"]
        svg_bytes = svg_string.encode("utf-8")

        # Preview scales responsively; downloaded geometry retains its
        # physical SVG dimensions. Preview size is not print scale.
        st.markdown("### Pattern preview")
        st.caption(
            "The preview adapts to the available page width. "
            "Use actual-size printing for the downloaded pattern, "
            "not Fit to Page."
        )

        import streamlit.components.v1 as components

        preview_svg = svg_string.replace(
            "<svg ",
            '<svg style="width:100%;height:auto;display:block" ',
            1,
        )

        components.html(
            f"""
            <div style="width:100%;overflow:auto;background:white;
                        border:1px solid #ddd;border-radius:10px;padding:8px">
                {preview_svg}
            </div>
            """,
            height=650,
            scrolling=True,
        )

        try:
            pdf_bytes = cairosvg.svg2pdf(bytestring=svg_bytes)

            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(
                zip_buffer, "w", zipfile.ZIP_DEFLATED
            ) as archive:
                archive.writestr(
                    "straight_kurti_prototype.svg", svg_bytes
                )
                archive.writestr(
                    "straight_kurti_prototype.pdf", pdf_bytes
                )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.download_button(
                    "Download SVG",
                    data=svg_bytes,
                    file_name="straight_kurti_prototype.svg",
                    mime="image/svg+xml",
                    use_container_width=True,
                )

            with col2:
                st.download_button(
                    "Download PDF",
                    data=pdf_bytes,
                    file_name="straight_kurti_prototype.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            with col3:
                st.download_button(
                    "Download both (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="straight_kurti_files.zip",
                    mime="application/zip",
                    use_container_width=True,
                )

        except Exception as error:
            st.error(f"Export error: {error}")

        st.markdown("### Printing checklist")
        st.markdown("""
        - [ ] Print at 100% / Actual Size.
        - [ ] Disable Fit to Page or Shrink to Fit.
        - [ ] Measure the calibration square; it should be 5 × 5 cm.
        - [ ] Check every measurement and pattern line with a ruler.
        - [ ] Make a test garment in inexpensive fabric.
        - [ ] Correct fit before cutting the final fabric.
        """)

        st.error(
            "Validation status: UNVALIDATED. This prototype does not "
            "produce a verified, construction-ready kurti pattern. "
            "Do not rely on it for production cutting."
        )


# ==========================================================
# ABOUT / LIMITATIONS
# ==========================================================

with info_tab:
    st.subheader("About this system")

    st.markdown("""
    **Clothing recommendations**
    - Preference-based suggestions for multiple garment categories.
    - Visual inspiration images and styling advice.
    - Rule-based ranking; not a trained AI recommendation model.

    **Pattern generator**
    - Straight Kurti prototype.
    - Measurements in centimetres.
    - SVG and PDF export.
    - Calibration square for checking print scale.

    **Image sizing**
    - Recommendation images resize with their display columns.
    - The original image aspect ratio is preserved.
    - Images are not forced to a fixed height or cropped to fill a card.
    - Pattern previews resize for screen viewing, while printable pattern
      geometry must retain its physical dimensions.

    **Current limitations**
    - The pattern is not fit-validated.
    - Sleeve, placket, facing, darts and professional curved seam
      construction are not fully drafted.
    - External images require an internet connection.
    """)

st.divider()
st.caption(
    "AI-Assisted Custom Clothing System | Educational prototype"
)

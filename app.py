
import streamlit as st
import streamlit.components.v1 as components
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

st.set_page_config(
    page_title="Custom Clothing Studio",
    page_icon="👗",
    layout="wide"
)

st.title("👗 AI-Assisted Custom Clothing System")
st.write(
    "Explore women's clothing styles, enter body measurements, "
    "preview a design, and download a pattern diagram and report."
)

st.warning(
    "This is a prototype. Pattern diagrams are schematic starting "
    "blocks, not validated, ready-to-cut sewing patterns. Always "
    "make and fit a test garment before cutting final fabric."
)

GARMENTS = {
    "Straight Kurti": "body",
    "A-Line Kurti": "aline",
    "Everyday Tunic": "body",
    "Long Tunic": "aline",
    "Sleeveless Top": "top",
    "Basic Blouse": "blouse",
    "Shift Dress": "dress",
    "Maxi Dress": "maxi",
    "Gathered Skirt": "skirt",
    "Palazzo Trousers": "palazzo",
}

COLORS = {
    "Blush pink": "#e9a7b5",
    "Lavender": "#b8a6dc",
    "Sky blue": "#8fc7e8",
    "Sage green": "#9cb89a",
    "Black": "#55515a",
    "Cream": "#eadcc5",
}

with st.sidebar:
    st.header("Design preferences")
    age_group = st.selectbox(
        "Age group",
        ["Teen", "Young adult", "Adult", "Mature adult", "Senior adult"]
    )
    garment = st.selectbox("Garment", list(GARMENTS.keys()))
    fit = st.selectbox(
        "Preferred fit", ["Regular", "Relaxed", "Fitted"]
    )
    fabric = st.selectbox(
        "Fabric",
        ["Cotton", "Linen", "Rayon", "Silk", "Denim", "Crepe"]
    )
    occasion = st.selectbox(
        "Occasion",
        ["Everyday", "College", "Office", "Festive", "Party", "Formal"]
    )
    color_name = st.selectbox("Design color", list(COLORS.keys()))
    budget = st.selectbox(
        "Budget",
        ["Under ₹500", "₹500–₹1,000", "₹1,000–₹2,000", "Above ₹2,000"]
    )

st.header("1. Enter body measurements")
st.caption("Enter measurements in centimetres.")

left, right = st.columns(2)

with left:
    bust = st.number_input(
        "Bust circumference (cm)", min_value=40.0,
        max_value=180.0, value=90.0
    )
    waist = st.number_input(
        "Waist circumference (cm)", min_value=35.0,
        max_value=170.0, value=75.0
    )
    hip = st.number_input(
        "Hip circumference (cm)", min_value=40.0,
        max_value=190.0, value=98.0
    )
    shoulder = st.number_input(
        "Shoulder width (cm)", min_value=20.0,
        max_value=60.0, value=38.0
    )
    armhole = st.number_input(
        "Armhole circumference (cm)", min_value=20.0,
        max_value=75.0, value=42.0
    )

with right:
    length = st.number_input(
        "Garment length (cm)", min_value=20.0,
        max_value=180.0, value=75.0
    )
    sleeve = st.number_input(
        "Sleeve length (cm)", min_value=0.0,
        max_value=85.0, value=20.0
    )
    ease = st.number_input(
        "Ease allowance (cm)", min_value=0.0,
        max_value=20.0, value=4.0
    )
    seam = st.number_input(
        "Seam allowance setting (cm)", min_value=0.0,
        max_value=3.0, value=1.5
    )

st.caption(
    "Age is used only as a style preference. The pattern preview "
    "uses the measurements you enter."
)


def make_recommendation(occasion, fabric, fit):
    suggestions = {
        "Everyday": "Prioritize comfort and easy-care construction.",
        "College": "Consider a versatile design for everyday movement.",
        "Office": "Consider a clean silhouette and neat finishing.",
        "Festive": "Consider decorative trims or embroidery.",
        "Party": "Consider statement details and suitable fabric drape.",
        "Formal": "Consider structured styling and refined finishing.",
    }
    return (
        f"{suggestions[occasion]} "
        f"Fabric preference: {fabric}. Preferred fit: {fit.lower()}."
    )


def draft_outline(kind, bust, waist, hip, length, ease, fit):
    """Create an illustrative outline, not a validated garment pattern."""
    fit_adjustment = 4 if fit == "Relaxed" else -2 if fit == "Fitted" else 0
    effective_ease = max(0, ease + fit_adjustment)

    quarter_bust = bust / 4 + effective_ease / 4
    quarter_waist = waist / 4 + effective_ease / 4
    quarter_hip = hip / 4 + effective_ease / 4

    if kind == "body":
        top = max(quarter_bust, quarter_hip)
        waist_width = max(quarter_waist, top * 0.85)
        hem = top
        points = [
            (0, 0), (top, 0),
            (waist_width, length * 0.48),
            (hem, length), (0, length)
        ]
    elif kind == "aline":
        top = max(quarter_bust, quarter_hip)
        hem = top + min(length * 0.18, 18)
        points = [
            (0, 0), (top, 0), (hem, length), (0, length)
        ]
    elif kind in ("top", "blouse"):
        top = max(quarter_bust, quarter_waist)
        hem = max(quarter_hip, quarter_waist)
        body_length = min(length, 45 if kind == "blouse" else 65)
        points = [
            (0, 0), (top, 0), (hem, body_length), (0, body_length)
        ]
    elif kind in ("dress", "maxi"):
        top = max(quarter_bust, quarter_hip)
        middle = max(top, quarter_waist)
        hem = top + (12 if kind == "maxi" else 5)
        points = [
            (0, 0), (top, 0),
            (middle, length * 0.45),
            (hem, length), (0, length)
        ]
    elif kind == "skirt":
        top = waist / 2 + effective_ease / 2
        hem = top * 1.35
        points = [
            (0, 0), (top, 0), (hem, length), (0, length)
        ]
    else:
        top = hip / 2 + effective_ease / 2
        leg = max(16, top * 0.62)
        points = [
            (0, 0), (top, 0),
            (top * 0.85, length * 0.22),
            (leg, length), (0, length)
        ]

    return points, quarter_bust, quarter_waist, quarter_hip


def pattern_svg(points, garment, seam):
    padding = 20
    scale = 8  # Drawing scale only; this is not a full-scale pattern.
    max_x = max(x for x, y in points)
    max_y = max(y for x, y in points)

    width = (max_x + padding * 2) * scale
    height = (max_y + padding * 2) * scale

    coordinates = " ".join(
        f"{(x + padding) * scale:.1f},{(y + padding) * scale:.1f}"
        for x, y in points
    )

    grain_x = (max_x / 2 + padding) * scale
    grain_top = (padding + 5) * scale
    grain_bottom = (max_y + padding - 5) * scale

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
        width="{width}" height="{height}"
        viewBox="0 0 {width} {height}">
        <rect width="100%" height="100%" fill="white"/>
        <text x="20" y="22" font-size="16" font-weight="bold">
        {escape(garment)} — Schematic Pattern Block</text>
        <polygon points="{coordinates}"
        fill="#f9e4eb" stroke="#292929" stroke-width="2"/>
        <line x1="{grain_x}" y1="{grain_top}"
        x2="{grain_x}" y2="{grain_bottom}"
        stroke="#2274a5" stroke-width="2" stroke-dasharray="8 5"/>
        <text x="{grain_x + 8}" y="{(max_y / 2 + padding) * scale}"
        font-size="12" fill="#2274a5">Grainline</text>
        <text x="20" y="{height - 15}" font-size="12">
        Drawing scale is schematic. Seam allowance setting: {seam} cm.
        This outline does not contain validated seam offsets or shaping.
        </text>
        </svg>"""


def garment_svg(garment, color):
    kind = GARMENTS[garment]

    if kind in ("body", "aline", "dress", "maxi"):
        points = (
            "65,45 135,45 155,85 175,220 25,220 45,85"
            if kind in ("aline", "maxi")
            else "65,45 135,45 155,85 145,155 55,155 45,85"
        )
        if kind == "maxi":
            points = "65,45 135,45 155,85 185,235 15,235 45,85"
    elif kind in ("top", "blouse"):
        points = "65,45 135,45 155,85 145,150 55,150 45,85"
    elif kind == "skirt":
        points = "65,55 135,55 175,185 25,185"
    else:
        points = "65,45 135,45 155,85 125,115 120,210 90,210 100,115 80,115 70,210 40,210 45,85"

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
        width="240" height="290" viewBox="0 0 240 290">
        <rect width="240" height="290" rx="12" fill="#faf7f5"/>
        <circle cx="120" cy="25" r="14" fill="#d8b49b"/>
        <path d="M106 20 Q120 0 134 20" fill="#49362e"/>
        <polygon points="{points}" transform="translate(0,30)"
        fill="{color}" stroke="#55434b" stroke-width="2"/>
        <text x="120" y="275" text-anchor="middle"
        font-size="12" fill="#333">{escape(garment)}</text>
        </svg>"""


def create_pdf(report):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    page_width, page_height = A4
    y = page_height - 50

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, "Custom Clothing Design Report")
    y -= 30
    pdf.setFont("Helvetica", 10)

    for key, value in report.items():
        if y < 45:
            pdf.showPage()
            y = page_height - 45
            pdf.setFont("Helvetica", 10)

        pdf.drawString(40, y, f"{key}: {str(value)[:100]}")
        y -= 19

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


if st.button("Generate garment illustration and pattern", type="primary"):
    points, qb, qw, qh = draft_outline(
        GARMENTS[garment], bust, waist, hip, length, ease, fit
    )

    report = {
        "Age group": age_group,
        "Garment": garment,
        "Fit": fit,
        "Fabric": fabric,
        "Occasion": occasion,
        "Color": color_name,
        "Budget": budget,
        "Bust (cm)": bust,
        "Waist (cm)": waist,
        "Hip (cm)": hip,
        "Shoulder width (cm)": shoulder,
        "Armhole circumference (cm)": armhole,
        "Garment length (cm)": length,
        "Sleeve length (cm)": sleeve,
        "Ease allowance (cm)": ease,
        "Seam allowance setting (cm)": seam,
        "Quarter bust (cm)": round(qb, 2),
        "Quarter waist (cm)": round(qw, 2),
        "Quarter hip (cm)": round(qh, 2),
        "Recommendation": make_recommendation(occasion, fabric, fit),
    }

    st.session_state["pattern"] = pattern_svg(points, garment, seam)
    st.session_state["illustration"] = garment_svg(
        garment, COLORS[color_name]
    )
    st.session_state["report"] = report

if "pattern" in st.session_state:
    st.header("2. Generated design")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Garment illustration")
        components.html(
            st.session_state["illustration"], height=310, scrolling=False
        )
        st.download_button(
            "Download garment illustration (SVG)",
            data=st.session_state["illustration"],
            file_name="garment_illustration.svg",
            mime="image/svg+xml",
        )

    with col2:
        st.subheader("Pattern diagram")
        components.html(
            st.session_state["pattern"], height=480, scrolling=True
        )
        st.download_button(
            "Download pattern diagram (SVG)",
            data=st.session_state["pattern"],
            file_name="pattern_preview.svg",
            mime="image/svg+xml",
        )

    st.header("3. Recommendation and report")
    for key, value in st.session_state["report"].items():
        st.write(f"**{key}:** {value}")

    st.download_button(
        "Download measurement report (PDF)",
        data=create_pdf(st.session_state["report"]),
        file_name="clothing_design_report.pdf",
        mime="application/pdf",
    )

    st.warning(
        "The pattern is a schematic preview, not a validated sewing pattern. "
        "It does not yet construct accurate armholes, necklines, darts, "
        "sleeve caps, crotch curves, closures, or true seam-allowance offsets. "
        "Do not cut final fabric from this diagram."
    )

st.divider()
st.caption(
    "Future development: tested garment-specific drafting rules, "
    "front and back pattern pieces, printable tiled patterns, and "
    "optional AI-generated fashion images."
)

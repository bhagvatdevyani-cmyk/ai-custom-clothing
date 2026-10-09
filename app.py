
from pathlib import Path
from io import BytesIO
import html
import math
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
IMAGE_DIR = APP_DIR / "images"

st.set_page_config(
    page_title="AI-Assisted Custom Clothing System",
    page_icon="🧵",
    layout="wide",
)

# No network calls, analytics, external AI APIs, or saved measurements.
st.markdown("""
<style>
.block-container {max-width: 1400px; padding-top: 1.2rem;}
[data-testid="stImage"] img {
    width: 100%; max-width: 100%; height: auto;
    object-fit: contain;
}
.pattern-preview {
    width: 100%; overflow: auto; border: 1px solid #ddd;
    padding: 8px; border-radius: 8px;
}
.small-note {font-size: 0.9rem; color: #666;}
</style>
""", unsafe_allow_html=True)

st.title("🧵 AI-Assisted Custom Clothing System")
st.caption("Local-first prototype • Measurements in centimetres • No external AI service")

st.info(
    "Privacy note: this app does not intentionally transmit or save your measurements. "
    "Streamlit session state is temporary, but your hosting provider or browser may "
    "still have its own logs. For the strongest privacy, run the app on your own computer."
)

# Recommendations are local text data; images are optional local files.
CATALOGUE = [
    {
        "name": "Straight Kurti", "style": "Traditional", "occasion": "Daily wear",
        "fabric": "Cotton", "colour": "Pastel", "fit": "Regular",
        "description": "A versatile straight silhouette for everyday comfort.",
        "tip": "Pair with straight pants, leggings, or palazzos.",
        "image": "straight_kurti.jpg",
    },
    {
        "name": "A-Line Kurti", "style": "Traditional", "occasion": "College",
        "fabric": "Rayon", "colour": "Bright", "fit": "Relaxed",
        "description": "A gently flared shape for easy movement.",
        "tip": "Try slim trousers and simple earrings.",
        "image": "a_line_kurti.jpg",
    },
    {
        "name": "Indo-Western Tunic", "style": "Indo-western", "occasion": "Casual outing",
        "fabric": "Linen", "colour": "Neutral", "fit": "Relaxed",
        "description": "A contemporary tunic with clean, versatile styling.",
        "tip": "Style with jeans or tapered pants.",
        "image": "tunic.jpg",
    },
    {
        "name": "Statement Top", "style": "Western", "occasion": "Party",
        "fabric": "Satin", "colour": "Dark", "fit": "Fitted",
        "description": "A dressy top for an evening or special occasion.",
        "tip": "Combine with wide-leg trousers or a skirt.",
        "image": "statement_top.jpg",
    },
    {
        "name": "Classic Blouse", "style": "Traditional", "occasion": "Festive",
        "fabric": "Silk blend", "colour": "Bright", "fit": "Fitted",
        "description": "A classic blouse concept for festive styling.",
        "tip": "Coordinate the neckline and sleeve with your saree border.",
        "image": "blouse.jpg",
    },
    {
        "name": "Midi Dress", "style": "Western", "occasion": "Casual outing",
        "fabric": "Cotton", "colour": "Pastel", "fit": "Regular",
        "description": "A simple midi dress for casual or daytime wear.",
        "tip": "Add flats and a small crossbody bag.",
        "image": "midi_dress.jpg",
    },
    {
        "name": "Flared Skirt", "style": "Indo-western", "occasion": "Festive",
        "fabric": "Silk blend", "colour": "Bright", "fit": "Relaxed",
        "description": "A flared skirt concept with room for movement.",
        "tip": "Pair with a fitted blouse or crop top.",
        "image": "flared_skirt.jpg",
    },
    {
        "name": "Palazzo Pants", "style": "Indo-western", "occasion": "College",
        "fabric": "Rayon", "colour": "Neutral", "fit": "Relaxed",
        "description": "Wide-leg trousers suitable for casual outfits.",
        "tip": "Balance the volume with a fitted or tucked-in top.",
        "image": "palazzo.jpg",
    },
]


def show_local_image(filename):
    """Only display an image from this app's local images folder."""
    path = IMAGE_DIR / filename
    try:
        if path.is_file() and path.resolve().parent == IMAGE_DIR.resolve():
            st.image(str(path), use_container_width=True)
        else:
            st.info(
                f"Image not added yet: `{filename}`. "
                "Add your own licensed image to the local images folder."
            )
    except (OSError, ValueError):
        st.warning("This image could not be displayed.")


def valid_measurements(values):
    """Reject non-numeric, non-finite, and implausible inputs."""
    for label, value in values.items():
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            return f"{label} must be a valid number."
        if value <= 0 or value > 300:
            return f"{label} must be greater than 0 and no more than 300 cm."
    return None


def create_svg(m):
    """
    Experimental block-pattern illustration.
    This is not a validated garment drafting system.
    Dimensions are in mm so SVG has a physical scale.
    """
    scale = 10  # 1 cm = 10 mm
    seam = m["Seam allowance"]
    hem = m["Hem allowance"]
    ease = m["Ease"]
    length = m["Kurti length"]

    body_width_cm = max(
        (m["Bust"] + ease) / 4,
        (m["Waist"] + ease) / 4,
        (m["Hip"] + ease) / 4,
    )
    piece_w = (body_width_cm + seam) * scale
    piece_h = (length + hem + seam) * scale
    margin = 30 * scale
    gap = 15 * scale
    canvas_w = margin * 2 + piece_w * 2 + gap
    canvas_h = margin * 2 + piece_h

    def fmt(n):
        return f"{n:.1f}"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{fmt(canvas_w)}mm" height="{fmt(canvas_h)}mm" '
        f'viewBox="0 0 {fmt(canvas_w)} {fmt(canvas_h)}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}'
        '.label{font-size:40px}.small{font-size:26px}'
        '.outline{fill:none;stroke:#111;stroke-width:3}'
        '.guide{fill:none;stroke:#666;stroke-width:2;stroke-dasharray:10 8}'
        '</style>',
        '<text x="300" y="100" class="label">STRAIGHT KURTI — EXPERIMENTAL BLOCK</text>',
        '<text x="300" y="150" class="small">Units: cm • Print at 100% / Actual size</text>',
    ]

    for idx, label in enumerate(("BACK — cut on fold", "FRONT")):
        x = margin + idx * (piece_w + gap)
        y = margin
        # Simple block shape, not a production-ready fitted armhole/neckline.
        pts = [
            (x, y),
            (x + piece_w * 0.70, y),
            (x + piece_w, y + piece_h * 0.12),
            (x + piece_w, y + piece_h),
            (x, y + piece_h),
        ]
        point_str = " ".join(f"{fmt(a)},{fmt(b)}" for a, b in pts)
        parts.append(f'<polygon points="{point_str}" class="outline"/>')
        parts.append(
            f'<text x="{fmt(x + 15)}" y="{fmt(y + 55)}" class="small">'
            f'{html.escape(label)}</text>'
        )
        # Grainline
        gx = x + piece_w * 0.45
        parts.append(
            f'<line x1="{fmt(gx)}" y1="{fmt(y + 100)}" '
            f'x2="{fmt(gx)}" y2="{fmt(y + piece_h - 100)}" '
            f'stroke="#111" stroke-width="3"/>'
        )
        parts.append(
            f'<path d="M {fmt(gx-12)} {fmt(y+125)} '
            f'L {fmt(gx)} {fmt(y+100)} L {fmt(gx+12)} {fmt(y+125)}" '
            f'fill="none" stroke="#111" stroke-width="3"/>'
        )
        parts.append(
            f'<text x="{fmt(x + 15)}" y="{fmt(y + piece_h - 25)}" '
            f'class="small">Length: {length:.1f} cm</text>'
        )
        # Notches (illustrative only)
        ny = y + piece_h * 0.25
        parts.append(
            f'<path d="M {fmt(x+piece_w-18)} {fmt(ny-12)} '
            f'L {fmt(x+piece_w+8)} {fmt(ny)} '
            f'L {fmt(x+piece_w-18)} {fmt(ny+12)}" '
            f'fill="none" stroke="#111" stroke-width="3"/>'
        )
        # Seam allowance note
        parts.append(
            f'<text x="{fmt(x + 15)}" y="{fmt(y + 105)}" class="small">'
            f'SA: {seam:.1f} cm • Hem: {hem:.1f} cm</text>'
        )

    # 5 cm calibration square
    sq = 5 * scale
    sx, sy = margin, canvas_h - 20 * scale
    parts.append(
        f'<rect x="{fmt(sx)}" y="{fmt(sy)}" width="{fmt(sq)}" '
        f'height="{fmt(sq)}" class="outline"/>'
    )
    parts.append(
        f'<text x="{fmt(sx + sq + 20)}" y="{fmt(sy + sq/2)}" class="small">'
        'Calibration square must measure 5 × 5 cm</text>'
    )
    parts.append(
        '<text x="300" y="' + fmt(canvas_h - 50) +
        '" class="small">PROTOTYPE ONLY — verify with a qualified pattern maker before cutting fabric.</text>'
    )
    parts.append('</svg>')
    return "\n".join(parts).encode("utf-8"), canvas_w, canvas_h


def create_pdf(m, canvas_w_mm, canvas_h_mm):
    """Create a PDF with the same physical canvas dimensions as the SVG."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
    except ImportError as exc:
        raise RuntimeError("PDF export requires ReportLab. Install requirements.txt.") from exc

    buffer = BytesIO()
    c = canvas.Canvas(
        buffer,
        pagesize=(canvas_w_mm * mm, canvas_h_mm * mm),
        pageCompression=1,
    )
    w = canvas_w_mm * mm
    h = canvas_h_mm * mm
    scale = 10  # mm per cm

    c.setFont("Helvetica-Bold", 14)
    c.drawString(30 * scale * mm, h - 10 * scale * mm,
                 "STRAIGHT KURTI — EXPERIMENTAL BLOCK")
    c.setFont("Helvetica", 9)
    c.drawString(30 * scale * mm, h - 15 * scale * mm,
                 "Units: cm | Print at 100% / Actual size")

    seam = m["Seam allowance"]
    hem = m["Hem allowance"]
    length = m["Kurti length"]
    body_width_cm = max(
        (m["Bust"] + m["Ease"]) / 4,
        (m["Waist"] + m["Ease"]) / 4,
        (m["Hip"] + m["Ease"]) / 4,
    )
    piece_w = (body_width_cm + seam) * scale
    piece_h = (length + hem + seam) * scale
    margin = 30 * scale
    gap = 15 * scale

    for idx, label in enumerate(("BACK — cut on fold", "FRONT")):
        x_mm = margin + idx * (piece_w + gap)
        y_mm = canvas_h_mm - margin - piece_h
        coords = [
            (x_mm, y_mm + piece_h),
            (x_mm + piece_w * 0.70, y_mm + piece_h),
            (x_mm + piece_w, y_mm + piece_h * 0.88),
            (x_mm + piece_w, y_mm),
            (x_mm, y_mm),
        ]
        p = c.beginPath()
        p.moveTo(coords[0][0] * mm, coords[0][1] * mm)
        for px, py in coords[1:]:
            p.lineTo(px * mm, py * mm)
        p.close()
        c.setLineWidth(1)
        c.drawPath(p, stroke=1, fill=0)
        c.setFont("Helvetica", 8)
        c.drawString((x_mm + 2) * mm, (y_mm + piece_h - 6) * mm, label)
        gx = x_mm + piece_w * 0.45
        c.line(gx * mm, (y_mm + 10) * mm,
               gx * mm, (y_mm + piece_h - 10) * mm)
        c.drawCentredString(gx * mm, (y_mm + piece_h / 2) * mm, "GRAINLINE")
        c.drawString((x_mm + 2) * mm, (y_mm + 3) * mm,
                     f"Length {length:.1f} cm | SA {seam:.1f} cm | Hem {hem:.1f} cm")

    # 5 × 5 cm print calibration square
    sq_mm = 50
    sx_mm, sy_mm = margin, 20
    c.rect(sx_mm * mm, sy_mm * mm, sq_mm * mm, sq_mm * mm)
    c.setFont("Helvetica", 8)
    c.drawString((sx_mm + sq_mm + 5) * mm, (sy_mm + 25) * mm,
                 "Calibration square: 5 x 5 cm")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(30 * scale * mm, 8 * mm,
                 "PROTOTYPE ONLY — verify before cutting fabric.")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


tab_recommend, tab_pattern, tab_privacy = st.tabs([
    "Clothing Recommendations",
    "Straight Kurti Pattern",
    "Privacy & Setup",
])

with tab_recommend:
    st.subheader("Find outfit inspiration")
    c1, c2, c3 = st.columns(3)
    with c1:
        occasion = st.selectbox(
            "Occasion",
            ["Any", "Daily wear", "College", "Casual outing", "Party", "Festive"],
        )
    with c2:
        style = st.selectbox(
            "Style", ["Any", "Traditional", "Indo-western", "Western"]
        )
    with c3:
        fit = st.selectbox("Fit preference", ["Any", "Fitted", "Regular", "Relaxed"])

    results = []
    for item in CATALOGUE:
        if occasion != "Any" and item["occasion"] != occasion:
            continue
        if style != "Any" and item["style"] != style:
            continue
        if fit != "Any" and item["fit"] != fit:
            continue
        results.append(item)

    if not results:
        st.warning("No exact matches. Try changing one or more filters.")
    else:
        st.caption(f"{len(results)} outfit suggestion(s)")
        cols = st.columns(3)
        for i, item in enumerate(results):
            with cols[i % 3]:
                st.markdown(f"### {item['name']}")
                show_local_image(item["image"])
                st.write(item["description"])
                st.caption(
                    f"{item['style']} • {item['occasion']} • "
                    f"{item['fabric']} • {item['colour']} • {item['fit']} fit"
                )
                st.write(f"**Styling tip:** {item['tip']}")

    st.markdown("---")
    st.write("**Add your own image suggestions:** put image files in the local `images` folder.")
    st.code(
        "images/straight_kurti.jpg\n"
        "images/a_line_kurti.jpg\n"
        "images/tunic.jpg\n"
        "images/statement_top.jpg\n"
        "images/blouse.jpg\n"
        "images/midi_dress.jpg\n"
        "images/flared_skirt.jpg\n"
        "images/palazzo.jpg",
        language="text",
    )

with tab_pattern:
    st.subheader("Measurement-based Straight Kurti prototype")
    st.warning(
        "This is an experimental block, not a validated sewing pattern. "
        "It does not yet calculate a professionally drafted neckline, armhole, "
        "dart, or fitting corrections. Make and test a muslin/toile first."
    )

    with st.form("kurti_measurements"):
        col_a, col_b = st.columns(2)
        with col_a:
            bust = st.number_input("Bust circumference (cm)", 50.0, 180.0, 90.0, 0.5)
            waist = st.number_input("Waist circumference (cm)", 40.0, 170.0, 76.0, 0.5)
            hip = st.number_input("Hip circumference (cm)", 50.0, 190.0, 96.0, 0.5)
            shoulder = st.number_input("Shoulder width (cm)", 25.0, 60.0, 38.0, 0.5)
            armhole = st.number_input("Armhole depth (cm)", 12.0, 35.0, 21.0, 0.5)
        with col_b:
            length = st.number_input("Kurti length (cm)", 40.0, 150.0, 90.0, 0.5)
            neck_width = st.number_input("Neck width (cm)", 5.0, 20.0, 8.0, 0.5)
            front_neck = st.number_input("Front neck depth (cm)", 3.0, 35.0, 15.0, 0.5)
            back_neck = st.number_input("Back neck depth (cm)", 1.0, 20.0, 3.0, 0.5)
            ease = st.number_input("Total circumference ease (cm)", 0.0, 30.0, 8.0, 0.5)
        col_c, col_d = st.columns(2)
        with col_c:
            seam = st.number_input("Seam allowance (cm)", 0.0, 3.0, 1.0, 0.1)
        with col_d:
            hem = st.number_input("Hem allowance (cm)", 0.0, 10.0, 3.0, 0.5)

        submitted = st.form_submit_button("Generate prototype")

    if submitted:
        measurements = {
            "Bust": bust, "Waist": waist, "Hip": hip,
            "Shoulder": shoulder, "Armhole depth": armhole,
            "Kurti length": length, "Neck width": neck_width,
            "Front neck depth": front_neck, "Back neck depth": back_neck,
            "Ease": ease, "Seam allowance": seam, "Hem allowance": hem,
        }
        error = valid_measurements(measurements)

        if error:
            st.error(error)
        elif front_neck >= length or back_neck >= length:
            st.error("Neck depth must be smaller than the kurti length.")
        elif shoulder >= bust:
            st.error("Shoulder width looks implausible compared with bust circumference.")
        elif armhole >= length:
            st.error("Armhole depth must be smaller than kurti length.")
        else:
            try:
                svg_bytes, canvas_w, canvas_h = create_svg(measurements)
                pdf_bytes = create_pdf(measurements, canvas_w, canvas_h)

                st.success("Prototype files generated. This does not validate fit or drafting accuracy.")
                st.download_button(
                    "Download SVG pattern",
                    data=svg_bytes,
                    file_name="straight_kurti_prototype.svg",
                    mime="image/svg+xml",
                )
                st.download_button(
                    "Download PDF pattern",
                    data=pdf_bytes,
                    file_name="straight_kurti_prototype.pdf",
                    mime="application/pdf",
                )
                st.caption(
                    f"Physical page size: {canvas_w / 10:.1f} × {canvas_h / 10:.1f} cm. "
                    "Print PDF at 100% / Actual size; do not select Fit to page."
                )
                st.code(
                    "Check the printed 5 × 5 cm calibration square with a ruler. "
                    "If it is not exactly 5 × 5 cm, adjust printer scaling before use.",
                    language="text",
                )
                # SVG generated by this app is displayed inline without external resources.
                st.markdown(
                    '<div class="pattern-preview">' +
                    svg_bytes.decode("utf-8") + "</div>",
                    unsafe_allow_html=True,
                )
            except Exception as exc:
                # Avoid exposing system paths, environment variables, or tracebacks.
                st.error("Pattern export failed. Check the installed requirements and try again.")
                st.caption(f"Error type: {type(exc).__name__}")

with tab_privacy:
    st.subheader("Privacy and local setup")
    st.markdown("""
- No external AI API or third-party image service is used.
- Measurements are processed when you submit the form and are not intentionally saved by this code.
- Clothing images must be supplied locally by you; use images you own or are licensed to use.
- Do not deploy this app publicly with real customer measurements unless you add appropriate access controls and a privacy policy.
- Do not put passwords, API keys, or personal data in source code.
- This app is a prototype. The generated pattern has not been professionally validated.
""")
    st.write("Expected project structure:")
    st.code(
        "your_project/\n"
        "├── app.py\n"
        "├── requirements.txt\n"
        "└── images/\n"
        "    ├── straight_kurti.jpg\n"
        "    └── ... (optional local images)",
        language="text",
    )

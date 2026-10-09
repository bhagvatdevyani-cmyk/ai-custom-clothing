import streamlit as st
import streamlit.components.v1 as components
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from xml.sax.saxutils import escape
import io
import math

st.set_page_config(
    page_title="AI Custom Clothing System",
    page_icon="👗",
    layout="wide"
)

GARMENTS = {
    "Straight Kurti": "kurti",
    "A-Line Kurti": "dress",
    "Everyday Tunic": "tunic",
    "Long Tunic": "tunic",
    "Sleeveless Top": "top",
    "Basic Blouse": "blouse",
    "Shift Dress": "dress",
    "Maxi Dress": "dress",
    "Gathered Skirt": "skirt",
    "Palazzo Trousers": "trousers",
}

st.title("👗 AI-Assisted Custom Clothing System")
st.write(
    "Explore clothing recommendations using your measurements, "
    "style preferences, fabric choice and occasion."
)
st.info(
    "Project prototype: the illustrations and pattern diagrams are "
    "basic visual previews, not production-ready sewing patterns."
)

st.header("1. Your preferences")

col1, col2 = st.columns(2)

with col1:
    age_group = st.selectbox(
        "Age group",
        ["Teen", "Young adult", "Adult", "Mature adult", "Senior adult"]
    )
    garment = st.selectbox("Choose a garment", list(GARMENTS.keys()))
    fit = st.selectbox(
        "Preferred fit",
        ["Comfortable", "Regular", "Fitted", "Loose"]
    )
    fabric = st.selectbox(
        "Preferred fabric",
        ["Cotton", "Linen", "Rayon/Viscose", "Denim", "Silk", "Polyester", "Other"]
    )

with col2:
    occasion = st.selectbox(
        "Occasion",
        ["Daily wear", "College", "Office", "Party", "Festive", "Formal"]
    )
    colour = st.selectbox(
        "Preferred colour",
        ["Black", "White", "Pink", "Blue", "Green", "Red", "Purple", "Beige", "Other"]
    )
    budget = st.selectbox(
        "Budget",
        ["Under Rs. 500", "Rs. 500–1000", "Rs. 1000–2000", "Above Rs. 2000"]
    )
    sleeve_style = st.selectbox(
        "Sleeve preference",
        ["Sleeveless", "Short sleeve", "Three-quarter sleeve", "Full sleeve"]
    )

st.header("2. Enter body measurements")
st.caption(
    "Enter measurements in centimetres. Use a measuring tape and "
    "measure over light clothing. Ask someone to help for better accuracy."
)

m1, m2, m3 = st.columns(3)

with m1:
    bust = st.number_input("Bust (cm)", min_value=40.0, max_value=180.0, value=90.0, step=1.0)
    waist = st.number_input("Waist (cm)", min_value=35.0, max_value=160.0, value=75.0, step=1.0)
    hip = st.number_input("Hip (cm)", min_value=40.0, max_value=180.0, value=96.0, step=1.0)

with m2:
    shoulder = st.number_input("Shoulder width (cm)", min_value=20.0, max_value=65.0, value=38.0, step=1.0)
    armhole = st.number_input("Armhole circumference (cm)", min_value=20.0, max_value=80.0, value=42.0, step=1.0)
    garment_length = st.number_input("Garment length (cm)", min_value=20.0, max_value=180.0, value=90.0, step=1.0)

with m3:
    sleeve_length = st.number_input("Sleeve length (cm)", min_value=0.0, max_value=90.0, value=20.0, step=1.0)
    ease = st.number_input("Ease allowance (cm)", min_value=0.0, max_value=15.0, value=4.0, step=0.5)
    seam = st.number_input("Seam allowance (cm)", min_value=0.0, max_value=3.0, value=1.0, step=0.5)

if st.button("✨ Generate my clothing recommendation", type="primary"):
    st.session_state["generated"] = True

if st.session_state.get("generated", False):
    st.header("3. Your clothing recommendation")

    if garment == "Palazzo Trousers":
        recommended_fit = "A comfortable fit with room for movement."
    elif fit == "Fitted":
        recommended_fit = "A closer silhouette; ensure movement and comfort."
    elif fit == "Loose":
        recommended_fit = "A relaxed silhouette with extra room."
    else:
        recommended_fit = "A balanced silhouette for everyday comfort."

    recommendations = {
        "Cotton": "Breathable and suitable for everyday clothing.",
        "Linen": "Lightweight and airy, with a naturally textured appearance.",
        "Rayon/Viscose": "Soft drape and fluid movement.",
        "Denim": "Structured appearance; suitable for casual styles.",
        "Silk": "Smooth appearance, often suited to occasion wear.",
        "Polyester": "Often wrinkle-resistant and available in many finishes.",
        "Other": "Choose a fabric based on drape, comfort and care requirements."
    }

    st.success(f"Suggested style: {colour} {garment} for {occasion.lower()}.")
    st.write(f"**Age group:** {age_group}")
    st.write(f"**Fit:** {recommended_fit}")
    st.write(f"**Fabric suggestion:** {recommendations[fabric]}")
    st.write(f"**Sleeve preference:** {sleeve_style}")
    st.write(f"**Budget:** {budget}")

    if age_group == "Teen":
        st.write("Style idea: youthful details, comfortable shapes and playful colours.")
    elif age_group == "Young adult":
        st.write("Style idea: versatile designs that work for college, outings and occasions.")
    elif age_group == "Adult":
        st.write("Style idea: practical silhouettes that can be dressed up or down.")
    elif age_group == "Mature adult":
        st.write("Style idea: refined details, comfortable movement and a flattering silhouette.")
    else:
        st.write("Style idea: ease of dressing, comfortable movement and practical details.")

    st.caption(
        "These suggestions use simple rules in this prototype. They are not "
        "generated by a trained AI model."
    )

    st.header("4. Garment illustration")

    def garment_svg(kind, colour_name):
        colour_map = {
            "Black": "#222222", "White": "#F5F5F5", "Pink": "#E9A3B8",
            "Blue": "#6799D0", "Green": "#6C9B72", "Red": "#D74A55",
            "Purple": "#9877C4", "Beige": "#D8C2A0", "Other": "#9AA0A6"
        }
        fill = colour_map.get(colour_name, "#6799D0")
        stroke = "#333333"

        if kind in ["kurti", "dress", "tunic", "blouse", "top"]:
            if kind == "top" or kind == "blouse":
                path = "M100 70 L135 45 L160 65 L180 45 L215 70 L200 115 L185 105 L185 170 L130 170 L130 105 L115 115 Z"
            elif kind == "tunic":
                path = "M100 70 L135 45 L160 65 L180 45 L215 70 L200 115 L185 105 L205 270 L110 270 L130 105 L115 115 Z"
            else:
                path = "M100 70 L135 45 L160 65 L180 45 L215 70 L200 115 L185 105 L220 320 L95 320 L130 105 L115 115 Z"

            return f'''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="360" viewBox="0 0 320 360">
            <rect width="320" height="360" rx="18" fill="#FAF7F2"/>
            <text x="160" y="28" font-size="14" text-anchor="middle" fill="#444">{escape(kind.title())} concept</text>
            <path d="{path}" transform="translate(0,8)" fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>
            <path d="M160 66 L160 300" stroke="{stroke}" stroke-width="1" stroke-dasharray="4 4" opacity=".45"/>
            <circle cx="160" cy="85" r="3" fill="{stroke}"/>
            <text x="160" y="345" font-size="11" text-anchor="middle" fill="#555">Illustrative concept only</text>
            </svg>'''

        if kind == "skirt":
            path = "M105 65 L215 65 L245 290 L75 290 Z"
        else:
            path = "M105 65 L140 65 L145 155 L135 310 L100 310 L110 160 L105 160 L95 310 L60 310 L65 155 Z"

        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="360" viewBox="0 0 320 360">
        <rect width="320" height="360" rx="18" fill="#FAF7F2"/>
        <text x="160" y="28" font-size="14" text-anchor="middle" fill="#444">{escape(kind.title())} concept</text>
        <path d="{path}" transform="translate(30,8)" fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>
        <text x="160" y="345" font-size="11" text-anchor="middle" fill="#555">Illustrative concept only</text>
        </svg>'''

    illustration = garment_svg(GARMENTS[garment], colour)
    components.html(illustration, height=380)

    st.download_button(
        "Download garment illustration (SVG)",
        data=illustration.encode("utf-8"),
        file_name="garment_illustration.svg",
        mime="image/svg+xml"
    )

    st.header("5. Basic pattern preview")

    # Simplified rectangular pattern blocks, not production-ready patterns.
    body_measurement = bust if garment not in ["Palazzo Trousers", "Gathered Skirt"] else hip
    width_cm = max(10.0, (body_measurement + ease) / 4.0)
    length_cm = garment_length
    scale = 3.0
    width_px = width_cm * scale
    length_px = length_cm * scale
    canvas_width = max(300, int(width_px + 100))
    canvas_height = max(300, int(length_px + 120))

    pattern = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" height="{canvas_height}" viewBox="0 0 {canvas_width} {canvas_height}">
    <rect width="100%" height="100%" fill="#FAF7F2"/>
    <text x="{canvas_width/2}" y="28" text-anchor="middle" font-size="15" fill="#333">{escape(garment)} — basic block preview</text>
    <rect x="50" y="55" width="{width_px}" height="{length_px}" fill="#DCE8F4" stroke="#365D83" stroke-width="2"/>
    <line x1="{50 + width_px/2}" y1="65" x2="{50 + width_px/2}" y2="{55 + length_px - 10}" stroke="#365D83" stroke-dasharray="5 5"/>
    <path d="M{50 + width_px/2 - 5} 80 L{50 + width_px/2} 65 L{50 + width_px/2 + 5} 80" fill="none" stroke="#365D83" stroke-width="2"/>
    <text x="{50 + width_px/2}" y="{55 + length_px + 22}" text-anchor="middle" font-size="12" fill="#333">Width: {width_cm:.1f} cm (approx.)</text>
    <text x="{50 + width_px + 12}" y="{55 + length_px/2}" font-size="12" fill="#333" transform="rotate(90 {50 + width_px + 12} {55 + length_px/2})">Length: {length_cm:.1f} cm</text>
    <text x="{canvas_width/2}" y="{canvas_height - 15}" text-anchor="middle" font-size="11" fill="#8B3030">Schematic only — not for fabric cutting</text>
    </svg>'''

    components.html(pattern, height=min(canvas_height + 20, 750), scrolling=True)

    st.download_button(
        "Download pattern preview (SVG)",
        data=pattern.encode("utf-8"),
        file_name="basic_pattern_preview.svg",
        mime="image/svg+xml"
    )

    st.warning(
        "Important: this pattern is only a simple measurement-based block. "
        "It does not yet include validated armholes, necklines, darts, sleeves, "
        "crotch curves, closures or correctly offset seam allowances. "
        "Do not use it to cut fabric."
    )

    st.header("6. Download your measurement report")

    report_data = {
        "Age group": age_group,
        "Garment": garment,
        "Fit": fit,
        "Fabric": fabric,
        "Occasion": occasion,
        "Colour": colour,
        "Sleeve preference": sleeve_style,
        "Budget": budget,
        "Bust": f"{bust} cm",
        "Waist": f"{waist} cm",
        "Hip": f"{hip} cm",
        "Shoulder width": f"{shoulder} cm",
        "Armhole circumference": f"{armhole} cm",
        "Garment length": f"{garment_length} cm",
        "Sleeve length": f"{sleeve_length} cm",
        "Ease allowance": f"{ease} cm",
        "Intended seam allowance": f"{seam} cm",
    }

    pdf_buffer = io.BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
    page_width, page_height = A4

    pdf.setTitle("Custom Clothing Measurement Report")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, page_height - 50, "Custom Clothing Measurement Report")

    y = page_height - 85
    pdf.setFont("Helvetica", 10)

    for key, value in report_data.items():
        line = f"{key}: {str(value)[:100]}".replace("₹", "Rs. ")
        pdf.drawString(40, y, line)
        y -= 19

        if y < 65:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = page_height - 50

    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(40, 40, "Prototype report. Verify all patterns with a qualified pattern maker.")
    pdf.save()
    pdf_buffer.seek(0)

    st.download_button(
        "Download PDF report",
        data=pdf_buffer.getvalue(),
        file_name="custom_clothing_report.pdf",
        mime="application/pdf"
    )

st.divider()
st.caption(
    "Future development: accurate garment-specific drafting, validated pattern "
    "shapes, image generation and a trained recommendation model."
)

"""
Lochkamera-Simulation – Streamlit Web-Version
Interaktive Lernsoftware für die 7. Klasse (Browser-basiert)

Starten mit:
    streamlit run lochkamera_web.py

Dann im Handy-Browser die Network URL öffnen (z.B. http://192.168.x.x:8501)
"""

import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

# ── Seitenkonfiguration ──────────────────────────────────────────
st.set_page_config(
    page_title="🔬 Lochkamera-Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS für schönere Optik ────────────────────────────────
st.markdown("""
<style>
    .main {
        background-color: #F5F5FA;
    }
    h1 {
        color: #4A90D9;
        text-align: center;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        width: 100%;
        background-color: #4A90D9;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #3670B0;
    }
    div[data-testid="metric-container"] {
        background-color: white;
        border: 2px solid #E0E0E0;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #4A90D9;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar: Steuerung ───────────────────────────────────────────
st.sidebar.title("🔬 Lochkamera")
st.sidebar.caption("Interaktive Simulation für die 7. Klasse")
st.sidebar.markdown("---")

st.sidebar.markdown("### ⚙️ Parameter einstellen")

aperture = st.sidebar.slider(
    "⊙ Lochgröße (Apertur)",
    min_value=0.5,
    max_value=10.0,
    value=3.0,
    step=0.5,
    help="Größe der Öffnung in Millimetern. Kleineres Loch = schärfer aber dunkler."
)

cam_length = st.sidebar.slider(
    "↔ Kameralänge",
    min_value=80,
    max_value=300,
    value=180,
    step=5,
    help="Abstand zwischen Loch und Schirm in Millimetern. Länger = größeres Bild."
)

obj_distance = st.sidebar.slider(
    "🕯 Abstand zum Objekt",
    min_value=100,
    max_value=600,
    value=300,
    step=10,
    help="Abstand zwischen Kerze und Loch in Millimetern. Näher = größeres Bild."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📎 Lochblenden-Wechsel")
st.sidebar.caption("Schnell eine vorgefertigte Blende aufclipsen:")

col1, col2, col3, col4 = st.sidebar.columns(4)
if col1.button("1 mm"):
    st.session_state.aperture = 1.0
    aperture = 1.0
if col2.button("3 mm"):
    st.session_state.aperture = 3.0
    aperture = 3.0
if col3.button("5 mm"):
    st.session_state.aperture = 5.0
    aperture = 5.0
if col4.button("8 mm"):
    st.session_state.aperture = 8.0
    aperture = 8.0

# ── Hauptbereich: Titel ──────────────────────────────────────────
st.title("🔬 Lochkamera – Camera Obscura")
st.markdown("**Wie entsteht ein auf dem Kopf stehendes Bild?**")

# ── Berechnungen ─────────────────────────────────────────────────
magnification = cam_length / obj_distance
sharpness = max(0, min(100, 100 - aperture * 10))
brightness = min(100, aperture * 12 + 20)
blur_factor = aperture * 0.35

# ── Zeichnung mit Pillow ─────────────────────────────────────────
W, H = 1200, 550
img = Image.new("RGB", (W, H), "#F5F5FA")
draw = ImageDraw.Draw(img)

# Skalierung & Positionen
scene_width_mm = obj_distance + cam_length + 80
scale = (W - 140) / scene_width_mm
cy = H // 2

obj_x = 70
hole_x = int(obj_x + obj_distance * scale)
screen_x = int(hole_x + cam_length * scale)

obj_h = min(int(H * 0.35), max(50, int(65 * scale)))
cam_h = max(90, int(H * 0.30))
half_cam = cam_h // 2
half_ap = max(2, int(aperture * scale * 1.8 / 2))

candle_top = cy - obj_h // 2
candle_bot = cy + obj_h // 2

# ── Kerze zeichnen ───────────────────────────────────────────────
cw = 16
draw.rectangle([obj_x - cw // 2, cy, obj_x + cw // 2, candle_bot],
               fill="#F5F0E0", outline="#CCC", width=1)
# Docht
draw.line([obj_x, cy, obj_x, candle_top + 14], fill="#555", width=3)
# Flamme
draw.ellipse([obj_x - 11, candle_top - 2, obj_x + 11, candle_top + 24],
             fill="#FFB300", outline="#FF8F00", width=1)
draw.ellipse([obj_x - 5, candle_top + 4, obj_x + 5, candle_top + 18],
             fill="#FFF3E0")
# Beschriftung
try:
    fnt = ImageFont.truetype("arial.ttf", 14)
    fnt_sm = ImageFont.truetype("arial.ttf", 11)
    fnt_title = ImageFont.truetype("arial.ttf", 16)
except (OSError, IOError):
    fnt = ImageFont.load_default()
    fnt_sm = fnt
    fnt_title = fnt

draw.text((obj_x - 25, candle_bot + 12), "Objekt\n(Kerze)", fill="#666",
          font=fnt_sm, align="center")

# ── Kamera (Chipsdose) ───────────────────────────────────────────
# Äußere Dose (rot)
draw.rectangle([hole_x - 20, cy - half_cam, screen_x + 12, cy + half_cam],
               fill="#C0392B", outline="#922", width=2)
# Innere Tonpapierröhre (schwarz)
inner_margin = 10
draw.rectangle([hole_x - 16, cy - half_cam + inner_margin,
                screen_x + 8, cy + half_cam - inner_margin],
               fill="#1C1C1C", outline="#333", width=1)
# Blenden-Platte
draw.rectangle([hole_x - 5, cy - half_cam, hole_x + 5, cy + half_cam],
               fill="#C0392B", outline="#922", width=1)
# Loch
draw.rectangle([hole_x - 3, cy - half_ap, hole_x + 3, cy + half_ap],
               fill="#222")
# Apertur-Markierung
draw.ellipse([hole_x - half_ap - 3, cy - half_ap - 3,
              hole_x + half_ap + 3, cy + half_ap + 3],
             outline="#3DBB8F", width=2)

# Butterbrotpapier-Schirm
screen_inner_top = cy - half_cam + inner_margin
screen_inner_bot = cy + half_cam - inner_margin
draw.rectangle([screen_x - 2, screen_inner_top,
                screen_x + 6, screen_inner_bot],
               fill="#F0E6D2", outline="#C8B89A", width=2)

# Beschriftungen Kamera
draw.text((hole_x - 8, cy + half_cam + 15), "Loch", fill="#666", font=fnt_sm)
draw.text(((hole_x + screen_x) // 2 - 40, cy - half_cam - 20),
          "Chipsdose (Kamera)", fill="#C0392B", font=fnt_title)
draw.text((screen_x - 25, cy + half_cam + 15), "Schirm\n(Butterbrot-\npapier)",
          fill="#888", font=fnt_sm, align="center")

# ── Lichtstrahlen zeichnen ───────────────────────────────────────
obj_points = [
    candle_top + 8,
    cy - obj_h // 4,
    cy,
    cy + obj_h // 4,
    candle_bot - 8
]
ray_colors = [
    (181, 126, 220),
    (240, 199, 94),
    (181, 126, 220),
    (240, 199, 94),
    (181, 126, 220)
]

img_h = min(obj_h * magnification, (half_cam - inner_margin) * 1.85)

for idx, obj_y in enumerate(obj_points):
    n_rays = max(2, int(aperture * 1.5))
    ray_color = ray_colors[idx % len(ray_colors)]

    for r in range(n_rays):
        if n_rays == 1:
            h_off = 0
        else:
            h_off = -half_ap + 2 * half_ap * r / (n_rays - 1)

        hole_y = cy + h_off
        dx = hole_x - obj_x
        if dx == 0:
            continue
        slope = (hole_y - obj_y) / dx
        img_y = int(hole_y + slope * (screen_x - hole_x))

        # Strahl eingehend
        draw.line([obj_x, obj_y, hole_x, hole_y], fill=ray_color, width=1)
        # Strahl ausgehend
        draw.line([hole_x, hole_y, screen_x, img_y], fill=ray_color, width=1)

# ── Projiziertes Bild auf Schirm ─────────────────────────────────
img_top = int(cy - img_h / 2)
img_bot = int(cy + img_h / 2)
icw = max(4, int(8 * magnification * 0.65))
flame_h = max(5, int(16 * magnification * 0.65))

# Invertierte Kerze (Flamme unten, Körper oben)
# Kerzenkörper
draw.rectangle([screen_x - icw, img_top, screen_x + icw + 2,
                img_bot - flame_h],
               fill="#F5F0E0", outline="#CCC", width=1)
# Flamme (unten, weil invertiert)
draw.ellipse([screen_x - icw - 3, img_bot - flame_h - 2,
              screen_x + icw + 5, img_bot + 2],
             fill="#FFB300", outline="#FF8F00", width=1)
# Innere Flamme
if flame_h > 8:
    draw.ellipse([screen_x - icw // 2, img_bot - flame_h // 2,
                  screen_x + icw // 2 + 2, img_bot],
                 fill="#FFF3E0")

# Unschärfe anwenden
if blur_factor > 0.5:
    box = (max(0, screen_x - icw - 8), max(0, img_top - 8),
           min(W, screen_x + icw + 12), min(H, img_bot + 8))
    try:
        region = img.crop(box).filter(ImageFilter.GaussianBlur(blur_factor))
        img.paste(region, box)
    except:
        pass

# ── Abstandslinien ───────────────────────────────────────────────
line_y = cy + half_cam + 45
# Objekt → Loch
draw.line([obj_x, line_y, hole_x, line_y], fill="#999", width=2)
draw.polygon([obj_x, line_y - 4, obj_x + 6, line_y, obj_x, line_y + 4],
             fill="#999")
draw.polygon([hole_x, line_y - 4, hole_x - 6, line_y, hole_x, line_y + 4],
             fill="#999")
draw.text(((obj_x + hole_x) // 2 - 30, line_y + 8),
          f"{obj_distance} mm", fill="#999", font=fnt_sm)

# Loch → Schirm
draw.line([hole_x, line_y, screen_x, line_y], fill="#999", width=2)
draw.polygon([hole_x, line_y - 4, hole_x + 6, line_y, hole_x, line_y + 4],
             fill="#999")
draw.polygon([screen_x, line_y - 4, screen_x - 6, line_y, screen_x, line_y + 4],
             fill="#999")
draw.text(((hole_x + screen_x) // 2 - 30, line_y + 8),
          f"{cam_length} mm", fill="#999", font=fnt_sm)

# ── Bild anzeigen ────────────────────────────────────────────────
st.image(img, use_container_width=True)

# ── Kennwerte in Metriken ────────────────────────────────────────
st.markdown("### 📊 Bild-Eigenschaften")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="🔍 Vergrößerung",
        value=f"{magnification:.2f}×",
        help="Verhältnis: Bildgröße / Objektgröße"
    )

with col2:
    delta_sharp = "Optimal" if 60 <= sharpness <= 90 else (
        "Zu unscharf" if sharpness < 60 else "Etwas dunkel")
    st.metric(
        label="🎯 Schärfe",
        value=f"{sharpness:.0f} %",
        delta=delta_sharp,
        help="Kleineres Loch = schärfer"
    )

with col3:
    delta_bright = "Gut" if brightness >= 40 else "Zu dunkel"
    st.metric(
        label="💡 Helligkeit",
        value=f"{brightness:.0f} %",
        delta=delta_bright,
        help="Größeres Loch = heller"
    )

# ── Fortschrittsbalken ───────────────────────────────────────────
st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Schärfe:**")
    st.progress(int(sharpness) / 100)
with col_b:
    st.markdown("**Helligkeit:**")
    st.progress(int(brightness) / 100)

# ── Info-Bereich expandierbar ───────────────────────────────────
st.markdown("---")
with st.expander("❓ **Wie funktioniert die Lochkamera?**", expanded=False):
    st.markdown("""
    ### 📖 Die Physik dahinter

    **Lichtstrahlen reisen immer geradeaus.**

    Jeder Punkt des Objekts (hier: die Kerze) sendet Licht in alle Richtungen aus.
    Das kleine **Loch** lässt nur einen schmalen Lichtstrahl von jedem Punkt durch.

    #### 🔄 Warum steht das Bild auf dem Kopf?

    Die Strahlen von der **Flamme (oben)** kreuzen sich im Loch mit den Strahlen
    vom **Kerzenkörper (unten)**. Nach der Kreuzung landet der obere Strahl unten
    auf dem Schirm – das Bild ist **invertiert** (auf dem Kopf und seitenverkehrt)!

    ---

    #### 🔬 Experimentiere mit den Parametern:

    | Parameter | Auswirkung |
    |-----------|-----------|
    | **Kleineres Loch** (1–2 mm) | ✅ Bild wird **schärfer**<br>❌ Bild wird **dunkler** (weniger Licht) |
    | **Größeres Loch** (8–10 mm) | ✅ Bild wird **heller**<br>❌ Bild wird **unschärfer** (Lichtstrahlen überlappen) |
    | **Längere Kamera** | ✅ Bild wird **größer** (wie Zoomen)<br>❌ Bild wird etwas unschärfer |
    | **Objekt näher** | ✅ Bild wird **größer**<br>❌ Vergrößerung steigt |

    ---

    #### 🎓 Das nennt man **Strahlensatz**:

    ```
    Bildgröße / Objektgröße = Kameralänge / Objektabstand
    ```

    Deshalb wird das Bild größer, wenn du die Kamera länger machst oder das Objekt
    näher an die Kamera bewegst!
    """)

# ── Strahlensatz-Diagramm ────────────────────────────────────────
with st.expander("📐 **Strahlensatz-Diagramm anzeigen**", expanded=False):
    st.markdown("### Wie kreuzen sich die Lichtstrahlen?")

    diag_w, diag_h = 700, 300
    diag = Image.new("RGB", (diag_w, diag_h), "white")
    d_draw = ImageDraw.Draw(diag)

    d_cx, d_cy = 350, 150
    obj_line_x = 100
    hole_line_x = d_cx
    screen_line_x = 600

    # Objekt (vertikale Linie)
    d_draw.line([obj_line_x, 60, obj_line_x, 240], fill="#E74C3C", width=4)
    d_draw.text((obj_line_x - 30, 50), "A", fill="#E74C3C", font=fnt_title)
    d_draw.text((obj_line_x - 30, 240), "B", fill="#E74C3C", font=fnt_title)
    d_draw.text((obj_line_x - 20, 250), "Objekt", fill="#666", font=fnt_sm)

    # Loch
    d_draw.ellipse([hole_line_x - 8, d_cy - 8, hole_line_x + 8, d_cy + 8],
                   fill="#222")
    d_draw.text((hole_line_x - 15, d_cy + 20), "Loch", fill="#666", font=fnt_sm)

    # Schirm
    d_draw.line([screen_line_x, 60, screen_line_x, 240], fill="#888", width=3)
    d_draw.text((screen_line_x - 20, 250), "Schirm", fill="#888", font=fnt_sm)

    # Strahlen: A (oben) → Loch → B' (unten)
    d_draw.line([obj_line_x, 60, hole_line_x, d_cy], fill="#B57EDC", width=3)
    d_draw.line([hole_line_x, d_cy, screen_line_x, 240], fill="#B57EDC", width=3)
    d_draw.text((screen_line_x + 10, 240), "A'", fill="#B57EDC", font=fnt_title)

    # Strahlen: B (unten) → Loch → A' (oben)
    d_draw.line([obj_line_x, 240, hole_line_x, d_cy], fill="#F0C75E", width=3)
    d_draw.line([hole_line_x, d_cy, screen_line_x, 60], fill="#F0C75E", width=3)
    d_draw.text((screen_line_x + 10, 50), "B'", fill="#F0C75E", font=fnt_title)

    # Kreuzungspunkt markieren
    d_draw.ellipse([hole_line_x - 12, d_cy - 12, hole_line_x + 12, d_cy + 12],
                   outline="#3DBB8F", width=3)

    st.image(diag, caption="Strahlenkreuzung im Loch → Bild steht auf dem Kopf")

# ── Fußzeile ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 12px;">
    🔬 Lochkamera-Simulation · Entwickelt für die 7. Klasse ·
    Physik macht Spaß! 🎓
</div>
""", unsafe_allow_html=True)

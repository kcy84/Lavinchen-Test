"""
Lochkamera-Simulation – Streamlit Web-Version (Mobile-optimiert)
Starten: py -m streamlit run lochkamera_web.py
Dann im Handy-Browser die Network URL öffnen (z.B. http://192.168.x.x:8501)
"""

import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

# ── Seitenkonfiguration ──────────────────────────────────────────
st.set_page_config(
    page_title="🔬 Lochkamera",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Responsives CSS (Mobile-First) ─────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #F0F2F6; }
    h1 { color: #2C3E50; font-size: clamp(18px, 5vw, 30px) !important; }
    h3 { color: #4A90D9; font-size: clamp(14px, 4vw, 20px) !important; }
    .stSlider label {
        font-size: clamp(13px, 3.5vw, 16px) !important;
        font-weight: 600 !important;
        color: #2C3E50 !important;
    }
    .stButton > button {
        border-radius: 10px !important;
        font-size: clamp(12px, 3vw, 15px) !important;
        font-weight: 700 !important;
        background: #4A90D9 !important;
        color: white !important;
        border: none !important;
        padding: 8px 4px !important;
        width: 100% !important;
    }
    .stButton > button:hover { background: #2C70B0 !important; }
    div[data-testid="metric-container"] {
        background: white;
        border-radius: 12px;
        border: 1px solid #DDE3EC;
        padding: 10px 8px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.07);
        text-align: center;
    }
    [data-testid="stMetricValue"] {
        font-size: clamp(18px, 5vw, 26px) !important;
        color: #4A90D9 !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: clamp(10px, 2.5vw, 13px) !important;
    }
    .block-container {
        padding-left: 12px !important;
        padding-right: 12px !important;
        padding-top: 16px !important;
        max-width: 900px !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Titel ────────────────────────────────────────────────────────
st.markdown("# 🔬 Lochkamera – Camera Obscura")
st.caption("Interaktive Simulation für die 7. Klasse · Physik")
st.divider()

# ── Blenden-Presets (oben, gut auf Handy erreichbar) ─────────────
st.markdown("**📎 Lochblende aufclipsen:**")
if "aperture" not in st.session_state:
    st.session_state.aperture = 3.0

b1, b2, b3, b4 = st.columns(4)
if b1.button("⊙ 1 mm"):
    st.session_state.aperture = 1.0
if b2.button("⊙ 3 mm"):
    st.session_state.aperture = 3.0
if b3.button("⊙ 5 mm"):
    st.session_state.aperture = 5.0
if b4.button("⊙ 8 mm"):
    st.session_state.aperture = 8.0
st.divider()

# ── Schieberegler (gestapelt, mobile-freundlich) ──────────────────
st.markdown("### ⚙️ Parameter einstellen")

aperture = st.slider(
    "⊙  Lochgröße (Apertur) in mm",
    min_value=0.5, max_value=10.0,
    value=float(st.session_state.aperture),
    step=0.5,
    help="Kleineres Loch = schärfer aber dunkler"
)
st.session_state.aperture = aperture

cam_length = st.slider(
    "↔  Kameralänge in mm",
    min_value=80, max_value=300, value=180, step=5,
    help="Länger = größeres Bild auf dem Schirm"
)

obj_distance = st.slider(
    "🕯  Abstand zum Objekt in mm",
    min_value=100, max_value=600, value=300, step=10,
    help="Näher = größeres Bild auf dem Schirm"
)
st.divider()

# ── Berechnungen ─────────────────────────────────────────────────
magnification = cam_length / obj_distance
sharpness = max(0, min(100, 100 - aperture * 10))
brightness = min(100, aperture * 12 + 20)
blur_factor = aperture * 0.35

# ── Zeichnung mit Pillow ─────────────────────────────────────────
W, H = 900, 420
img = Image.new("RGB", (W, H), "#F0F2F6")
draw = ImageDraw.Draw(img)

# Skalierung & Positionen
scene_width_mm = obj_distance + cam_length + 60
scale = (W - 100) / scene_width_mm
cy = H // 2

obj_x = 45
hole_x = int(obj_x + obj_distance * scale)
screen_x = int(hole_x + cam_length * scale)

obj_h = min(int(H * 0.38), max(45, int(60 * scale)))
cam_h = max(80, int(H * 0.32))
half_cam = cam_h // 2
half_ap = max(2, int(aperture * scale * 1.8 / 2))

candle_top = cy - obj_h // 2
candle_bot = cy + obj_h // 2

# Fonts
try:
    fnt_title = ImageFont.truetype("arial.ttf", 15)
    fnt       = ImageFont.truetype("arial.ttf", 13)
    fnt_sm    = ImageFont.truetype("arial.ttf", 11)
except (OSError, IOError):
    fnt_title = ImageFont.load_default()
    fnt       = fnt_title
    fnt_sm    = fnt_title

# ── Kerze ─────────────────────────────────────────────────────────
cw = 14
draw.rectangle([obj_x - cw//2, cy, obj_x + cw//2, candle_bot],
               fill="#F5F0E0", outline="#CCBBAA", width=1)
draw.line([obj_x, cy, obj_x, candle_top + 12], fill="#555", width=2)
draw.ellipse([obj_x - 10, candle_top - 2, obj_x + 10, candle_top + 22],
             fill="#FFB300", outline="#FF8F00")
draw.ellipse([obj_x - 4, candle_top + 4, obj_x + 4, candle_top + 16],
             fill="#FFF3E0")
draw.text((obj_x - 20, candle_bot + 10), "Objekt\n(Kerze)",
          fill="#555", font=fnt_sm)

# ── Kamera (Chipsdose) ────────────────────────────────────────────
inner_margin = 9
# Hintergrund
draw.rectangle([hole_x - 22, cy - half_cam - 2,
                screen_x + 14, cy + half_cam + 2],
               fill="#E8E8E8", outline=None)
# Äußere Dose (rot, abgerundet)
draw.rounded_rectangle([hole_x - 20, cy - half_cam,
                         screen_x + 12, cy + half_cam],
                        radius=6, fill="#C0392B", outline="#8B1A1A", width=2)
# Innere Röhre
draw.rounded_rectangle([hole_x - 15, cy - half_cam + inner_margin,
                         screen_x + 8, cy + half_cam - inner_margin],
                        radius=4, fill="#1C1C1C", outline="#333")
# Blenden-Platte + Loch
draw.rectangle([hole_x - 5, cy - half_cam, hole_x + 5, cy + half_cam],
               fill="#C0392B", outline="#8B1A1A")
draw.rectangle([hole_x - 3, cy - half_ap, hole_x + 3, cy + half_ap],
               fill="#111")
draw.ellipse([hole_x - half_ap - 4, cy - half_ap - 4,
              hole_x + half_ap + 4, cy + half_ap + 4],
             outline="#3DBB8F", width=2)
# Schirm
draw.rectangle([screen_x - 2, cy - half_cam + inner_margin,
                screen_x + 6, cy + half_cam - inner_margin],
               fill="#F0E6D2", outline="#C8B89A", width=2)
# Labels
draw.text(((hole_x + screen_x)//2 - 50, cy - half_cam - 18),
          "Chipsdose (Kamera)", fill="#C0392B", font=fnt_title)
draw.text((hole_x - 8, cy + half_cam + 8), "Loch", fill="#555", font=fnt_sm)
draw.text((screen_x - 22, cy + half_cam + 8), "Schirm", fill="#777", font=fnt_sm)

# ── Lichtstrahlen ─────────────────────────────────────────────────
img_h      = min(obj_h * magnification, (half_cam - inner_margin) * 1.85)
obj_points = [candle_top+6, cy-obj_h//4, cy, cy+obj_h//4, candle_bot-6]
ray_cols   = [(181,126,220),(240,199,94),(181,126,220),(240,199,94),(181,126,220)]

for idx, oy in enumerate(obj_points):
    n  = max(2, int(aperture * 1.4))
    rc = ray_cols[idx % len(ray_cols)]
    for r in range(n):
        h_off  = 0 if n == 1 else (-half_ap + 2*half_ap*r/(n-1))
        hole_y = cy + h_off
        dx     = hole_x - obj_x
        if dx == 0:
            continue
        slope = (hole_y - oy) / dx
        img_y = int(hole_y + slope * (screen_x - hole_x))
        draw.line([obj_x, oy, hole_x, int(hole_y)], fill=rc, width=1)
        draw.line([hole_x, int(hole_y), screen_x, img_y], fill=rc, width=1)

# ── Projiziertes Bild (invertierte Kerze) ────────────────────────
img_top = int(cy - img_h / 2)
img_bot = int(cy + img_h / 2)
icw     = max(4, int(7 * magnification * 0.7))
flame_h = max(4, int(14 * magnification * 0.7))

draw.rectangle([screen_x - icw, img_top, screen_x + icw + 2, img_bot - flame_h],
               fill="#F5F0E0", outline="#CCC")
draw.ellipse([screen_x - icw - 3, img_bot - flame_h - 2,
              screen_x + icw + 5, img_bot + 2],
             fill="#FFB300", outline="#FF8F00")
if flame_h > 7:
    draw.ellipse([screen_x - icw//2, img_bot - flame_h//2,
                  screen_x + icw//2 + 2, img_bot], fill="#FFF3E0")

if blur_factor > 0.5:
    box = (max(0, screen_x-icw-8), max(0, img_top-6),
           min(W, screen_x+icw+12), min(H, img_bot+6))
    try:
        region = img.crop(box).filter(ImageFilter.GaussianBlur(blur_factor))
        img.paste(region, box)
    except Exception:
        pass

# ── Abstandslinien ────────────────────────────────────────────────
ly = cy + half_cam + 30
for x1, x2, label in [
    (obj_x, hole_x, f"{obj_distance} mm"),
    (hole_x, screen_x, f"{cam_length} mm"),
]:
    draw.line([x1, ly, x2, ly], fill="#AAAAAA", width=1)
    draw.polygon([x1, ly-3, x1+5, ly, x1, ly+3], fill="#AAAAAA")
    draw.polygon([x2, ly-3, x2-5, ly, x2, ly+3], fill="#AAAAAA")
    draw.text(((x1+x2)//2-20, ly+5), label, fill="#AAAAAA", font=fnt_sm)

# ── Bild anzeigen ────────────────────────────────────────────────
st.image(img, use_container_width=True)

st.divider()
# ── Kennwerte ─────────────────────────────────────────────────────
st.markdown("### 📊 Bild-Eigenschaften")
m1, m2, m3 = st.columns(3)
m1.metric("🔍 Vergrößerung", f"{magnification:.2f}×")
m2.metric("🎯 Schärfe",      f"{sharpness:.0f} %",
          delta="scharf" if sharpness >= 60 else "unscharf")
m3.metric("💡 Helligkeit",   f"{brightness:.0f} %",
          delta="hell" if brightness >= 50 else "dunkel")

col_a, col_b = st.columns(2)
with col_a:
    st.caption("Schärfe")
    st.progress(int(sharpness) / 100)
with col_b:
    st.caption("Helligkeit")
    st.progress(int(brightness) / 100)

# ── Info-Bereich expandierbar ───────────────────────────────────
st.divider()
with st.expander("❓  Wie funktioniert die Lochkamera?"):
    st.markdown("""
**Lichtstrahlen reisen immer geradeaus.**

Jeder Punkt der Kerze schickt Licht in alle Richtungen.
Das **Loch** lässt nur einen schmalen Strahl pro Punkt durch.

#### 🔄 Warum steht das Bild auf dem Kopf?
Die Strahlen von der **Flamme (oben)** und vom **Kerzenkörper (unten)**
kreuzen sich genau im Loch → danach sind sie vertauscht → **Bild ist invertiert!**

---

| Parameter | Auswirkung |
|-----------|------------|
| Kleineres Loch | ✅ Schärfer  ❌ Dunkler |
| Größeres Loch  | ✅ Heller   ❌ Unschärfer |
| Längere Kamera | ✅ Größeres Bild (Zoom) |
| Objekt näher   | ✅ Größeres Bild |

**Strahlensatz:**
> Bildgröße ÷ Objektgröße = Kameralänge ÷ Objektabstand
    """)

with st.expander("📐  Strahlendiagramm anzeigen"):
    dW, dH = 700, 280
    diag   = Image.new("RGB", (dW, dH), "white")
    dd     = ImageDraw.Draw(diag)
    ox2, hx2, sx2 = 90, 350, 610
    dcy2 = dH // 2
    dd.line([ox2, 55, ox2, dH-55], fill="#E74C3C", width=4)
    dd.text((ox2-20, 42),     "A",      fill="#E74C3C", font=fnt_title)
    dd.text((ox2-20, dH-55),  "B",      fill="#E74C3C", font=fnt_title)
    dd.text((ox2-15, dH-32),  "Objekt", fill="#888",    font=fnt_sm)
    dd.ellipse([hx2-8, dcy2-8, hx2+8, dcy2+8], fill="#111")
    dd.text((hx2-12, dcy2+14), "Loch",   fill="#888", font=fnt_sm)
    dd.line([sx2, 55, sx2, dH-55], fill="#888", width=3)
    dd.text((sx2-18, dH-32), "Schirm", fill="#888", font=fnt_sm)
    dd.line([ox2, 55,    hx2, dcy2],   fill="#B57EDC", width=3)
    dd.line([hx2, dcy2,  sx2, dH-55],  fill="#B57EDC", width=3)
    dd.text((sx2+8, dH-60), "A'", fill="#B57EDC", font=fnt_title)
    dd.line([ox2, dH-55, hx2, dcy2],   fill="#F0C75E", width=3)
    dd.line([hx2, dcy2,  sx2, 55],     fill="#F0C75E", width=3)
    dd.text((sx2+8, 42),  "B'", fill="#F0C75E", font=fnt_title)
    dd.ellipse([hx2-12, dcy2-12, hx2+12, dcy2+12], outline="#3DBB8F", width=3)
    st.image(diag, use_container_width=True,
             caption="Strahlen kreuzen sich im Loch → Bild steht auf dem Kopf")

st.divider()
st.markdown("""
<div style="text-align:center; color:#AAA; font-size:12px;">
🔬 Lochkamera-Simulation · 7. Klasse Physik 🎓
</div>
""", unsafe_allow_html=True)

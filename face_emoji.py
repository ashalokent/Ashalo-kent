import cv2
import mediapipe as mp
import numpy as np

# ── MediaPipe setup ───────────────────────────────────────────────────────────
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils
draw_spec = mp_draw.DrawingSpec(thickness=1, circle_radius=1, color=(0, 255, 0))

# ── Emoji map (Unicode → rendered via PIL) ────────────────────────────────────
# We use PIL to render emoji text onto the OpenCV frame
from PIL import Image, ImageDraw, ImageFont
import os


EMOJI_MAP = {
    "happy":     "😄",
    "sad":       "😢",
    "surprised": "😲",
    "angry":     "😠",
    "neutral":   "😐",
}

EMOJI_SIZE = 100   # px

def render_emoji(expression: str) -> np.ndarray:
    """Render an emoji character to a numpy BGRA image."""
    emoji_char = EMOJI_MAP.get(expression, "😐")
    img = Image.new("RGBA", (EMOJI_SIZE, EMOJI_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Try to find a colour emoji font; fall back gracefully
    font = None
    font_paths = [
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",          # Linux
        "/System/Library/Fonts/Apple Color Emoji.ttc",                 # macOS
        "C:/Windows/Fonts/seguiemj.ttf",                               # Windows
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, EMOJI_SIZE - 10)
            except Exception:
                pass
            break

    if font is None:
        # Pillow built-in fallback (no colour, but functional)
        font = ImageFont.load_default()

    draw.text((5, 5), emoji_char, font=font, embedded_color=True)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)


# Pre-render all emojis once for performance
EMOJI_IMGS = {expr: render_emoji(expr) for expr in EMOJI_MAP}


def overlay_emoji(frame: np.ndarray, emoji_bgra: np.ndarray, x: int, y: int):
    """Alpha-blend emoji onto frame at position (x, y)."""
    h, w = emoji_bgra.shape[:2]
    fh, fw = frame.shape[:2]

    # Clamp to frame boundaries
    x1, y1 = max(x, 0), max(y, 0)
    x2, y2 = min(x + w, fw), min(y + h, fh)
    ex1, ey1 = x1 - x, y1 - y
    ex2, ey2 = ex1 + (x2 - x1), ey1 + (y2 - y1)

    if x2 <= x1 or y2 <= y1:
        return

    roi        = frame[y1:y2, x1:x2].astype(np.float32)
    emoji_crop = emoji_bgra[ey1:ey2, ex1:ex2]
    alpha      = emoji_crop[:, :, 3:4].astype(np.float32) / 255.0
    emoji_rgb  = emoji_crop[:, :, :3].astype(np.float32)

    blended = roi * (1 - alpha) + emoji_rgb * alpha
    frame[y1:y2, x1:x2] = blended.astype(np.uint8)


# ── Landmark index helpers ────────────────────────────────────────────────────
# MediaPipe 468-point face mesh indices (canonical)
MOUTH_TOP    = 13
MOUTH_BOTTOM = 14
MOUTH_LEFT   = 61
MOUTH_RIGHT  = 291
LEFT_EYE_TOP    = 159
LEFT_EYE_BOTTOM = 145
RIGHT_EYE_TOP   = 386
RIGHT_EYE_BOTTOM= 374
LEFT_BROW_INNER = 107
LEFT_BROW_OUTER = 70
RIGHT_BROW_INNER= 336
RIGHT_BROW_OUTER= 300
NOSE_TIP     = 1


def dist(a, b):
    return np.linalg.norm(np.array([a.x - b.x, a.y - b.y]))


def classify_expression(lm) -> str:
    """Rule-based expression classifier using facial landmark ratios."""
    pts = lm.landmark

    # ── Mouth openness (vertical gap / mouth width) ──────────────────────────
    mouth_open   = dist(pts[MOUTH_TOP], pts[MOUTH_BOTTOM])
    mouth_width  = dist(pts[MOUTH_LEFT], pts[MOUTH_RIGHT])
    open_ratio   = mouth_open / (mouth_width + 1e-6)

    # ── Mouth corner lift (smile) ─────────────────────────────────────────────
    # Positive = corners above centre line → smile
    mouth_center_y = (pts[MOUTH_TOP].y + pts[MOUTH_BOTTOM].y) / 2
    corner_lift = mouth_center_y - (pts[MOUTH_LEFT].y + pts[MOUTH_RIGHT].y) / 2

    # ── Eyebrow raise ─────────────────────────────────────────────────────────
    eye_top_y    = (pts[LEFT_EYE_TOP].y + pts[RIGHT_EYE_TOP].y) / 2
    brow_y       = (pts[LEFT_BROW_INNER].y + pts[RIGHT_BROW_INNER].y) / 2
    brow_raise   = eye_top_y - brow_y   # larger = brows higher

    # ── Eye openness ──────────────────────────────────────────────────────────
    eye_open = (dist(pts[LEFT_EYE_TOP], pts[LEFT_EYE_BOTTOM]) +
                dist(pts[RIGHT_EYE_TOP], pts[RIGHT_EYE_BOTTOM])) / 2

    # ── Classification rules ──────────────────────────────────────────────────
    if open_ratio > 0.35 and brow_raise > 0.06:
        return "surprised"
    if corner_lift > 0.01 and open_ratio > 0.08:
        return "happy"
    if corner_lift > 0.005:
        return "happy"
    if corner_lift < -0.005 and brow_raise < 0.04:
        return "angry"
    if corner_lift < -0.003:
        return "sad"
    return "neutral"


# ── Smoothing: keep last N frames to avoid flickering ─────────────────────────
from collections import deque, Counter
HISTORY = deque(maxlen=10)


# ── Main loop ─────────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)
print("Press  Q  to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w  = frame.shape[:2]
    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    expression = "neutral"

    if result.multi_face_landmarks:
        face_lm = result.multi_face_landmarks[0]

        # Draw subtle mesh
        mp_draw.draw_landmarks(
            frame, face_lm,
            mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_draw.DrawingSpec(
                color=(80, 80, 80), thickness=1)
        )

        expression = classify_expression(face_lm)
        HISTORY.append(expression)
        # Majority vote for stability
        expression = Counter(HISTORY).most_common(1)[0][0]

        # Place emoji at top-right of face bounding box
        xs = [lm.x * w for lm in face_lm.landmark]
        ys = [lm.y * h for lm in face_lm.landmark]
        ex = int(max(xs)) + 10
        ey = int(min(ys)) - EMOJI_SIZE - 10
        overlay_emoji(frame, EMOJI_IMGS[expression], ex, ey)

    # ── HUD label ─────────────────────────────────────────────────────────────
    label = f"Expression: {expression.upper()}"
    cv2.rectangle(frame, (0, 0), (320, 40), (0, 0, 0), -1)
    cv2.putText(frame, label, (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 255, 180), 2)

    cv2.imshow("Face Expression → Emoji", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

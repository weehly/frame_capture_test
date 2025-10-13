#!/usr/bin/env python3
import os, cv2, datetime, numpy as np
from pathlib import Path

# ---- ROOT ermitteln: .env optional, sonst Ordner der Datei nutzen ----
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

ROOT = Path(os.getenv("/dev/video1") or Path(__file__).resolve().parent)
print("/dev/video1", ROOT)

# ---- Pfade ----
IMAGE_DIR = ROOT / "Skalierung_Zoom_Daten" / "Beispielbilder"
OUT_DIR   = ROOT / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def save_snapshot(frame_bgr: np.ndarray) -> Path:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUT_DIR / f"shot_{ts}.jpg"
    cv2.imwrite(str(path), frame_bgr)
    print(f"[Gespeichert] {path}")
    return path

# ==================== RASPI: USB-Framegrabber (AKTIV) ====================
def run_opencv_grabber(device_index: int = 0, width: int = 1280, height: int = 720, fps: int = 30, fourcc: str = "MJPG"):
    # Raspi/Linux: V4L2; Windows wäre CAP_DSHOW, aber hier Pi-Fokus
    cap = cv2.VideoCapture(device_index, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS,          fps)

    if not cap.isOpened():
        print(f"[Fehler] /dev/video{device_index} nicht verfügbar."); return

    print("[Info] Grabber aktiv. 's' = Screenshot speichern, 'q' = Quit.")
    while True:
        ok, f = cap.read()
        if not ok:
            print("[Warnung] Frame konnte nicht gelesen werden."); break
        cv2.imshow("Preview", f)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('s'):
            save_snapshot(f)
        if k == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ==================== PC-TEST: Bilderordner (AUSKOMMENTIERT) ====================
# def run_folder_stream():
#     paths = sorted([p for ext in ("*.png","*.jpg","*.jpeg","*.bmp") for p in IMAGE_DIR.glob(ext)])
#     if not paths:
#         print("[Fehler] Keine Testbilder gefunden:", IMAGE_DIR); return
#     i = 0
#     print("[Info] PC-Testmodus. 's' = Screenshot speichern, 'q' = Quit.")
#     while True:
#         f = cv2.imread(str(paths[i]), cv2.IMREAD_COLOR)
#         if f is None: break
#         cv2.imshow("Preview", f)
#         k = cv2.waitKey(1) & 0xFF
#         if k == ord('s'):
#             save_snapshot(f)
#         if k == ord('q'):
#             break
#         i = (i + 1) % len(paths)
#     cv2.destroyAllWindows()

# ==================== FFmpeg-Pipe (optional, AUSKOMMENTIERT) ====================
# import subprocess, shlex
# def run_ffmpeg_pipe(device="/dev/video0", width=1280, height=720, fps=30):
#     cmd = f"ffmpeg -hide_banner -loglevel error -f v4l2 -framerate {fps} -video_size {width}x{height} -i {device} -f rawvideo -pix_fmt bgr24 -"
#     p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, bufsize=10**7)
#     n = width * height * 3
#     print("[Info] FFmpeg-Grabber. 's' = Screenshot, 'q' = Quit.")
#     while True:
#         b = p.stdout.read(n)
#         if len(b) != n: break
#         f = np.frombuffer(b, np.uint8).reshape((height, width, 3))
#         cv2.imshow("Preview", f)
#         k = cv2.waitKey(1) & 0xFF
#         if k == ord('s'): save_snapshot(f)
#         if k == ord('q'): break
#     p.terminate(); cv2.destroyAllWindows()

if __name__ == "__main__":
    run_opencv_grabber()      # <-- Raspi/USB aktiv
    # run_folder_stream()     # <-- PC-Test aktivieren, wenn nötig
    # run_ffmpeg_pipe()       # <-- Alternative Pipeline aktivieren

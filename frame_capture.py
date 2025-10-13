#!/usr/bin/env python3#!/usr/bin/env python3
import cv2, glob, os, numpy as np, datetime
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
ROOT = Path(os.getenv("ROOT_PATH"))
print(ROOT)

# -------- Pfade --------

IMAGE_DIR = ROOT / "Skalierung_Zoom_Daten" / "Beispielbilder"
OUT_DIR   = ROOT / "screenshots"
os.makedirs(OUT_DIR, exist_ok=True)

# -------- Testpfade --------

#IMAGE_DIR = ROOT / "Skalierung_Zoom_Daten" / "Beispielbilder"
#OUT_DIR   = ROOT / "screenshots"
#os.makedirs(OUT_DIR, exist_ok=True)

def save_snapshot(frame_bgr):
    """Speichert Frame als JPG-Datei und gibt Pfad zurück"""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    #Pfad wo gespeichert wird: "C:..\Frame_Capture\screenshots\shot_20251002_135503.jpg"
    path = os.path.join(OUT_DIR, f"shot_{ts}.jpg")
    cv2.imwrite(path, frame_bgr)
    print(f"[Gespeichert] {path}")
    return path

def run_folder_stream():
    paths = sorted([p for ext in ("*.png","*.jpg","*.jpeg","*.bmp")
                    for p in glob.glob(os.path.join(IMAGE_DIR, ext))])
    if not paths:
        print("[Fehler] Keine Bilder im IMAGE_DIR gefunden."); return
    i = 0
    print("[Info] Läuft im PC-Testmodus. 's'=Screenshot speichern, 'q'=Quit.")
    while True:
        f = cv2.imread(paths[i], cv2.IMREAD_COLOR)
        if f is None: break
        cv2.imshow("Preview", f)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('s'):                        # Bild speichern für weitergabe
            save_snapshot(f)
        if k == ord('q'): break
        i = (i + 1) % len(paths)
    cv2.destroyAllWindows()

# ====== FRAMEGRABBER (OpenCV) — AUSKOMMENTIERT für später ======
# def run_opencv_grabber(device_index=0, width=1280, height=720, fps=30, fourcc="MJPG"):
#     cap = cv2.VideoCapture(device_index, cv2.CAP_V4L2 if os.name!='nt' else cv2.CAP_DSHOW)
#     cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH,  width)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
#     cap.set(cv2.CAP_PROP_FPS, fps)
#     print("[Info] OpenCV-Grabber. 's'=Screenshot speichern, 'q'=Quit.")
#     while True:
#         ok, f = cap.read()
#         if not ok: break
#         cv2.imshow("Preview", f)
#         k = cv2.waitKey(1) & 0xFF
#         if k == ord('s'): save_snapshot(f)
#         if k == ord('q'): break
#     cap.release(); cv2.destroyAllWindows()

# ====== FRAMEGRABBER (FFmpeg-Pipe) — AUSKOMMENTIERT für später ======
# import subprocess, shlex
# def run_ffmpeg_pipe(device="/dev/video0", width=1280, height=720, fps=30):
#     cmd = (f"ffmpeg -hide_banner -loglevel error "
#            f"{'-f dshow -i '+device if os.name=='nt' else f'-f v4l2 -framerate {fps} -video_size {width}x{height} -i {device}'} "
#            f"-vf scale={width}:{height},fps={fps} -f rawvideo -pix_fmt bgr24 -")
#     p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, bufsize=10**7)
#     n = width * height * 3
#     print("[Info] FFmpeg-Grabber. 's'=Screenshot speichern, 'q'=Quit.")
#     while True:
#         b = p.stdout.read(n)
#         if len(b)!=n: break
#         f = np.frombuffer(b, np.uint8).reshape(height, width, 3)
#         cv2.imshow("Preview", f)
#         k = cv2.waitKey(1)&0xFF
#         if k == ord('s'): save_snapshot(f)
#         if k == ord('q'): break
#     p.terminate(); cv2.destroyAllWindows()


if __name__ == "__main__":
    run_folder_stream()     # <- PC-Test aktiv
    # run_opencv_grabber()  # <- für Framegrabber aktivieren
    # run_ffmpeg_pipe()     # <- alternativ FFmpeg aktivieren


def run():
    # Wrapper, damit main.py frame_capture.run() aufrufen kann
    run_folder_stream()
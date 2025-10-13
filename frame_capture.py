#!/usr/bin/env python3
import cv2, datetime
from pathlib import Path

WIDTH, HEIGHT, FPS = 1280, 720, 30
FULLSCREEN = True
OUT_DIR = Path("screenshots"); OUT_DIR.mkdir(exist_ok=True, parents=True)

def save_jpg(img):
    p = OUT_DIR / f"shot_{datetime.datetime.now():%Y%m%d_%H%M%S}.jpg"
    cv2.imwrite(str(p), img); print("[Gespeichert]", p)

def try_open(idx, fourcc="MJPG"):
    cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS,          FPS)
    ok, f = cap.read()
    return cap if ok and f is not None else (cap.release() or None)

def main():
    cap = try_open(0,"MJPG") or try_open(1,"MJPG") or try_open(0,"YUYV") or try_open(1,"YUYV")
    if not cap: print("[Fehler] Kein USB-Grabber auf /dev/video0/1."); return

    cv2.namedWindow("Preview", cv2.WINDOW_NORMAL)
    if FULLSCREEN:
        cv2.setWindowProperty("Preview", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[Info] Vorschau aktiv: {w}x{h}  |  S = Screenshot, Q = Quit")

    while True:
        ok, f = cap.read()
        if not ok: print("[Warnung] Frame read failed"); break
        cv2.imshow("Preview", f)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('s'): save_jpg(f)
        if k == ord('q'): break

    cap.release(); cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

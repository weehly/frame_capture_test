#!/usr/bin/env python3
import cv2, datetime, time
from pathlib import Path
import RPi.GPIO as GPIO

# ==== Einstellungen ====
DEVICE = 0                 # /dev/video0=0, /dev/video1=1
WIDTH, HEIGHT, FPS = 1280, 720, 30
FOURCC = "MJPG"            # Fallback auf "YUYV" möglich
BTN_GPIO = 17              # Taster an BCM 17 (Pin 11 -> gegen GND)
FULLSCREEN = True          # Vorschau im Vollbild

OUT_DIR = Path("screenshots")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def save_jpg(img):
    p = OUT_DIR / f"shot_{datetime.datetime.now():%Y%m%d_%H%M%S}.jpg"
    cv2.imwrite(str(p), img)
    print("[Gespeichert]", p)
    return p

def open_cap(idx, fourcc="MJPG"):
    cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS,          FPS)
    ok, f = cap.read()
    if not ok or f is None:
        cap.release()
        return None
    return cap

def main():
    # --- GPIO ---
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BTN_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    button_pressed = [False]

    def on_button(_): button_pressed.__setitem__(0, True)
    GPIO.add_event_detect(BTN_GPIO, GPIO.FALLING, callback=on_button, bouncetime=250)

    # --- Capture ---
    cap = open_cap(DEVICE, FOURCC) or open_cap(DEVICE, "YUYV")
    if cap is None:
        print(f"[Fehler] Konnte /dev/video{DEVICE} nicht öffnen."); GPIO.cleanup(); return

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[Info] Capture: /dev/video{DEVICE} {w}x{h} @~{FPS}fps")
    show = True
    try:
        # Fenster vorbereiten (falls Display verfügbar)
        try:
            cv2.namedWindow("Preview", cv2.WINDOW_NORMAL)
            if FULLSCREEN:
                cv2.setWindowProperty("Preview", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        except cv2.error:
            print("[Hinweis] Kein Display verfügbar -> Headless-Modus.")
            show = False

        last_flash = 0.0
        while True:
            ok, frame = cap.read()
            if not ok: print("[Warnung] Frame read failed"); time.sleep(0.01); continue

            # Overlay (nur Anzeige)
            if show:
                cv2.putText(frame, "Button=Save  |  S=Save  Q=Quit", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2, cv2.LINE_AA)
                if time.time() - last_flash < 0.15:  # kurzer „Flash“ nach Save
                    cv2.rectangle(frame, (0,0), (w,h), (0,255,0), 30)

                cv2.imshow("Preview", frame)
                k = cv2.waitKey(1) & 0xFF
                if k == ord('s'):
                    save_jpg(frame); last_flash = time.time()
                elif k == ord('q'):
                    break
            else:
                # Headless: nur auf Button hören; CPU schonen
                time.sleep(0.005)

            if button_pressed[0]:
                save_jpg(frame); last_flash = time.time()
                button_pressed[0] = False

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        if show: cv2.destroyAllWindows()
        GPIO.cleanup()
        print("[Info] Beendet.")

if __name__ == "__main__":
    main()

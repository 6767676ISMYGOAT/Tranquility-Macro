
import cv2
import numpy as np
import mss
import pyautogui
import keyboard
import time

# =================================
# TRANQUILITY MACRO - VERSION 0.1
# =================================

# Screen positions based on your screenshot.
# Roblox should be maximized in windowed mode.

LANES = {
    "D": 0.220,
    "F": 0.382,
    "J": 0.544,
    "K": 0.706
}

HIT_LINE = 0.785
HIT_TOLERANCE = 15

AUTO_PRESS = False
RUNNING = True

# Color ranges in OpenCV HSV format
COLORS = {
    "D": ((80, 65, 90), (105, 255, 255)),
    "F": ((115, 55, 90), (165, 255, 255)),
    "J": ((18, 75, 100), (42, 255, 255)),
    "K": ((160, 55, 100), (179, 255, 255))
}

last_inside = {key: False for key in LANES}

def toggle_auto():
    global AUTO_PRESS
    AUTO_PRESS = not AUTO_PRESS
    print("AUTO PRESS:", "ON" if AUTO_PRESS else "OFF")

def stop_macro():
    global RUNNING
    RUNNING = False
    print("Stopping Tranquility Macro...")

keyboard.add_hotkey("F8", toggle_auto)
keyboard.add_hotkey("F9", stop_macro)

print("================================")
print("     TRANQUILITY MACRO")
print("================================")
print("F8 = Toggle automatic key presses")
print("F9 = Exit")
print("Detection mode enabled.")
print("")

with mss.mss() as sct:

    monitor = sct.monitors[1]

    while RUNNING:

        screenshot = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        height, width = frame.shape[:2]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        target_y = int(height * HIT_LINE)

        for key, ratio in LANES.items():

            lane_x = int(width * ratio)

            lower, upper = COLORS[key]

            mask = cv2.inRange(
                hsv,
                np.array(lower),
                np.array(upper)
            )

            contours, _ = cv2.findContours(
                mask,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            detected = False

            for contour in contours:

                area = cv2.contourArea(contour)

                if area < 900:
                    continue

                perimeter = cv2.arcLength(contour, True)

                if perimeter == 0:
                    continue

                circularity = (
                    4 * np.pi * area / (perimeter * perimeter)
                )

                if circularity < 0.60:
                    continue

                (cx, cy), radius = cv2.minEnclosingCircle(contour)

                cx = int(cx)
                cy = int(cy)
                radius = int(radius)

                if not 18 <= radius <= 65:
                    continue

                # Only inspect circles in their matching lane
                if abs(cx - lane_x) > width * 0.045:
                    continue

                # Filled circle check helps reject the stationary
                # hollow target rings.
                if mask[cy, cx] == 0:
                    continue

                if abs(cy - target_y) <= HIT_TOLERANCE:

                    detected = True

                    if not last_inside[key]:

                        print("NOTE:", key)

                        if AUTO_PRESS:
                            pyautogui.press(key.lower())

                    break

            last_inside[key] = detected

        time.sleep(0.005)

print("Macro closed.")

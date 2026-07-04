import pyautogui


class KeyboardController:

    def __init__(self):

        pyautogui.FAILSAFE = False

    def press(self, key):

        if key == "SPACE":
            pyautogui.press("space")
        elif key == "BACKSPACE":
            pyautogui.press("backspace")
        else:
            pyautogui.write(key)
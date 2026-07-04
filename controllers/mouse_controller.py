import pyautogui

pyautogui.FAILSAFE = False


class MouseController:

    def __init__(self):

        self.screen_width, self.screen_height = pyautogui.size()

    def move(self, x, y):

        pyautogui.moveTo(x, y)

    def left_click(self):

        pyautogui.click()


    def right_click(self):
        
        pyautogui.rightClick()
        
        
    def mouse_down(self):
        
        pyautogui.mouseDown()
        
        
    def mouse_up(self):
    
        pyautogui.mouseUp()


    def scroll(self, amount):

        pyautogui.scroll(amount)     

    def drag_start(self):
        pyautogui.mouseDown()


    def drag_end(self):
        pyautogui.mouseUp()  
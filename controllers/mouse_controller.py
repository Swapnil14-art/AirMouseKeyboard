import pyautogui

pyautogui.FAILSAFE = False


class MouseController:

    def __init__(self):

        self.screen_width, self.screen_height = pyautogui.size()

        self.prev_x = 0
        self.prev_y = 0

        self.smoothing = 6

    def move(self, x, y):

        current_x = self.prev_x + (x - self.prev_x) / self.smoothing
        current_y = self.prev_y + (y - self.prev_y) / self.smoothing

        pyautogui.moveTo(current_x, current_y)

        self.prev_x = current_x
        self.prev_y = current_y

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
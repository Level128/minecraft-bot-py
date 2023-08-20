#!/usr/bin/python3

import cv2
import numpy as np 
from pathlib import Path
import mss
import keyboard
import time


class ColorFinder():
    resize = True
    invert = False
    cols = [[0, 0, 0], [179, 255, 255]]
    control_window_name = 'Control Window'
    img_windows = [None]
    img_hsv = [None]
    sct = None
    

    def __init__(self):
        # Control window setup
        cv2.namedWindow(self.control_window_name, cv2.WINDOW_AUTOSIZE)
        self.create_gui()

    def create_gui(self):
        '''Function that creates the trackbar interface'''

        cv2.createTrackbar("Low Hue", self.control_window_name, 0, 179, lambda x: self.update_values(x, 0, 0))
        cv2.createTrackbar("High Hue", self.control_window_name, 179, 179, lambda x: self.update_values(x, 1, 0))
        cv2.createTrackbar("Low Sat", self.control_window_name, 0, 255, lambda x: self.update_values(x, 0, 1))
        cv2.createTrackbar("High Sat", self.control_window_name, 255, 255, lambda x: self.update_values(x, 1, 1))
        cv2.createTrackbar("Low Val", self.control_window_name, 0, 255, lambda x: self.update_values(x, 0, 2))
        cv2.createTrackbar("High Val", self.control_window_name, 255, 255, lambda x: self.update_values(x, 1, 2))
        cv2.createTrackbar("Invert", self.control_window_name, 0, 1, self.do_invert)
        
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    def do_invert(self, val):
        '''Function that alters mask inversion'''
        self.invert = val == 1
        self.update_images()

    def update_values(self, val, colrange, param):
        '''Function that updates the value ranges as set by the trackbars '''
        self.cols[colrange][param] = val
        self.update_images()

    def update_images(self):
        '''Displays image, masked with updated values'''
        for idx, img in enumerate(self.img_hsv):
            window_name = f'{self.image_paths[idx]}'
            mask = cv2.inRange(img, tuple(self.cols[0]), tuple(self.cols[1]))
            if self.invert:
                mask = cv2.bitwise_not(mask)
            res = cv2.bitwise_and(img, img, mask=mask)
            cv2.imshow(window_name, res)

    def use_images(self, image_paths):
        self.image_paths = image_paths
        self.img_windows = [cv2.imread(img) for img in image_paths]
        self.img_hsv = [cv2.cvtColor(window, cv2.COLOR_BGR2HSV) for window in self.img_windows]
        for idx, img in enumerate(self.img_hsv):
            window_name = f'{self.image_paths[idx]}'
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            if self.resize == True and (img.shape[0] > 600 or img.shape[1] > 800):
                cv2.resizeWindow(window_name, (800, 600))
            cv2.imshow(window_name, img)
        
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def init_mss(self):
        if self.sct == None:
            import mss
            self.sct = mss.mss()

    def follow_mouse(self, width=50, height=50):
        import pyautogui
        max_width, max_height = pyautogui.size()
        max_width -= width
        max_height -= height
        self.init_mss()
        freeze = False
        
        while True:
            try:
                # only works as ROOT on linux
                # should work on Windows
                if keyboard.is_pressed("p"):
                    freeze = True
            except:
                pass
            if freeze == False:
                self.mx, self.my = pyautogui.position()
                
            # grab around the current mouse position
            self.last_screenshot = np.array(
                self.sct.grab({
                    "top": min(max_height, max(height // 2, self.my - height // 2)), 
                    "left": min(max_width, max(width // 2, self.mx - width // 2)), 
                    "width": width, 
                    "height": height
                    }
                )
            )

            # convert colors to HSV
            self.last_screenshotHSV = cv2.cvtColor(
                cv2.UMat(self.last_screenshot), cv2.COLOR_BGR2HSV)

            self.img_hsv[0] = self.last_screenshotHSV
            self.update_images()
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
        if cv2.waitKey(30) & 0xFF == ord('q'):
            cv2.destroyWindow(winname)
    
    def use_live_screen(self, x=0, y=0, width=50, height=50):
        self.init_mss()
        
        while True:
            self.last_screenshot = np.array(
            # grab a 150x150 box around the current mouse position
            self.sct.grab({"top": max(height // 2, y - height // 2), "left": max(width // 2, x - width // 2), "width": width, "height": height}))
            # self.sct.grab({"top": 100, "left": 100, "width": width, "height": height}))

            # convert colors to HSV
            self.last_screenshotHSV = cv2.cvtColor(
                cv2.UMat(self.last_screenshot), cv2.COLOR_BGR2HSV)

            self.img_hsv[0] = self.last_screenshotHSV
            self.update_images()
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()



if __name__ == '__main__':
    # images = ["./images/bobber3.png", "./images/bobber2.png", "./images/bobber4.png"]
    images = [str(x) for x in Path('./images').rglob('ore*.*g')]
    # print(images)
    cf = ColorFinder()
    cf.use_images(images)
    # cf.use_live_screen(100, 100, 259, 250)
    # cf.follow_mouse()
    # img = cv2.imread(images[0])
    # print([x for x in dir(img) if not x.startswith("__")])
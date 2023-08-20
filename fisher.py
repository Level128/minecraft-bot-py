#!/usr/bin/python3

import pyautogui
import pydirectinput
import keyboard
import time
import numpy as np
import cv2
from mss import mss


class FishingBot():
    debug = False
    sct = mss()
    last_screenshot = None
    last_screenshotHSV = None
    capture_height = 150
    capture_width = 150

    # delay in milliseconds
    # https://docs.opencv.org/2.4/modules/highgui/doc/user_interface.html?highlight=waitkey#waitkey
    wait_key_delay = 20

    # mining attributes
    found_diamonds = False
    placing_torch = False
    is_moving_forward = False
    is_mining = False
    torches_placed = 0

    # fishing attributes
    catches = 0
    fishing_fail_count = 0

    # old working
    # lower_range_bobber = np.array([0, 170, 0], np.uint8)
    # upper_range_bobber = np.array([17, 215, 255], np.uint8)

    # New Test
    lower_range_bobber = np.array([0, 175, 125], np.uint8)
    upper_range_bobber = np.array([179, 215, 215], np.uint8)

    def capture_screenshot(self, imageName):
        # get the mouse cursor position
        mx, my = pyautogui.position()
        max_width, max_height = pyautogui.size()
        max_width -= self.capture_width
        max_height -= self.capture_height

        self.last_screenshot = np.array(
            # grab a 150x150 box around the current mouse position
            self.sct.grab({
                "top": min(max_height, max(self.capture_height // 2, my - self.capture_height // 2)), 
                "left": min(max_width, max(self.capture_width // 2, mx - self.capture_width // 2)), 
                "width": self.capture_width, 
                "height": self.capture_height
                }
            )
        )

        # convert colors to HSV
        self.last_screenshotHSV = cv2.cvtColor(
            cv2.UMat(self.last_screenshot), cv2.COLOR_BGR2HSV)

        # show image for debugging purposes
        if self.debug == True:
            cv2.imshow(imageName, self.last_screenshot)
            if cv2.waitKey(self.wait_key_delay) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
        # cv2.imwrite("bobber2.png", self.last_screenshot)

    def is_bobber_visible(self):
        self.capture_screenshot("Bobber")
        mask_bobber = cv2.inRange(
            self.last_screenshotHSV, self.lower_range_bobber, self.upper_range_bobber)
        mask_bobber_pixel_count = cv2.countNonZero(mask_bobber)

        if self.debug == True:
            cv2.imwrite("mask_bobber.png", mask_bobber)
            cv2.imshow("bobber", mask_bobber)
            print(f"mask_bobber pixel count: {mask_bobber_pixel_count}")

        if int(mask_bobber_pixel_count) == 0:
            # Bobber is under the water or missing
            return False
        return True

    def check_kill_switch(self):
        if keyboard.is_pressed("u"):
            if self.is_mining == True:
                self.stop_mining()
            quit()
            return True
        return False

    def start_bot(self):
        print("Starting bot in 3 seconds...")
        for _ in range(3, 0, -1):
            print(_)
            time.sleep(1)
        print("Running...")

        self.init_bobber()
        self.fishing_loop()

    def recast_line(self):
        pyautogui.rightClick()
        time.sleep(0.5)
        pyautogui.rightClick()
        time.sleep(2)

    def init_bobber(self):
        attempts = 1
        while self.is_bobber_visible() == False:
            if attempts > 5:
                print("Failed init fishing bobber, check for game issues")
                quit()
            else:
                print(f"Init bobber attempt {attempts}/5")
                attempts += 1
                pyautogui.rightClick()
                time.sleep(2)
        self.fishing_fail_count = 0
        print("Bobber initialized")
        return True

    def fishing_loop(self):
        last_cast_time = time.time()
        self.fishing_fail_count = 0
        averageTime = 0

        while True:
            if self.check_kill_switch():
                break

            if self.is_bobber_visible() == False:
                # check if bobber was not found too fast
                if time.time() - last_cast_time < 0.5:
                    self.fishing_fail_count += 1
                    print(f"Counting failure, {self.fishing_fail_count=}")
                else:
                    self.fishing_fail_count = 0
                    castTime = time.time() - last_cast_time
                    averageTime = ((averageTime*self.catches) +
                                   castTime)/(self.catches + 1)
                    self.catches += 1
                    print(
                        f"Reeling in! Took {round(castTime, 2)} seconds, found {self.catches} item{'s' if self.catches > 1 else ''} so far! - Avg. {round(averageTime, 2)} secs")
                if (self.fishing_fail_count > 2):
                    print("Failed to find bobber, trying to reinitialize bobber...")
                    self.init_bobber()
                self.recast_line()
                last_cast_time = time.time()

if __name__ == "__main__":
    bot = FishingBot()
    bot.start_bot()

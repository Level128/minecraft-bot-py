#!/usr/bin/python3

import pyautogui
import pydirectinput
import keyboard
import time
import numpy as np
import cv2
from mss import mss


class MiningBot():
    found_diamonds = False
    placing_torch = False
    is_moving_forward = False
    is_mining = False
    torches_placed = 0
    last_screenshot = None
    sct = None

    lower_range_diamond = np.array([88, 42, 7], np.uint8)
    upper_range_diamond = np.array([99, 99, 255], np.uint8)
    lower_range_lava = np.array([6, 177, 161], np.uint8)
    upper_range_lava = np.array([34, 255, 235], np.uint8)
    # lower_range_lava = np.array([0, 177, 144], np.uint8) # worked but found copper
    # upper_range_lava = np.array([32, 255, 235], np.uint8)
    # lower_range_lava = np.array([7, 216, 193], np.uint8)
    # upper_range_lava = np.array([23, 255, 255], np.uint8)

    def __init__(self):
        self.sct = mss()

    def start_moving_forward(self):
        # pydirectinput.keyDown("c")
        # pydirectinput.mouseDown()
        pydirectinput.keyDown("shift")
        pydirectinput.keyDown("w")
        return True

    def start_mining(self):
        pydirectinput.mouseDown()
        self.mining = True
        return True

    def capture_screen(self):
        self.lastScreenshot = np.array(
            self.sct.grab({"top": 30, "left": 0, "width": 1920, "height": 1000}))
        self.lastScreenshotHSV = cv2.cvtColor(
            cv2.UMat(self.lastScreenshot), cv2.COLOR_BGR2HSV)

    def is_diamonds_present(self):
        mask_diamond = cv2.inRange(
            self.lastScreenshotHSV, self.lower_range_diamond, self.upper_range_diamond)

        # cv2.imwrite("HSV.png", hsv)
        # cv2.imwrite("CurrentMaskDiamond.png", mask_diamond)
        # cv2.imwrite("CurrentMaskLava.png", mask_lava)
        # print(f"Blue pixels: {cv2.countNonZero(mask_diamond)}")

        # if more than 12,000 pixels of diamonds found, STOP!
        if (int(cv2.countNonZero(mask_diamond)) > 12000):
            self.stop_actions()
            print("Found Diamonds")
            return True
        return False

    def turn(self):
        time.sleep(3)
        pyautogui.moveRel(-700, 0)

    def is_lava_present(self):
        mask_lava = cv2.inRange(self.lastScreenshotHSV,
                                self.lower_range_lava, self.upper_range_lava)

        # cv2.imwrite("HSV.png", hsv)
        # cv2.imwrite("CurrentMaskDiamond.png", mask_diamond)
        # cv2.imwrite("CurrentMaskLava.png", mask_lava)
        # print(f"Orange pixels: {cv2.countNonZero(mask_lava)}")

        # if more than 20,000 pixels of lava found, STOP!
        if (int(cv2.countNonZero(mask_lava)) > 20000):
            self.stop_actions()
            # pydirectinput.moveRel(0, -1000)
            # pydirectinput.moveRel(0, -1000)
            # pydirectinput.moveRel(0, -1000)
            # pydirectinput.press("8")
            # pydirectinput.rightClick()
            # pydirectinput.press("c")
            print("Found Lava! Backing up!!!")
            self.walk_backwards()
            return True
        return False

    def walk_backwards(self):
        pydirectinput.keyDown("s")
        time.sleep(5)
        pydirectinput.keyUp("s")
        return True

    def stop_actions(self):
        pydirectinput.keyUp("w")
        pydirectinput.keyUp("shift")
        pydirectinput.mouseUp()
        self.movingForward = False
        self.mining = False
        return True

    def check_kill_switch(self):
        if keyboard.is_pressed("u"):
            self.stop_actions()
            return True
        return False

    def start_bot(self):
        print("Starting bot in 3 seconds...")
        for _ in range(3, 0, -1):
            print(_)
            time.sleep(1)
        print("Running...")
        self.start_moving_forward()
        self.start_mining()
        self.mining_loop()

    def mining_loop(self):
        while True:
            self.capture_screen()
            if self.check_kill_switch() or self.is_lava_present():
                break
            else:
                self.start_mining()


'''
def mining_forward():
    # if not placing_torch:
    #     pydirectinput.keyDown("c")
    #     pydirectinput.mouseDown()
    #     pydirectinput.keyDown("w")
    if keyboard.is_pressed("u"):
        pydirectinput.keyUp("w")
        pydirectinput.mouseUp()
        terminated = True


def timer():
    global t
    # torch_time = time.time()
    # screenshot_time = time.time()
    pydirectinput.keyDown("c")
    pydirectinput.mouseDown()
    pydirectinput.keyDown("w")
    while not found_diamonds and not terminated:
        print(f"{time.time() - t}")
        t = time.time()
        # mining_forward()
        # if(time.time() > torch_time + 6):
        #     torch_time = time.time()
        #     place_torch()
        detect_color()
        # if(time.time() > screenshot_time + 0.4):
        #     screenshot_time = time.time()
        #     if not placing_torch:
        #         detect_color()


def place_torch():
    global placing_torch
    global torches_placed
    torches_placed += 1
    if torches_placed % 64 == 0:
        pydirectinput.press(str(torches_placed / 64))
        pydirectinput.press("f")
        pydirectinput.press("9")
    placing_torch = True
    pydirectinput.mouseUp()
    pydirectinput.moveRel(700, 400)
    pydirectinput.rightClick()
    pydirectinput.moveRel(-700, -400)
    placing_torch = False


def detect_color():
    # im1 = pyautogui.screenshot("currentImg.png", region=(0, 30, 1920, 1000))
    im1 = np.array(
        sct.grab({"top": 30, "left": 0, "width": 1920, "height": 1000}))
    # im1 = cv2.imread("currentImg.png")
    hsv = cv2.cvtColor(cv2.UMat(im1), cv2.COLOR_BGR2HSV)
    mask_diamond = cv2.inRange(hsv, lower_range_diamond, upper_range_diamond)
    mask_lava = cv2.inRange(hsv, lower_range_lava, upper_range_lava)

    # cv2.imwrite("HSV.png", hsv)
    # cv2.imwrite("CurrentMaskDiamond.png", mask_diamond)
    # cv2.imwrite("CurrentMaskLava.png", mask_lava)
    print(f"Blue pixels: {cv2.countNonZero(mask_diamond)}")
    print(f"Orange pixels: {cv2.countNonZero(mask_lava)}")

    if (int(cv2.countNonZero(mask_diamond)) > 12000):
        release_inputs()
        print("Found Diamonds")
        quit()
    if (int(cv2.countNonZero(mask_lava)) > 20000):
        release_inputs()
        # pydirectinput.moveRel(0, -1000)
        # pydirectinput.moveRel(0, -1000)
        # pydirectinput.moveRel(0, -1000)
        # pydirectinput.press("8")
        # pydirectinput.rightClick()
        # pydirectinput.press("c")
        print("Found Lava! Backing up!!!")
        pydirectinput.keyDown("s")
        time.sleep(5)
        pydirectinput.keyUp("s")
        quit()


def release_inputs():
    pydirectinput.keyUp("w")
    pydirectinput.mouseUp()
'''


if __name__ == "__main__":
    bot = MiningBot()
    bot.start_bot()


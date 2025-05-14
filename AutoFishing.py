import numpy as np
import time
import threading
import signal
import keyboard
import pyautogui
import tkinter as tk
from tkinter import messagebox
from tracker import *
from area_detector import *
from fish_detector import *

# Đường dẫn đến hình ảnh mẫu
target_path = "images/target.png"
special_area_path = "images/special_area.png"
fish_path = "images/Fish.png"
exit_path = "images/exit.png"

# Khai báo biến toàn cục
running = False
selected_mode = "Day"
program_state = "Baitting"
isBaiting = threading.Event()
isHooking = threading.Event()
isExiting = threading.Event()

def create_gui():
    """Hàm tạo giao diện GUI"""
    # Biến toàn cục để lưu chế độ người dùng chọn
    global target_path, special_area_path, fish_path, exit_path
    global running, selected_mode
    def set_mode(mode):
        """Hàm để cập nhật chế độ được chọn"""
        global selected_mode
        selected_mode = mode

    def start_program():
        """Hàm được gọi khi nhấn nút Start"""
        # messagebox.showinfo("Chế độ được chọn", f"Bạn đã chọn chế độ: {selected_mode}")
        # Thực hiện logic khởi chạy chương trình
        global target_path, special_area_path, fish_path, exit_path
        global running, selected_mode
        if selected_mode == "Day":
            # Tham chiếu tới ảnh mục tiêu cho chế độ "Day"
            target_path = "images/target.png"
            special_area_path = "images/special_area.png"
            fish_path = "images/Fish.png"
            exit_path = "images/exit.png"
        elif selected_mode == "Night":
            # Tham chiếu tới ảnh mục tiêu cho chế độ "Night"
            target_path = "images/target.png"
            special_area_path = "images/special_area_night.png"
            fish_path = "images/Fish_night.png"
            exit_path = "images/exit.png"

        print(f"Đang sử dụng ảnh mục tiêu: {selected_mode}")
        # Gọi hàm chính hoặc thực hiện logic tiếp theo
        window.destroy()
        main()  # Giả sử đây là hàm chính

    # Tạo giao diện Tkinter
    window = tk.Tk()
    window.title("AutoFishing")

    # Tạo các nút chọn chế độ
    frame = tk.Frame(window)
    frame.pack(pady=10)

    day_button = tk.Button(frame, text="Day", command=lambda: set_mode("Day"), width=10, bg="lightblue")
    day_button.grid(row=0, column=0, padx=10)

    night_button = tk.Button(frame, text="Night", command=lambda: set_mode("Night"), width=10, bg="gray")
    night_button.grid(row=0, column=1, padx=10)

    # Tạo nút Start
    start_button = tk.Button(window, text="Start", command=start_program, bg="green", fg="white", width=15)
    start_button.pack(pady=20)

    # Khởi chạy giao diện
    window.mainloop()

# Hàm xử lý tín hiệu SIGINT
def send_sigint(signal_number, frame):
    global running, isBaiting, isHooking, isExiting
    running = False
    isBaiting.clear()
    isHooking.clear()
    isExiting.clear()
    print("\nĐã nhận tín hiệu SIGINT. Dừng chương trình.")
    create_gui()

# Đăng ký tín hiệu SIGINT
signal.signal(signal.SIGINT, send_sigint)

# Hàm lắng nghe phím nhấn 'q'
def f_kill():
    global running
    while running:
        if keyboard.is_pressed('q'):  # Nếu nhấn phím 'q'
            print("Nhấn 'q' để dừng chương trình.")
            signal.raise_signal(signal.SIGINT)  # Gửi tín hiệu SIGINT
            break
        time.sleep(0.35)

def f_checkBait(running, isBaiting, isHooking, isExiting, target_click_pos):
    global program_state
    
    # Thời gian timeout (tính bằng số lần không tìm thấy bait)
    timeout_duration = 20
    timeout_start = 0  # Lưu thời điểm bắt đầu kiểm tra

    while running:
        # print("I'm in f_checkBait")
        isBaiting.wait()
        # region=(1140, 572, 1242-1140, 670-572)
        time.sleep(0.2)
        try:
            check_bait = pyautogui.locateOnScreen(
                target_path, 
                region=(495, 151, 621-495, 194-151),
                confidence=0.5)
                
            if check_bait != None:
                print("Baited !!!")
                isBaiting.clear()
                isHooking.set()
                isExiting.clear()
                program_state = "hooking"
                timeout_start = 0
                # pyautogui.click(target_click_pos)
                # keyboard.press_and_release('f')
                
                    
        except pyautogui.ImageNotFoundException:
            if timeout_start >= timeout_duration:
                isBaiting.clear()  # Hủy trạng thái Baiting
                isExiting.set()
                # print(f"timeout_start: {timeout_start}")
                # print("Timeout! Không tìm thấy bait trong thời gian cho phép.")
                timeout_start = 0
                exit_click_pos = (916, 195)
                f_exit(exit_click_pos)
                # keyboard.press_and_release('0')
                # continue
            else:
                timeout_start += 1
                # print(f"timeout_start: {timeout_start}")
                # print("No bait yet")
                pyautogui.click(target_click_pos)
                # keyboard.press_and_release('f')
        time.sleep(0.35)



def f_checkResult(running, isHooking, isExiting, exit_click_pos):
    global program_state
    while running:
        isHooking.wait()
        # Kiểm tra sự tồn tại của ảnh exit
        try:
            check_exit = pyautogui.locateOnScreen(
                exit_path, 
                region=(850, 100, 950-850, 250-120),
                confidence=0.7)
                
            if check_exit != None:
                # print("Exit image found! Stopping...")
                isExiting.set()
                isHooking.clear()
                program_state = "exiting"
                f_exit(exit_click_pos)
                    
        except pyautogui.ImageNotFoundException:
            # print("No exit yet")
            pass       
        time.sleep(0.7)    
         

def f_exit(exit_click_pos):
    global program_state, isBaiting, isHooking, isExiting
    isExiting.wait()
    # print("I'm in f_exit")
    time.sleep(0.5)
    pyautogui.click(exit_click_pos)
    # keyboard.press_and_release('0')
    isExiting.clear()
    isHooking.clear()
    isBaiting.set()
    program_state= "baiting" # Nhớ chỉnh về baiting sau đó
    
    # print("I'm in f_exit")

def main():
    global running, program_state, isBaiting, isHooking, isExiting
    running = True
    # ... (khởi tạo biến, tracker, object_detector, special_area_detector,...)
    region = {"top": 120, "left": 975, "width": 135, "height": 430}
    target_click_pos = (1192, 615)
    exit_click_pos = (916, 195)
    lower_fish_color = np.array([0, 0, 245])
    upper_fish_color = np.array([179, 255, 255])
    debug_mode = True
    
    isBaiting.set()
    isHooking.clear()
    isExiting.clear()
    
    # Khởi động luồng lắng nghe phím nhấn 'q'
    kill_thread = threading.Thread(target=f_kill)
    kill_thread.start()    
    
    # Khởi động luồng baiting
    checkBait_thread = threading.Thread(target=f_checkBait, 
                                        args=(running, isBaiting, isHooking, isExiting, target_click_pos),
                                        daemon=True)
    checkBait_thread.start()
    
    # Khởi động luồng hooking
    checkFish_thread = threading.Thread(target=detect_and_click_fish, 
                                        args=(running, isBaiting, isHooking, region, target_click_pos, special_area_path, fish_path, lower_fish_color, upper_fish_color, debug_mode), 
                                        daemon=True)
    checkFish_thread.start()
    
    # Khởi động luồng exiting
    checkResult_thread = threading.Thread(target=f_checkResult, 
                                          args=(running, isHooking, isExiting, exit_click_pos), 
                                          daemon=True)
    checkResult_thread.start()
    
      
    kill_thread.join()  # Đợi thread lắng nghe phím kết thúc
    print("Chương trình đã dừng.")


create_gui()


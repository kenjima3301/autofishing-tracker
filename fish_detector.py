import cv2
import numpy as np
import pyautogui
import keyboard
from tracker import *
from area_detector import *
from mss import mss
import time

def detect_and_click_fish(running, isBaiting, isHooking, region, target_click_pos, 
                          special_area_path, fish_path,
                          lower_fish_color, upper_fish_color,
                          debug_mode):

    # Create tracker object
    tracker = EuclideanDistTracker()
    
    # Object detection from Stable camera
    object_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)
    
    # Khởi tạo SpecialAreaDetector với template
    specialArea = cv2.imread(special_area_path, cv2.IMREAD_COLOR)
    special_area_detector = SpecialAreaDetector(specialArea, max_history=5, similarity_threshold=0.591)
    
    # Khởi tạo mục tiêu cần tracking
    fish = cv2.imread(fish_path, cv2.IMREAD_GRAYSCALE)
    fish_height, fish_width = fish.shape[:2]  # Lấy kích thước template
    
    fish_in_area_frames = 0  # Biến đếm số frame cá ở trong special area
    fish_in_area_timer = 0
    click_delay = 0.025 # Thời gian chờ để bắt đầu đếm frame
    frame_threshold = 1  # Ngưỡng số frame
    
    # Thời gian timeout (tính bằng số lần không tìm thấy special area)
    timeout_duration = 250
    timeout_start = 0  # Lưu thời điểm bắt đầu kiểm tra
    
    with mss() as sct:
        if debug_mode:
            # Tạo cửa sổ hiển thị
            cv2.namedWindow("Mask", cv2.WINDOW_NORMAL)
            cv2.moveWindow("Mask", 100, 100)    # Di chuyển đến vị trí mong muốn
            cv2.setWindowProperty("Mask", cv2.WND_PROP_TOPMOST, 1)
            
            # Tạo cửa sổ hiển thị
            cv2.namedWindow("roi", cv2.WINDOW_NORMAL)
            cv2.moveWindow("roi", 300, 100)    # Di chuyển đến vị trí mong muốn
            cv2.setWindowProperty("roi", cv2.WND_PROP_TOPMOST, 1)
        
    
        while running:
            isHooking.wait()
            start_time = time.time() # Khởi tạo thời gian bắt đầu của mỗi frame
            
            # Chụp màn hình khu vực định sẵn
            screenshot = np.array(sct.grab(region))
            # Đổi từ chế độ màu RGB sang BGR để tương thích với OpenCV
            frame = screenshot
            
            roi = frame[0: 430, 0: 135]
        
            # 0. Detect special area
            special_area_coords = special_area_detector.detect_special_area(roi)
            # print(f"Special area coords: {special_area_coords}")
            if special_area_coords:
                # Nếu tìm thấy special_area, reset thời gian timeout
                timeout_start = 0
                # print(f"timeout_start: {timeout_start}")
                
                x_area, y_area, w_area, h_area = special_area_coords
                cv2.rectangle(frame, (x_area, y_area), (x_area + w_area, y_area + h_area), (0, 0, 255), 2)
                cv2.putText(frame, "Special Area", (x_area, y_area - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)
            
            elif timeout_start >= timeout_duration:
                isHooking.clear()  # Hủy trạng thái hooking
                isBaiting.set()
                # print(f"timeout_start: {timeout_start}")
                # print("Timeout! Không tìm thấy special area trong thời gian cho phép.")
                timeout_start = 0
                continue
            else:
                timeout_start += 1
                # print(f"timeout_start: {timeout_start}")


                
            # 1. Object Detection
            mask_motion = object_detector.apply(roi)
            _, mask_motion = cv2.threshold(mask_motion, 254, 255, cv2.THRESH_BINARY)
            
            # Filtering color
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            mask_color = cv2.inRange(hsv, lower_fish_color, upper_fish_color)
            # Masks combination
            mask = cv2.bitwise_and(mask_motion, mask_color)
            
            # 2. Object Tracking
            if special_area_coords:
                contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                detections = []
                for cnt in contours:
                    # Calculate area and remove small elements
                    area = cv2.contourArea(cnt)
                    if area > 220:
                        #cv2.drawContours(roi, [cnt], -1, (0, 255, 0), 2)
                        x, y, w, h = cv2.boundingRect(cnt)
                        detections.append([x, y, w, h])
            
                    
                boxes_ids = tracker.update(detections)
                for box_id in boxes_ids:
                    x_obj, y_obj, w_obj, h_obj, id = box_id
                    cv2.putText(roi, str(id), (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                    cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 3)
                    
                    # Kiểm tra object có nằm trong special area không
                
                    if (
                        y_obj >= y_area
                        and y_obj + h_obj <= y_area + h_area
                    ):
                        if fish_in_area_timer > click_delay:
                            fish_in_area_frames += 1
                            # print(f"Object {id} đã vào vùng Special Area, frame {fish_in_area_frames}!")    
                        else:
                            fish_in_area_timer += time.time() - start_time    
                                            
                        if fish_in_area_frames >= frame_threshold:
                            # pyautogui.click(1192, 615)
                            keyboard.press_and_release('f')
                            fish_in_area_frames = 0
                            fish_in_area_timer = 0
                    else:
                        fish_in_area_frames = 0
                        fish_in_area_timer = 0
                        
            if debug_mode:
                cv2.imshow("roi", roi)
                cv2.imshow("Mask", mask)        
                
            if cv2.waitKey(30) == 27:  # Phím ESC để thoát
                break
        
        cv2.destroyAllWindows()

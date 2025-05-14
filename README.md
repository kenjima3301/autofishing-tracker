# 🎣 AutoFishing Tracker

Một dự án nhỏ sử dụng Python để tự động theo dõi và thực hiện hành động trong trò chơi câu cá thông qua nhận diện hình ảnh và kỹ thuật object tracking.

## 📹 Video demo: https://tinyurl.com/3h4zkb9b

## 🧠 Mô tả

Dự án mô phỏng một chương trình tự động chơi mini-game câu cá bằng cách:
- Theo dõi các đối tượng trên màn hình (vùng đặc biệt, cá, nút thoát, v.v.)
- Thực hiện hành động click chuột dựa trên trạng thái
- Giao diện người dùng đơn giản bằng Tkinter để chọn chế độ (Day/Night)

Ứng dụng các kỹ thuật:
- **Object tracking** với `EuclideanDistTracker` (custom implementation)
- **Nhận diện ảnh theo khuôn mẫu** (`pyautogui.locateOnScreen`)
- **Tự động hóa thao tác người dùng** (chuột, bàn phím)
- **Xử lý đa luồng** (`threading`) để xử lý các trạng thái song song
- **Xử lý hình ảnh** với OpenCV để phát hiện đối tượng dựa vào màu sắc

## 🛠️ Công nghệ sử dụng

- Python
- OpenCV
- PyAutoGUI
- Tkinter
- NumPy
- Threading (đa luồng)

## 📁 Cấu trúc chính
```
autofishing-tracker/
│
├── tracker.py # Theo dõi đối tượng bằng Euclidean Distance
├── fish_detector.py # Phát hiện cá dựa trên ngưỡng màu HSV
├── area_detector.py # Phát hiện khu vực đặc biệt
├── main.py # Luồng chính điều khiển trạng thái chương trình
├── images/ # Thư mục chứa các ảnh mẫu
├── README.md # Tài liệu mô tả dự án
```

## ⚠️ Lưu ý

- Dự án **chỉ mang mục đích học tập và trình diễn kỹ thuật**.
- Không khuyến khích sử dụng cho mục đích gian lận trong game thực tế.

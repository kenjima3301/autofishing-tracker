import cv2
import numpy as np
import statistics


class SpecialAreaDetector:
    def __init__(self, template, max_history=3, similarity_threshold=0.35):
        """
        Khởi tạo lớp kiểm tra Special Area.
        
        Args:
            template (numpy.ndarray): Ảnh mẫu để phát hiện khu vực đặc biệt.
            max_history (int): Số lượng khung hình giữ lại để tính toán ổn định.
            similarity_threshold (float): Ngưỡng độ tương đồng để xác nhận special area.
        """
        self.template = cv2.GaussianBlur(template, (5, 5), 0)  # Làm mờ template
        self.template_hist = self._compute_histogram(self.template)
        self.template_h, self.template_w = template.shape[:2]
        self.max_history = max_history
        self.similarity_threshold = similarity_threshold
        self.special_area_history = []

    def _compute_histogram(self, image):
        """Tính histogram của ảnh với mask mặc định."""
        hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        cv2.normalize(hist, hist)
        return hist

    def detect_special_area(self, roi):
        """
        Tìm special area trong một ROI.
        
        Args:
            roi (numpy.ndarray): Vùng ảnh (ROI) cần kiểm tra.

        Returns:
            tuple: Tọa độ (x, y, w, h) của vùng special area nếu tìm thấy, None nếu không.
        """
        best_match_coords = None
        max_similarity = 0

        for y in range(0, roi.shape[0] - self.template_h, 20):
            for x in range(0, roi.shape[1] - self.template_w, 20):
                window = roi[y:y + self.template_h, x:x + self.template_w]
                window_blurred = cv2.GaussianBlur(window, (5, 5), 0)
                window_hist = self._compute_histogram(window_blurred)

                # Tính độ tương đồng
                similarity = cv2.compareHist(self.template_hist, window_hist, cv2.HISTCMP_CORREL)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match_coords = (x, y, self.template_w, self.template_h)

        # Lưu lại tọa độ nếu độ tương đồng vượt ngưỡng
        if max_similarity > self.similarity_threshold and best_match_coords:
            self.special_area_history.append(best_match_coords)
            if len(self.special_area_history) > self.max_history:
                self.special_area_history.pop(0)
            return self._get_stable_area()
        return None

    def _get_stable_area(self):
        """Tính tọa độ ổn định của vùng special area dựa trên lịch sử."""
        xs = [coords[0] for coords in self.special_area_history]
        ys = [coords[1] for coords in self.special_area_history]
        ws = [coords[2] for coords in self.special_area_history]
        hs = [coords[3] for coords in self.special_area_history]
        return (int(statistics.mean(xs)), int(statistics.mean(ys)),
                int(statistics.mean(ws)), int(statistics.mean(hs)))

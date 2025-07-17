import cv2
import os
from datetime import datetime
import requests
from yolov8 import YOLOv8

class cctv_surveillence:
    def __init__(self, model_path, capture_dir="captured_images", frame_width=640, frame_height=480, conf_thres=0.5, iou_thres=0.5, bot_token='', chat_id=''):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
        
        self.yolov8_detector = YOLOv8(model_path, conf_thres=conf_thres, iou_thres=iou_thres)
        
        self.capture_dir = capture_dir
        os.makedirs(self.capture_dir, exist_ok=True)
        
        self.detected_objects = {}
        self.frame_count = 0
        
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_photo_to_telegram(self, photo_path, caption=""):
        url = f'https://api.telegram.org/bot{self.bot_token}/sendPhoto'
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': self.chat_id, 'caption': caption}
            response = requests.post(url, files=files, data=data)
        return response

    def process_frame(self, frame):
        boxes, scores, class_ids = self.yolov8_detector(frame)
        current_time = datetime.now()
        new_detected_objects = set()

        for index, box in enumerate(boxes):
            x, y, w, h = box
            box_center = (x + w / 2, y + h / 2)
            new_detected_objects.add(index)

            if index not in self.detected_objects:
                timestamp = current_time.strftime("%Y%m%d_%H%M%S_%f")
                filename = os.path.join(self.capture_dir, f"captured_image_{timestamp}.jpg")
                cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                print(f"Gambar diambil: {filename}")
                self.send_photo_to_telegram(filename, caption="ORANG TERDETEKSI")
                self.detected_objects[index] = current_time

        for index in list(self.detected_objects.keys()):
            if index not in new_detected_objects:
                del self.detected_objects[index]

    def check_capture_signal(self, frame):
        if os.path.exists('capture_signal.txt'):
            current_time = datetime.now()
            timestamp = current_time.strftime("%Y%m%d_%H%M%S_%f")
            filename = os.path.join(self.capture_dir, f"captured_image_{timestamp}.jpg")
            cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            print(f"Gambar diambil: {filename}")
            self.send_photo_to_telegram(filename, caption="KONDISI HALAMAN")
            os.remove('capture_signal.txt')

    def run(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Gagal membaca frame dari webcam.")
                break

            self.frame_count += 1
            if self.frame_count % 5 == 0:
                self.process_frame(frame)

            self.check_capture_signal(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    model_path = r"/home/picam/cctv/yolov8n320.onnx"
    bot_token = 'YOUR_BOT_TOKEN'
    chat_id = 'YOUR_CHAT_ID'
    surveillance_system = Cctv_surveillence(model_path, bot_token=bot_token, chat_id=chat_id)
    surveillance_system.run()

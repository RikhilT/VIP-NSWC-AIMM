import pyzed.sl as sl
import cv2
from ultralytics import YOLO
import numpy as np

# model = YOLO('/home/jetson/Documents/boat/yolov5su.pt')
model = YOLO('/home/jetson/Documents/boat/yolov8n.pt')

def yolo_to_zed_custom_box(frame):
    print("predicting")
    results = model.predict(frame, classes=[0], half=True)  # 39, 67, 73 , imgsz=320
    # print("got predictions")

    custom_object_data = []
    for result in results:
        for box in result.boxes:
            tmp = sl.CustomBoxObjectData()

            tmp.unique_object_id = sl.generate_unique_id()
            tmp.probability = float(box.conf[0])
            tmp.label = int(box.cls[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            tmp.bounding_box_2d = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
            tmp.is_grounded = True  # objects are moving on the floor plane and tracked in 2D only
            custom_object_data.append(tmp)

    return custom_object_data

    # label = f"{model.names[class_id]} {confidence:.2f}"
    # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

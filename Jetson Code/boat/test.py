print("Importing Libraries")
import socket, pickle, struct, cv2
import pyzed.sl as sl
import camera_functions as cf
import time

# Create Camera
print("Creating Camera")
zed = sl.Camera()

init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.AUTO # Use HD720 opr HD1200 video mode, depending on camera type.
init_params.camera_fps = 30  # Set fps at 60
init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
init_params.coordinate_units = sl.UNIT.METER
init_params.sdk_verbose = 1

err = zed.open(init_params)
if err != sl.ERROR_CODE.SUCCESS:
    print("Camera Open : "+repr(err)+". Exit program.")
    exit()

detection_parameters = sl.ObjectDetectionParameters()
detection_parameters.detection_model = sl.OBJECT_DETECTION_MODEL.CUSTOM_BOX_OBJECTS  # Mandatory for this mode
detection_parameters.enable_tracking = True  # Objects will keep the same ID between frames
positional_tracking_parameters = sl.PositionalTrackingParameters()
zed.enable_positional_tracking(positional_tracking_parameters)

zed_error = zed.enable_object_detection(detection_parameters)
if zed_error != sl.ERROR_CODE.SUCCESS:
    print("enable_object_detection", zed_error, "\nExit program.")
    zed.close()
    exit(-1)

image = sl.Mat()
objects = sl.Objects()
runtime_parameters = sl.RuntimeParameters()
obj_runtime_param = sl.ObjectDetectionRuntimeParameters()

# Create Socket
print("Creating Socket")
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ip = '10.42.0.1' # Jetson ip when running JetsonBoat hotspot
port = 54321
server_socket.bind((ip, port))

# Wait until someone connects to the socket
server_socket.listen(5)
print(f"LISTENING AT: {ip}:{port}")

client_socket,addr = server_socket.accept()
print('GOT CONNECTION FROM:',addr)

# JPEG encoding parameters
quality = 60
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]

try: # Just to close the sockets on CRTL-C or client disconnection
    if client_socket:
        while True:
            start = time.time()
            if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
                # get image from left camera and convert to a numpy array
                zed.retrieve_image(image, sl.VIEW.LEFT)
                cvimage = image.get_data()

                # print(cvimage.shape)
                # h, w = cvimage.shape[:2]
                # cvimage = cv2.resize(cvimage, (int(w/2), int(h/2)))
                # print(cvimage.shape)

                custom_object_data = cf.yolo_to_zed_custom_box(cvimage[:, :, :3])
                yolo_time = time.time()
                print(f"Time for Yolo: {yolo_time - start}")
                zed.ingest_custom_box_objects(custom_object_data)
                zed.retrieve_objects(objects, obj_runtime_param)
                zed_time = time.time()
                print(f"Time for ZED: {zed_time - yolo_time}")


                # for obj in objects.object_list:
                #     points = obj.bounding_box_2d.astype(int)
                #     x1, y1 = map(int, points[0])
                #     x3, y3 = map(int, points[2])
                #     print(type(x1))
                #     cv2.rectangle(cvimage, (x1,y1), (x3,y3), (0, 255, 0), 2)

                objects_points = [obj.bounding_box_2d.astype(int) for obj in objects.object_list]
                    
                # encode the image as JPEG to reduce the byte size then pack and send to client
                # print("Encoding Image")
                idk, cvimage = cv2.imencode('.jpg', cvimage, encode_param)
                a = pickle.dumps(cvimage)
                # print(f"image size: {len(a)}")
                message = struct.pack("Q",len(a))+a
                client_socket.sendall(message)

                # print("Encoding obj data")
                a = pickle.dumps(objects_points)
                # print(f"obj data size: {len(a)}")
                message = struct.pack("Q",len(a))+a
                client_socket.sendall(message)

            end = time.time()
            print(f"Loop time: {end - start}")



except Exception as e:
    print(f"Error: {e}")
    pass
finally:
    print("Closing program and sockets")
    client_socket.close()
    server_socket.close()
    zed.close()
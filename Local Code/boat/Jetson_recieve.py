import socket, cv2, pickle, struct
from threading import Thread
import plotting

# create socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting...")
client_socket.connect(('10.42.0.1', 54321))
print("Connected!")

# cv2.startWindowThread()
# cv2.namedWindow("ZED", cv2.WINDOW_NORMAL)
#
# points_plotting_thread = Thread(target=plotting.plot_points3d())
# points_plotting_thread.start()

# setup data variables
data = b""
payload_size = struct.calcsize("Q")
while True:
    ########### IMAGE DATA ###########
    # run until there is enough data to extract the msg size
    while len(data) < payload_size:
        packet = client_socket.recv(4 * 1024)  # 4K
        if not packet: break
        data += packet
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0] # get the message size

    # run until there is enough data to read the full message (image data)
    while len(data) < msg_size:
        data += client_socket.recv(4 * 1024)
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR) # decode the JPEG for viewing

    ########### OBJECT DATA ###########
    # run until there is enough data to extract the msg size
    while len(data) < payload_size:
        packet = client_socket.recv(4 * 1024)  # 4K
        if not packet: break
        data += packet
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0] # get the message size

    # run until there is enough data to read the full message (image data)
    while len(data) < msg_size:
        data += client_socket.recv(4 * 1024)
    obj_data = data[:msg_size]
    data = data[msg_size:]
    objects_points = pickle.loads(obj_data) # get the object data

    ########### PROCESSING ###########

    for points in objects_points:
        x1, y1 = map(int, points[0])
        x3, y3 = map(int, points[2])
        # print(type(x1))
        cv2.rectangle(frame, (x1,y1), (x3,y3), (0, 255, 0), 2)

    # h, w = frame.shape[:2]
    # frame = cv2.resize(frame, (w * 2, h * 2))

    cv2.imshow("ZED", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break


client_socket.close()
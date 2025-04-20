import socket, pickle, struct, cv2
import pyzed.sl as sl


# Create Camera
zed = sl.Camera()
init_params = sl.InitParameters()
err = zed.open(init_params)
if err != sl.ERROR_CODE.SUCCESS:
    print("Camera Open : "+repr(err)+". Exit program.")
    exit()

image = sl.Mat()
runtime_parameters = sl.RuntimeParameters()

# Create Socket
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
quality = 80
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]

try: # Just to close the sockets on CRTL-C or client disconnection
    if client_socket:
        while True:
            if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
                # get image from left camera and convert to a numpy array
                zed.retrieve_image(image, sl.VIEW.LEFT)
                cvimage = image.get_data()

                # encode the image as JPEG to reduce the byte size then pack and send to client
                idk, cvimage = cv2.imencode('.jpg', cvimage, encode_param)
                a = pickle.dumps(cvimage)
                message = struct.pack("Q",len(a))+a
                client_socket.sendall(message)
                # print(len(message))
except:
    pass
finally:
    print("Closing program and sockets")
    client_socket.close()
    server_socket.close()
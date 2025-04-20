import pyzed.sl as sl
import cv2
import camera_functions as cf
from threading import Thread
import plotting


def main():

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

    cv2.startWindowThread()
    cv2.namedWindow("ZED", cv2.WINDOW_NORMAL)

    points_plotting_thread = Thread(target=plotting.plot_points3d())
    points_plotting_thread.start()

    while True:
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image, sl.VIEW.LEFT)
            cvimage = image.get_data()
            custom_object_data = cf.yolo_to_zed_custom_box(cvimage[:, :, :3])
            zed.ingest_custom_box_objects(custom_object_data)
            zed.retrieve_objects(objects, obj_runtime_param)

            plotting.set_points3d(objects)

            for obj in objects.object_list:
                points = obj.bounding_box_2d.astype(int)
                cv2.rectangle(cvimage, points[0], points[2], (0, 255, 0), 2)

            cv2.imshow("ZED", cvimage)
            # timestamp = zed.get_timestamp(sl.TIME_REFERENCE.CURRENT)  # Get the timestamp at the time the image was captured
            # print("Image resolution: {0} x {1} || Image timestamp: {2}\n".format(image.get_width(), image.get_height(), timestamp.get_milliseconds()))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    zed.close()

if __name__ == "__main__":
    main()

import cv2
import yaml
import time

def get_calib_matrices(w=None, h=None, cam=None):
    """
    Given either 1) width, height of camera frame
       or option 2) cam = cv2.VideoCapture object
    Returns calibration matrices as a yaml string
    """
    if cam is not None:
        _, image = cam.read()
        while image is None:
            print("Trying to access given camera...")
            _, image = cam.read()
        h, w = image.shape[:2]
    
    cx = w / 2
    cy = h / 2
    f_l = (w + h) / 2
    
    camera_matrix = [
        [f_l, 0.0, cx],
        [0.0, f_l, cy],
        [0.0, 0.0, 1.0]
    ]
    calib_matrices = {
        "camera_matrix": camera_matrix,
        "dist_coeff": [[0, 0, 0, 0, 0]]
    }
    return yaml.dump(calib_matrices)

def video_to_image(video_dir, image_dir, stride=1):
    """
    Extract frames from a video of an aruco board
    """
    video = cv2.VideoCapture(video_dir)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_stride = int(fps * stride)

    for i in range(9999):
        ret, frame = video.read()
        if not ret: break
        if i % frame_stride == 0:
            cv2.imwrite(f"{image_dir}/frame_{i}.png", 
                frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
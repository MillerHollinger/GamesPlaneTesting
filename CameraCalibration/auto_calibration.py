import yaml

def get_calib_matrices(w, h, mode="yaml"):
    """
    Given the width and height of the camera frame
        # initialize cam = cv2.VideoCapture(0),
        #            h,w = cam.read().shape[:2])
    Returns calib_matrices:
        A) as a dictionary, if mode=="dict"
        B) as a yaml_string if mode=="yaml"
            # result = yaml.safe_load(yaml_string)
    """
    
    cx = w / 2
    cy = h / 2
    f_l = (w + h) / 2
    
    camera_matrix = [
        [f_l, 0.0, cx],
        [0.0, f_l, cy],
        [0.0, 0.0, 1.0]
    ]
    calib_matrices = {
        'camera_matrix': camera_matrix,
        'dist_coeff': [[0, 0, 0, 0, 0]]
    }
    if mode == "dict":
        return calib_matrices
    if mode == "yaml":
        return yaml.dump(calib_matrices)
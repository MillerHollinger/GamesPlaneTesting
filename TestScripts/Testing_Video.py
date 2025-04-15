import cv2
import yaml
import time
import sys
sys.path.append(".")
from Games.DummyGameTTT import *
from CameraCalibration.auto_calibration import *

YAML = "CameraCalibration/good_calibration.yaml"

#ARGUMENT PARSE
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str, default="LIVE",
	help="Path to video. Blank for webcam")
ap.add_argument("-s", "--scale", type=float, default=1.0,
	help="Scale factor s*(x,y) for frames")
ap.add_argument("-d", "--delay", type=int, default=1,
	help="Delay (ms) between frames shown")

args = vars(ap.parse_args())
name = args["video"]
scale= args["scale"]

# CAMERA WINDOW
cv2.namedWindow(name, cv2.WINDOW_NORMAL)

if name == "LIVE":
    print("Accessing live camera...")
    video = cv2.VideoCapture(0)
else:
    print("Processing video " + name)
    video = cv2.VideoCapture(name)

# auto calibration
_, image = video.read()
h, w = image.shape[:2]
yaml_str = get_calib_matrices(w, h, mode="yaml")

# RESCALE CALIB
if scale != 1.0:
    calib = yaml.safe_load(yaml_str)
    
    cam = calib["camera_matrix"]
    cam[0][0] *= scale  # f_x
    cam[1][1] *= scale  # f_y
    cam[0][2] *= scale  # c_x
    cam[1][2] *= scale  # c_y
    yaml_str = yaml.dump(calib)

game = DummyGame(yaml_str)
print(f"Starting instance of {game.name}")

# PROCESS VIDEO
times, ret = [], 1
while ret is not None:
    # If no viable frames in video, ends loop

    start_time = time.time()                # TIMER START
    ret, image = video.read()
    if scale != 1.0:
        image = cv2.resize(image, None, fx=scale, fy=scale)
    
    # If no viable arucos in frame, try again
    try:
        pieces, anchors = game.process_image(image)
        for info in pieces + anchors:
            info.put_summary_graphic(image)
            info.put_bounds(image)
        # print(game.to_board(pieces))
    except Exception:
        print("No viable arucos in frame.")
    
    cv2.imshow(name, image)
    cv2.waitKey(args["delay"])
    times.append(time.time() - start_time)  # TIMER END

# PROCESS STATS
video.release()
cv2.destroyAllWindows()

if len(times) == 0:
    raise Exception("No viable frames in video.")
avg_time = sum(times) / len(times)

print(f"Total time  : {sum(times):.3f} seconds")
print(f"Total frames: {len(times):.3f} frames")
print(f"Average time: {avg_time:.3f} s/frame")
print(f"Average FPS : {1/avg_time:.3f} fps")
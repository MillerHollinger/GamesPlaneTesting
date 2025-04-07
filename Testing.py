import cv2
import yaml
import time
from Games.DummyGame import *

YAML = "josh_calibration.yaml"

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str, required=True,
	help="Path to video with ARUCO tag(s)")
ap.add_argument("-s", "--scale", type=float, default=1.0,
	help="Scale factor s*(x,y) for frames")
ap.add_argument("-d", "--delay", type=int, default=1,
	help="Delay (ms) between frames shown")

args = vars(ap.parse_args())
name = args["video"]
scale= args["scale"]
print("Processing video " + name)

if scale != 1.0:
    with open(YAML, "r") as file:
        calib = yaml.safe_load(file)
    
    cam = calib["camera_matrix"]
    cam[0][0] *= scale  # f_x
    cam[1][1] *= scale  # f_y
    cam[0][2] *= scale  # c_x
    cam[1][2] *= scale  # c_y
    
    YAML = f"scaled_{scale}_{YAML}"
    with open(YAML, "w") as file:
        yaml.dump(calib, file)


game = DummyGame(YAML)
print(f"Starting instance of {game.name}")
cv2.namedWindow(name, cv2.WINDOW_NORMAL)
video = cv2.VideoCapture(name)
times = []

while True:
    start_time = time.time()                # TIMER START
    ret, image = video.read()
    if not ret: break
    if scale != 1.0:
        image = cv2.resize(image, None, fx=scale, fy=scale)

    pieces, anchors = game.process_image(image)
    for info in pieces + anchors:
        info.put_summary_graphic(image)
        info.put_bounds(image)
    # print(game.to_board(pieces))
    
    cv2.imshow(name, image)
    cv2.waitKey(args["delay"])
    times.append(time.time() - start_time)  # TIMER END

video.release()
cv2.destroyAllWindows()

avg_time = sum(times) / len(times)
print(f"Total time  : {sum(times):.3f} secs")
print(f"Total frames: {len(times)} frames")
print(f"Average time: {avg_time:.3f} s/frame")
print(f"Average FPS : {1/avg_time:.3f}")
import cv2

def video_to_image(video_path, out_folder, stride_s=1):
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_stride = int(fps * stride_s)
    frame_n, n = 0, 0

    while True:
        ret, frame = video.read()
        if not ret: break
        if frame_n % frame_stride == 0:
            cv2.imwrite(f"{out_folder}/frame_{n}.png", 
                       frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            n += 1
        frame_n += 1
    video.release()

if __name__ == "__main__":
    video_to_image("0.mov", "aruco_data")
import cv2

def readVideo(videoPath):
    cap = cv2.VideoCapture(videoPath)
    frames=[]
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    return frames

def saveVideo(outputVideoFrames,outputPath):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(outputPath,fourcc,24,(outputVideoFrames[0].shape[1],outputVideoFrames[0].shape[0]))
    for frame in outputVideoFrames:
        out.write(frame)
    out.release()
# Football Computer Vision Project: Football Video Analysis

This program employs computer vision techniques to analyze football videos. It is possible to track players, referees, the ball, and assign teams by color, while also estimating possession metrics. It uses the following technologies: OpenCV for video processing, YOLO (You Only Look Once) for object detection, ByteTrack for object tracking, and Flask for the web interface and API.


https://github.com/user-attachments/assets/53bfe96c-83de-44c4-b9fa-9ee3fa42171c




## Features

Player, Referee, and Ball Detection: Uses the YOLO object detection model to identify and locate players, referees, and the ball in each frame of the video.
Object Tracking: Utilizes ByteTrack to maintain the identities of players, referees, and the ball across video frames, ensuring continuous tracking.
Possession Calculation: Computes possession statistics by determining which team has control of the ball over the duration of the video.
Web Interface: Provides an easy-to-use web interface for uploading videos and retrieving processed results.

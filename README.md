# Football Computer Vision Project: Football Video Analysis

This program employs computer vision techniques to analyze football videos. The program tracks players, referees, the ball, and automatically detects teams by color, while also estimating possession metrics. It uses the following technologies: OpenCV for video processing, YOLO (You Only Look Once) for object detection, ByteTrack for object tracking, and Flask for the web interface and API.



https://github.com/user-attachments/assets/45a4139d-10ee-40f3-bd1b-c84c405c7567



## Features

* Player, Referee, and Ball Detection: Uses a trained YOLO object detection model to identify and locate players, referees, and the ball in each frame of the video.

* Object Tracking: Utilizes ByteTrack to maintain the identities of players, referees, and the ball across video frames.

* Color-Based Team Segmentation: Utilizes K-means clustering to differentiate between two teams based on player colors.
  
* Inertia for Accuracy: Employs a historical record (with inertia) to improve team assignment stability and reduce errors.

* Possession Calculation: Computes possession statistics by determining which team has control of the ball over the duration of the video.

* Web Interface: Provides an easy-to-use web interface for uploading videos and retrieving processed results.

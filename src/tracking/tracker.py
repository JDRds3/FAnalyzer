from ultralytics import YOLO
from drawing import Drawer
from concurrent.futures import ThreadPoolExecutor
import supervision as sv
import pickle
import os
import numpy as np
import cv2
import sys
sys.path.append('../')
from utils import get_center_of_bbox, get_foot_position

class Tracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()
        self.drawer = Drawer()

    def add_position_to_tracks(self, tracks):
        for obj, obj_tracks in tracks.items():
            for frame_num, track in enumerate(obj_tracks):
                for track_id, track_info in track.items():
                    bbox = track_info['bbox']
                    position = get_center_of_bbox(bbox) if obj == 'ball' else get_foot_position(bbox)
                    tracks[obj][frame_num][track_id]['position'] = position

    def detect_frames(self, frames, batch_size=20, conf=0.1):
        detections = []
        for i in range(0, len(frames), batch_size):
            detections_batch = self.model.predict(frames[i:i+batch_size], conf=conf)
            detections.extend(detections_batch)
        return detections

    def get_object_trackings(self, frames, read_from_cache=False, cache_path=None):
        if read_from_cache and cache_path and os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                return pickle.load(f)

        detections = self.detect_frames(frames)

        tracks = { "players": [], "referees": [], "ball": [] }

        for frame_num, detection in enumerate(detections):
            cls_names = detection.names
            cls_names_inv = {v: k for k, v in cls_names.items()}

            detection_supervision = sv.Detections.from_ultralytics(detection)

            for obj_ind, class_id in enumerate(detection_supervision.class_id):
                if cls_names[class_id] == "goalkeeper":
                    detection_supervision.class_id[obj_ind] = cls_names_inv["player"]

            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})

            for frame_detection in detection_with_tracks:
                bbox, cls_id, track_id = frame_detection[0].tolist(), frame_detection[3], frame_detection[4]

                if cls_id == cls_names_inv['player']:
                    tracks["players"][frame_num][track_id] = {"bbox": bbox}
                elif cls_id == cls_names_inv['referee']:
                    tracks["referees"][frame_num][track_id] = {"bbox": bbox}

            for frame_detection in detection_supervision:
                bbox, cls_id = frame_detection[0].tolist(), frame_detection[3]
                if cls_id == cls_names_inv['ball']:
                    tracks["ball"][frame_num][1] = {"bbox": bbox}

        if cache_path:
            with open(cache_path, 'wb') as f:
                pickle.dump(tracks, f)

        return tracks

    def estimate_team_ball_control(self, frame_num, team_ball_control):
        team_ball_control_till_frame = team_ball_control[:frame_num + 1]
        valid_team_ball_control = team_ball_control_till_frame[team_ball_control_till_frame != -1]

        if valid_team_ball_control.size > 0:
            team_1_frames = np.sum(valid_team_ball_control == 1)
            team_2_frames = np.sum(valid_team_ball_control == 2)

            total_frames = team_1_frames + team_2_frames
            team_1_percentage = team_1_frames / total_frames if total_frames > 0 else 0
            team_2_percentage = team_2_frames / total_frames if total_frames > 0 else 0

            last_possessor = valid_team_ball_control[-1]
            possession_adjustment = 0.05

            if last_possessor == 1:
                team_2_percentage = max(0, team_2_percentage - possession_adjustment)
            elif last_possessor == 2:
                team_1_percentage = max(0, team_1_percentage - possession_adjustment)
        else:
            team_1_percentage = team_2_percentage = 0

        return team_1_percentage, team_2_percentage


    def create_annotations(self, video_frames, tracks, team_ball_control, team1color, team2color):
        def process_frame(frame_num):
            frame = video_frames[frame_num].copy()
            player_dict = tracks["players"][frame_num]
            ball_dict = tracks["ball"][frame_num]
            referee_dict = tracks["referees"][frame_num]
            frame = self.drawer.draw_players(frame, player_dict)
            frame = self.drawer.draw_referees(frame, referee_dict)
            frame = self.drawer.draw_ball(frame, ball_dict)
            team_1_percentage, team_2_percentage = self.estimate_team_ball_control(frame_num,team_ball_control)
            frame = self.drawer.draw_team_ball_control(frame, team_1_percentage, team_2_percentage, team1color, team2color)

            return frame

        with ThreadPoolExecutor() as executor:
            output_video_frames = list(executor.map(process_frame, range(len(video_frames))))

        return output_video_frames

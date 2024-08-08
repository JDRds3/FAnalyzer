import cv2
import numpy as np
import sys
sys.path.append('../')
from utils import get_center_of_bbox, get_bbox_width

class Drawer: 
    def __init__(self):
        pass
    
    def draw_ellipse(self, frame, bbox, color, track_id=None):
        y2 = int(bbox[3])
        x_center, _ = get_center_of_bbox(bbox)
        width = get_bbox_width(bbox)
        ellipse_axes = (int(width), int(0.35 * width))

        cv2.ellipse(
            frame,
            center=(x_center, y2),
            axes=ellipse_axes,
            angle=0.0,
            startAngle=-45,
            endAngle=235,
            color=color,
            thickness=2,
            lineType=cv2.LINE_4
        )

        if track_id is not None:
            rectangle_width, rectangle_height = 40, 20
            x1_rect = x_center - rectangle_width // 2
            y1_rect = y2 - rectangle_height // 2 + 15

            cv2.rectangle(frame, (x1_rect, y1_rect), (x1_rect + rectangle_width, y1_rect + rectangle_height), color, cv2.FILLED)

            x1_text = x1_rect + 12 - 10 * (track_id > 99)
            cv2.putText(
                frame,
                f"{track_id}",
                (x1_text, y1_rect + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
            )

        return frame

    def draw_boundingbox(self, frame, bbox, color, track_id=None):
        x1, y1, x2, y2 = map(int, bbox)
        thickness = 2
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

        if track_id is not None:
            label = f"ID: {track_id}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_thickness = 1

            (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
            text_x = x1
            text_y = y1 - 10

            cv2.rectangle(frame, (text_x, text_y - text_height - 10), (text_x + text_width + 5, text_y + 5), color, cv2.FILLED)
            cv2.putText(frame, label, (text_x + 2, text_y - 2), font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

        return frame
    
    def draw_triangle(self, frame, bbox, color):
        y = int(bbox[1])
        x, _ = get_center_of_bbox(bbox)

        triangle_points = np.array([
            [x, y],
            [x - 10, y - 20],
            [x + 10, y - 20],
        ])
        cv2.drawContours(frame, [triangle_points], 0, color, cv2.FILLED)
        cv2.drawContours(frame, [triangle_points], 0, (0, 0, 0), 2)

        return frame
    
    def draw_team_ball_control(self, frame, team_1_percentage, team_2_percentage, team1color, team2color):
        frame_height, frame_width, _ = frame.shape
        rect_width, rect_height = 600, 100
        rect_top_left = (50, frame_height - rect_height - 50)
        rect_bottom_right = (rect_top_left[0] + rect_width, rect_top_left[1] + rect_height)

        overlay = frame.copy()
        cv2.rectangle(overlay, rect_top_left, rect_bottom_right, (255, 255, 255), -1)
        alpha = 0.4
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        bar_width, bar_height = 200, 20
        bar_x = rect_top_left[0] + 20
        bar_y = rect_top_left[1] + 20
        bar_spacing = 30
        
        # Team 1 progress bar
        self._draw_progress_bar(frame, bar_x, bar_y, bar_width, bar_height, team_1_percentage, team1color, "Team 1 Possession", (bar_x + bar_width + 10, bar_y + bar_height - 5))
        
        # Team 2 progress bar
        bar_y2 = bar_y + bar_height + bar_spacing
        self._draw_progress_bar(frame, bar_x, bar_y2, bar_width, bar_height, team_2_percentage, team2color, "Team 2 Possession", (bar_x + bar_width + 10, bar_y2 + bar_height - 5))
        
        return frame
    
    def _draw_progress_bar(self, frame, x, y, width, height, percentage, color, text, text_pos):
        cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 255, 255), -1)
        cv2.rectangle(frame, (x, y), (x + int(width * percentage), y + height), color, -1)
        cv2.putText(frame, f"{text} {percentage * 100:.2f}%", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        
    def draw_players(self, frame, player_dict):
        for track_id, player in player_dict.items():
            color = player.get("team_color", (0, 0, 255))
            frame = self.draw_ellipse(frame, player["bbox"], color, track_id)
            if player.get('has_ball', False):
                frame = self.draw_triangle(frame, player["bbox"], (0, 0, 255))
        return frame

    def draw_referees(self, frame, referee_dict):
        for track_id, referee in referee_dict.items():
            frame = self.draw_boundingbox(frame, referee["bbox"], (245, 66, 66), track_id)
        return frame

    def draw_ball(self, frame, ball_dict):
        for track_id, ball in ball_dict.items():
            frame = self.draw_triangle(frame, ball["bbox"], (0, 255, 0))
        return frame

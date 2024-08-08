
from utils import readVideo,saveVideo
from tracking import Tracker
from team_assignments import TeamAssigner
from player_ball_assigner import PlayerBallAssigner
from player_map import PlayerMap # Future
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
class VideoAnalyzer:
    
    def __init__(self):
        self.video_frames = []
        self.tracker = None
        self.tracks = {}
        self.team_assigner = None
        self.player_assigner = None
        self.team_ball_control = []
        self.output_video_frames = []
    
    def get_video(self,path):
        self.video_frames = readVideo(path)
    
    def setup_tracker(self,model_path,read_from_cache=False):
        self.tracker = Tracker(model_path)
        self.tracks = self.tracker.get_object_trackings(self.video_frames,
                                            read_from_cache=read_from_cache,cache_path='../cached_tracks/track_cache.pkl')
        self.tracker.add_position_to_tracks(self.tracks)
    
    def assign_teams(self):
        self.team_assigner = TeamAssigner()
        self.team_assigner.assign_team_color(self.video_frames[0], self.tracks['players'][0])
        
        for frame_num, player_track in enumerate(self.tracks['players']):
            frame_players = self.tracks['players'][frame_num]
            for player_id, track in player_track.items():
                team = self.team_assigner.get_player_team(self.video_frames[frame_num], track['bbox'], player_id)
                frame_players[player_id]['team'] = team
                frame_players[player_id]['team_color'] = self.team_assigner.team_colors.get(team)
                
    def assign_ball_possesors(self):
        self.player_assigner = PlayerBallAssigner()
        self.team_ball_control = []
        for frame_num, player_track in enumerate(self.tracks['players']):
            frame_players = self.tracks['players'][frame_num]
            ball_bbox = self.tracks['ball'][frame_num].get(1, {}).get('bbox', None)
            if ball_bbox:
                assigned_player = self.player_assigner.assign_ball_to_player(player_track, ball_bbox)
                if assigned_player != -1:
                    frame_players[assigned_player]['has_ball'] = True
                    self.team_ball_control.append(frame_players[assigned_player]['team'])
                else:
                    self.team_ball_control.append(-1)
            else:
                self.team_ball_control.append(-1)
    
        self.team_ball_control = np.array(self.team_ball_control)
        
    def create_output(self,output_path):
        output_video_frames = self.tracker.create_annotations(self.video_frames,self.tracks,self.team_ball_control,self.team_assigner.team1_color,self.team_assigner.team2_color)
        saveVideo(output_video_frames,output_path)
        
                
    
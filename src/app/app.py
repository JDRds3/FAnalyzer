import os
import sys
import logging
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import warnings
warnings.filterwarnings("ignore")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from video_analyzer.video_analyzer import VideoAnalyzer


warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(levelname)s: %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout),  
                              logging.FileHandler('app.log')])

app = Flask(__name__)
CORS(app)
@app.route('/process_video', methods=['POST'])
def process_video():
    video_file = request.files['video']
    model_path = request.form['model_path']
    
    output_name = request.form.get('output_name', 'output_video.mp4')
    if not output_name.lower().endswith('.mp4'):
        output_name += '.mp4'
    
    input_video_path = os.path.join('uploads', video_file.filename)
    print("Received video: ",input_video_path)
    video_file.save(input_video_path)
    
    print("Loading model: ",model_path)
    if not os.path.isfile(model_path):
        return jsonify({"error": f"Model file not found: {model_path}"}), 400
    
    output_dir = os.path.join('output_video',output_name)
    

    video_analyzer = VideoAnalyzer()
    video_analyzer.get_video(input_video_path)
    video_analyzer.setup_tracker(model_path,False)
    video_analyzer.assign_teams()
    video_analyzer.assign_ball_possesors()
    video_analyzer.create_output(output_dir)
    
    print("sending file.........")
        
    return send_file(output_dir, mimetype="video/mp4", as_attachment=True)

@app.route('/get_video/<path:path>', methods=['GET'])
def get_video(path):
    if not path.lower().endswith('.mp4'):
        path += '.mp4'
    return send_from_directory("output_video",path,as_attachment=True,)

@app.route('/models', methods=['GET'])
def list_models():
    models_dir = '../models'
    models = [model for model in os.listdir(models_dir) if model.endswith('.pt')]
    return jsonify(models)


if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('output_video', exist_ok=True)
    app.run()

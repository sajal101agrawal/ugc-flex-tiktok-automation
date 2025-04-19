from TikTokApi import TikTokApi
from flask import Flask, request, jsonify
from main import main

app = Flask(__name__)

# Initialize TikTokApi
# api = TikTokApi.get_instance()

@app.route('/add_comment', methods=['POST'])
def add_comment():
    data = request.get_json()
    video_url = data.get('video_url')
    comment = data.get('comment')

    if not video_url or not comment:
        return jsonify({"error": "videoUrl and comment are required"}), 400

    try:
        main(video_url=video_url, comment=comment)

        return jsonify({"message": "Comment added successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to comment: {e}"}), 500

# @app.route('/reply_comment', methods=['POST'])
# def reply_comment():
#     data = request.get_json()
#     video_url = data.get('videoUrl')
#     comment = data.get('comment')
#     reply = data.get('replyComment')

#     if not video_url or not comment or not reply:
#         return jsonify({"error": "videoUrl, comment, and replyComment are required"}), 400

#     comments = video_comments.get(video_url, [])
    
#     for c in comments:
#         if c["comment"] == comment:
#             c["replies"].append(reply)
#             return jsonify({"message": "Reply added successfully"}), 200

#     return jsonify({"error": "Comment not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)

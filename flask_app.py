from flask import Flask, request, jsonify
from main import main

app = Flask(__name__)

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


@app.route('/reply_comment', methods=['POST'])
def reply_comment():
    data = request.get_json()
    video_url = data.get('video_url')
    comment = data.get('comment')
    reply = data.get('reply_comment')

    if not video_url or not comment or not reply:
        return jsonify({"error": "video Url, comment, and reply Comment are required"}), 400

    try:
        main(video_url=video_url, comment=comment, reply=reply)

        return jsonify({"message": "Comment added successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to comment: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True)

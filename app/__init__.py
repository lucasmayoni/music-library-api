from flask import Flask

app = Flask(__name__)


from app.resources.song_resource import song_api

app.register_blueprint(song_api)

with app.app_context():
    app.run(debug=True)

from functools import wraps
from flask import Blueprint, request, jsonify
from app.model.song_list import SongList, ListNotFoundException
from flask_restful import marshal_with

song_api = Blueprint('song_api', __name__)


def authenticate(func):
    @wraps(func)
    def validate_token(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Request is unauthorized'}), 401
        return func(*args, **kwargs)

    return validate_token


@song_api.route('/list', methods=['POST'])
@authenticate
def create_song_list():
    list_data = request.get_json()
    try:
        SongList.create_song_list(list_data)
        return {'message': 'Song List created Successfully!'}, 201
    except Exception as e:
        return {'message': str(e)}, 400


@song_api.route('/list/<string:list_id>/song/add', methods=['PUT'])
@authenticate
def add_song_to_list(list_id: str):
    song_data = request.get_json()
    try:
        SongList.add_song_to_list(song_data, list_id)
        return {'message': f'Song Added to list {list_id} Successfully!'}, 201
    except ListNotFoundException:
        return {'message': f'List {list_id} not found'}, 404
    except Exception as e:
        return {'message': str(e)}, 400


@song_api.route('/list/<string:list_id>/song/remove', methods=['PUT'])
@authenticate
def remove_song_from_list(list_id: str):
    song_data = request.get_json()
    try:
        SongList.remove_song_from_list(song_data, list_id)
        return {'message': f'Song removed from list {list_id} Successfully!'}, 410
    except ListNotFoundException:
        return {'message': f'List {list_id} not found'}, 404
    except Exception as e:
        return {'message': str(e)}, 400


@song_api.route('/list/search', methods=['GET'])
@authenticate
def find_list_with_song():
    title = request.args.get('song_title')
    artist = request.args.get('artist')
    album = request.args.get('album')

    try:
        song_lists = SongList.search_songs(title, artist, album)
        if song_lists:
            return song_lists, 200
        return {'message': 'No list found'}, 404
    except Exception as e:
        return {'message': str(e)}, 400


@song_api.route('/list/<string:list_id>', methods=['DELETE'])
@authenticate
def remove_list(list_id: str):
    try:
        SongList.remove_list(list_id)
        return {'message': 'Song List removed Successfully!'}, 410
    except ListNotFoundException:
        return {'message': f'List {list_id} not found'}, 404
    except Exception as e:
        return {'message': str(e)}, 400

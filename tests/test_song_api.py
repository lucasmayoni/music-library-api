import json

import pytest
from app import app
from unittest.mock import MagicMock

from app.model.song_list import ListNotFoundException


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def headers():
    return {
        'Authorization': 'Bearer 123',
        'Content-type': 'application/json'
    }


@pytest.fixture
def mock_data():
    return {

        'id': '1234456abc',
        'name': 'lista nombre',
        'songs': [
            {
                'title': 'cancion titulo',
                'artist': 'cancion artista',
                'album': 'cancion album'
            }
        ]

    }


def test_fails_when_no_authorization(client, mock_data):
    response = client.post('/list', data=json.dumps(mock_data))
    assert response.status_code == 401
    assert response.json == {'error': 'Request is unauthorized'}


def test_add_song_list(client, mock_data, headers, mocker):
    mock_create_song_list = mocker.patch('app.model.song_list.SongList.create_song_list')
    mock_create_song_list.return_value = None

    response = client.post('/list', data=json.dumps(mock_data), headers=headers)
    assert response.status_code == 201
    assert response.json == {'message': 'Song List created Successfully!'}

    mock_create_song_list.assert_called_once_with(mock_data)


def test_add_song_to_list_not_exists(client, headers, mocker):
    mock_add_song_to_list = mocker.patch('app.model.song_list.SongList.add_song_to_list')
    mock_add_song_to_list.side_effect = ListNotFoundException("List not found")

    song = {
        'title': 'Song Title',
        'artist': 'Artist',
        'album': 'Album'
    }
    response = client.put('/list/1234456abc/song/add', data=json.dumps(song), headers=headers)

    assert response.status_code == 404
    assert response.json == {'message': f'List 1234456abc not found'}

    mock_add_song_to_list.assert_called_once_with(song, '1234456abc')


def test_add_song_to_list(client, headers, mocker):
    mock_add_song_to_list = mocker.patch('app.model.song_list.SongList.add_song_to_list')
    mock_add_song_to_list.return_value = None

    song = {
        'title': 'Song Title',
        'artist': 'Artist',
        'album': 'Album'
    }
    response = client.put('/list/1234456abc/song/add', data=json.dumps(song), headers=headers)

    assert response.status_code == 201
    assert response.json == {'message': f'Song Added to list 1234456abc Successfully!'}

    mock_add_song_to_list.assert_called_once_with(song, '1234456abc')


def test_remove_song_from_list_not_exist(client, headers, mocker):
    mock_remove_song_from_list = mocker.patch('app.model.song_list.SongList.remove_song_from_list')
    mock_remove_song_from_list.side_effect = ListNotFoundException("List not found")
    song = {
        'title': 'Song Title',
        'artist': 'Artist',
        'album': 'Album'
    }
    response = client.put('/list/1234456abc/song/remove', data=json.dumps(song), headers=headers)
    assert response.status_code == 404
    assert response.json == {'message': f'List 1234456abc not found'}

    mock_remove_song_from_list.assert_called_once_with(song, '1234456abc')


def test_remove_song_from_list(client, headers, mocker):
    mock_remove_song_from_list = mocker.patch('app.model.song_list.SongList.remove_song_from_list')
    mock_remove_song_from_list.return_value = None
    song = {
        'title': 'Song Title',
        'artist': 'Artist',
        'album': 'Album'
    }
    response = client.put('/list/1234456abc/song/remove', data=json.dumps(song), headers=headers)
    assert response.status_code == 410
    assert response.json == {'message': f'Song removed from list 1234456abc Successfully!'}

    mock_remove_song_from_list.assert_called_once_with(song, '1234456abc')


def test_remove_list(client, headers, mocker):
    mock_remove_list = mocker.patch('app.model.song_list.SongList.remove_list')
    mock_remove_list.return_value = None
    response = client.delete('/list/1234456abc', headers=headers)

    assert response.status_code == 410
    assert response.json == {'message': 'Song List removed Successfully!'}

    mock_remove_list.assert_called_once_with('1234456abc')


def test_remove_list_not_exists(client, headers, mocker):
    mock_remove_list = mocker.patch('app.model.song_list.SongList.remove_list')
    mock_remove_list.side_effect = ListNotFoundException("List not found")
    response = client.delete('/list/1234456abc', headers=headers)
    assert response.status_code == 404
    assert response.json == {'message': f'List 1234456abc not found'}

    mock_remove_list.assert_called_once_with('1234456abc')


def test_search_list_with_song(client, headers, mocker):
    mock_search_songs = mocker.patch('app.model.song_list.SongList.search_songs')
    mock_search_songs.return_value = [{'list_id': '123', 'name': 'List Name'}]
    form_data = {'song_title': 'cancion titulo',
                 'artist': 'cancion artista',
                 'album': 'cancion album'}
    response = client.get('/list/search', headers=headers, query_string=form_data)
    assert response.status_code == 200
    assert response.json == [{'list_id': '123', 'name': 'List Name'}]
    mock_search_songs.assert_called_once_with('cancion titulo', 'cancion artista', 'cancion album')


def test_search_list_with_song_not_found(client, headers, mocker):
    mock_search_songs = mocker.patch('app.model.song_list.SongList.search_songs')
    mock_search_songs.return_value = []
    form_data = {'song_title': 'cancion titulo'}
    response = client.get('/list/search', headers=headers, query_string=form_data)
    assert response.status_code == 404
    assert response.json == {'message': 'No list found'}
    mock_search_songs.assert_called_once_with('cancion titulo', None, None)


def test_methods_throws_exception(client, headers, mocker, mock_data):
    mock_create_song_list = mocker.patch('app.model.song_list.SongList.create_song_list')
    mock_create_song_list.side_effect = Exception("Exception")

    response = client.post('/list', data=json.dumps(mock_data), headers=headers)
    assert response.status_code == 400
    assert response.json == {'message': 'Exception'}

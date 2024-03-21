import json
import pytest

from app.model.song_list import SongList, ListNotFoundException


@pytest.fixture
def mock_file_path(tmp_path):
    return tmp_path / 'test_song.json'


@pytest.fixture()
def mocked_list_data():
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


@pytest.fixture
def mock_data():
    return {
        'lists': [
            {
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
        ]
    }


def test_save_to_file(mock_data, mock_file_path):
    song_list = SongList()
    song_list.SONG_PATH_FILE = str(mock_file_path)
    song_list.save_to_file(mock_data)

    assert mock_file_path.exists()


def test_get_from_file(mocker, tmp_path):
    file_path = tmp_path / 'test_song.json'
    with open(file_path, 'w') as f:
        json.dump({'lists': [{'id': '123'}]}, f)

    mocker.patch.object(SongList, 'SONG_PATH_FILE', str(file_path))
    song_list = SongList()
    data = song_list.get_from_file()

    assert data == {'lists': [{'id': '123'}]}


def test_get_from_file_file_is_empty(tmp_path, mocker):
    file_path = tmp_path / 'test_song.json'
    file_path.touch()
    mocker.patch.object(SongList, 'SONG_PATH_FILE', str(file_path))
    song_list = SongList()
    data = song_list.get_from_file()
    assert data == {}


def test_get_from_file_data_is_no_dict(tmp_path, mocker):
    file_path = tmp_path / 'test_song.json'
    with open(file_path, 'w') as f:
        f.write('NOT DICT OR JSON')

    mocker.patch.object(SongList, 'SONG_PATH_FILE', str(file_path))
    song_list = SongList()
    data = song_list.get_from_file()
    assert data == {}


def test_get_from_file_not_exists(mocker):
    mocker.patch.object(SongList, 'SONG_PATH_FILE', '')
    song_list = SongList()
    data = song_list.get_from_file()
    assert data == {}


def test_create_song_list(mocker, mocked_list_data):
    mock_get_from_file = mocker.patch('app.model.song_list.SongList.get_from_file')
    mock_get_from_file.return_value = None

    mock_save_to_file = mocker.patch('app.model.song_list.SongList.save_to_file')
    mock_save_to_file.return_value = None

    song_list = SongList()

    song_list.create_song_list(mocked_list_data)
    mock_get_from_file.assert_called_once()
    expected_json_data = {'lists': [mocked_list_data]}
    mock_save_to_file.assert_called_once_with(expected_json_data)


def test_add_song_to_list(mocker):
    mock_get_from_file = mocker.patch('app.model.song_list.SongList.get_from_file')
    mock_get_from_file.return_value = {'lists': [{'id': '123', 'name': 'name', 'songs': []}]}

    mock_get_list_by_id = mocker.patch('app.model.song_list.SongList.get_list_by_id',
                                       values='123')
    mock_get_list_by_id.return_value = {'id': '123', 'name': 'name', 'songs': []}

    mock_save_to_file = mocker.patch('app.model.song_list.SongList.save_to_file')
    mock_save_to_file.return_value = None

    song = {
        'title': 'cancion titulo',
        'artist': 'cancion artista',
        'album': 'cancion album'
    }

    song_list = SongList()
    song_list.add_song_to_list(song, '123')
    mock_get_from_file.assert_called_once()
    expected_json_data = {'lists': [{'id': '123', 'name': 'name', 'songs': [song]}]}
    mock_save_to_file.assert_called_once_with(expected_json_data)


def test_add_song_list_not_found(mocker):
    mock_get_list_by_id = mocker.patch('app.model.song_list.SongList.get_list_by_id', return_value=[])
    mock_get_list_by_id.side_effect = ListNotFoundException()

    song = {
        'title': 'cancion titulo',
        'artist': 'cancion artista',
        'album': 'cancion album'
    }

    song_list = SongList()
    try:
        song_list.add_song_to_list(song, '123')
        assert False, "ListNotFoundException not raised"
    except ListNotFoundException:
        assert True


def test_remove_song_from_list(mocker, mock_data):
    mock_get_from_file = mocker.patch('app.model.song_list.SongList.get_from_file')
    mock_get_from_file.return_value = mock_data

    song = {
        'title': 'cancion titulo',
        'artist': 'cancion artista',
        'album': 'cancion album'
    }

    mock_get_list_by_id = mocker.patch('app.model.song_list.SongList.get_list_by_id')

    mock_get_list_by_id.return_value = {'id': '123', 'name': 'name', 'songs': [song]}

    mock_save_to_file = mocker.patch('app.model.song_list.SongList.save_to_file')
    mock_save_to_file.return_value = None

    song_list = SongList()
    song_list.remove_song_from_list(song, '1234456abc')
    mock_get_from_file.assert_called_once()
    expected_json_data = {'lists': [{'id': '1234456abc', 'name': 'lista nombre', 'songs': []}]}
    mock_save_to_file.assert_called_once_with(expected_json_data)


def test_remove_list_not_found(mocker):
    mock_get_list_by_id = mocker.patch('app.model.song_list.SongList.get_list_by_id', return_value=[])
    mock_get_list_by_id.side_effect = ListNotFoundException()

    song = {
        'title': 'cancion titulo',
        'artist': 'cancion artista',
        'album': 'cancion album'
    }

    song_list = SongList()
    try:
        song_list.remove_song_from_list(song, '123')
        assert False, "ListNotFoundException not raised"
    except ListNotFoundException:
        assert True


def test_remove_list(mock_data, mocker):
    mock_get_from_file = mocker.patch('app.model.song_list.SongList.get_from_file')
    mock_get_from_file.return_value = mock_data

    mock_save_to_file = mocker.patch('app.model.song_list.SongList.save_to_file')
    mock_save_to_file.return_value = None

    song_list = SongList()
    song_list.remove_list('1234456abc')
    mock_get_from_file.assert_called_once()
    expected_json_data = {'lists': []}
    mock_save_to_file.assert_called_once_with(expected_json_data)


def test_search_songs(mocker, mock_data, mocked_list_data):
    mock_get_from_file = mocker.patch('app.model.song_list.SongList.get_from_file')
    mock_get_from_file.return_value = mock_data

    mock_matched_songs = mocker.patch('app.model.song_list.SongList._matched_songs')
    mock_matched_songs.return_value = True

    title = 'cancion titulo'
    song_list = SongList()
    found_list = song_list.search_songs(title, None, None)
    mock_get_from_file.assert_called_once()
    expected_json_data = mocked_list_data
    assert [expected_json_data] == found_list


def test_search_songs_not_found(mocker, mock_data):
    mock_get_from_file = mocker.patch('app.model.song_list.SongList.get_from_file')
    mock_get_from_file.return_value = mock_data

    mock_matched_songs = mocker.patch('app.model.song_list.SongList._matched_songs')
    mock_matched_songs.return_value = False

    title = 'cancion titulo'
    song_list = SongList()
    found_list = song_list.search_songs(title, None, None)
    mock_get_from_file.assert_called_once()
    assert [] == found_list


def test_get_list_by_id(mocker, mock_data, mocked_list_data):
    mock_get_from_file = mocker.patch('app.model.song_list.SongList.get_from_file')
    mock_get_from_file.return_value = mock_data

    song_list = SongList()
    found_list = song_list.get_list_by_id("1234456abc")
    mock_get_from_file.assert_called_once()
    expected_json_data = mocked_list_data
    assert [expected_json_data] == found_list

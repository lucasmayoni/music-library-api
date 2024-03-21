import json
import os


class ListNotFoundException(Exception):
    pass


class SongList:
    SONG_PATH_FILE = 'app/mock/song_lists.json'

    @classmethod
    def save_to_file(cls, data):
        """ Save the song list to a file
        :param data: dictionary
        :return:
        """
        os.makedirs(os.path.dirname(cls.SONG_PATH_FILE), exist_ok=True)
        with open(cls.SONG_PATH_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def get_from_file(cls):
        """ Get the song list from a file
        :return: dictionary
        """
        if os.path.exists(cls.SONG_PATH_FILE):
            with open(cls.SONG_PATH_FILE, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    return {}
            if not data or not isinstance(data, dict):
                return {}
            else:
                return data
        else:
            return {}

    @classmethod
    def create_song_list(cls, data):
        """ Create a list of songs
        :param data: dictionary
        :return:
        """
        json_data = cls.get_from_file()
        if not json_data:
            # creates the empty structure once
            json_data = {'lists': []}
        json_data.get('lists').append(data)
        cls.save_to_file(json_data)

    @classmethod
    def add_song_to_list(cls, song, list_id):
        """ Add a song to a list
        :param song: dictionary
        :param list_id: string
        :return:
        """
        if not cls.get_list_by_id(list_id):
            raise ListNotFoundException()
        json_data = cls.get_from_file()
        for list_data in json_data.get("lists", []):
            if list_data.get('id') == list_id:
                list_data['songs'].append(song)
                break

        cls.save_to_file(json_data)

    @classmethod
    def remove_song_from_list(cls, song, list_id):
        """ Remove a song from a list
        :param song: dictionary
        :param list_id: string
        :return:
        """
        if not cls.get_list_by_id(list_id):
            raise ListNotFoundException()
        json_data = cls.get_from_file()
        for list_data in json_data.get("lists", []):
            if list_data.get('id') == list_id:
                index_to_remove = list_data['songs'].index(song)
                list_data['songs'].pop(index_to_remove)
                break

        cls.save_to_file(json_data)

    @classmethod
    def get_list_by_id(cls, list_id):
        """ Get a list of songs from a list
        :param list_id: string
        :return: dictionary
        """
        json_data = cls.get_from_file()
        list_data = [slist for slist in json_data.get("lists", []) if slist['id'] == list_id]
        return list_data

    @classmethod
    def remove_list(cls, list_id):
        """ Remove a list
        :param list_id: string
        :return:
        """
        json_data = cls.get_from_file()
        for idx, item in enumerate(json_data["lists"]):
            if item["id"] == list_id:
                del json_data["lists"][idx]
                break
        cls.save_to_file(json_data)

    @classmethod
    def search_songs(cls, title, artist, album):
        """ Search for a list of songs
        :param title: string
        :param artist: string
        :param album: string
        :return: list
        """
        json_data = cls.get_from_file()
        list_found = []
        for song_list in json_data.get("lists", []):
            for song in song_list.get("songs", []):
                if cls._matched_songs(song, title, artist, album):
                    list_found.append(song_list)
                    break

        return list_found

    @staticmethod
    def _matched_songs(song, title, artist, album):
        return (not title or title.lower() in song.get('title', '').lower()) and \
            (not artist or artist.lower() in song.get('artist', '').lower()) and \
            (not album or album.lower() in song.get('album', '').lower())

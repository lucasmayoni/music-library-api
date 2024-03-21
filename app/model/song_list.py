import json
import os


class ListNotFoundException(Exception):
    pass


class SongList:
    SONG_PATH_FILE = 'app/mock/song_lists.json'

    def save_to_file(self, data):
        """ Save the song list to a file
        :param data: dictionary
        :return:
        """
        os.makedirs(os.path.dirname(self.SONG_PATH_FILE), exist_ok=True)
        with open(self.SONG_PATH_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def get_from_file(self):
        """ Get the song list from a file
        :return: dictionary
        """
        if os.path.exists(self.SONG_PATH_FILE):
            with open(self.SONG_PATH_FILE, 'r') as f:
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

    def create_song_list(self, data):
        """ Create a list of songs
        :param data: dictionary
        :return:
        """
        json_data = self.get_from_file()
        if not json_data:
            # creates the empty structure once
            json_data = {'lists': []}
        json_data.get('lists').append(data)
        self.save_to_file(json_data)

    def add_song_to_list(self, song, list_id):
        """ Add a song to a list
        :param song: dictionary
        :param list_id: string
        :return:
        """
        if not self.get_list_by_id(list_id):
            raise ListNotFoundException()
        json_data = self.get_from_file()
        for list_data in json_data.get("lists", []):
            if list_data.get('id') == list_id:
                list_data['songs'].append(song)
                break

        self.save_to_file(json_data)

    def remove_song_from_list(self, song, list_id):
        """ Remove a song from a list
        :param song: dictionary
        :param list_id: string
        :return:
        """
        if not self.get_list_by_id(list_id):
            raise ListNotFoundException()
        json_data = self.get_from_file()
        for list_data in json_data.get("lists", []):
            if list_data.get('id') == list_id:
                index_to_remove = list_data['songs'].index(song)
                list_data['songs'].pop(index_to_remove)
                break

        self.save_to_file(json_data)

    def get_list_by_id(self, list_id):
        """ Get a list of songs from a list
        :param list_id: string
        :return: dictionary
        """
        json_data = self.get_from_file()
        list_data = [slist for slist in json_data.get("lists", []) if slist['id'] == list_id]
        return list_data

    def remove_list(self, list_id):
        """ Remove a list
        :param list_id: string
        :return:
        """
        json_data = self.get_from_file()
        for idx, item in enumerate(json_data["lists"]):
            if item["id"] == list_id:
                del json_data["lists"][idx]
                break
        self.save_to_file(json_data)

    def search_songs(self, title, artist, album):
        """ Search for a list of songs
        :param title: string
        :param artist: string
        :param album: string
        :return: list
        """
        json_data = self.get_from_file()
        list_found = []
        for song_list in json_data.get("lists", []):
            for song in song_list.get("songs", []):
                if self._matched_songs(song, title, artist, album):
                    list_found.append(song_list)
                    break

        return list_found

    @staticmethod
    def _matched_songs(song, title, artist, album):
        return (not title or title.lower() in song.get('title', '').lower()) and \
            (not artist or artist.lower() in song.get('artist', '').lower()) and \
            (not album or album.lower() in song.get('album', '').lower())

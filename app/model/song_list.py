import json
import os


class SongList:
    SONG_PATH_FILE = 'app/mock/song_lists.json'

    def save_to_file(self, data):
        os.makedirs(os.path.dirname(self.SONG_PATH_FILE), exist_ok=True)
        with open(self.SONG_PATH_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def get_from_file(self):
        if os.path.exists(self.SONG_PATH_FILE):
            with open(self.SONG_PATH_FILE, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    # Handle the case when the file is empty or contains invalid JSON
                    return {}
            if not data or not isinstance(data, dict):
                return {}
            else:
                return data
        else:
            return {}

    def create_song_list(self, data):
        json_data = self.get_from_file()
        if not json_data:
            # creates the empty structure once
            json_data = {'lists': []}
        json_data.get('lists').append(data)
        self.save_to_file(json_data)

    def add_song_to_list(self, song, list_id):
        json_data = self.get_from_file()
        for list_data in json_data.get("lists", []):
            if list_data.get('id') == list_id:
                list_data['songs'].append(song)
                break

        self.save_to_file(json_data)

    def remove_song_from_list(self, song, list_id):
        json_data = self.get_from_file()
        for list_data in json_data.get("lists", []):
            if list_data.get('id') == list_id:
                index_to_remove = list_data['songs'].index(song)
                list_data['songs'].pop(index_to_remove)
                break

        self.save_to_file(json_data)

    def get_list_by_id(self, list_id):
        json_data = self.get_from_file()
        list_data = [slist for slist in json_data if slist['id'] == list_id]
        return list_data

    def remove_list(self, list_id):
        json_data = self.get_from_file()
        for idx, item in enumerate(json_data["lists"]):
            # Check if the current list item's id matches the given list_id
            if item["id"] == list_id:
                # Remove the list item from the "lists" array
                del json_data["lists"][idx]
                break  # Return True to indicate successful deletion
        self.save_to_file(json_data)

import googlemaps
import sys
import threading
from typing import Final
from cefpython3 import cefpython as cef
import endecoder as ed

class MapLoader:
    CAHCING_MAP_HTML_PATH: Final = "caching_map.html"

    def __init__(self):
        self.__maps = None
        self.__map_html = None
        self.__browser_thread = None
        self.__browser = None

        # key_file = open("api_keys/google_key")
        # self.__api_key = key_file.readline()
        # key_file.close()
        #
        # map_html_file = open("base_map_html.txt", encoding='UTF-8')
        # self.__map_html = map_html_file.read().replace("@WRITE_KEY", self.__api_key)
        #
        # self.__browser_thread = threading.Thread(target=self.__show_map, args=(frame,))
        # self.__browser_thread.daemon = True
        #
        # self.__browser = None

    def connect_api(self, api_key_file):
        try:
            key_file = open(api_key_file, 'rb')
            encrypted_key = key_file.read()
        except:
            return False

        try:
            key = ed.decrypt_key(encrypted_key).decode("ascii")
        except:
            return False

        try:
            self.__maps = googlemaps.Client(key=key)

            map_html_file = open("base_map_html.txt", encoding='UTF-8')
            self.__map_html = map_html_file.read().replace("@WRITE_KEY", key)
        except KeyError:
            return False

        return True

    def attach_to_frame(self, frame):
        self.__browser_thread = threading.Thread(target=self.__show_map, args=(frame,))
        self.__browser_thread.daemon = True
        self.__browser = None

    def find_lat_lng(self, address):
        locations = self.__maps.geocode(address)

        return locations[0]['geometry']['location'] if locations else None

    def show_map(self, lat_lng):
        map_html_file = open(self.CAHCING_MAP_HTML_PATH, 'w', encoding='UTF-8')
        map_html = self.__map_html.replace("@WRITE_LAT", str(lat_lng["lat"])).replace("@WRITE_LNG", str(lat_lng["lng"]))
        map_html_file.write(map_html)
        map_html_file.close()

        if self.__browser_thread.is_alive():
            self.__browser.Reload()
        else:
            self.__browser_thread.start()

    def __show_map(self, frame):
        sys.excepthook = cef.ExceptHook

        cef.Initialize()
        window_info = cef.WindowInfo(frame.winfo_id())
        window_info.SetAsChild(frame.winfo_id(), [0, 0, frame.cget("width"), frame.cget("height")])
        self.__browser = cef.CreateBrowserSync(window_info, url='file:///' + self.CAHCING_MAP_HTML_PATH)

        cef.MessageLoop()

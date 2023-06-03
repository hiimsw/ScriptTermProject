import googlemaps
import sys
import threading
from typing import Final
from cefpython3 import cefpython as cef


class MapLoader:
    CAHCING_MAP_HTML_PATH: Final = "data/caching_map.html"

    def __init__(self, frame):
        self.__maps = None
        self.__map_base_html = None

        self.__browser = None
        self.__browser_thread = threading.Thread(target=self.__show_map, args=(frame,))
        self.__browser_thread.daemon = True

    def connect_api(self, key):
        try:
            self.__maps = googlemaps.Client(key=key)

            map_base_html_file = open("data/map_base_html.txt", encoding='UTF-8')
            self.__map_base_html = map_base_html_file.read().replace("@WRITE_KEY", key)
        except:
            return False

        return True

    def find_lat_lng(self, address):
        locations = self.__maps.geocode(address)

        return locations[0]['geometry']['location'] if locations else None

    def show_map(self, tourist_spot, lat_lng):
        assert self.is_api_connected(), "api가 연결되지 않는 상태에서 이 함수를 호출할 수 없습니다."

        map_html_file = open(self.CAHCING_MAP_HTML_PATH, 'w', encoding='UTF-8')
        map_html = self.__map_base_html
        map_html = map_html.replace("@MARK", tourist_spot)
        map_html = map_html.replace("@WRITE_LAT", str(lat_lng["lat"]))
        map_html = map_html.replace("@WRITE_LNG", str(lat_lng["lng"]))
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

    def is_api_connected(self):
        return self.__maps is not None

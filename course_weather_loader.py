import re
from typing import Final
import requests
import xml.etree.ElementTree as ET
from enum import Enum

class WeatherSearchResult(Enum):
    SUCCESS = 0
    NOT_FOUND = 1

class CourseWeatherLoader:
    URL: Final = 'https://apis.data.go.kr/1360000/TourStnInfoService1/getTourStnVilageFcst1'
    NUM_OF_ROWS: Final = 100

    def __init__(self):
        self.__key = None
        self.__courses = {}

        course_root = ET.parse("course.xml")
        for item in course_root.iter("item"):
            course_id = int(item.findtext("id"))
            self.__courses[course_id] = []
            self.__courses[course_id].append(item.findtext("name"))

            tourist_spots = item.findall("tourist_spot")
            for tourist_spot in tourist_spots:
                self.__courses[course_id].append(tourist_spot.text)

    def connect_api(self, key):
        query_params = {"ServiceKey": key,
                        "pageNo": 1,
                        "numOfRows": 1,
                        "CURRENT_DATE": "2023010100",  # 정보 조회를 위해 날짜를 조정합니다.
                        "HOUR": 0,
                        "COURSE_ID": 1}

        response = requests.get(self.URL, params=query_params)

        if not ("SERVICE_KEY_IS_NOT_REGISTERED_ERROR" in response.text):
            self.__key = key
            return True
        else:
            return False

    def find_tourist_spots(self, spot_keyword):
        found_tourist_spots = []

        courses = list(self.__courses.items())
        for course in courses:
            course: tuple = tuple(course)
            tourist_spots = course[1]
            for i in range(1, len(tourist_spots)):
                tourist_spot = tourist_spots[i]
                tourist_spot = tourist_spot[tourist_spot.find(')') + 1:]  # 지역명을 제외합니다. ex) (포항)호미곶 -> 호미곶
                if spot_keyword in tourist_spot:
                    found_tourist_spots.append((course[0], tourist_spots[i]))

        return found_tourist_spots

    def find_tourist_spots_by_local_name(self, local_name):
        found_tourist_spots = []

        courses = list(self.__courses.items())
        for course in courses:
            course: tuple = tuple(course)
            tourist_spots = course[1]
            for i in range(1, len(tourist_spots)):
                tourist_spot = tourist_spots[i]
                if local_name == tourist_spot[1:tourist_spot.find(')')]:
                    found_tourist_spots.append((course[0], tourist_spot))

        return found_tourist_spots

    def find_recommand_course(self, course_id):
        assert course_id in self.__courses, "존재하지 않는 코스 ID입니다."
        tourist_spots = self.__courses[course_id]
        return tourist_spots[:]

    def search_weather(self, course_id, tourist_spot, date):
        assert self.is_api_connected(), "api가 연결되지 않는 상태에서 이 함수를 호출할 수 없습니다."

        searched_weather = {}
        total_page_count = 0
        page_no = 1

        query_params = {"ServiceKey": self.__key,
                        "pageNo": page_no,
                        "numOfRows": self.NUM_OF_ROWS,
                        "CURRENT_DATE": date[:-2] + "00",  # 정보 조회를 위해 날짜를 조정합니다.
                        "HOUR": 0,
                        "COURSE_ID": course_id}

        while True:
            response = requests.get(self.URL, params=query_params)

            if "DB_ERROR" in response.text:
                return WeatherSearchResult.NOT_FOUND, None

            root = ET.fromstring(response.text)
            body = root.find("body")
            items = body.find("items")

            for e in items:
                if tourist_spot != e.findtext("spotName"):
                    continue

                tm = re.split(r"[-: ]", e.findtext("tm"))  # 시간
                tm = "".join(tm[:-1])
                if tm != date:
                    continue

                th3 = e.findtext("th3")  # 기온
                wd = e.findtext("wd")  # 풍향(deg)
                ws = e.findtext("ws")  # 풍속(m/s)
                sky = e.findtext("sky")  # 하늘상태(1:맑음, 3:구름많음, 4:흐림)
                rhm = e.findtext("rhm")  # 습도(%)
                pop = e.findtext("pop")  # 강수 확률(%)
                searched_weather.update({"th3": th3, "wd": wd, "ws": ws, "sky": sky, "rhm": rhm, "pop": pop})

                return WeatherSearchResult.SUCCESS, searched_weather

            total_page_count += self.NUM_OF_ROWS
            if total_page_count >= int(body.findtext("totalCount")):
                break

            query_params["pageNo"] += 1

        return WeatherSearchResult.NOT_FOUND, None

    def is_api_connected(self):
        return self.__key is not None

if __name__ == '__main__':
    cwl = CourseWeatherLoader()
    cwl.search_weather(123, "(포항)호미곶해맞이광장/국립등대박물관", "2023052403")

import requests
import xml.etree.ElementTree as ET


class CourseWeatherLoader:
    def __init__(self):
        self.__courses = {}

        course_root = ET.parse("course.xml")
        for item in course_root.iter("item"):
            course_id = int(item.findtext("id"))
            self.__courses[course_id] = []
            self.__courses[course_id].append(item.findtext("name"))

            courses = item.findall("course")
            for course in courses:
                self.__courses[course_id].append(course.text)

    def find_course_names_by_local_name(self, local_name):
        found_course_names = []

        for course_list in self.__courses.values():
            for i, course_name in enumerate(course_list):
                # 코스명은 지역명 검색에서 제외합니다.
                if i == 0:
                    continue

                if local_name == course_name[1:course_name.find(')')]:
                    found_course_names.append(course_name)

        return found_course_names

    def run(self):
        pass

        # url = 'https://apis.data.go.kr/1360000/TourStnInfoService1/getTourStnVilageFcst1'
        # service_key = "e/rfOsl+wjVcIDYyMVTu3nk5mQgunZXDeAEfr2gvG8+xq/VGPFSUThoVw1YJmmLy2wzC7OUCqQyt3MoUZicA/Q=="
        # page_no = 1
        # num_of_rows = 10
        # current_date = 2023051800
        # hour = 0
        # course_id = 1
        #
        # query_params = {"ServiceKey": service_key,
        #                 "pageNo": page_no,
        #                 "numOfRows": num_of_rows,
        #                 "CURRENT_DATE": current_date,
        #                 "HOUR": hour,
        #                 "COURSE_ID": course_id}
        #
        # response = requests.get(url, params=query_params)
        # print(response.text)
        #
        # root = ET.fromstring(response.text)
        #
        # elements = root.find("body").find("items")
        # for e in elements:
        #     th3 = e.findtext("th3")
        #     wd = e.findtext("wd")  # 풍향(deg)
        #     ws = e.findtext("ws")  # 풍속(m/s)
        #     sky = e.findtext("sky")  # 하늘상태(1:맑음, 3:구름많음, 4:흐림)
        #     rhm = e.findtext("rhm")  # 습도(%)
        #     pop = e.findtext("pop")  # 강수 확률(%)

if __name__ == '__main__':
    cwl = CourseWeatherLoader()
    cwl.run()

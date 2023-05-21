import requests
import xml.etree.ElementTree as ET


class CourseWeatherLoader:
    def __init__(self):
        pass

    def run(self):
        url = 'https://apis.data.go.kr/1360000/TourStnInfoService1/getTourStnVilageFcst1'
        service_key = "e/rfOsl+wjVcIDYyMVTu3nk5mQgunZXDeAEfr2gvG8+xq/VGPFSUThoVw1YJmmLy2wzC7OUCqQyt3MoUZicA/Q=="
        page_no = 1
        num_of_rows = 10
        current_date = 2023052000
        hour = 0
        course_id = 1

        query_params = {"ServiceKey": service_key,
                        "pageNo": page_no,
                        "numOfRows": num_of_rows,
                        "CURRENT_DATE": current_date,
                        "HOUR": hour,
                        "COURSE_ID": course_id}

        response = requests.get(url, params=query_params)
        print(response.text)

        root = ET.fromstring(response.text)

        elements = root.find("body").find("items")
        for e in elements:
            th3 = e.findtext("th3")
            wd = e.findtext("wd")
            ws = e.findtext("ws")
            sky = e.findtext("sky")
            rhm = e.findtext("rhm")
            pop = e.findtext("pop")
            print(th3)

if __name__ == '__main__':
    cwl = CourseWeatherLoader()
    cwl.run()

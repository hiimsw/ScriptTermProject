import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
from course_weather_loader import CourseWeatherLoader
from map_loader import MapLoader


class Core:
    def __init__(self):
        self.__app = None
        self.__basic_font = None
        self.__search_frame = None
        self.__search_menu = None
        self.__search_entry = None
        self.__search_button = None
        self.__searched_keyword = []
        self.__selected_keyword_button_index = 0
        self.__year_entry = None
        self.__month_entry = None
        self.__day_entry = None
        self.__time_entry = None
        self.__date_search_button = None
        self.__search_result_frame = None
        self.__recommand_course_frame = None
        self.__recommand_tourist_spot_buttons = []
        self.__selected_tourist_spot_button_index = 0

        self.__selected_tourist_spot_course_id = 0
        self.__cw_loader = None
        self.__map_loader = None

    def run(self):
        self.__cw_loader = CourseWeatherLoader()
        self.__initialize_gui()
        self.__app.mainloop()

    def __initialize_gui(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")

        self.__app = ctk.CTk()
        self.__app.geometry("890x550")
        self.__app.title("Travel & Weather")
        self.__app.grid_rowconfigure(0, weight=1)

        self.__basic_font = ctk.CTkFont(family="맑은 고딕", size=12)

        # region 검색 프레임을 정의합니다.
        self.__search_frame = ctk.CTkFrame(master=self.__app, fg_color='transparent', corner_radius=0)
        self.__search_frame.grid(row=0, column=0, padx=(10, 0), pady=(20, 20), rowspan=6, sticky="nsew")
        self.__search_frame.grid_rowconfigure(4, weight=1)

        self.__search_menu = ctk.CTkOptionMenu(self.__search_frame,
                                               values=["지역명", "관광지명", "시군구"],
                                               font=self.__basic_font,
                                               height=20,
                                               dropdown_font=self.__basic_font,
                                               corner_radius=0)
        self.__search_menu.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        self.__search_entry = ctk.CTkEntry(self.__search_frame, font=self.__basic_font, corner_radius=0)
        self.__search_entry.grid(row=1, column=0, padx=(0, 0), pady=(5, 0), sticky="nsew")

        self.__search_button = ctk.CTkButton(self.__search_frame,
                                             font=self.__basic_font,
                                             text="키워드 검색",
                                             width=30,
                                             height=20,
                                             corner_radius=0,
                                             command=self.__on_keyword_searched)
        self.__search_button.grid(row=2, column=0, pady=(5, 0), sticky="nsew")
        # endregion

        # 검색 결과 프레임을 정의합니다.
        self.__create_search_result_frame()

        # region 추천 코스 프레임을 정의합니다.
        self.__recommand_course_frame = ctk.CTkScrollableFrame(master=self.__search_frame,
                                                               label_font=self.__basic_font,
                                                               label_text="추천 코스",
                                                               corner_radius=5)
        self.__recommand_course_frame.grid(row=4, column=0, pady=(10, 0), sticky="nsew")
        self.__recommand_course_frame.grid_columnconfigure(0, weight=1)
        # endregion

        # region 날씨 프레임을 정의합니다.
        weather_frame = ctk.CTkFrame(master=self.__app, width=250)
        weather_frame.grid(row=0, column=1, padx=(10, 0), pady=(20, 20), sticky="nsew")
        weather_frame.grid_rowconfigure(2, weight=1)

        date_frame = ctk.CTkFrame(master=weather_frame)
        date_frame.grid(row=0, column=0, sticky="nsew")

        years = [str(2000 + i) for i in range(23, 18, -1)]
        self.__year_entry = ctk.CTkOptionMenu(date_frame,
                                              values=years,
                                              font=self.__basic_font,
                                              width=65,
                                              height=20,
                                              dropdown_font=self.__basic_font,
                                              corner_radius=0)
        self.__year_entry.grid(row=0, column=0, stick="nsew")

        months = [f"{i:02}" for i in range(1, 13)]
        self.__month_entry = ctk.CTkOptionMenu(date_frame,
                                               values=months,
                                               font=self.__basic_font,
                                               width=65,
                                               height=20,
                                               dropdown_font=self.__basic_font,
                                               corner_radius=0)
        self.__month_entry.grid(row=0, column=1, stick="nsew")

        days = [f"{i:02}" for i in range(1, 32)]
        self.__day_entry = ctk.CTkOptionMenu(date_frame,
                                             values=days,
                                             font=self.__basic_font,
                                             width=65,
                                             height=20,
                                             dropdown_font=self.__basic_font,
                                             corner_radius=0)
        self.__day_entry.grid(row=0, column=2, stick="nsew")

        times = [f"{i:02}:00" for i in range(0, 22, 3)]
        self.__time_entry = ctk.CTkOptionMenu(date_frame,
                                              values=times,
                                              font=self.__basic_font,
                                              width=65,
                                              height=20,
                                              dropdown_font=self.__basic_font,
                                              corner_radius=0)
        self.__time_entry.grid(row=0, column=3, stick="nsew")

        self.__date_search_button = ctk.CTkButton(master=date_frame,
                                                  font=self.__basic_font,
                                                  text="날짜 선택",
                                                  width=65,
                                                  height=20,
                                                  corner_radius=0,
                                                  command=self.__on_weather_selected)
        self.__date_search_button.grid(row=0, column=4, stick="nsew")

        weather_info_frame = ctk.CTkFrame(master=weather_frame, fg_color="transparent")
        weather_info_frame.grid(row=1, column=0, pady=(20, 0), sticky="nsew")
        weather_info_frame.grid_rowconfigure(1, minsize=200)

        temperature_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="기온")
        temperature_label.grid(row=0, column=0, padx=(20, 0), stick="nsw")

        wind_direction_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="풍향")
        wind_direction_label.grid(row=0, column=1, padx=(100, 0), stick="nsew")

        wind_speed_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="풍속")
        wind_speed_label.grid(row=0, column=2, padx=(90, 0), stick="nsew")

        sky_state_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="하늘상태")
        sky_state_label.grid(row=2, column=0, padx=(10, 0), stick="nsew")

        humidity_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="습도")
        humidity_label.grid(row=2, column=1, padx=(100, 0), stick='nsew')

        rainfall_probability = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="강수확률")
        rainfall_probability.grid(row=2, column=2, padx=(80, 0), stick='nsew')

        weather_details_button = ctk.CTkButton(weather_frame,
                                               font=self.__basic_font,
                                               text="상세보기",
                                               width=10,
                                               height=15,
                                               corner_radius=5)
        weather_details_button.grid(row=3, column=0, padx=(0, 0), pady=(0, 15))
        # endregion

        # region 지도 프레임을 정의합니다
        map_frame = tk.Frame(master=self.__app, width=300, height=200, bg='#E5E5E5')
        map_frame.grid(row=0, column=2, padx=(10, 0), sticky="ew")
        map_frame.grid_rowconfigure(0, weight=1)

        self.__map_loader = MapLoader(map_frame)
        # endregion

    def __create_search_result_frame(self):
        self.__search_result_frame = ctk.CTkScrollableFrame(master=self.__search_frame,
                                                            label_font=self.__basic_font,
                                                            label_text="검색 결과",
                                                            corner_radius=5)
        self.__search_result_frame.grid(row=3, column=0, pady=(10, 0), sticky="nsew")
        self.__search_result_frame.grid_columnconfigure(0, weight=1)

    def __on_keyword_searched(self):
        search_keyword = self.__search_entry.get()
        if search_keyword == '':
            return

        search_type = self.__search_menu.get()

        for button in self.__recommand_tourist_spot_buttons:
            button.destroy()
        self.__recommand_tourist_spot_buttons.clear()

        if search_type == '지역명':
            for button in self.__searched_keyword:
                button.destroy()
            self.__searched_keyword.clear()

            # 스크롤 뷰 상태를 초기화하기 위해 검색 결과 프레임을 재생성합니다.
            self.__search_result_frame.destroy()
            self.__create_search_result_frame()

            tourist_spots = self.__cw_loader.find_tourist_spots_by_local_name(search_keyword)
            for i, tourist_spot in enumerate(tourist_spots):
                button = ctk.CTkButton(master=self.__search_result_frame,
                                       font=self.__basic_font,
                                       text=tourist_spot[1],
                                       fg_color='transparent',
                                       text_color="black",
                                       text_color_disabled="black",
                                       corner_radius=0,
                                       command=lambda x=i, y=tourist_spot[0]: self.__on_keyword_selected(x, y))
                button.grid(row=i, column=0, padx=(5, 0))
                self.__searched_keyword.append(button)
        elif search_type == '관광지명':
            pass
        elif search_type == "시군구":
            pass
        else:
            assert False, "지원하지 않는 검색 유형입니다."

        self.__selected_keyword_button_index = 0

    def __on_keyword_selected(self, selected_button_index, course_id):
        prev_button = self.__searched_keyword[self.__selected_keyword_button_index]
        prev_button.configure(state="normal", fg_color="transparent")

        selected_button = self.__searched_keyword[selected_button_index]
        selected_button.configure(state="disabled", fg_color=['#3a7ebf', '#1f538d'])
        selected_tourist_spot = selected_button.cget("text")
        recommand_course = self.__cw_loader.find_recommand_course(course_id)

        for button in self.__recommand_tourist_spot_buttons:
            button.destroy()
        self.__recommand_tourist_spot_buttons.clear()
        self.__selected_tourist_spot_button_index = 0

        for i in range(1, len(recommand_course)):
            tourist_spot = recommand_course[i]
            button_index = i - 1
            button = ctk.CTkButton(master=self.__recommand_course_frame,
                                   font=self.__basic_font,
                                   text=tourist_spot,
                                   fg_color='transparent',
                                   text_color="black",
                                   text_color_disabled="black",
                                   corner_radius=0,
                                   command=lambda x=button_index: self.__on_tourist_spot_selected(x))
            button.grid(row=i, column=0)
            self.__recommand_tourist_spot_buttons.append(button)

            if tourist_spot == selected_tourist_spot:
                button.configure(state="disabled", fg_color=['#3a7ebf', '#1f538d'])
                self.__on_tourist_spot_selected(button_index)
                self.__selected_tourist_spot_button_index = button_index

        self.__selected_keyword_button_index = selected_button_index
        self.__selected_tourist_spot_course_id = course_id

    def __on_tourist_spot_selected(self, selected_button_index):
        prev_button = self.__recommand_tourist_spot_buttons[self.__selected_tourist_spot_button_index]
        prev_button.configure(state="normal", fg_color="transparent")

        selected_button = self.__recommand_tourist_spot_buttons[selected_button_index]
        selected_button.configure(state="disabled", fg_color=['#3a7ebf', '#1f538d'])

        lat_lng = self.__map_loader.find_lat_lng(selected_button.cget("text"))
        if lat_lng:
            self.__map_loader.load_map(lat_lng)
        else:
            print("해당 관광지의 좌표를 알 수 없습니다.")

        self.__selected_tourist_spot_button_index = selected_button_index

    def __on_weather_selected(self):
        assert self.__selected_tourist_spot_course_id > 0, "관광지를 선택해 주세요."

        year = self.__year_entry.get()
        month = self.__month_entry.get()
        day = self.__day_entry.get()
        time = self.__time_entry.get().split(':')[0]
        date = year + month + day + time

        tourist_spot = self.__recommand_tourist_spot_buttons[self.__selected_tourist_spot_button_index].cget("text")
        searched_weather = self.__cw_loader.search_weather(self.__selected_tourist_spot_course_id,
                                                           tourist_spot,
                                                           date)

        if searched_weather is not None:
            print(searched_weather)
        else:
            # HACK: 텍스트로 표시하자.
            print("지정한 지역과 날짜에 대한 날씨 정보가 조회되지 않습니다.")


if __name__ == '__main__':
    core = Core()
    core.run()

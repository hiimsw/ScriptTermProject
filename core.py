import tkinter
import customtkinter as ctk


class Core:
    def __init__(self):
        self.__app = None

        self.__basic_font = None
        self.__search_menu = None
        self.__search_entry = None
        self.__searched_locations = []
        self.__selected_location_button_index = 0

        self.__year_entry = None
        self.__month_entry = None
        self.__day_entry = None
        self.__time_entry = None

    def run(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")

        self.__app = ctk.CTk()
        self.__app.geometry("860x550")
        self.__app.title("Travel & Weather")
        self.__app.grid_rowconfigure(0, weight=1)

        self.__basic_font = ctk.CTkFont(family="맑은 고딕", size=12)

        # region 검색 프레임을 정의합니다.
        search_frame = ctk.CTkFrame(master=self.__app,
                                    fg_color='transparent',
                                    corner_radius=0)
        search_frame.grid(row=0, column=0, padx=(10, 0), pady=(20, 20), rowspan=6, sticky="nsew")
        search_frame.grid_rowconfigure(5, weight=1)

        self.__search_menu = ctk.CTkOptionMenu(search_frame,
                                               values=["지역명", "관광지명", "시군구"],
                                               font=self.__basic_font,
                                               height=20,
                                               dropdown_font=self.__basic_font,
                                               corner_radius=0)
        self.__search_menu.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        self.__search_entry = ctk.CTkEntry(search_frame, font=self.__basic_font, corner_radius=0)
        self.__search_entry.grid(row=1, column=0, padx=(0, 0), pady=(5, 0), sticky="nsew")

        search_button = ctk.CTkButton(search_frame,
                                      font=self.__basic_font,
                                      text="검색",
                                      width=30,
                                      height=15,
                                      corner_radius=0,
                                      command=self.__search_keyword)
        search_button.grid(row=2, column=0, padx=(0, 0), pady=(5, 0), sticky="nsew")
        # endregion

        # region 검색 결과 프레임을 정의합니다.
        search_result_frame = ctk.CTkScrollableFrame(master=search_frame,
                                                     height=150,
                                                     label_font=self.__basic_font,
                                                     label_text="검색 결과",
                                                     corner_radius=5)
        search_result_frame.grid(row=3, column=0, pady=(10, 0), sticky="nsew")
        search_result_frame.grid_columnconfigure(0, weight=1)

        for i in range(100):
            button = ctk.CTkButton(master=search_result_frame,
                                   font=self.__basic_font,
                                   text=f"CTkSwitch {i}",
                                   width=search_frame.cget("width"),
                                   fg_color='transparent',
                                   text_color="black",
                                   text_color_disabled="black",
                                   corner_radius=0,
                                   command=lambda x=i: self.__on_location_selected(x))
            button.grid(row=i, column=0, padx=(5, 0))

            self.__searched_locations.append(button)
        # endregion

        # region 추천 코스 프레임을 정의합니다.
        course_frame = ctk.CTkFrame(master=search_frame
                                    , corner_radius=5)
        course_frame.grid(row=5, column=0, pady=(10, 0), sticky="nsew")
        course_frame.grid_columnconfigure(0, weight=1)

        course_label = ctk.CTkLabel(master=course_frame,
                                    font=self.__basic_font,
                                    text="코스",
                                    bg_color=search_result_frame.cget("label_fg_color"),
                                    corner_radius=10)
        course_label.grid(row=0, column=0, padx=(5, 5), pady=(5, 0), sticky="nsew")

        a = ctk.CTkLabel(master=course_frame,
                         font=self.__basic_font,
                         text="포항")
        a.grid(row=1, column=0, pady=(5, 0))

        n = ctk.CTkLabel(master=course_frame,
                         font=self.__basic_font,
                         text="포항")
        n.grid(row=2, column=0)
        # endregion

        # region 날씨 프레임을 정의합니다.
        weather_frame = ctk.CTkFrame(master=self.__app, width=250)
        weather_frame.grid(row=0, column=1, padx=(10, 0), pady=(20, 20), rowspan=1, sticky="nsew")
        weather_frame.grid_rowconfigure(1, minsize=30)
        weather_frame.grid_rowconfigure(3, minsize=150)
        weather_frame.grid_rowconfigure(5, weight=1)

        years = [str(2000 + i) for i in range(23, -1, -1)]
        self.__year_entry = ctk.CTkOptionMenu(weather_frame,
                                              values=years,
                                              font=self.__basic_font,
                                              width=100,
                                              height=20,
                                              dropdown_font=self.__basic_font,
                                              corner_radius=0,
                                              command=self.__on_date_changed)
        self.__year_entry.grid(row=0, column=0, stick="nsew")

        months = [str(i) for i in range(1, 13)]
        self.__month_entry = ctk.CTkOptionMenu(weather_frame,
                                               values=months,
                                               font=self.__basic_font,
                                               width=100,
                                               height=20,
                                               dropdown_font=self.__basic_font,
                                               corner_radius=0,
                                               command=self.__on_date_changed)
        self.__month_entry.grid(row=0, column=1, stick="nsew")

        days = [str(i) for i in range(1, 32)]
        self.__day_entry = ctk.CTkOptionMenu(weather_frame,
                                             values=days,
                                             font=self.__basic_font,
                                             width=100,
                                             height=20,
                                             dropdown_font=self.__basic_font,
                                             corner_radius=0,
                                             command=self.__on_date_changed)
        self.__day_entry.grid(row=0, column=2, stick="nsew")

        temperature_label = ctk.CTkLabel(master=weather_frame,
                                         font=self.__basic_font,
                                         text="기온")
        temperature_label.grid(row=2, column=0, stick="nsew")

        wind_direction_label = ctk.CTkLabel(master=weather_frame,
                                            font=self.__basic_font,
                                            text="풍향")
        wind_direction_label.grid(row=2, column=1, stick="nsew")

        wind_speed_label = ctk.CTkLabel(master=weather_frame,
                                        font=self.__basic_font,
                                        text="풍속")
        wind_speed_label.grid(row=2, column=2, stick="nsew")

        sky_state_label = ctk.CTkLabel(master=weather_frame,
                                       font=self.__basic_font,
                                       text="하늘상태")
        sky_state_label.grid(row=4, column=0, stick="nsew")

        humidity_label = ctk.CTkLabel(master=weather_frame,
                                      font=self.__basic_font,
                                      text="습도")
        humidity_label.grid(row=4, column=1, stick='nsew')

        rainfall_probability = ctk.CTkLabel(master=weather_frame,
                                            font=self.__basic_font,
                                            text="강수확률")
        rainfall_probability.grid(row=4, column=2, stick='nsew')

        weather_details_button = ctk.CTkButton(weather_frame,
                                               font=self.__basic_font,
                                               text="상세보기",
                                               width=10,
                                               height=15,
                                               corner_radius=5,
                                               command=self.__search_keyword)
        weather_details_button.grid(row=6, column=1, padx=(0, 0), pady=(0, 15))
        # endregion

        # region 지도 프레임을 정의합니다
        map_frame = ctk.CTkFrame(master=self.__app,
                                 width=300)
        map_frame.grid(row=0, column=2, padx=(10, 0), pady=(100, 100), sticky="nsew")
        map_frame.grid_rowconfigure(0, weight=1)
        # endregion

        self.__app.mainloop()

    def __search_keyword(self):
        search_type = self.__search_menu.get()
        search_keyword = self.__search_entry.get()

        if search_type == '지역명':
            pass
        elif search_type == '관광지명':
            pass
        elif search_type == "시군구":
            pass
        else:
            assert (False, "지원하지 않는 검색 유형입니다.")

        print(search_type + search_keyword)

    def __on_location_selected(self, button_index):
        prev_button = self.__searched_locations[self.__selected_location_button_index]
        prev_button.configure(state="normal", fg_color="transparent")

        button = self.__searched_locations[button_index]
        button.configure(state="disabled", fg_color=['#3a7ebf', '#1f538d'])

        self.__selected_location_button_index = button_index

    def __on_date_changed(self, value):
        pass


if __name__ == '__main__':
    core = Core()
    core.run()

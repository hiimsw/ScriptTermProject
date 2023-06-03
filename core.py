import tkinter as tk
import customtkinter as ctk
from course_weather_loader import CourseWeatherLoader, WeatherSearchResult
from map_loader import MapLoader
from PIL import Image
import endecoder as ed


class Core:
    def __init__(self):
        self.__app = None
        self.__current_frame = None
        self.__main_frame = None
        self.__option_frame = None
        self.__basic_font = None
        self.__basic_font_color = None
        self.__weather_frame = None
        self.__weather_details_frame = None
        self.__current_weather_frame = None
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
        self.__temperature_label = None
        self.__wind_direction_label = None
        self.__wind_speed_label = None
        self.__sky_state_label = None
        self.__humidity_label = None
        self.__rainfall_probability = None
        self.__main_frame_message_label = None
        self.__weather_graphs = []
        self.__weather_graph_value_labels = []

        self.__google_api_key_label = None
        self.__google_api_key_entry = None
        self.__data_api_key_label = None
        self.__data_api_key_entry = None
        self.__option_frame_message_label = None

        self.__selected_tourist_spot_course_id = 0
        self.__cw_loader = None
        self.__map_loader = None

        self.__weather_infos = [{} for _ in range(3)]
        self.__message_label_show_remaining_time = 0.0

    def run(self):
        self.__initialize()
        self.__update()
        self.__app.mainloop()

    def __update(self):
        if self.__message_label_show_remaining_time > 0.0:
            self.__message_label_show_remaining_time -= 30

            if self.__message_label_show_remaining_time <= 0.0:
                self.__message_label_show_remaining_time = 0.0
                self.__print_message("", 0.0)

        if self.__current_weather_frame == self.__weather_details_frame:
            weather_element_names = ["th3", "wd", "ws", "sky", "rhm", "pop"]
            max_weather_elements = [0.0 for _ in range(len(weather_element_names))]

            # 각 날씨 요소의 최대값을 구합니다.
            for weather_info in self.__weather_infos:
                if len(weather_info) == 0:
                    continue

                for j, weather_element_name in enumerate(weather_element_names):
                    max_weather_elements[j] = max(max_weather_elements[j], float(weather_info[weather_element_name]))

            # 각 날씨 요소를 그래프에 반영합니다.
            for i, weather_info in enumerate(self.__weather_infos):
                if len(weather_info) == 0:
                    continue

                for j, weather_element_name in enumerate(weather_element_names):
                    graph_index = i + (j * 3)
                    element_value = weather_info[weather_element_name]

                    if max_weather_elements[j] != 0.0:
                        cur_value = self.__weather_graphs[graph_index].get()
                        to_value = float(element_value) / max_weather_elements[j]
                        self.__weather_graphs[graph_index].set(self.__lerp(cur_value, to_value, 0.35))
                        self.__weather_graph_value_labels[graph_index].configure(text=str(element_value))
                    else:
                        self.__weather_graphs[graph_index].set(0.01)
                        self.__weather_graph_value_labels[graph_index].configure(text=str(element_value))

        self.__app.after(30, self.__update)

    def __initialize(self):
        self.__cw_loader = CourseWeatherLoader()

        decrypted_key = self.__load_key("data")
        if decrypted_key != '':
            self.__cw_loader.connect_api(decrypted_key)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")

        self.__app = ctk.CTk()
        self.__app.geometry("890x550")
        self.__app.resizable(False, False)
        self.__app.title("Travel & Weather")
        self.__basic_font = ctk.CTkFont(family="맑은 고딕", size=12)
        self.__basic_font_color = ['gray14', 'gray84']

        self.__initialize_main_frame()
        self.__initialize_option_frame()
        self.__current_frame = self.__main_frame

    def __initialize_main_frame(self):
        self.__main_frame = ctk.CTkFrame(master=self.__app, fg_color="transparent")
        self.__main_frame.grid_rowconfigure(0, weight=1)
        self.__main_frame.pack(fill="both", expand=True)

        # region 검색 프레임을 정의합니다.
        self.__search_frame = ctk.CTkFrame(master=self.__main_frame, fg_color='transparent', corner_radius=0)
        self.__search_frame.grid(row=0, column=0, padx=(10, 0), pady=(20, 30), rowspan=6, sticky="nsew")
        self.__search_frame.grid_rowconfigure(4, weight=1)

        self.__search_menu = ctk.CTkOptionMenu(self.__search_frame,
                                               values=["지역명", "관광지명"],
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

        self.__create_search_result_frame()

        self.__recommand_course_frame = ctk.CTkScrollableFrame(master=self.__search_frame,
                                                               label_font=self.__basic_font,
                                                               label_text="추천 코스",
                                                               corner_radius=5)
        self.__recommand_course_frame.grid(row=4, column=0, pady=(10, 0), sticky="nsew")
        self.__recommand_course_frame.grid_columnconfigure(0, weight=1)
        # endregion

        # region 날씨 프레임을 정의합니다.
        self.__weather_frame = ctk.CTkFrame(master=self.__main_frame)
        self.__weather_frame.grid(row=0, column=1, padx=(10, 0), pady=(20, 30), sticky="nsew")
        self.__weather_frame.grid_rowconfigure(2, weight=1)

        self.__weather_details_frame = ctk.CTkFrame(master=self.__main_frame)
        self.__weather_details_frame.grid_columnconfigure(0, minsize=325)
        self.__weather_details_frame.grid_rowconfigure(2, weight=1)

        date_frame = ctk.CTkFrame(master=self.__weather_frame)
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

        weather_info_frame = ctk.CTkFrame(master=self.__weather_frame, fg_color="transparent")
        weather_info_frame.grid(row=1, column=0, pady=(20, 0), sticky="nsew")
        weather_info_frame.grid_rowconfigure(3, minsize=100)

        temperature_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="기온")
        temperature_label.grid(row=0, column=0, padx=(10, 0), stick="nsew")

        wind_direction_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="풍향")
        wind_direction_label.grid(row=0, column=1, padx=(80, 0), stick="nsew")

        wind_speed_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="풍속")
        wind_speed_label.grid(row=0, column=2, padx=(90, 0), stick="nsew")

        sky_state_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="하늘상태")
        sky_state_label.grid(row=4, column=0, padx=(10, 0), stick="nsew")

        humidity_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="습도")
        humidity_label.grid(row=4, column=1, padx=(80, 0), stick='nsew')

        rainfall_probability = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="강수확률")
        rainfall_probability.grid(row=4, column=2, padx=(80, 0), stick='nsew')

        image_0 = ctk.CTkImage(Image.open("assets/0.png"), size=(15, 36))
        image_0_label = ctk.CTkLabel(master=weather_info_frame, text='', image=image_0)
        image_0_label.grid(row=1, column=0, padx=(10, 0), stick='nsew')

        image_1 = ctk.CTkImage(Image.open("assets/1.png"), size=(39, 18))
        image_1_label = ctk.CTkLabel(master=weather_info_frame, text='', image=image_1)
        image_1_label.grid(row=1, column=1, padx=(80, 0), stick='nsew')

        image_2 = ctk.CTkImage(Image.open("assets/2.png"), size=(34, 32))
        image_2_label = ctk.CTkLabel(master=weather_info_frame, text='', image=image_2)
        image_2_label.grid(row=1, column=2, padx=(87, 0), stick='nsew')

        image_3 = ctk.CTkImage(Image.open("assets/3.png"), size=(45, 45))
        image_3_label = ctk.CTkLabel(master=weather_info_frame, text='', image=image_3)
        image_3_label.grid(row=5, column=0, padx=(10, 0), stick='nsew')

        image_4 = ctk.CTkImage(Image.open("assets/4.png"), size=(15, 22))
        image_4_label = ctk.CTkLabel(master=weather_info_frame, text='', image=image_4)
        image_4_label.grid(row=5, column=1, padx=(83, 0), stick='nsew')

        image_5 = ctk.CTkImage(Image.open("assets/5.png"), size=(34, 36))
        image_5_label = ctk.CTkLabel(master=weather_info_frame, text='', image=image_5)
        image_5_label.grid(row=5, column=2, padx=(87, 0), stick='nsew')

        self.__temperature_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="-")
        self.__temperature_label.grid(row=2, column=0, padx=(13, 0), stick="nsew")

        self.__wind_direction_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="-")
        self.__wind_direction_label.grid(row=2, column=1, padx=(81, 0), stick="nsew")

        self.__wind_speed_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="-")
        self.__wind_speed_label.grid(row=2, column=2, padx=(87, 0), stick="nsew")

        self.__sky_state_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="-")
        self.__sky_state_label.grid(row=6, column=0, padx=(9, 0), stick="nsew")

        self.__humidity_label = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="-")
        self.__humidity_label.grid(row=6, column=1, padx=(85, 0), stick='nsew')

        self.__rainfall_probability = ctk.CTkLabel(master=weather_info_frame, font=self.__basic_font, text="-")
        self.__rainfall_probability.grid(row=6, column=2, padx=(87, 0), stick='nsew')

        small_font = ctk.CTkFont(family="맑은 고딕", size=11)
        self.__weather_graphs.clear()
        self.__weather_graph_value_labels.clear()

        for i in range(2):
            for j in range(9):
                graph = ctk.CTkProgressBar(master=self.__weather_details_frame,
                                           orientation="vertical",
                                           height=150,
                                           width=20,
                                           corner_radius=0,
                                           fg_color=self.__weather_details_frame.cget("fg_color"))
                graph.place(relx=j * 0.085 + (j // 3 * 0.08) + 0.04, rely=(i * 0.43) + 0.06)
                graph.set(0.01)
                self.__weather_graphs.append(graph)

                value_label = ctk.CTkLabel(master=self.__weather_details_frame, font=small_font, text="-")
                value_label.place(relx=j * 0.089 + (j // 3 * 0.067) + 0.065, rely=(i * 0.43) + 0.39, anchor=ctk.CENTER)
                self.__weather_graph_value_labels.append(value_label)

        ctk.CTkLabel(master=self.__weather_details_frame,
                     font=self.__basic_font,
                     text="기온(℃)").place(relx=0.1, rely=0.4)

        ctk.CTkLabel(master=self.__weather_details_frame,
                     font=self.__basic_font,
                     text="풍향(°)").place(relx=0.425, rely=0.4)

        ctk.CTkLabel(master=self.__weather_details_frame,
                     font=self.__basic_font,
                     text="풍속(m/s)").place(relx=0.76, rely=0.4)

        ctk.CTkLabel(master=self.__weather_details_frame,
                     font=self.__basic_font,
                     text="하늘상태").place(relx=0.09, rely=0.83)

        ctk.CTkLabel(master=self.__weather_details_frame,
                     font=self.__basic_font,
                     text="습도(%)").place(relx=0.44, rely=0.83)

        ctk.CTkLabel(master=self.__weather_details_frame,
                     font=self.__basic_font,
                     text="강수확률(%)").place(relx=0.73, rely=0.83)

        for i in range(2):
            if i == 0:
                weather_view_mode_frame = ctk.CTkFrame(master=self.__weather_frame)
            else:
                weather_view_mode_frame = ctk.CTkFrame(master=self.__weather_details_frame)
            weather_view_mode_frame.grid(row=3, column=0, padx=(0, 0), pady=(0, 15))

            weather_view_button = ctk.CTkButton(master=weather_view_mode_frame,
                                                font=self.__basic_font,
                                                text="이날의 날씨",
                                                width=10,
                                                height=15,
                                                corner_radius=0,
                                                command=lambda x=0: self.__change_weather_frame(x))
            weather_view_button.grid(row=0, column=0)

            weather_details_button = ctk.CTkButton(master=weather_view_mode_frame,
                                                   font=self.__basic_font,
                                                   text="자세한 날씨",
                                                   width=10,
                                                   height=15,
                                                   corner_radius=0,
                                                   command=lambda x=1: self.__change_weather_frame(x))
            weather_details_button.grid(row=0, column=1)
        # endregion

        # region 지도 프레임을 정의합니다
        map_frame = tk.Frame(master=self.__main_frame, width=300, height=200, bg='#E5E5E5')
        map_frame.grid(row=0, column=2, padx=(10, 0), sticky="ew")
        map_frame.grid_rowconfigure(0, weight=1)
        self.__map_loader = MapLoader(map_frame)

        decrypted_key = self.__load_key("google_map")
        if decrypted_key != '':
            self.__map_loader.connect_api(decrypted_key)
        # endregion

        # region 옵션 버튼을 정의합니다.
        configuration_image = ctk.CTkImage(Image.open("assets/configure.png"), size=(24, 24))
        configuration_button = ctk.CTkButton(master=self.__main_frame,
                                             text='',
                                             image=configuration_image,
                                             width=24,
                                             fg_color='transparent',
                                             hover_color='#E5E5E5',
                                             command=self.__change_frame)
        configuration_button.place(relx=0.95, rely=0.93)
        # endregion

        # region 하단 상태 메시지 프레임을 정의합니다.
        self.__main_frame_message_label = ctk.CTkLabel(master=self.__main_frame,
                                                       font=self.__basic_font,
                                                       fg_color="transparent",
                                                       text_color='#FF2020',
                                                       text="")
        self.__main_frame_message_label.place(relx=0.015, rely=0.947)
        # endregion

    def __initialize_option_frame(self):
        self.__option_frame = ctk.CTkFrame(master=self.__app, fg_color="transparent")
        self.__option_frame.grid_columnconfigure(0, weight=1)
        self.__option_frame.grid_columnconfigure(2, weight=1)

        # region 키 입력 프레임을 정의합니다.
        api_key_input_frame = ctk.CTkFrame(master=self.__option_frame, fg_color="transparent")
        api_key_input_frame.grid(row=0, column=1, pady=(200, 0), sticky="nsew")

        self.__google_api_key_label = ctk.CTkLabel(master=api_key_input_frame,
                                                   font=self.__basic_font,
                                                   text="GOOGLE_KEY")
        self.__google_api_key_label.grid(row=0, column=0)

        if not self.__map_loader.is_api_connected():
            self.__google_api_key_label.configure(text_color="#FF2020")

        self.__google_api_key_entry = ctk.CTkEntry(master=api_key_input_frame,
                                                   font=self.__basic_font,
                                                   width=500,
                                                   corner_radius=0)
        self.__google_api_key_entry.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        google_api_key_button = ctk.CTkButton(api_key_input_frame,
                                              font=self.__basic_font,
                                              text="등록",
                                              width=30,
                                              corner_radius=0,
                                              command=self.__register_google_api_key)
        google_api_key_button.grid(row=0, column=2, padx=(3, 0), sticky="nsew")

        self.__data_api_key_label = ctk.CTkLabel(master=api_key_input_frame,
                                                 font=self.__basic_font,
                                                 text="DATA_KEY")
        self.__data_api_key_label.grid(row=1, column=0, pady=(10, 0))

        if not self.__cw_loader.is_api_connected():
            self.__data_api_key_label.configure(text_color="#FF2020")

        self.__data_api_key_entry = ctk.CTkEntry(master=api_key_input_frame,
                                                 font=self.__basic_font,
                                                 width=500,
                                                 corner_radius=0)
        self.__data_api_key_entry.grid(row=1, column=1, padx=(10, 0), pady=(10, 0), sticky="nsew")

        data_api_key_button = ctk.CTkButton(api_key_input_frame,
                                            font=self.__basic_font,
                                            text="등록",
                                            width=30,
                                            corner_radius=0,
                                            command=self.__register_data_api_key)
        data_api_key_button.grid(row=1, column=2, padx=(3, 0), pady=(10, 0), sticky="nsew")
        # endregion

        # region 돌아가기 버튼을 정의합니다.
        return_image = ctk.CTkImage(Image.open("assets/return.png"), size=(24, 24))
        return_button = ctk.CTkButton(master=self.__option_frame,
                                      text='',
                                      image=return_image,
                                      width=24,
                                      fg_color='transparent',
                                      hover_color='#E5E5E5',
                                      command=self.__change_frame)
        return_button.place(relx=0.95, rely=0.929)
        # endregion

        # region 하단 상태 메시지 프레임을 정의합니다.
        self.__option_frame_message_label = ctk.CTkLabel(master=self.__option_frame,
                                                         font=self.__basic_font,
                                                         fg_color="transparent",
                                                         text_color="#FF2020",
                                                         text="")
        self.__option_frame_message_label.place(relx=0.015, rely=0.947)
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
            self.__print_message("키워드를 입력해 주세요.")
            return

        search_type = self.__search_menu.get()

        for button in self.__recommand_tourist_spot_buttons:
            button.destroy()
        self.__recommand_tourist_spot_buttons.clear()

        for button in self.__searched_keyword:
            button.destroy()
        self.__searched_keyword.clear()

        # 스크롤 뷰 상태를 초기화하기 위해 검색 결과 프레임을 재생성합니다.
        self.__search_result_frame.destroy()
        self.__create_search_result_frame()

        if search_type == '지역명':
            tourist_spots = self.__cw_loader.find_tourist_spots_by_local_name(search_keyword)
        elif search_type == '관광지명':
            tourist_spots = self.__cw_loader.find_tourist_spots(search_keyword)
        else:
            assert False, "지원하지 않는 검색 유형입니다."

        if len(tourist_spots) > 0:
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
        else:
            self.__print_message("검색된 결과가 없습니다.")

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

        tourist_spot = selected_button.cget("text")

        if self.__map_loader.is_api_connected():
            lat_lng = self.__map_loader.find_lat_lng(tourist_spot)
            if lat_lng:
                self.__map_loader.show_map(lat_lng)
            else:
                self.__print_message("'" + tourist_spot + "'의 좌표를 알 수 없어 지도가 표시되지 않습니다.", 3500.0)
        else:
            self.__print_message("구글 지도 API 키가 유효하지 않아 지도를 표시할 수 없습니다. 키를 다시 확인해 주세요", 4000.0)

        self.__selected_tourist_spot_button_index = selected_button_index

    def __on_weather_selected(self):
        if self.__selected_tourist_spot_course_id == 0:
            self.__print_message("관광지가 선택되어 있지 않아 날씨를 조회할 수 없습니다.", 3500.0)
            return

        if not self.__cw_loader.is_api_connected():
            self.__print_message("공공데이터포털 API 키가 유효하지 않아 날씨를 조회할 수 없습니다. 키를 다시 확인해 주세요", 4000.0)
            return

        year = self.__year_entry.get()
        month = self.__month_entry.get()
        day = self.__day_entry.get()
        time = self.__time_entry.get().split(':')[0]
        date = int(year + month + day + time)
        tourist_spot = self.__recommand_tourist_spot_buttons[self.__selected_tourist_spot_button_index].cget("text")

        search_result, searched_weather = self.__cw_loader.search_weather(self.__selected_tourist_spot_course_id,
                                                                          tourist_spot,
                                                                          str(date))

        if search_result == WeatherSearchResult.NOT_FOUND:
            self.__print_message("'" + tourist_spot + "'" + "의 해당 날짜에는 날씨를 조회할 수 없습니다.")
            return

        th3 = searched_weather['th3']
        wd = searched_weather['wd']
        ws = searched_weather['ws']
        rhm = searched_weather['rhm']
        pop = searched_weather['pop']
        sky = searched_weather['sky']

        self.__temperature_label.configure(text=th3 + '℃')
        self.__wind_direction_label.configure(text=wd + '°')
        self.__wind_speed_label.configure(text=ws + 'm/s')
        self.__humidity_label.configure(text=rhm + '%')
        self.__rainfall_probability.configure(text=pop + '%')

        sky = int(sky)
        if sky == 1:
            self.__sky_state_label.configure(text='맑음')
        elif sky == 3:
            self.__sky_state_label.configure(text='구름 많음')
        elif sky == 4:
            self.__sky_state_label.configure(text='흐림')

        self.__weather_infos[1] = searched_weather

        search_result, searched_weather = self.__cw_loader.search_weather(self.__selected_tourist_spot_course_id,
                                                                          tourist_spot,
                                                                          str(date - 100))

        if search_result != WeatherSearchResult.NOT_FOUND:
            self.__weather_infos[0] = searched_weather
        else:
            self.__weather_infos[0] = {}

        search_result, searched_weather = self.__cw_loader.search_weather(self.__selected_tourist_spot_course_id,
                                                                          tourist_spot,
                                                                          str(date + 100))

        if search_result != WeatherSearchResult.NOT_FOUND:
            self.__weather_infos[2] = searched_weather
        else:
            self.__weather_infos[2] = {}

    def __change_frame(self):
        self.__current_frame.pack_forget()

        if self.__current_frame == self.__main_frame:
            self.__current_frame = self.__option_frame
            self.__main_frame_message_label.configure(text="")
        else:
            self.__current_frame = self.__main_frame
            self.__option_frame_message_label.configure(text="")

        self.__current_frame.pack(fill="both", expand=True)

    def __change_weather_frame(self, button_index):
        if button_index == 0:
            self.__weather_details_frame.grid_forget()
            self.__weather_frame.grid(row=0, column=1, padx=(10, 0), pady=(20, 30), sticky="nsew")
            self.__current_weather_frame = self.__weather_frame
        elif button_index == 1:
            self.__weather_frame.grid_forget()
            self.__weather_details_frame.grid(row=0, column=1, padx=(10, 0), pady=(20, 30), sticky="nsew")
            self.__current_weather_frame = self.__weather_details_frame

            for i in range(len(self.__weather_graphs)):
                self.__weather_graphs[i].set(0.01)

        else:
            assert False, "지원하지 않는 버튼 인덱스입니다."

    def __register_google_api_key(self):
        input_key = self.__google_api_key_entry.get()
        if self.__map_loader.connect_api(input_key):
            encrypted_key = ed.encrypt_key(bytes(input_key, "ascii"))
            key_file = open("api_keys/google_map", 'wb')
            key_file.write(encrypted_key)

            self.__google_api_key_label.configure(text_color=self.__basic_font_color)
            self.__google_api_key_entry.delete(0, "end")
            self.__print_message("구글 지도 API 키가 정상적으로 등록되었습니다.", 3500.0, "#2020FF")
        else:
            self.__print_message("유효하지 않는 키입니다. 다시 확인해 주세요.")

    def __register_data_api_key(self):
        input_key = self.__data_api_key_entry.get()
        if self.__cw_loader.connect_api(input_key):
            encrypted_key = ed.encrypt_key(bytes(input_key, "ascii"))
            key_file = open("api_keys/data", 'wb')
            key_file.write(encrypted_key)

            self.__data_api_key_label.configure(text_color=self.__basic_font_color)
            self.__data_api_key_entry.delete(0, "end")
            self.__print_message("공공데이터포털 API 키가 정상적으로 등록되었습니다.", 3500.0, "#2020FF")
        else:
            self.__print_message("유효하지 않는 키입니다. 다시 확인해 주세요.")

    @staticmethod
    def __load_key(file_name):
        try:
            key_file = open("api_keys/" + file_name, 'rb')
        except:
            return ''

        encrypted_key = key_file.read()

        try:
            decrypted_key = ed.decrypt_key(encrypted_key).decode("ascii")
        except:  # 바이너리 데이터가 아닌 경우
            return ''

        return decrypted_key

    def __print_message(self, message, show_delay=2000.0, text_color="#FF2020"):
        if self.__current_frame is self.__main_frame:
            self.__main_frame_message_label.configure(text=message, text_color=text_color)
        else:
            self.__option_frame_message_label.configure(text=message, text_color=text_color)
        self.__message_label_show_remaining_time = show_delay

    @staticmethod
    def __lerp(a, b, t):
        return a * (1 - t) + b * t

if __name__ == '__main__':
    core = Core()
    core.run()

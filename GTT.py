# -*- coding: utf-8 -*-
"""
Kivy introduction code!
"""

import kivy
import sqlite3
import pandas as pd
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from datetime import datetime

#Define our different screens
class HomeWindow(Screen):
    pass

class StudyWindow(Screen):
    pass

class AccessWindow(Screen):
    pass

class WindowManager(ScreenManager):
    pass

kv = Builder.load_file('GTT.kv')

class GTTApp(App):
    sw_seconds = 0
    sw_started = False
    fix_bool = False
    fix_id = []
    lineitem_list = []
    elements_list = []
    eletimes_list = []
    study_name_load = []
    
    def on_start(self):
        Clock.schedule_interval(self.update_time, 0)
        self.root.get_screen("Study").ids.stopwatch.text = "0.00"
        
    def get_id(self, instance):
        for id, widget in self.root.get_screen("Study").ids.items():
            if widget.__self__ == instance:
                return id
            
    def update_time(self, nap):
        if self.sw_started:
            self.sw_seconds += nap
        part_seconds = self.sw_seconds * 100 % 100
        self.root.get_screen("Study").ids.stopwatch.text = f'{int(self.sw_seconds)}.{int(part_seconds):02}'    
    
    def start(self):
        if self.sw_seconds == 0:
            self.sw_started = not self.sw_started
            
    def pause_play(self):
        if self.sw_seconds > 0:
            self.root.get_screen("Study").ids.pause_play.text = "Resume" if self.sw_started else "Pause"
            self.sw_started = not self.sw_started
            
    def ele_split(self, instance):
        if self.sw_started and (not self.fix_bool):
            self.lineitem_list.append(str(len(self.lineitem_list)))
            self.elements_list.append(self.get_id(instance))
            self.eletimes_list.append(str(round(self.sw_seconds, 2)))
            
            self.root.get_screen("Study").ids.StudyGrid.add_widget(Label(text = self.lineitem_list[len(self.lineitem_list) - 1],
                color = (0, 0, 0, 1),                                                      
                size_hint_x = 0.6,
                size_hint_y = None,
                height = 30))
            
            ele_button = Button(text = self.elements_list[len(self.elements_list) - 1],
                size_hint_x = 0.4,
                size_hint_y = None,
                height = 30)
            ele_button.id = "E" + str(len(self.lineitem_list) - 1)
            
            ele_button.bind(on_press = self.fix_state)
            
            self.root.get_screen("Study").ids.StudyGrid.add_widget(ele_button)
            
            self.root.get_screen("Study").ids.StudyGrid.add_widget(Label(text = self.eletimes_list[len(self.eletimes_list) - 1], 
                color = (0, 0, 0, 1),
                size_hint_y = None,
                height = 30))
            
            self.sw_seconds = 0  
            
    def fix_state(self, instance):
        buttons_in_ebg = [ele for ind, ele in enumerate(self.root.get_screen("Study").ids.EleButtonGrid.children)] + [self.root.get_screen("Study").ids.U]
        self.fix_bool = not self.fix_bool
        
        if self.fix_bool:
            self.fix_id.append(instance.id[1:])
            for child in buttons_in_ebg:
                child.background_color = [0.5, 0, 0, 0.75]
        if not self.fix_bool:
            self.fix_id = []
            for child in buttons_in_ebg:
                child.background_color = [0, 0.34, 1, 0.8]
            
    def ele_fix(self, instance):
        buttons_in_ebg = [ele for ind, ele in enumerate(self.root.get_screen("Study").ids.EleButtonGrid.children)] + [self.root.get_screen("Study").ids.U]
        
        if self.fix_bool:
            buttons_in_sg = [ele for ind, ele in enumerate(self.root.get_screen("Study").ids.StudyGrid.children) if ind % 3 == 1]
            for child in buttons_in_sg:
                if(child.id[1:]) == self.fix_id[0]:
                    child.text = self.get_id(instance)
                    self.elements_list[int(self.fix_id[0])] = self.get_id(instance)
                    
            self.fix_id = []
            self.fix_bool = False
        if not self.fix_bool:
            for child in buttons_in_ebg:
                child.background_color = [0, 0.34, 1, 0.8]
            
    def clear_study_grid(self):
        self.root.get_screen("Study").ids.StudyGrid.clear_widgets()
    
    def save_and_exit(self):
        now = datetime.now()
        StudyName = self.root.get_screen("Study").ids.StudyTitleInput.text
        StudyName = "Untitled " + now.strftime("%m%d%Y, %H%M%S") if not StudyName.strip() else StudyName
        
        conn = sqlite3.connect('study_db.db')
        curs = conn.cursor()
        
        curs.execute("DELETE FROM studies WHERE study = ?", (StudyName, )
            )
        
        curs.execute("""CREATE TABLE IF NOT EXISTS studies(
            study TEXT, 
            litems TEXT,
            elements TEXT,
            times TEXT,
            CONSTRAINT pk_tbl_studies_study_litems PRIMARY KEY (study, litems)
            )
        """)
        
        for i in range(0, len(self.lineitem_list)):
            curs.execute("INSERT INTO studies (study, litems, elements, times) VALUES (?, ?, ?, ?)",
                (StudyName, self.lineitem_list[i], self.elements_list[i], self.eletimes_list[i])
                )
        
        conn.commit()
        conn.close()
        
        self.sw_seconds = 0
        self.sw_started = False
        self.fix_bool = False
        self.fix_id = []
        self.lineitem_list = []
        self.elements_list = []
        self.eletimes_list = []
        
        self.root.get_screen("Study").ids.StudyTitleInput.text = ""
        self.root.get_screen("Study").ids.StudyGrid.clear_widgets()
    
    def gen_study_list(self):
        self.root.get_screen("Access").ids.SavedGrid.clear_widgets()
        
        conn = sqlite3.connect('study_db.db')
        curs = conn.cursor()
        
        curs.execute("SELECT DISTINCT study FROM studies")
        
        loaded_studies= curs.fetchall()
        
        for item in loaded_studies:
            study_label= Label(text = item[0], 
                color = (0, 0, 0, 1),
                font_size = 14,
                size_hint_x = 1,
                size_hint_y = None,
                height = 30)
            study_label.id = "Name " + item[0]
            
            self.root.get_screen("Access").ids.SavedGrid.add_widget(study_label)
            
            load_button = Button(text = "Load",
                font_size = 12,
                size_hint_x = 0.25,
                size_hint_y = None,
                height = 30)
            load_button.id = "Load " + item[0]
            load_button.bind(on_press = self.load_study, on_release = self.load_screen_switch)
            
            self.root.get_screen("Access").ids.SavedGrid.add_widget(load_button)
            
            export_button = Button(text = "Export",
                background_color = (0, 1, 0, 1),
                font_size = 12,
                size_hint_x = 0.25,
                size_hint_y = None,
                height = 30)
            export_button.id = "Expt " + item[0]
            export_button.bind(on_press = self.export_study)
            
            self.root.get_screen("Access").ids.SavedGrid.add_widget(export_button)
            
            remove_button = Button(text = "X",
                background_color = (1, 0, 0, 1),
                font_size = 12,
                size_hint_x = 0.25,
                size_hint_y = None,
                height = 30)
            remove_button.id = "Remv " + item[0]
            remove_button.bind(on_press = self.remove_study)
            
            self.root.get_screen("Access").ids.SavedGrid.add_widget(remove_button)
            
            conn.close()
            
    def load_screen_switch(self, *args):
        self.root.current = "Study" 
    
    def load_study(self, instance):
        study_id = instance.id[5:]
        
        conn = sqlite3.connect('study_db.db')
        curs = conn.cursor()
        
        curs.execute("SELECT * FROM studies WHERE study = ?", (study_id, ))
        
        study_data = curs.fetchall()
        print(study_data)
        
        for item in study_data:
            self.lineitem_list.append(item[1])
            self.elements_list.append(item[2])
            self.eletimes_list.append(item[3])
            
            self.root.get_screen("Study").ids.StudyTitleInput.text = item[0]
            
            self.root.get_screen("Study").ids.StudyGrid.add_widget(Label(text = self.lineitem_list[len(self.lineitem_list) - 1], 
                color = (0, 0, 0, 1),
                size_hint_x = 0.4,
                size_hint_y = None,
                height = 30))
            
            ele_button = Button(text = self.elements_list[len(self.elements_list) - 1],
                size_hint_x = 0.4,
                size_hint_y = None,
                height = 30)
            ele_button.id = "E" + str(len(self.lineitem_list) - 1)
            
            ele_button.bind(on_press = self.fix_state)
            
            self.root.get_screen("Study").ids.StudyGrid.add_widget(ele_button)
            
            self.root.get_screen("Study").ids.StudyGrid.add_widget(Label(text = self.eletimes_list[len(self.eletimes_list) - 1], 
                color = (0, 0, 0, 1),
                size_hint_y = None,
                height = 30))
            
            self.sw_seconds = 0
        
        conn.close()
            
    def export_study(self, instance):
        study_id = instance.id[5:]
        
        conn = sqlite3.connect('study_db.db')
        curs = conn.cursor()
        
        curs.execute("SELECT * FROM studies WHERE study = ?", (study_id, ))
        
        study_data = curs.fetchall()
        
        study_df = pd.DataFrame(study_data, columns = ["Study", "Line Item", "Element", "Time (sec)"])
        study_df.to_csv(study_id + ".csv", index = False)
        
        conn.close()
    
    def remove_study(self, instance):
        study_id = instance.id[5:]
        
        conn = sqlite3.connect('study_db.db')
        curs = conn.cursor()
        
        curs.execute("DELETE FROM studies WHERE study = ?", (study_id, )
            )
        
        conn.commit()
        
        study_id_widgets = [ele for ele in self.root.get_screen("Access").ids.SavedGrid.children if ele.id[5:] == study_id]
        for child in study_id_widgets:
            self.root.get_screen("Access").ids.SavedGrid.remove_widget(child)
        
        conn.close()

if __name__ == '__main__':
    GTTApp().run()
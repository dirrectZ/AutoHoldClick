import tkinter
from tkinter import ttk
import keyboard
import pyautogui
import json
from os import path
import os


class App(tkinter.Tk):
	settings = {
		"stand_by_key": 'right shift',
		"start_stop_key": 'end',
	}
	
	def __init__(self):
		super().__init__()
		self.title = 'AutoHoldClick'
		self.geometry('480x240')
		self.tabs_manager = ttk.Notebook(self)
		self.tabs_manager.pack(anchor='n', fill='both', expand=True)
		
		self.main_page = MainPage()
		self.settings_page = SettingsPage()
		self.tabs_manager.add(self.main_page)
		self.tabs_manager.tab(0, text="Main")
		self.tabs_manager.add(self.settings_page)
		self.tabs_manager.tab(1, text="Settings")


class MainPage(tkinter.Frame):
	STATUS = {
		0: {  # Stopped status
			'text': 'Stopped',
			'color': '#f00',
		},
		1: {  # Stand By status
			'text': 'Waiting for key press...',
			'color': '#ff0',
		},
		2: {  # Started status
			'text': 'Started',
			'color': '#0f0',
		},
	}
	
	def __init__(self):
		super().__init__()
		self.status_text = tkinter.StringVar(value=self.STATUS[0]['text'])
		self.status_displayer = tkinter.Label(self, textvariable=self.status_text, font=("", 24),
											  fg=self.STATUS[0]['color'])
		self.status_displayer.grid(row=0, column=0, sticky='nsew')
		
		self.standby_button = tkinter.Button(self, text="Start/Stop", font=("", 24), command=self.standby_command)
		self.standby_button.grid(row=1, column=0, sticky='nsew', padx=(70, 70), pady=(30, 30))
		
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		self.columnconfigure(0, weight=1)
		
		self.stand_by_key = str()
		self.start_stop_key = str()
		self.read_settings()
		
		self.status = 0
		
		self.after(100, self.event_loop)
	
	def event_loop(self):
		if self.change_status():
			self.update_displayer()
			
			if self.status == 2:
				pyautogui.mouseDown()
				self.after(500, self.event_loop)
			else:
				pyautogui.mouseUp()
				self.after(500, self.event_loop)
		else:
			self.after(100, self.event_loop)
			
	def change_status(self) -> bool:
		if keyboard.is_pressed(self.stand_by_key):
			if self.status == 0:
				self.status = 1
			else:
				self.status = 0
		elif keyboard.is_pressed(self.start_stop_key):
			if self.status == 1:
				self.status = 2
			elif self.status == 2:
				self.status = 1
		else:
			return False
		return True
	
	def update_displayer(self):
		self.status_displayer.config(fg=self.STATUS[self.status]['color'])
		self.status_text.set(value=self.STATUS[self.status]['text'])
		
	def standby_command(self):
		if self.status == 1:
			self.status = 0
		else:
			self.status = 1
			
		self.update_displayer()
	
	def read_settings(self):
		with open(path.abspath(path.join(path.dirname(__file__), 'settings.json')), "r") as settings_file:
			settings = json.load(settings_file)
			self.stand_by_key = settings['standby_key']
			self.start_stop_key = settings['start_stop_key']


class SettingsPage(tkinter.Frame):
	def __init__(self):
		super().__init__()
		self.standby_frame = tkinter.LabelFrame(self, text='Stand By', labelanchor='n')
		self.standby_frame.grid(row=0, column=0, sticky='nsew')
		
		self.standby_key = tkinter.StringVar()
		self.standby_key_entry = tkinter.Entry(self.standby_frame, textvariable=self.standby_key, font=('', 22),
											   state='readonly')
		
		self.standby_key_entry.grid(row=0, column=0, sticky='ew', padx=(20, 0))
		
		self.record_button_sby = tkinter.Button(self.standby_frame, text='Record', command=self.record_standby)
		self.record_button_sby.grid(row=0, column=1, sticky='ew', padx=(0, 20))
		
		self.standby_frame.rowconfigure(0, weight=1)
		self.standby_frame.columnconfigure(0, weight=3)
		self.standby_frame.columnconfigure(1, weight=1)
		
		#  START/STOP
		self.start_stop_frame = tkinter.LabelFrame(self, text='Start/Stop', labelanchor='n')
		self.start_stop_frame.grid(row=1, column=0, sticky='nsew')
		
		self.start_stop_key = tkinter.StringVar()
		self.start_stop_key_entry = tkinter.Entry(self.start_stop_frame, textvariable=self.start_stop_key, font=('', 22),
											   state='readonly')
		
		self.start_stop_key_entry.grid(row=0, column=0, sticky='ew', padx=(20, 0))
		
		self.record_button_st = tkinter.Button(self.start_stop_frame, text='Record', command=self.record_start_stop)
		self.record_button_st.grid(row=0, column=1, sticky='ew', padx=(0, 20))
		
		self.start_stop_frame.rowconfigure(0, weight=1)
		self.start_stop_frame.columnconfigure(0, weight=3)
		self.start_stop_frame.columnconfigure(1, weight=1)
		
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		self.columnconfigure(0, weight=1)
		
		self.read_settings()
		
	def record(self, key_to_record):
		key = keyboard.read_key()
		if not str(key).isnumeric() and key != self.standby_key.get() and key != self.start_stop_key.get():
			if key_to_record == 'standby_key':
				self.standby_key.set(key)
			else:
				self.start_stop_key.set(key)
			
			settings = {}
			
			with open(path.abspath(path.join(path.dirname(__file__), 'settings.json')), "r") as settings_file:
				settings = json.load(settings_file)
			
			settings[key_to_record] = str(key)
			
			with open(path.abspath(path.join(path.dirname(__file__), 'settings.json')), "w") as settings_file:
				json.dump(settings, settings_file)
			
			self.after(1000, self.apply_settings)
		
	def apply_settings(self):
		self.master.main_page.read_settings()
	
	def record_standby(self):
		self.record('standby_key')
	
	def record_start_stop(self):
		self.record('start_stop_key')
	
	def read_settings(self):
		with open(path.abspath(path.join(path.dirname(__file__), 'settings.json')), "r") as settings_file:
			settings = json.load(settings_file)
			self.standby_key.set(settings['standby_key'])
			self.start_stop_key.set(settings['start_stop_key'])


if __name__ == '__main__':
	print(os.path.expanduser('~'))
	App().mainloop()

import tkinter
import time
import pynput.mouse
import pygame.mixer as sound
import json
from os import path

class App(tkinter.Tk):
	def __init__(self):
		super().__init__()
		self.title = 'AutoHoldClick'
		self.geometry('480x240')
		self.main_page = MainPage()
		self.main_page.pack(anchor='n', fill='both', expand=True)


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

		self.status = 0
		self.mouse_controller = pynput.mouse.Controller()
		
		self.click_timer = 0
		self.mdbutton_timer = 0
		self.mdbutton_pressed = False
		
		sound.init()
		self.activated_sound = sound.Sound(path.abspath(path.join(path.dirname(__file__), 'audio/activated.mp3')))
		self.deactivated_sound = sound.Sound(path.abspath(path.join(path.dirname(__file__), 'audio/deactivated.mp3')))
		
		mouse_listener = pynput.mouse.Listener(on_click=self.on_click)
		mouse_listener.start()
		self.after(50, self.event_handler)
		
	def update_displayer(self):
		self.status_displayer.config(fg=self.STATUS[self.status]['color'])
		self.status_text.set(value=self.STATUS[self.status]['text'])
		
	def standby_command(self):
		if self.status == 1:
			self.status = 0
		else:
			self.status = 1
			
		self.update_displayer()
		
	def on_click(self, x, y, button, pressed):
		if button == pynput.mouse.Button.left and not pressed and self.status != 0:
			if self.status == 1:
				self.status = 2
				self.mouse_controller.press(pynput.mouse.Button.left)
				self.click_timer = time.time()
			elif self.status == 2 and time.time() - self.click_timer >= 1:
				self.status = 1
			
		elif button == pynput.mouse.Button.middle:
			if pressed:
				self.mdbutton_timer = time.time()
			self.mdbutton_pressed = pressed
			
		self.update_displayer()
		
	def event_handler(self):
		if self.mdbutton_pressed:
			if int(time.time()) - self.mdbutton_timer >= 1:
				self.mdbutton_timer = 0
				if self.status == 0:
					self.status = 1
					self.activated_sound.play()
				else:
					self.status = 0
					self.deactivated_sound.play()
					# TODO release click when this is deactivated and inspect the behavior of click release
					
					
				self.mdbutton_pressed = False
				self.update_displayer()
		
		self.after(50, self.event_handler)


if __name__ == '__main__':
	App().mainloop()


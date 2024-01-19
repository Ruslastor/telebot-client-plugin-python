#TELEBOT CLIENT PLUGIN version 1.2 __STABLE__
#BY RUSLAN ASSYLGAREYEV 01/17/2024



import telebot
import threading
from telebot import types
import os
import sqlite3 as sql
import time

bot = None

db_connection = sql.connect('bot_database.db', check_same_thread=False)
ban_list_cursor = db_connection.cursor()
userdata_headers = []
with open('bot_token.txt', 'r') as file:
	token, headers = file.read().split('\n')
	bot = telebot.TeleBot(token)
	fstr = "CREATE TABLE IF NOT EXISTS userdata(chat_id INTEGER PRIMARY KEY,"

	for name_len in headers.split(';'):
		name, leng = name_len.split(',')
		fstr += f'{name} VARCHAR({leng}),'
		userdata_headers.append(name)

	ban_list_cursor.execute(fstr[:-1] + ')')

class Element:
	ELEMENTS : dict = {}
	
	def __init__(self):
		self.id = id(self)
		Element.ELEMENTS[self.id] = self
	def delete(self):
		del Element.ELEMENTS[self.id]


class Button(Element):
	def __init__(self,label, callback):
		super().__init__()
		self.label = label
		self.callback = callback
		self.button = types.InlineKeyboardButton(text=self.label, callback_data='b;'+str(self.id))

class InputButton(Element):
	INPUT_QUERY : dict = {}
	INPUT_TEXT = 0
	INPUT_PHOTO = 1
	def __init__(self,label, callback, input_type):
		super().__init__()
		self.label = label
		self.input_type = input_type
		self.callback = callback
		self.button = types.InlineKeyboardButton(text='✏️'+self.label, callback_data='i;'+str(self.id))
	def add_to_input_query(self, chat_id):
		InputButton.INPUT_QUERY[chat_id] = self
	def delete_from_input_query(self, chat_id):
		del InputButton.INPUT_QUERY[chat_id]

class LinkButton(Element):
	def __init__(self, label, link):
		super().__init__()
		self.label = label
		self.link = link
		self.button = types.InlineKeyboardButton(text='🔗'+self.label, url=link)

class TelePhoto:
	def __init__(self, path):
		self.data = None
		with open(path, 'rb') as file:
			self.data = file.read()
	@staticmethod
	def from_path(path):
		with open(path, 'rb') as file:
			return file.read()
	@staticmethod
	def from_message(message):
		return message.photo[-1].file_id



global _on_user_initialization
_on_user_initialization = None
global _on_data_saving
_on_data_saving = None
global _on_data_loading
_on_data_loading = None


class User:
	USERS = {}
	MAX_AFK_SECONDS = 5
	AFK_CHECK_PERIOD = 10
	MINIMAL_MESSAGING_PERIOD = 0.1
	MAX_BAN_ACTION_COUNT = 20
	def __init__(self, message):
		self.chat_id = message.chat.id
		self.name = message.from_user.first_name

		self.menues = {}
		self.user_data = {i:None for i in userdata_headers}
		self.last_interraction_time = time.time()
		self.ban_actions_count = 0
		self.db_cursor = db_connection.cursor()
		_on_user_initialization(self)
	def delete(self):
		for menue_id in list(self.menues.keys()):
			self.menues[menue_id].clear()
			del self.menues[menue_id]
		del User.USERS[self.chat_id]
	def delete_menue(self, menue_id):
		self.menues[menue_id].clear()
		del self.menues[menue_id]

	def update_last_interraction_time(self):
		self.last_interraction_time = time.time()
	def try_to_ban(self):
		c_time = time.time()
		if c_time - self.last_interraction_time <= MINIMAL_MESSAGING_PERIOD:
			self.ban_actions_count += 1
		if self.ban_actions_count >= MAX_BAN_ACTION_COUNT:
			ban_list_cursor.execute(f"""INSERT INTO banlist(chat_id) VALUES({self.chat_id})""")
			ban_list_cursor.commit()
			self.delete()
	def save_to_db(self):
		self.db_cursor.execute(f"""SELECT * FROM userdata WHERE chat_id={self.chat_id}""")
		self.user_data = _on_data_saving(self.user_data)
		if not self.db_cursor.fetchone():
			self.db_cursor.execute(f"""INSERT INTO userdata (chat_id,{','.join(userdata_headers)}) VALUES ({self.chat_id},{ ','.join([f"'{self.user_data[i]}'" for i in userdata_headers]) })""")
		else:
			self.db_cursor.execute(f"""UPDATE userdata SET {','.join([f"{i}='{self.user_data[i]}'" for i in userdata_headers])} WHERE chat_id = {self.chat_id}""")

	@staticmethod
	def user_exists(message):
		return message.chat.id in User.USERS.keys()
	@staticmethod
	def init_user(message):
		if not User.user_exists(message):			
			ban_list_cursor.execute(f"""SELECT * FROM banlist WHERE chat_id={message.chat.id}""")
			if ban_list_cursor.fetchone():
				return 
			ban_list_cursor.execute(f"""SELECT * FROM userdata WHERE chat_id={message.chat.id}""")
			result = _on_data_loading(ban_list_cursor.fetchone())
			new_user = User(message)
			User.USERS[message.chat.id] = new_user
			if result:
				for value, key in zip(result[1:], userdata_headers):
					new_user.user_data[key] = value


class Menue:
	def __init__(self, chat_id, text, buttons=None, initial_button_alignment=None, image=None):	
		self.buttons = buttons 
		self.button_alignment = initial_button_alignment
		
		self.text = text
		self.image = image

		self.chat_id = chat_id

		self.message_id = None
		if self.image:
			if isinstance(self.image, TelePhoto):
				self.message_id = bot.send_photo(self.chat_id, photo=self.image.data, caption=self.text, reply_markup = self.get_keyboard_markup(), parse_mode='html').message_id
			else:
				self.message_id = bot.send_photo(self.chat_id, photo=self.image, caption=self.text, reply_markup = self.get_keyboard_markup(), parse_mode='html').message_id
		else:
			self.message_id = bot.send_message(chat_id, text=self.text, reply_markup=self.get_keyboard_markup(), parse_mode='html').message_id

	def clear(self):
		bot.delete_message(self.chat_id, self.message_id)
	
	def update(self, new_text=None, new_button_alignment=None, new_image=None):
		if new_image:
			self.image = new_image
			if isinstance(self.image, TelePhoto):
				bot.edit_message_media(chat_id=self.chat_id, message_id=self.message_id, media=types.InputMediaPhoto(self.image.data))
			else:
				bot.edit_message_media(chat_id=self.chat_id, message_id=self.message_id, media=types.InputMediaPhoto(self.image))
		if new_text:
			self.text = new_text
		if new_button_alignment:
			self.button_alignment=new_button_alignment
		if self.image:
			bot.edit_message_caption(chat_id=self.chat_id, message_id=self.message_id, caption=self.text, reply_markup=self.get_keyboard_markup(), parse_mode='html')
		else:
			bot.edit_message_text(chat_id=self.chat_id, message_id=self.message_id, text=self.text, reply_markup=self.get_keyboard_markup(), parse_mode='html')
	
	def get_keyboard_markup(self):
		if self.buttons and self.button_alignment:
			return types.InlineKeyboardMarkup(Menue.get_buttons_from_alignment(self.button_alignment,self.buttons))
		return None

	@staticmethod
	def get_buttons_from_alignment(alignment, buttons):
		result = []
		if alignment:
			for item in alignment:
				if isinstance(item, list):
					recursion = Menue.get_buttons_from_alignment(item, buttons)
					if recursion:
						result.append(recursion)
				else:
					result.append(buttons[item].button)
			return result
		return None


#secure ent ICT and CYBERSECURITY

@bot.callback_query_handler(func=lambda callback: callback.data)
def callback_handler(callback):
	user = User.USERS.get(callback.message.chat.id, None)
	if not user:
		return
	command, element_id = callback.data.split(';')
	element = Element.ELEMENTS[int(element_id)]
	match command:
		case 'b':
			element.callback(user)
		case 'i':
			element.add_to_input_query(callback.message.chat.id)
	user.update_last_interraction_time()

@bot.message_handler(commands=['start'])
def new_user_init(message):
	User.init_user(message)
	bot.delete_message(message.chat.id, message.message_id)

@bot.message_handler(content_types=['text','photo'])
def user_input_handler(message):
	user = User.USERS.get(message.chat.id, None)
	if  not user:
		return
	bot.delete_message(message.chat.id, message.id)
	if message.chat.id in InputButton.INPUT_QUERY:
		element = InputButton.INPUT_QUERY[message.chat.id]
		if element.input_type == InputButton.INPUT_TEXT and message.text:
			element.callback(user, message.text)
		if element.input_type == InputButton.INPUT_PHOTO and message.photo:
			element.callback(user, TelePhoto.from_message(message))
		element.delete_from_input_query(message.chat.id)

		user.update_last_interraction_time()

debug = True



def afk_checker():
	while True:
		user_ids = tuple(User.USERS.values())
		for user in user_ids:
			if time.time() - user.last_interraction_time > User.MAX_AFK_SECONDS:
				user.save_to_db()
				user.delete()
		db_connection.commit()
		time.sleep(User.AFK_CHECK_PERIOD)


def start_polling():
	ban_list_cursor.execute("""CREATE TABLE IF NOT EXISTS banlist (chat_id INTEGER PRIMARY KEY);""")
	
	afk_checker_thread = threading.Thread(target=afk_checker)
	afk_checker_thread.start()
	while True:
		if debug:
			bot.polling()
		else:
			try:
				bot.polling()
			except:
				print('ERROR')
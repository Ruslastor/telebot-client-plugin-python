#TELEBOT CLIENT PLUGIN version 1.2 __STABLE__
#BY RUSLAN ASSYLGAREYEV 01/17/2024

import telebot
import threading
from telebot import types
import time

bot = None

userdata_headers = []
with open('bot_token.txt', 'r') as file:
	token = file.read()
	bot = telebot.TeleBot(token)

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
	def __init__(self, label, helper_label, callback, input_type):
		super().__init__()
		self.label = label
		self.helper_label = helper_label
		self.input_type = input_type
		self.callback = callback
		self.button = types.InlineKeyboardButton(text='✏️'+self.label, callback_data='i;'+str(self.id))

	def add_to_input_query(self, chat_id):
		InputButton.INPUT_QUERY[chat_id] = (self, bot.send_message(chat_id, text=self.helper_label, parse_mode='html').message_id)
	def delete_from_input_query(self, chat_id):
		_, help_id = InputButton.INPUT_QUERY[chat_id]
		bot.delete_message(chat_id, help_id)
		del InputButton.INPUT_QUERY[chat_id]

class LinkButton(Element):
	def __init__(self, label, link):
		super().__init__()
		self.label = label
		self.link = link
		self.button = types.InlineKeyboardButton(text='🔗'+self.label, url=link)

class TelePhoto:
	def __init__(self, message=None, file_id=None):
		self.file_id = file_id
		if message:
			self.file_id = message.photo[-1].file_id

class StaticPhoto:
	def __init__(self, path):
		self.data = None
		with open(path, 'rb') as file:
			self.data = file.read()

global _on_user_initialization
_on_user_initialization = None
global _on_location_response
_on_location_response = None
global _on_user_afk_detected
_on_user_afk_detected = None


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
		self.afk = False
		_on_user_initialization(self)
	def delete(self):
		for menue_id in list(self.menues.keys()):
			self.menues[menue_id].clear()
			del self.menues[menue_id]
		del User.USERS[self.chat_id]
	def delete_menue(self, menue_id):
		self.menues[menue_id].clear()
		del self.menues[menue_id]

	def set_active_menues(self, menue_ids):
		for i in self.menues.values():
			i.clear()
		for i in menue_ids:
			self.menues[i].publish()

	def update_last_interraction_time(self):
		self.afk = False
		self.last_interraction_time = time.time()

	@staticmethod
	def user_exists(message):
		return message.chat.id in User.USERS.keys()
	@staticmethod
	def init_user(message):
		if not User.user_exists(message):			
			new_user = User(message)
			User.USERS[message.chat.id] = new_user


class Menue:
	def __init__(self, chat_id, text, buttons=None, initial_button_alignment=None, image=None, request_location=False):	
		self.buttons = buttons 
		self.button_alignment = initial_button_alignment
		self.is_location_requester = request_location

		self.text = text
		self.image = image
		self.chat_id = chat_id

		self.message_id = None

	def publish(self):
		if self.image:
			if isinstance(self.image, TelePhoto):
				self.message_id = bot.send_photo(self.chat_id, photo=self.image.file_id, caption=self.text, reply_markup = self.get_keyboard_markup(), parse_mode='html').message_id
			elif isinstance(self.image, StaticPhoto):
				msg = bot.send_photo(self.chat_id, photo=self.image.data, caption=self.text, reply_markup = self.get_keyboard_markup(), parse_mode='html')
				self.message_id = msg.message_id
				self.image = TelePhoto(message=msg)
		else:
			self.message_id = bot.send_message(self.chat_id, text=self.text, reply_markup=self.get_keyboard_markup(), parse_mode='html').message_id

	def clear(self):
		if self.message_id and self.chat_id:
			bot.delete_message(self.chat_id, self.message_id)
			self.message_id = None

	
	def update(self, new_text=None, new_button_alignment=None, new_image=None):
		if new_image:
			self.image = new_image
			if isinstance(self.image, TelePhoto):
				bot.edit_message_media(chat_id=self.chat_id, message_id=self.message_id, media=types.InputMediaPhoto(self.image.file_id))
			elif isinstance(self.image, StaticPhoto):
				msg = bot.edit_message_media(chat_id=self.chat_id, message_id=self.message_id, media=types.InputMediaPhoto(self.image.data))
				self.message_id = msg.message_id
				self.image = TelePhoto(message=msg)
		if new_text:
			self.text = new_text
		if new_button_alignment:
			self.button_alignment=new_button_alignment
		if self.image:
			bot.edit_message_caption(chat_id=self.chat_id, message_id=self.message_id, caption=self.text, reply_markup=self.get_keyboard_markup(), parse_mode='html')
		else:
			bot.edit_message_text(chat_id=self.chat_id, message_id=self.message_id, text=self.text, reply_markup=self.get_keyboard_markup(), parse_mode='html')
	def get_keyboard_markup(self):
		if self.is_location_requester:
			markup = types.ReplyKeyboardMarkup()
			markup.add(types.KeyboardButton(text='📍 Send location', request_location=True))
			return markup
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


@bot.callback_query_handler(func=lambda callback: callback.data)
def callback_handler(callback):
	user = User.USERS.get(callback.message.chat.id, None)
	if not user:
		return
	command, element_id = callback.data.split(';')
	element = Element.ELEMENTS[int(element_id)]
	match command:
		case 'b':
			element.callback(user, element)
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
		element, help_id = InputButton.INPUT_QUERY[message.chat.id]
		if element.input_type == InputButton.INPUT_TEXT and message.text:
			element.callback(user, message.text)
		if element.input_type == InputButton.INPUT_PHOTO and message.photo:
			element.callback(user, TelePhoto(message=message))
		element.delete_from_input_query(message.chat.id)


		user.update_last_interraction_time()

@bot.message_handler(content_types=['location'])
def location_handler(message):
	user = User.USERS.get(message.chat.id, None)
	if not user:
		return
	bot.delete_message(message.chat.id, message.id)
	_on_location_response(user, (message.location.latitude, message.location.longitude))
	user.update_last_interraction_time()

debug = True

def afk_checker():
	while True:
		user_ids = tuple(User.USERS.values())
		for user in user_ids:
			if not(user.afk) and time.time() - user.last_interraction_time > User.MAX_AFK_SECONDS:
				if _on_user_afk_detected:
					user.afk = True
					_on_user_afk_detected(user)
		time.sleep(User.AFK_CHECK_PERIOD)


async def messaging_task():
    thread = threading.Thread(target=bot.polling, daemon=True)
    thread.start()
    afk_checker_thread = threading.Thread(target=afk_checker)
    afk_checker_thread.start()

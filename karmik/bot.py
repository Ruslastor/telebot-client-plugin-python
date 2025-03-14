
import telebot_client_plugin as tp
import asyncio
import websockets
import threading

import subprocess

result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
print("Return code:", result.returncode)
print("Output:", result.stdout)
print("Error:", result.stderr)


WAIT_TIMEOUT : float = 0.01


class Peer:
	PEERS : dict = {}
	PEERS_COUNT : int = 0
	def __init__(self, socket):
		self.socket = socket
		self.messaging_task = asyncio.create_task(self.message_handler())
	@staticmethod
	def create_peer(socket):
		Peer.PEERS[socket] = Peer(socket)
		Peer.PEERS_COUNT +=1
	@staticmethod
	def delete_peer(socket):
		Peer.PEERS.pop(socket)
		Peer.PEERS_COUNT -=1
	async def message_handler(self):
		while True:
			client_message = await self.get_text()
			if client_message != "":
				print(f"got message from {self} : {client_message}")
				await self.send_text("hehehe")

	async def send_text(self, text):
		try:
			await asyncio.wait_for(self.socket.send(text), WAIT_TIMEOUT)
		except asyncio.TimeoutError:
			pass
		except websockets.ConnectionClosed:
			print(f"Connection closed for {self}")

	async def get_text(self):
		msg = ""
		try:
			msg = await asyncio.wait_for(self.socket.recv(), WAIT_TIMEOUT)
		except asyncio.TimeoutError:
			pass
		except websockets.ConnectionClosed:
			print(f"Connection closed for {self}")
		return msg






class Feeder:
	def __init__(self, peer):
		self.peer = peer
		self.online = False
	def feed(self, user):
		asyncio.run(self.peer.send_text("feed;"+user.user_data['feeding_times']))
















def switch_to_main(user, element):
	user.set_active_menues(['main'])
def switch_to_feeder(user, element):
	user.set_active_menues(['feeder'])
def switch_to_fermenter(user, element):
	pass


def feeder_feed(user, element):
	print(f"{user.name} wants to feed Mizi")
def feeder_set_feeding_count(user, inpt):
	user.menues['feeder'].update(new_text=f"Feed Mizi!\n\nFeed count: " + inpt)


def user_ready(user):
	print("user ready! : " + user.name)

	user.menues = {
		'main' : tp.Menue(user.chat_id, f"Welcome to Mizi Hub, {user.name}.", buttons={
				'feeder':tp.Button('Feed Mizi', switch_to_feeder),
				'fermenter':tp.Button('Fermenter', switch_to_fermenter)
			}, 
			initial_button_alignment=[['feeder'], ['fermenter']]
		),

		'feeder' : tp.Menue(user.chat_id, f"Feed Mizi!\n\nFeed count: 1", buttons={
				'feed':tp.Button('Feed!', feeder_feed),
				'feed_count':tp.InputButton('Set Feed Count', "Enter feed count..", feeder_set_feeding_count, tp.InputButton.INPUT_TEXT),
				'main':tp.Button('Back', switch_to_main)
			}, 
			initial_button_alignment=[['feed', 'feed_count'],['main']]
		),

		'afk' : tp.Menue(user.chat_id, f"Afk.., {user.name}.", buttons={
				'stop_afk':tp.Button('Back', switch_to_main),
			}, 
			initial_button_alignment=[['stop_afk']]
		)
	}
	user.set_active_menues(['main'])


def user_afk(user):
	print("user afk.. : " + user.name)
	user.set_active_menues(['afk'])


async def register(websocket):
	Peer.create_peer(websocket)
	print(f"new websocket detected, now available {Peer.PEERS_COUNT}")
	try:
		await websocket.wait_closed()
	finally:
		Peer.delete_peer(websocket)
		print(f"websocket deleted, now available: {Peer.PEERS_COUNT}")

async def main():
    ip = "192.168.134.33"
    port = 8765
    async with websockets.serve(register, ip, port):
        print(f"Server started on ws://{ip}:{port}")
        await tp.messaging_task()
        while True:  # Keeps the main function running
            await asyncio.sleep(0.1)

tp._on_user_initialization = user_ready
tp._on_user_afk_detected = user_afk

if __name__ == "__main__":
	asyncio.run(main())


import asyncio
import websockets




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
			client_message : str = ""
			try:
				client_message = await asyncio.wait_for(self.socket.recv(), WAIT_TIMEOUT)
			except asyncio.TimeoutError:
				continue
			except websockets.ConnectionClosed:
				print(f"Connection closed for {self}")
				break

			if client_message:
				print(f"got message from {self} : {client_message}")

			try:
				await asyncio.wait_for(self.socket.send("hehehe"), WAIT_TIMEOUT)
			except asyncio.TimeoutError:
				continue
			except websockets.ConnectionClosed:
				print(f"Connection closed for {self}")
				break

	async def send_text(self, text):
		try:
			await asyncio.wait_for(self.socket.send(text), WAIT_TIMEOUT)
			print("text sent")
		except websockets.ConnectionClosed:
			print(f"Connection closed for {self}")



async def register(websocket):
	Peer.create_peer(websocket)
	print(f"new websocket detected, now available {Peer.PEERS_COUNT}")
	try:
		await websocket.wait_closed()
	finally:
		Peer.delete_peer(websocket)
		print(f"websocket deleted, now available: {Peer.PEERS_COUNT}")









async def main():
    ip = "192.168.68.33"
    port = 8765
    async with websockets.serve(register, ip, port):
        print(f"Server started on ws://{ip}:{port}")
        await messaging_task()
        while True:  # Keeps the main function running
            await asyncio.sleep(1)


@bot.message_handler(content_types=['text','photo'])
def user_input_handler(message):
	bot.send_message(message.chat.id, text="got you message")
	if message.text == "run":
		keys = list(Peer.PEERS.keys())[0]
		asyncio.run(Peer.PEERS[keys].send_text("hujnia"))



if __name__ == "__main__":
	asyncio.run(main())





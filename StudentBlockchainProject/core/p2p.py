import asyncio
import websockets
import json

class P2PNode:
    def __init__(self, host, port, blockchain):
        self.host = host
        self.port = port
        self.blockchain = blockchain
        self.peers = set()

    async def start_server(self):
        """Ham start luồng"""
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()  # Run mãi mãi

    async def handler(self, websocket):
        """Ham lang nghe message"""
        async for message in websocket:
            try:
                data = json.loads(message)

                # 1. Lưu địa chỉ server thực tế của Node gửi (Handshake)
                if "sender_server" in data:
                    self.peers.add(data["sender_server"])

                # 2. Khi một Node mới yêu cầu đồng bộ Sổ cái (On-chain)
                if data['type'] == 'REQUEST_ONCHAIN_SYNC':
                    all_blocks = self.blockchain.db.get_all_blocks_raw()
                    await websocket.send(json.dumps({
                        "type": "RESPONSE_ONCHAIN_SYNC",
                        "payload": all_blocks
                    }))

                # 3. Khi nhận được 1 Block mới vừa được tạo (Real-time)
                elif data['type'] == 'SYNC_BLOCK':
                    self.blockchain.db.save_block(data['block'])

            except Exception as e:
                print(f"Lỗi xử lý tin nhắn: {e}")

    async def broadcast(self, message_dict):
        """Phát tán tin nhắn song song tới toàn bộ các peer"""
        # 1. Tự khai báo địa chỉ của mình để các node khác lưu lại
        message_dict["sender_server"] = f"ws://{self.host}:{self.port}"

        # 2. Tạo danh sách các tác vụ gửi tin nhắn song song
        tasks = [self._send_to_peer(peer, message_dict) for peer in list(self.peers)]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_to_peer(self, peer, message_dict):
        """Hàm gửi tin nhắn an toàn với timeout và xử lý đồng bộ"""
        try:
            async with websockets.connect(peer, open_timeout=5) as ws:
                await ws.send(json.dumps(message_dict))

                # Nếu là yêu cầu đồng bộ ban đầu, đợi nhận phản hồi
                if message_dict['type'] == 'REQUEST_ONCHAIN_SYNC':
                    response = await asyncio.wait_for(ws.recv(), timeout=10)
                    res_data = json.loads(response)
                    if res_data['type'] == 'RESPONSE_ONCHAIN_SYNC':
                        for b in res_data['payload']:
                            self.blockchain.db.save_block(b)
                        print(f"Đã đồng bộ xong {len(res_data['payload'])} khối từ {peer}")
        except Exception as e:
            print(f"Lỗi kết nối tới {peer}: {e}")

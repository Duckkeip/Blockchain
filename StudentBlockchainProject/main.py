from flask import Flask, request, jsonify, render_template
from core.blockchain import Blockchain
from core.wallet import Wallet
from database.db_manager import DBManager
from core.p2p import P2PNode
import sys, threading, asyncio, uuid
import hashlib

app = Flask(__name__, template_folder='web/templates')

# Danh sách các Node peer để kết nối ban đầu
BOOTSTRAP_PEERS = ["ws://127.0.0.1:6000", "ws://127.0.0.1:6001", "ws://127.0.0.1:6002"]

# Chạy: python main.py 5000 FACULTY 1
port = int(sys.argv[1])
role = sys.argv[2]
node_id = sys.argv[3]

db = DBManager(node_id)
blockchain = Blockchain(db, role)
wallet = Wallet()
p2p = P2PNode('localhost', port + 1000, blockchain)

# Biến toàn cục lưu Event Loop
global_p2p_loop = None

# --- ROUTES GIAO DIỆN ---
@app.route('/')
def index():
    if role == "LECTURER":
        return render_template('lecturer.html', port=port, node_id=node_id)
    elif role == "FACULTY":
        return render_template('faculty.html', port=port, node_id=node_id)
    elif role == "STUDENT":
        return render_template('student.html', port=port, node_id=node_id)
    elif role == "ADMIN":
        return render_template('admin.html', node_id=node_id)

# --- API XỬ LÝ OFF-CHAIN (DB TẬP TRUNG) ---
@app.route('/api/grades/add', methods=['POST'])
def add_grade():
    """Thêm điểm mới vào SQLite chung"""
    data = request.json
    id = str(uuid.uuid4())
    grade_data = {
        "id": id,
        "student_id": data['student_id'],
        "subject": data['subject'],
        "score": float(data['score']),
        "status": "PENDING",
        "hash": hashlib.sha256(f"{id}{data['student_id']}{data['subject']}{data['score']}".encode()).hexdigest()
    }

    # Lưu vào SQLite tập trung
    db.save_offchain_grade(grade_data)
    return jsonify({"status": "Success", "id": grade_data['id']})


@app.route('/api/grades/pending', methods=['GET'])
def get_pending():
    """Lấy danh sách điểm đang chờ duyệt từ DB tập trung"""
    cursor = db.sql_conn.execute("SELECT * FROM grades WHERE status='PENDING'")
    columns = [column[0] for column in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return jsonify(results)

@app.route('/api/grades/<student_id>', methods=['GET'])
def get_student_grades(student_id):
    """
    API tra cứu điểm cho sinh viên từ database tập trung
    """
    try:
        # Truy vấn tất cả các môn học của sinh viên dựa trên student_id
        query = "SELECT * FROM grades WHERE student_id = ?"
        cursor = db.sql_conn.execute(query, (student_id,))

        # Chuyển đổi kết quả từ tuple sang dictionary để trả về JSON
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return jsonify(results)
    except Exception as e:
        print(f"Lỗi tra cứu student_id {student_id}: {e}")
        return jsonify({"error": str(e)}), 500


# --- API XỬ LÝ ON-CHAIN & P2P ---
@app.route('/api/blockchain/approve', methods=['POST'])
def approve_grades():
    """Khoa duyệt điểm: Tạo Block và phát tán On-chain"""
    selected_ids = request.json.get('ids', [])
    if not selected_ids:
        return jsonify({"error": "No grades selected"}), 400

    # 1. Tạo Block mới chứa các ID giao dịch
    blockchain.pending_txs.extend(selected_ids)
    new_block = blockchain.create_block(wallet)

    # 2. Lưu Block vào sổ cái riêng của Node FACULTY
    db.save_block(new_block.to_dict())

    # 3. Cập nhật trạng thái trong SQLite chung sang APPROVED
    for g_id in selected_ids:
        db.update_offchain_status(g_id, "APPROVED")

    # 4. Phát tán Block mới tới các node khác (LECTURER, STUDENT)
    if global_p2p_loop:
        asyncio.run_coroutine_threadsafe(
            p2p.broadcast({
                "type": "SYNC_BLOCK",
                "block": new_block.to_dict()
            }),
            global_p2p_loop
        )
        print("Đã ra lệnh phát tán Block mới sang P2P Thread.")

    return jsonify({"status": "Approved & Block Mined", "block_index": new_block.index})

@app.route('/api/blockchain/blocks', methods=['GET'])
def get_blockchain_visual():
    """Lấy danh sách các block phục vụ hiển thị trực quan"""
    all_blocks = db.get_all_blocks_raw()
    return jsonify(all_blocks)

# --- LOGIC KHỞI CHẠY BẤT ĐỒNG BỘ ---
def run_p2p():
    """Chạy server P2P trong một thread riêng"""
    global global_p2p_loop
    global_p2p_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(global_p2p_loop)

    # Hàm tự động kết nối và xin Blocks khi vừa bật node
    async def start_and_sync():
        # Khởi động server lắng nghe
        server_task = asyncio.create_task(p2p.start_server())

        # Đợi server sẵn sàng
        await asyncio.sleep(2)
        my_p2p_addr = f"ws://127.0.0.1:{port + 1000}"

        for peer in BOOTSTRAP_PEERS:
            if peer != my_p2p_addr:
                p2p.peers.add(peer)

        # Gửi yêu cầu đồng bộ Sổ cái (On-chain)
        if p2p.peers:
            print(f"Node {node_id} đang yêu cầu đồng bộ Sổ cái On-chain...")
            await p2p.broadcast({"type": "REQUEST_ONCHAIN_SYNC"})

        await server_task

    global_p2p_loop.run_until_complete(start_and_sync())

if __name__ == '__main__':
    # Khởi chạy P2P Thread
    threading.Thread(target=run_p2p, daemon=True).start()

    # Khởi chạy App Web Server
    app.run(port=port, debug=False)

import sqlite3
import json
import os
from diskcache import Cache

class DBManager:
    def __init__(self, node_id):
        """Ham tao DB on-chain va off-chain"""
        os.makedirs("data_nodes", exist_ok=True)

        # On-chain
        self.onchain_path = f"data_nodes/node_{node_id}/onchain_data"
        os.makedirs(self.onchain_path, exist_ok=True)
        # Sử dụng DiskCache
        self.onchain_db = Cache(self.onchain_path)

        # Off-chain
        self.offchain_path = "data_nodes/offchain_data.db"
        # Sử dụng SQlite3 va tao table grades
        self.sql_conn = sqlite3.connect(self.offchain_path, check_same_thread=False)
        self._init_sql()

    def _init_sql(self):
        """Ham tao table grades trong DB off-chain"""
        self.sql_conn.execute("""
                    CREATE TABLE IF NOT EXISTS grades (
                        id TEXT PRIMARY KEY, 
                        student_id TEXT, 
                        subject TEXT, 
                        score REAL, 
                        status TEXT,
                        hash TEXT
                    )
                """)
        self.sql_conn.commit()

    # --- I. XỬ LÝ OFF-CHAIN TẬP TRUNG ---
    def save_offchain_grade(self, g_dict):
        """Lưu mới một record điểm (role LECTURER)"""
        query = """
            INSERT INTO grades (id, student_id, subject, score, status, hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.sql_conn.execute(query, (
            g_dict['id'], g_dict['student_id'], g_dict['subject'],
            g_dict['score'], g_dict.get('status', 'PENDING'), g_dict['hash']
        ))
        self.sql_conn.commit()
        print(f"Off-chain: Đã lưu điểm cho SV {g_dict['student_id']}")

    def update_offchain_status(self, grade_id, new_status):
        """Cập nhật status điểm (khi FACULTY duyệt vào Block)"""
        query = "UPDATE grades SET status = ? WHERE hash = ?"
        self.sql_conn.execute(query, (new_status, grade_id))
        self.sql_conn.commit()
        print(f"Off-chain: Đã cập nhật trạng thái {new_status} cho ID {grade_id}")

    # --- II. XỬ LÝ ON-CHAIN ĐỒNG BỘ ---
    def get_all_blocks_raw(self):
        """Lấy toàn bộ các Block để đồng bộ cho Node mới tham gia"""
        blocks = []
        last_idx = self.get_last_index()
        if last_idx is not None:
            for i in range(int(last_idx) + 1):
                block = self.get_block(i)
                if block:
                    blocks.append(block)
        return blocks

    def save_block(self, b_dict):
        """Lưu mới một block vao DB  on-chain (Cache)"""
        if not b_dict:
            return
        self.onchain_db[f"block_{b_dict['index']}"] = json.dumps(b_dict)
        self.onchain_db['last_index'] = b_dict['index']

    def get_block(self, idx):
        """Lay một block tư DB  on-chain (Cache)"""
        data = self.onchain_db.get(f"block_{idx}")
        return json.loads(data) if data else None

    def get_last_index(self):
        """Lay block cuối tư DB  on-chain (Cache)"""
        return self.onchain_db.get('last_index')

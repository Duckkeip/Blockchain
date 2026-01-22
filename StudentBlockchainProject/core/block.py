import hashlib
import json
import time

class Block:
    def __init__(self, index, transactions, previous_hash, validator="", signature="", timestamp=None):
        self.index = index
        self.transactions = transactions  # Danh sách ID giao dịch (hashes)
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.validator = validator  # Public Key của node phê duyệt (Faculty)
        self.signature = signature  # Chữ ký số của Faculty cho khối
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.calculate_hash()

    def calculate_merkle_root(self):
        """Tính Merkle Root từ danh sách ID giao dịch"""
        if not self.transactions:
            return "0"

        # Sao chép danh sách hash giao dịch để xử lý
        hashes = [str(tx) for tx in self.transactions]

        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])

            new_level = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()
                new_level.append(new_hash)
            hashes = new_level

        return hashes[0]

    def calculate_hash(self):
        """Tính mã Hash cho Block"""
        content = {
            "index": self.index,
            "merkle_root": self.merkle_root,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "validator": self.validator
        }
        return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()

    def to_dict(self):
        """Chuyển Block về dictionary"""
        return self.__dict__
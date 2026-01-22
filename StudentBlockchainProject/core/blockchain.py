from core.block import Block

class Blockchain:
    def __init__(self, db_manager, role):
        self.db = db_manager
        self.role = role
        self.pending_txs = []
        self._init_genesis()

    def _init_genesis(self):
        """Ham tao khoi dau tien"""
        if self.db.get_last_index() is None:
            genesis = Block(0, [], "0", "SYSTEM", "GENESIS_SIG")
            self.db.save_block(genesis.to_dict())

    def create_block(self, wallet):
        """Ham tao 1 khoi  moi"""
        if self.role != "FACULTY":
            raise PermissionError("Chỉ Faculty mới có quyền duyệt")

        if not self.pending_txs:
            return None

        last_idx = self.db.get_last_index()
        last_block = self.db.get_block(last_idx)

        new_block = Block(
            index=last_block['index'] + 1,
            transactions=self.pending_txs,
            previous_hash=last_block['hash'],
            validator=wallet.get_public_key_pem()
        )
        new_block.signature = wallet.sign_message(new_block.hash)
        self.db.save_block(new_block.to_dict())
        self.pending_txs = []
        return new_block

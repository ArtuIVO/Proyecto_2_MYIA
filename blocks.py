import os, json, uuid

BLOCKS_DIR = "fat_storage/blocks"
MAX_BLOCK_SIZE = 20

def ensure_blocks_dir():
    os.makedirs(BLOCKS_DIR, exist_ok=True)

def create_block(content, next_path=None, eof=False):
    ensure_blocks_dir()
    block_id = str(uuid.uuid4()) + ".json"
    path = os.path.join(BLOCKS_DIR, block_id)
    block = {"datos": content, "siguiente_archivo": next_path, "eof": eof}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(block, f, indent=2, ensure_ascii=False)
    return path

def read_block(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def delete_block_file(path):
    try:
        os.remove(path)
    except:
        pass

import os, json

USERS_FILE = "fat_storage/users.json"

def init_users():
    os.makedirs("fat_storage", exist_ok=True)
    if not os.path.exists(USERS_FILE):
        admin = {
            "username": "admin",
            "password": "admin",
            "owner_of": [],
            "is_admin": True
        }
        data = {"users": [admin], "permissions": {}}
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def find_user(username):
    data = load_users()
    for u in data["users"]:
        if u["username"] == username:
            return u
    return None

def check_credentials(username, password):
    u = find_user(username)
    if not u:
        return False
    return u["password"] == password

def create_user(username, password, creator):
    data = load_users()
    if find_user(username):
        return False, "usuario ya existe"
    user = {"username": username, "password": password, "owner_of": [], "is_admin": False}
    data["users"].append(user)
    save_users(data)
    return True, "usuario creado"

def assign_permission(file_name, owner_username, target_username, read=False, write=False, revoke=False):
    data = load_users()
    perms = data.get("permissions", {})
    if revoke:
        if file_name in perms and target_username in perms[file_name]:
            perms[file_name].pop(target_username, None)
    else:
        perms.setdefault(file_name, {})
        perms[file_name][target_username] = {"read": bool(read), "write": bool(write)}
    data["permissions"] = perms
    save_users(data)
    return True, "permiso actualizado"

def get_permissions_for(file_name):
    data = load_users()
    return data.get("permissions", {}).get(file_name, {})

def user_has_read(user, file_name, owner):
    if user == owner:
        return True
    perms = get_permissions_for(file_name)
    return perms.get(user, {}).get("read", False)

def user_has_write(user, file_name, owner):
    if user == owner:
        return True
    perms = get_permissions_for(file_name)
    return perms.get(user, {}).get("write", False)

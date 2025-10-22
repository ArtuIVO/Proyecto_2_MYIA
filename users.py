import os, json

USERS_FILE = "fat_storage/users.json"

def init_users():
    os.makedirs("fat_storage", exist_ok=True)
    if not os.path.exists(USERS_FILE):
        admin = {"username": "admin", "password": "admin", "owner_of": [], "is_admin": True}
        data = {"users": [admin]}
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

def create_user(username, password, creator="admin"):
    if not username or not password:
        return False, "no se permiten campos vacíos"
    data = load_users()
    if any(u["username"] == username for u in data["users"]):
        return False, "usuario ya existe"
    if creator != "admin":
        creador_data = find_user(creator)
        if not creador_data or not creador_data.get("is_admin"):
            return False, "solo el admin puede crear usuarios"
    user = {"username": username, "password": password, "owner_of": [], "is_admin": False}
    data["users"].append(user)
    save_users(data)
    return True, "usuario creado"

def toggle_admin_status(admin_username, target_username, make_admin):
    data = load_users()
    admin = next((u for u in data["users"] if u["username"] == admin_username), None)
    if not admin or not admin.get("is_admin"):
        return False, "solo el administrador puede cambiar roles"
    for u in data["users"]:
        if u["username"] == target_username:
            u["is_admin"] = bool(make_admin)
            save_users(data)
            return True, "rol actualizado"
    return False, "usuario no encontrado"

def validar_usuario(username, password):
    return check_credentials(username, password)

def crear_usuario(nombre, clave):
    return create_user(nombre, clave, creator="admin")

def asignar_permiso(owner, target, admin_state):
    return toggle_admin_status(owner, target, admin_state)

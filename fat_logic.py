import os, json
from datetime import datetime
from blocks import create_block, read_block, delete_block_file, MAX_BLOCK_SIZE
from users import user_has_read, user_has_write, load_users, save_users

FAT_DIR = "fat_storage/fats"

def ensure_dirs():
    os.makedirs(FAT_DIR, exist_ok=True)

def now():
    return datetime.now().isoformat()

def split_blocks(texto):
    bloques = []
    i = 0
    while i < len(texto):
        parte = texto[i:i+MAX_BLOCK_SIZE]
        bloques.append(parte)
        i += MAX_BLOCK_SIZE
    return bloques

def vaciar_papelera():
    ensure_dirs()
    fats = os.listdir(FAT_DIR)
    for f in fats:
        if not f.endswith(".fat.json"):
            continue
        ruta_fat = os.path.join(FAT_DIR, f)
        try:
            with open(ruta_fat, "r", encoding="utf-8") as arch:
                data = json.load(arch)
        except:
            continue

        if data.get("papelera"):
            bloque_actual = data.get("ruta_inicial")
            while bloque_actual and os.path.exists(bloque_actual):
                try:
                    with open(bloque_actual, "r", encoding="utf-8") as fb:
                        bloque_data = json.load(fb)
                    siguiente = bloque_data.get("siguiente_archivo")
                    os.remove(bloque_actual)
                    bloque_actual = siguiente
                except:
                    break

            try:
                os.remove(ruta_fat)
            except:
                pass
    fat_path = "fat_table.json"
    if not os.path.exists(fat_path):
        return

    with open(fat_path, "r") as f:
        try:
            fat_data = json.load(f)
        except:
            fat_data = []

    nuevos_archivos = []

    for archivo in fat_data:
        if archivo.get("papelera") is True:
            bloque_actual = archivo.get("ruta_inicial")
            while bloque_actual and os.path.exists(bloque_actual):
                try:
                    with open(bloque_actual, "r") as fb:
                        bloque_data = json.load(fb)
                    siguiente = bloque_data.get("siguiente")
                    os.remove(bloque_actual)
                    bloque_actual = siguiente
                except Exception as e:
                    break
        else:
            nuevos_archivos.append(archivo)

    with open(fat_path, "w") as f:
        json.dump(nuevos_archivos, f, indent=4)

def fat_path(nombre):
    return os.path.join(FAT_DIR, nombre.replace("/", "_") + ".fat.json")

def guardar_fat(nombre, data):
    with open(fat_path(nombre), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def cargar_fat(nombre):
    try:
        with open(fat_path(nombre), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def crear_archivo(nombre, contenido, owner):
    ensure_dirs()
    if cargar_fat(nombre):
        return False, "ya existe"
    bloques = split_blocks(contenido)
    anterior = None
    inicio = None
    for i, parte in enumerate(reversed(bloques)):
        eof = (i == 0)
        ruta = create_block(parte, anterior, eof)
        anterior = ruta
        inicio = ruta
    fat = {
        "nombre": nombre,
        "ruta_inicial": inicio,
        "papelera": False,
        "caracteres": len(contenido),
        "fecha_creacion": now(),
        "fecha_modificacion": now(),
        "fecha_eliminacion": None,
        "owner": owner
    }
    guardar_fat(nombre, fat)
    data = load_users()
    for u in data["users"]:
        if u["username"] == owner:
            u.setdefault("owner_of", []).append(nombre)
    save_users(data)
    return True, "archivo creado"

def leer_contenido(fat):
    partes = []
    p = fat["ruta_inicial"]
    while p:
        b = read_block(p)
        if not b:
            break
        partes.append(b["datos"])
        if b["eof"]:
            break
        p = b["siguiente_archivo"]
    return "".join(partes)

def modificar_archivo(nombre, nuevo_contenido, user):
    fat = cargar_fat(nombre)
    if not fat:
        return False, "no existe"
    if not user_has_write(user, nombre, fat["owner"]):
        return False, "sin permiso"
    viejo = fat["ruta_inicial"]
    bloques = split_blocks(nuevo_contenido)
    anterior = None
    inicio = None
    for i, parte in enumerate(reversed(bloques)):
        eof = (i == 0)
        ruta = create_block(parte, anterior, eof)
        anterior = ruta
        inicio = ruta
    fat["ruta_inicial"] = inicio
    fat["caracteres"] = len(nuevo_contenido)
    fat["fecha_modificacion"] = now()
    guardar_fat(nombre, fat)
    eliminar_bloques(viejo)
    return True, "modificado"

def eliminar_bloques(ruta):
    p = ruta
    while p:
        b = read_block(p)
        if not b:
            delete_block_file(p)
            break
        sig = b.get("siguiente_archivo")
        delete_block_file(p)
        if not sig:
            break
        p = sig

def eliminar_logico(nombre, user):
    fat = cargar_fat(nombre)
    if not fat:
        return False, "no existe"
    if fat["owner"] != user:
        return False, "solo el owner puede"
    fat["papelera"] = True
    fat["fecha_eliminacion"] = now()
    guardar_fat(nombre, fat)
    return True, "movido a papelera"

def recuperar(nombre, user):
    fat = cargar_fat(nombre)
    if not fat:
        return False, "no existe"
    if fat["owner"] != user:
        return False, "solo el owner puede"
    fat["papelera"] = False
    fat["fecha_modificacion"] = now()
    fat["fecha_eliminacion"] = None
    guardar_fat(nombre, fat)
    return True, "recuperado"

def listar(only_active=True):
    ensure_dirs()
    lista = []
    for f in os.listdir(FAT_DIR):
        if f.endswith(".fat.json"):
            ruta = os.path.join(FAT_DIR, f)
            with open(ruta, "r", encoding="utf-8") as arch:
                data = json.load(arch)
                if only_active and data["papelera"]:
                    continue
                lista.append(data)
    return lista

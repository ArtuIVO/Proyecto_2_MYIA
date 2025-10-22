import os
import json
from datetime import datetime

BASE_DIR = "archivos"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

FAT_FILE = os.path.join(BASE_DIR, "fat_table.json")

def _cargar_tabla():
    if not os.path.exists(FAT_FILE):
        return []
    with open(FAT_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def _guardar_tabla(tabla):
    with open(FAT_FILE, "w", encoding="utf-8") as f:
        json.dump(tabla, f, indent=4, ensure_ascii=False)

def _buscar_archivo(nombre, tabla=None):
    if tabla is None:
        tabla = _cargar_tabla()
    for a in tabla:
        if a["nombre"] == nombre:
            return a
    return None

def listar(incluir_activos=True):
    """Devuelve lista de archivos, incluyendo activos o papelera."""
    tabla = _cargar_tabla()
    if incluir_activos:
        return [a for a in tabla if not a.get("papelera", False)]
    else:
        return [a for a in tabla if a.get("papelera", False)]

def crear_archivo(nombre, contenido, owner):
    tabla = _cargar_tabla()
    if _buscar_archivo(nombre, tabla):
        return False, "Ya existe un archivo con ese nombre."

    ruta = os.path.join(BASE_DIR, f"{nombre}.txt")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)

    metadata = {
        "nombre": nombre,
        "ruta": ruta,
        "owner": owner,
        "creado": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modificado": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tamano": len(contenido.encode("utf-8")),
        "papelera": False
    }
    tabla.append(metadata)
    _guardar_tabla(tabla)
    return True, f"Archivo '{nombre}' creado correctamente."

def leer_contenido(fat_entry):
    """Lee contenido desde una entrada FAT."""
    ruta = fat_entry["ruta"]
    if not os.path.exists(ruta):
        return ""
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()

def modificar_archivo(nombre, nuevo_contenido, usuario, is_admin=False):
    tabla = _cargar_tabla()
    archivo = _buscar_archivo(nombre, tabla)
    if not archivo:
        return False, "El archivo no existe."
    if archivo["papelera"]:
        return False, "El archivo está en la papelera."
    if not is_admin and archivo["owner"] != usuario:
        return False, "No tiene permisos para modificar este archivo."

    with open(archivo["ruta"], "w", encoding="utf-8") as f:
        f.write(nuevo_contenido)

    archivo["modificado"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    archivo["tamano"] = len(nuevo_contenido.encode("utf-8"))
    _guardar_tabla(tabla)
    return True, f"Archivo '{nombre}' modificado correctamente."

def eliminar_logico(nombre, usuario, is_admin=False):
    tabla = _cargar_tabla()
    archivo = _buscar_archivo(nombre, tabla)
    if not archivo:
        return False, "El archivo no existe."
    if not is_admin and archivo["owner"] != usuario:
        return False, "No tiene permisos para eliminar este archivo."
    if archivo["papelera"]:
        return False, "El archivo ya está en la papelera."

    archivo["papelera"] = True
    archivo["modificado"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _guardar_tabla(tabla)
    return True, f"Archivo '{nombre}' movido a la papelera."

def recuperar(nombre, usuario):
    tabla = _cargar_tabla()
    archivo = _buscar_archivo(nombre, tabla)
    if not archivo:
        return False, "El archivo no existe."
    if not archivo.get("papelera", False):
        return False, "El archivo no está en la papelera."

    archivo["papelera"] = False
    archivo["modificado"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _guardar_tabla(tabla)
    return True, f"Archivo '{nombre}' recuperado."

def vaciar_papelera():
    tabla = _cargar_tabla()
    nuevos = []
    eliminados = []
    for a in tabla:
        if a.get("papelera", False):
            try:
                if os.path.exists(a["ruta"]):
                    os.remove(a["ruta"])
                eliminados.append(a["nombre"])
            except Exception:
                pass
        else:
            nuevos.append(a)
    _guardar_tabla(nuevos)
    return True, f"Papelera vaciada. Se eliminaron {len(eliminados)} archivos."

def cargar_fat(nombre):
    tabla = _cargar_tabla()
    archivo = _buscar_archivo(nombre, tabla)
    return archivo

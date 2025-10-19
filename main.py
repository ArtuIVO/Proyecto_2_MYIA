from users import init_users, check_credentials, create_user, find_user, assign_permission, get_permissions_for
from fat_logic import crear_archivo, leer_contenido, modificar_archivo, eliminar_logico, recuperar, listar, cargar_fat
import os

init_users()
usuario_actual = None

while True:
    if not usuario_actual:
        print("\n--- LOGIN ---")
        u = input("Usuario: ").strip()
        p = input("Contraseña: ").strip()
        if check_credentials(u, p):
            usuario_actual = u
            print("Bienvenido,", u)
        else:
            print("Credenciales incorrectas")
        continue

    print(f"\n[{usuario_actual}] Comandos:")
    print("crear, listar, papelera, abrir, modificar, eliminar, recuperar, permisos, crearuser, logout, salir")

    cmd = input(">> ").strip().lower()

    if cmd == "salir":
        break

    if cmd == "logout":
        usuario_actual = None
        continue

    if cmd == "crear":
        nombre = input("Nombre archivo: ").strip()
        print("Contenido (finaliza con .END):")
        lineas = []
        while True:
            t = input()
            if t.strip() == ".END":
                break
            lineas.append(t)
        texto = "\n".join(lineas)
        ok, msg = crear_archivo(nombre, texto, usuario_actual)
        print(msg)

    elif cmd == "listar":
        archivos = listar(True)
        if not archivos:
            print("No hay archivos.")
        else:
            for a in archivos:
                print(f"- {a['nombre']} (owner: {a['owner']})")

    elif cmd == "papelera":
        pap = listar(False)
        papel = [a for a in pap if a["papelera"]]
        if not papel:
            print("Papelera vacía.")
        else:
            for a in papel:
                print(f"- {a['nombre']} eliminado: {a['fecha_eliminacion']}")

    elif cmd == "abrir":
        nombre = input("Archivo: ").strip()
        fat = cargar_fat(nombre)
        if not fat:
            print("no existe")
            continue
        from users import user_has_read
        if not user_has_read(usuario_actual, nombre, fat["owner"]):
            print("sin permiso de lectura")
            continue
        if fat["papelera"]:
            print("archivo en papelera")
            continue
        print("\n--- CONTENIDO ---")
        print(leer_contenido(fat))

    elif cmd == "modificar":
        nombre = input("Archivo: ").strip()
        from users import user_has_write
        fat = cargar_fat(nombre)
        if not fat:
            print("no existe")
            continue
        if not user_has_write(usuario_actual, nombre, fat["owner"]):
            print("sin permiso de escritura")
            continue
        print("Nuevo contenido (.END para terminar):")
        lineas = []
        while True:
            t = input()
            if t.strip() == ".END":
                break
            lineas.append(t)
        texto = "\n".join(lineas)
        ok, msg = modificar_archivo(nombre, texto, usuario_actual)
        print(msg)

    elif cmd == "eliminar":
        nombre = input("Archivo: ").strip()
        ok, msg = eliminar_logico(nombre, usuario_actual)
        print(msg)

    elif cmd == "recuperar":
        nombre = input("Archivo: ").strip()
        ok, msg = recuperar(nombre, usuario_actual)
        print(msg)

    elif cmd == "crearuser":
        u = find_user(usuario_actual)
        if not u or not u.get("is_admin"):
            print("solo admin puede crear usuarios")
            continue
        n = input("Nuevo usuario: ").strip()
        p = input("Contraseña: ").strip()
        ok, msg = create_user(n, p, usuario_actual)
        print(msg)

    elif cmd == "permisos":
        nombre = input("Archivo: ").strip()
        fat = cargar_fat(nombre)
        if not fat:
            print("no existe")
            continue
        if fat["owner"] != usuario_actual:
            print("solo el owner puede asignar permisos")
            continue
        t = input("Usuario destino: ").strip()
        act = input("¿Revocar? (s/n): ").strip().lower()
        if act == "s":
            ok, msg = assign_permission(nombre, usuario_actual, t, revoke=True)
            print(msg)
        else:
            r = input("Lectura? (s/n): ").strip().lower()
            w = input("Escritura? (s/n): ").strip().lower()
            ok, msg = assign_permission(nombre, usuario_actual, t, read=(r=="s"), write=(w=="s"))
            print(msg)

    else:
        print("Comando no reconocido")

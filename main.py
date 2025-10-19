from users import init_users, check_credentials, create_user, find_user, assign_permission, get_permissions_for
from fat_logic import crear_archivo, leer_contenido, modificar_archivo, eliminar_logico, recuperar, listar, cargar_fat
import os

init_users()
usuario_actual = None

while True:
    if not usuario_actual:
        print("\n===== INICIO DE SESIÓN =====")
        u = input("Usuario: ").strip()
        p = input("Contraseña: ").strip()
        if check_credentials(u, p):
            usuario_actual = u
            print("Bienvenido,", u)
        else:
            print("Credenciales incorrectas")
        continue

    print(f"\n=== MENÚ PRINCIPAL ({usuario_actual}) ===")
    print("1. Crear archivo")
    print("2. Listar archivos")
    print("3. Ver papelera")
    print("4. Abrir archivo")
    print("5. Modificar archivo")
    print("6. Eliminar archivo (mover a papelera)")
    print("7. Recuperar archivo")
    print("8. Asignar permisos")
    print("9. Crear usuario (solo admin)")
    print("10. Cerrar sesión")
    print("0. Salir del programa")

    opcion = input("\nElige una opción: ").strip()

    if opcion == "0":
        print("Saliendo...")
        break

    if opcion == "10":
        usuario_actual = None
        continue

    if opcion == "1":
        nombre = input("Nombre del archivo: ").strip()
        print("Escribe el contenido (finaliza con .END):")
        lineas = []
        while True:
            t = input()
            if t.strip() == ".END":
                break
            lineas.append(t)
        texto = "\n".join(lineas)
        ok, msg = crear_archivo(nombre, texto, usuario_actual)
        print(msg)

    elif opcion == "2":
        archivos = listar(True)
        if not archivos:
            print("No hay archivos.")
        else:
            for a in archivos:
                print(f"- {a['nombre']} (owner: {a['owner']})")

    elif opcion == "3":
        pap = listar(False)
        papel = [a for a in pap if a["papelera"]]
        if not papel:
            print("Papelera vacía.")
        else:
            for a in papel:
                print(f"- {a['nombre']} eliminado: {a['fecha_eliminacion']}")

    elif opcion == "4":
        nombre = input("Nombre del archivo: ").strip()
        fat = cargar_fat(nombre)
        if not fat:
            print("Archivo no existe")
            continue
        from users import user_has_read
        if not user_has_read(usuario_actual, nombre, fat["owner"]):
            print("No tienes permiso de lectura")
            continue
        if fat["papelera"]:
            print("El archivo está en la papelera")
            continue
        print("\n--- CONTENIDO ---")
        print(leer_contenido(fat))

    elif opcion == "5":
        nombre = input("Archivo a modificar: ").strip()
        from users import user_has_write
        fat = cargar_fat(nombre)
        if not fat:
            print("No existe ese archivo")
            continue
        if not user_has_write(usuario_actual, nombre, fat["owner"]):
            print("No tienes permiso de escritura")
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

    elif opcion == "6":
        nombre = input("Archivo a eliminar: ").strip()
        ok, msg = eliminar_logico(nombre, usuario_actual)
        print(msg)

    elif opcion == "7":
        nombre = input("Archivo a recuperar: ").strip()
        ok, msg = recuperar(nombre, usuario_actual)
        print(msg)

    elif opcion == "8":
        nombre = input("Archivo: ").strip()
        fat = cargar_fat(nombre)
        if not fat:
            print("No existe")
            continue
        if fat["owner"] != usuario_actual:
            print("Solo el dueño puede asignar permisos")
            continue
        t = input("Usuario destino: ").strip()
        act = input("¿Revocar permiso? (s/n): ").strip().lower()
        if act == "s":
            ok, msg = assign_permission(nombre, usuario_actual, t, revoke=True)
            print(msg)
        else:
            r = input("Dar permiso de lectura? (s/n): ").strip().lower()
            w = input("Dar permiso de escritura? (s/n): ").strip().lower()
            ok, msg = assign_permission(nombre, usuario_actual, t, read=(r == "s"), write=(w == "s"))
            print(msg)

    elif opcion == "9":
        u = find_user(usuario_actual)
        if not u or not u.get("is_admin"):
            print("Solo el administrador puede crear usuarios")
            continue
        n = input("Nuevo usuario: ").strip()
        p = input("Contraseña: ").strip()
        ok, msg = create_user(n, p, usuario_actual)
        print(msg)

    else:
        print("Opción inválida, intenta de nuevo.")

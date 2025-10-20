from fat_logic import crear_archivo, listar, leer_contenido, modificar_archivo, eliminar_logico, recuperar, cargar_fat, vaciar_papelera
from users import init_users, check_credentials, create_user, assign_permission, find_user, user_has_read, user_has_write

init_users()
usuario_actual = None

while True:
    if not usuario_actual:
        print("\n=== LOGIN ===")
        u = input("Usuario: ").strip()
        p = input("Contraseña: ").strip()
        if not u or not p:
            print("Error: Usuario o contraseña vacíos.")
            continue
        if check_credentials(u, p):
            usuario_actual = u
            print(f"Bienvenido, {usuario_actual}")
        else:
            print("Error: Credenciales incorrectas.")
        continue

    print(f"\n=== MENU PRINCIPAL (Usuario: {usuario_actual}) ===")
    print("1. Crear archivo")
    print("2. Listar archivos")
    print("3. Abrir archivo")
    print("4. Modificar archivo")
    print("5. Eliminar archivo (mover a papelera)")
    print("6. Mostrar papelera")
    print("7. Recuperar archivo desde papelera")
    print("8. Vaciar papelera")
    print("9. Asignar permisos")
    print("10. Crear usuario (solo admin)")
    print("11. Cerrar sesión")
    print("12. Salir del sistema")

    opcion = input("Selecciona una opción: ").strip()

    if opcion == "1":
        nombre = input("Nombre del archivo: ").strip()
        if not nombre:
            print("Error: El nombre no puede estar vacío.")
            continue
        texto = input("Contenido del archivo: ").strip()
        if not texto:
            print("Error: El contenido no puede estar vacío.")
            continue
        ok, msg = crear_archivo(nombre, texto, usuario_actual)
        print(msg)

    elif opcion == "2":
        print("\nArchivos activos:")
        archivos = listar(True)
        activos = [a for a in archivos if not a["papelera"]]
        if not activos:
            print("No hay archivos disponibles.")
        else:
            for a in activos:
                print(f"- {a['nombre']} (Owner: {a['owner']})")

    elif opcion == "3":
        nombre = input("Nombre del archivo a abrir: ").strip()
        fat = cargar_fat(nombre)
        if not fat:
            print("Error: El archivo no existe.")
            continue
        if fat["papelera"]:
            print("Error: El archivo está en la papelera.")
            continue
        if not user_has_read(usuario_actual, nombre, fat["owner"]):
            print("Error: No tienes permiso de lectura.")
            continue
        contenido = leer_contenido(fat)
        print("\nContenido del archivo:")
        print(contenido)

    elif opcion == "4":
        nombre = input("Archivo a modificar: ").strip()
        fat = cargar_fat(nombre)
        if not fat:
            print("Error: El archivo no existe.")
            continue
        if not user_has_write(usuario_actual, nombre, fat["owner"]):
            print("Error: No tienes permiso de escritura.")
            continue
        nuevo = input("Nuevo contenido: ").strip()
        if not nuevo:
            print("Error: El contenido no puede estar vacío.")
            continue
        ok, msg = modificar_archivo(nombre, nuevo, usuario_actual)
        print(msg)

    elif opcion == "5":
        nombre = input("Archivo a eliminar: ").strip()
        ok, msg = eliminar_logico(nombre, usuario_actual)
        print(msg)

    elif opcion == "6":
        print("\nArchivos en papelera:")
        archivos = listar(False)
        papelera = [a for a in archivos if a["papelera"]]
        if not papelera:
            print("La papelera está vacía.")
        else:
            for a in papelera:
                print(f"- {a['nombre']} (Owner: {a['owner']})")

    elif opcion == "7":
        nombre = input("Archivo a recuperar: ").strip()
        ok, msg = recuperar(nombre, usuario_actual)
        print(msg)

    elif opcion == "8":
        confirm = input("¿Seguro que deseas vaciar la papelera? (s/n): ").strip().lower()
        if confirm == "s":
            vaciar_papelera()
            print("Papelera vaciada correctamente.")
        else:
            print("Operación cancelada.")

    elif opcion == "9":
        nombre = input("Archivo al que asignar permisos: ").strip()
        fat = cargar_fat(nombre)
        if not fat:
            print("Error: El archivo no existe.")
            continue
        if fat["owner"] != usuario_actual:
            print("Error: Solo el propietario puede asignar permisos.")
            continue
        usuario_destino = input("Usuario destino: ").strip()
        if not usuario_destino:
            print("Error: Usuario inválido.")
            continue
        r = input("¿Dar permiso de lectura? (s/n): ").strip().lower() == "s"
        w = input("¿Dar permiso de escritura? (s/n): ").strip().lower() == "s"
        ok, msg = assign_permission(nombre, usuario_actual, usuario_destino, read=r, write=w)
        print(msg)

    elif opcion == "10":
        u = find_user(usuario_actual)
        if not u or not u.get("is_admin"):
            print("Error: Solo el administrador puede crear usuarios.")
            continue
        nuevo = input("Nombre del nuevo usuario: ").strip()
        clave = input("Contraseña del nuevo usuario: ").strip()
        if not nuevo or not clave:
            print("Error: Usuario o contraseña no válidos.")
            continue
        ok, msg = create_user(nuevo, clave, usuario_actual)
        print(msg)

    elif opcion == "11":
        usuario_actual = None
        print("Sesión cerrada correctamente.")

    elif opcion == "12":
        print("Saliendo del sistema...")
        break

    else:
        print("Opción no válida. Intenta de nuevo.")

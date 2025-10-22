import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from fat_logic import crear_archivo, listar, leer_contenido, modificar_archivo, eliminar_logico, recuperar, vaciar_papelera
from users import validar_usuario, find_user, crear_usuario, asignar_permiso, load_users

usuario_actual = None

def refrescar_listas():
    lista_archivos.delete(0, tk.END)
    lista_papelera.delete(0, tk.END)
    for a in listar(True):
        lista_archivos.insert(tk.END, a["nombre"])
    for a in listar(False):
        if a["papelera"]:
            lista_papelera.insert(tk.END, a["nombre"])

def mostrar_usuarios():
    data = load_users()
    win = tk.Toplevel(ventana)
    win.title("Usuarios y Roles")
    win.geometry("400x300")
    lista = tk.Listbox(win, width=50, height=15, bg="#303030", fg="white", font=("Arial", 11))
    lista.pack(padx=10, pady=10)
    for u in data["users"]:
        rol = "Administrador" if u.get("is_admin", False) else "Usuario"
        lista.insert(tk.END, f"{u['username']} - {rol}")

def actualizar_visibilidad_botones():
    global boton_crear_usuario, boton_asignar_permiso, boton_recuperar, boton_mostrar_usuarios
    if not usuario_actual:
        boton_crear_usuario.grid_remove()
        boton_asignar_permiso.grid_remove()
        boton_recuperar.grid_remove()
        boton_mostrar_usuarios.grid_remove()
        return
    u = find_user(usuario_actual)
    es_admin = u.get("is_admin", False)  # type: ignore
    if es_admin:
        boton_crear_usuario.grid()
        boton_asignar_permiso.grid()
        boton_recuperar.grid()
        boton_mostrar_usuarios.grid()
    else:
        boton_crear_usuario.grid_remove()
        boton_asignar_permiso.grid_remove()
        boton_recuperar.grid_remove()
        boton_mostrar_usuarios.grid_remove()

def login_usuario():
    global usuario_actual
    nombre = simpledialog.askstring("Login", "Nombre de usuario:")
    clave = simpledialog.askstring("Login", "Contraseña:", show="*")
    if not nombre or not clave:
        messagebox.showerror("Error", "No puede haber campos vacíos")
        return
    if validar_usuario(nombre, clave):
        usuario_actual = nombre
        messagebox.showinfo("Bienvenido", f"Inicio de sesión como {usuario_actual}")
        refrescar_listas()
        actualizar_visibilidad_botones()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

def crear_archivo_ui():
    if not usuario_actual:
        messagebox.showerror("Error", "Debe iniciar sesión")
        return
    nombre = simpledialog.askstring("Crear archivo", "Nombre del archivo:")
    if not nombre:
        messagebox.showerror("Error", "El nombre no puede estar vacío")
        return
    win = tk.Toplevel(ventana)
    win.title("Contenido del archivo")
    txt = scrolledtext.ScrolledText(win, width=60, height=15, font=("Arial", 11))
    txt.pack(padx=10, pady=10)
    def guardar():
        contenido = txt.get("1.0", tk.END).strip()
        if not contenido:
            messagebox.showerror("Error", "El contenido no puede estar vacío")
            return
        ok, msg = crear_archivo(nombre, contenido, usuario_actual)
        messagebox.showinfo("Resultado", msg)
        win.destroy()
        refrescar_listas()
    tk.Button(win, text="Guardar", command=guardar).pack(pady=5)

def abrir_archivo():
    if not usuario_actual:
        messagebox.showerror("Error", "Debe iniciar sesión")
        return
    sel = lista_archivos.get(tk.ACTIVE)
    if not sel:
        messagebox.showerror("Error", "Seleccione un archivo")
        return
    from fat_logic import cargar_fat
    fat = cargar_fat(sel)
    if not fat:
        return
    contenido = leer_contenido(fat)
    win = tk.Toplevel(ventana)
    win.title(sel)
    area = scrolledtext.ScrolledText(win, width=60, height=15, font=("Arial", 11))
    area.insert(tk.END, contenido)
    area.config(state="disabled")
    area.pack(padx=10, pady=10)

def modificar_archivo_ui():
    if not usuario_actual:
        messagebox.showerror("Error", "Debe iniciar sesión")
        return
    sel = lista_archivos.get(tk.ACTIVE)
    if not sel:
        messagebox.showerror("Error", "Seleccione un archivo")
        return
    from fat_logic import cargar_fat
    fat = cargar_fat(sel)
    if not fat:
        return
    contenido = leer_contenido(fat)
    win = tk.Toplevel(ventana)
    win.title("Modificar archivo")
    txt = scrolledtext.ScrolledText(win, width=60, height=15, font=("Arial", 11))
    txt.insert(tk.END, contenido)
    txt.pack(padx=10, pady=10)
    def guardar():
        nuevo = txt.get("1.0", tk.END).strip()
        ok, msg = modificar_archivo(sel, nuevo, usuario_actual)
        messagebox.showinfo("Resultado", msg)
        win.destroy()
    tk.Button(win, text="Guardar Cambios", command=guardar).pack(pady=5)

def eliminar_archivo_ui():
    if not usuario_actual:
        messagebox.showerror("Error", "Debe iniciar sesión")
        return
    sel = lista_archivos.get(tk.ACTIVE)
    if not sel:
        messagebox.showerror("Error", "Seleccione un archivo")
        return
    ok, msg = eliminar_logico(sel, usuario_actual)
    messagebox.showinfo("Resultado", msg)
    refrescar_listas()

def recuperar_archivo():
    if not usuario_actual:
        messagebox.showerror("Error", "Debe iniciar sesión")
        return
    sel = lista_papelera.get(tk.ACTIVE)
    if not sel:
        messagebox.showerror("Error", "Seleccione un archivo")
        return
    ok, msg = recuperar(sel, usuario_actual)
    messagebox.showinfo("Resultado", msg)
    refrescar_listas()

def vaciar_papelera_ui():
    vaciar_papelera()
    refrescar_listas()
    messagebox.showinfo("Papelera", "La papelera ha sido vaciada")

def crear_usuario_ui():
    nombre = simpledialog.askstring("Nuevo usuario", "Nombre:")
    clave = simpledialog.askstring("Nuevo usuario", "Contraseña:")
    if not nombre or not clave:
        messagebox.showerror("Error", "Campos vacíos")
        return
    ok, msg = crear_usuario(nombre, clave)
    messagebox.showinfo("Resultado", msg)

def asignar_permiso_ui():
    usuario = simpledialog.askstring("Permiso", "Usuario a modificar:")
    if not usuario:
        messagebox.showerror("Error", "Usuario inválido")
        return
    respuesta = simpledialog.askstring("Rol", "Asignar admin? (s/n):")
    if not respuesta or respuesta.lower() not in ("s", "n"):
        messagebox.showerror("Error", "Respuesta inválida")
        return
    es_admin = respuesta.lower() == "s"
    ok, msg = asignar_permiso(usuario_actual, usuario, es_admin)
    messagebox.showinfo("Resultado", msg)
    refrescar_listas()
    actualizar_visibilidad_botones()

def salir():
    ventana.destroy()

ventana = tk.Tk()
ventana.title("Simulador FAT")
ventana.geometry("900x500")
ventana.configure(bg="#202020")

frame_izq = tk.Frame(ventana, bg="#202020")
frame_izq.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
frame_der = tk.Frame(ventana, bg="#202020")
frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

tk.Label(frame_izq, text="Archivos", fg="white", bg="#202020", font=("Arial", 13)).pack()
lista_archivos = tk.Listbox(frame_izq, width=40, height=15, bg="#303030", fg="white", font=("Arial", 10))
lista_archivos.pack(pady=10)
tk.Label(frame_izq, text="Papelera", fg="white", bg="#202020", font=("Arial", 13)).pack()
lista_papelera = tk.Listbox(frame_izq, width=40, height=10, bg="#303030", fg="white", font=("Arial", 10))
lista_papelera.pack(pady=10)

boton_login = tk.Button(frame_der, text="Iniciar Sesión", command=login_usuario, width=25, height=2)
boton_login.grid(row=0, column=0, pady=5)
boton_crear = tk.Button(frame_der, text="Crear Archivo", command=crear_archivo_ui, width=25, height=2)
boton_crear.grid(row=1, column=0, pady=5)
boton_abrir = tk.Button(frame_der, text="Abrir Archivo", command=abrir_archivo, width=25, height=2)
boton_abrir.grid(row=2, column=0, pady=5)
boton_modificar = tk.Button(frame_der, text="Modificar Archivo", command=modificar_archivo_ui, width=25, height=2)
boton_modificar.grid(row=3, column=0, pady=5)
boton_eliminar = tk.Button(frame_der, text="Eliminar Archivo", command=eliminar_archivo_ui, width=25, height=2)
boton_eliminar.grid(row=4, column=0, pady=5)
boton_recuperar = tk.Button(frame_der, text="Recuperar Archivo", command=recuperar_archivo, width=25, height=2)
boton_recuperar.grid(row=5, column=0, pady=5)
boton_vaciar = tk.Button(frame_der, text="Vaciar Papelera", command=vaciar_papelera_ui, width=25, height=2)
boton_vaciar.grid(row=6, column=0, pady=5)
boton_crear_usuario = tk.Button(frame_der, text="Crear Usuario", command=crear_usuario_ui, width=25, height=2)
boton_crear_usuario.grid(row=7, column=0, pady=5)
boton_asignar_permiso = tk.Button(frame_der, text="Asignar Permisos", command=asignar_permiso_ui, width=25, height=2)
boton_asignar_permiso.grid(row=8, column=0, pady=5)
boton_mostrar_usuarios = tk.Button(frame_der, text="Mostrar Usuarios", command=mostrar_usuarios, width=25, height=2)
boton_mostrar_usuarios.grid(row=9, column=0, pady=5)
boton_salir = tk.Button(frame_der, text="Salir", command=salir, width=25, height=2, bg="#a83232", fg="white")
boton_salir.grid(row=10, column=0, pady=10)

actualizar_visibilidad_botones()
refrescar_listas()
ventana.mainloop()

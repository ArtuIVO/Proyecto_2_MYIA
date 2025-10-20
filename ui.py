import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
from fat_logic import crear_archivo, listar, leer_contenido, modificar_archivo, eliminar_logico, recuperar, cargar_fat
from users import init_users, check_credentials, create_user, assign_permission, find_user, user_has_read, user_has_write

init_users()
usuario_actual = None

ventana = tk.Tk()
ventana.title("Simulador FAT - Sistema de Archivos")
ventana.geometry("600x500")
ventana.config(bg="#2b2b2b")

frame_login = tk.Frame(ventana, bg="#2b2b2b")
frame_main = tk.Frame(ventana, bg="#2b2b2b")
frame_login.pack(fill="both", expand=True)

def mostrar_login():
    frame_main.pack_forget()
    frame_login.pack(fill="both", expand=True)

def mostrar_main():
    frame_login.pack_forget()
    frame_main.pack(fill="both", expand=True)
    refrescar_lista()

def login():
    global usuario_actual
    u = entrada_usuario.get().strip()
    p = entrada_pass.get().strip()
    if not u or not p:
        messagebox.showerror("Error", "Usuario o contraseña vacíos.")
        return
    if check_credentials(u, p):
        usuario_actual = u
        label_usuario.config(text=f"Usuario: {usuario_actual}", fg="#fff")
        mostrar_main()
    else:
        messagebox.showerror("Error", "Credenciales incorrectas")

def logout():
    global usuario_actual
    usuario_actual = None
    entrada_usuario.delete(0, tk.END)
    entrada_pass.delete(0, tk.END)
    mostrar_login()

def salir():
    ventana.destroy()

def refrescar_lista():
    lista_archivos.delete(0, tk.END)
    for a in listar(True):
        lista_archivos.insert(tk.END, a["nombre"])

def crear():
    if not usuario_actual: return
    nombre = simpledialog.askstring("Nuevo archivo", "Nombre del archivo:")
    if not nombre or nombre.strip() == "":
        messagebox.showerror("Error", "El nombre no puede estar vacío.")
        return
    texto = simpledialog.askstring("Contenido", "Escribe el contenido del archivo:")
    if not texto or texto.strip() == "":
        messagebox.showerror("Error", "El contenido no puede estar vacío.")
        return
    ok, msg = crear_archivo(nombre, texto, usuario_actual)
    messagebox.showinfo("Resultado", msg)
    refrescar_lista()

def abrir():
    if not usuario_actual: return
    sel = lista_archivos.curselection()
    if not sel: return
    nombre = lista_archivos.get(sel)
    fat = cargar_fat(nombre)
    if not fat:
        messagebox.showerror("Error", "El archivo no existe")
        return
    if fat["papelera"]:
        messagebox.showwarning("Aviso", "El archivo está en la papelera")
        return
    if not user_has_read(usuario_actual, nombre, fat["owner"]):
        messagebox.showerror("Error", "No tienes permiso de lectura")
        return
    contenido = leer_contenido(fat)
    ventana_contenido = tk.Toplevel()
    ventana_contenido.title(nombre)
    ventana_contenido.config(bg="#1e1e1e")
    texto = scrolledtext.ScrolledText(ventana_contenido, width=60, height=20, bg="#1e1e1e", fg="#eaeaea", insertbackground="white")
    texto.insert(tk.END, contenido)
    texto.config(state="disabled")
    texto.pack(padx=10, pady=10)

def modificar():
    if not usuario_actual: return
    sel = lista_archivos.curselection()
    if not sel: return
    nombre = lista_archivos.get(sel)
    fat = cargar_fat(nombre)
    if not fat:
        messagebox.showerror("Error", "No existe el archivo")
        return
    if not user_has_write(usuario_actual, nombre, fat["owner"]):
        messagebox.showerror("Error", "No tienes permiso de escritura")
        return
    nuevo_texto = simpledialog.askstring("Modificar", "Nuevo contenido del archivo:")
    if not nuevo_texto or nuevo_texto.strip() == "":
        messagebox.showerror("Error", "El contenido no puede estar vacío.")
        return
    ok, msg = modificar_archivo(nombre, nuevo_texto, usuario_actual)
    messagebox.showinfo("Resultado", msg)
    refrescar_lista()

def eliminar():
    if not usuario_actual: return
    sel = lista_archivos.curselection()
    if not sel: return
    nombre = lista_archivos.get(sel)
    ok, msg = eliminar_logico(nombre, usuario_actual)
    messagebox.showinfo("Resultado", msg)
    refrescar_lista()

def ver_papelera():
    lista_archivos.delete(0, tk.END)
    for a in listar(False):
        if a["papelera"]:
            lista_archivos.insert(tk.END, f"{a['nombre']} (en papelera)")

def recuperar_archivo():
    if not usuario_actual: return
    sel = lista_archivos.curselection()
    if not sel: return
    nombre = lista_archivos.get(sel).replace(" (en papelera)", "")
    ok, msg = recuperar(nombre, usuario_actual)
    messagebox.showinfo("Resultado", msg)
    refrescar_lista()

def asignar_permiso():
    if not usuario_actual: return
    sel = lista_archivos.curselection()
    if not sel: return
    nombre = lista_archivos.get(sel)
    fat = cargar_fat(nombre)
    if not fat or fat["owner"] != usuario_actual:
        messagebox.showerror("Error", "Solo el propietario puede asignar permisos")
        return
    usuario_destino = simpledialog.askstring("Permisos", "Usuario destino:")
    if not usuario_destino or usuario_destino.strip() == "":
        messagebox.showerror("Error", "Usuario inválido.")
        return
    r = messagebox.askyesno("Lectura", "¿Dar permiso de lectura?")
    w = messagebox.askyesno("Escritura", "¿Dar permiso de escritura?")
    ok, msg = assign_permission(nombre, usuario_actual, usuario_destino, read=r, write=w)
    messagebox.showinfo("Resultado", msg)

def crear_usuario():
    if not usuario_actual: return
    u = find_user(usuario_actual)
    if not u or not u.get("is_admin"):
        messagebox.showerror("Error", "Solo el administrador puede crear usuarios")
        return
    nuevo = simpledialog.askstring("Nuevo usuario", "Nombre del nuevo usuario:")
    clave = simpledialog.askstring("Contraseña", "Contraseña del nuevo usuario:")
    if not nuevo or not clave or nuevo.strip() == "" or clave.strip() == "":
        messagebox.showerror("Error", "Usuario o contraseña no válidos.")
        return
    ok, msg = create_user(nuevo, clave, usuario_actual)
    messagebox.showinfo("Resultado", msg)

tk.Label(frame_login, text="Simulador FAT", font=("Arial", 20, "bold"), bg="#2b2b2b", fg="#ffffff").pack(pady=20)
tk.Label(frame_login, text="Usuario:", bg="#2b2b2b", fg="#ffffff").pack()
entrada_usuario = tk.Entry(frame_login, width=30)
entrada_usuario.pack(pady=5)
tk.Label(frame_login, text="Contraseña:", bg="#2b2b2b", fg="#ffffff").pack()
entrada_pass = tk.Entry(frame_login, show="*", width=30)
entrada_pass.pack(pady=5)
tk.Button(frame_login, text="Iniciar sesión", bg="#4a90e2", fg="white", width=20, command=login).pack(pady=10)
tk.Button(frame_login, text="Salir del sistema", bg="#a94442", fg="white", width=20, command=salir).pack()

label_usuario = tk.Label(frame_main, text="", bg="#2b2b2b", fg="#ffffff", font=("Arial", 12))
label_usuario.pack(pady=10)
tk.Button(frame_main, text="Cerrar sesión", bg="#777", fg="white", width=20, command=logout).pack(pady=5)
tk.Button(frame_main, text="Salir del sistema", bg="#a94442", fg="white", width=20, command=salir).pack(pady=5)

lista_archivos = tk.Listbox(frame_main, width=50, height=12, bg="#1e1e1e", fg="#eaeaea", selectbackground="#4a90e2", borderwidth=0)
lista_archivos.pack(pady=10)

botones = [
    ("Crear archivo", crear),
    ("Abrir archivo", abrir),
    ("Modificar archivo", modificar),
    ("Eliminar archivo", eliminar),
    ("Ver papelera", ver_papelera),
    ("Recuperar archivo", recuperar_archivo),
    ("Asignar permisos", asignar_permiso),
    ("Crear usuario", crear_usuario)
]

for t, f in botones:
    tk.Button(frame_main, text=t, bg="#4a90e2", fg="white", width=25, command=f, relief="flat", font=("Arial", 10)).pack(pady=3)

mostrar_login()
ventana.mainloop()

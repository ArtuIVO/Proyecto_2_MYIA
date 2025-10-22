import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from fat_logic import crear_archivo, listar, leer_contenido, modificar_archivo, eliminar_logico, recuperar, vaciar_papelera, cargar_fat
from users import validar_usuario, find_user, crear_usuario, asignar_permiso

usuario_actual = None
usuario_es_admin = False  

def refrescar_listas():
    lista_archivos.delete(0, tk.END)
    lista_papelera.delete(0, tk.END)
    for a in listar(True):
        lista_archivos.insert(tk.END, a["nombre"])
    for a in listar(False):
        if a["papelera"]:
            lista_papelera.insert(tk.END, a["nombre"])

def actualizar_visibilidad_botones():
    global boton_crear_usuario, boton_asignar_permiso, boton_recuperar
    if not usuario_actual:
        boton_crear_usuario.grid_remove()
        boton_asignar_permiso.grid_remove()
        boton_recuperar.grid_remove()
        return
    u = find_user(usuario_actual)
    global usuario_es_admin
    usuario_es_admin = u.get("is_admin", False) # type: ignore
    if usuario_es_admin:
        boton_crear_usuario.grid()
        boton_asignar_permiso.grid()
        boton_recuperar.grid()
    else:
        boton_crear_usuario.grid_remove()
        boton_asignar_permiso.grid_remove()
        boton_recuperar.grid_remove()

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
        ok, msg = modificar_archivo(sel, nuevo, usuario_actual, usuario_es_admin) # type: ignore
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
    ok, msg = eliminar_logico(sel, usuario_actual, usuario_es_admin) # type: ignore
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

def mostrar_metadata(event):
    sel = lista_archivos.curselection()
    if not sel:
        return
    nombre = lista_archivos.get(sel[0])
    fat = cargar_fat(nombre)
    if not fat:
        lbl_metadata.config(text="Sin metadatos")
        return
    propietario = fat.get("owner", "Desconocido")
    creado = fat.get("creado", "N/A")
    modificado = fat.get("modificado", "N/A")
    tam = fat.get("tamano", "N/A")
    lbl_metadata.config(
        text=f"📄 Archivo: {nombre}\n👤 Propietario: {propietario}\n📅 Creado: {creado}\n🕓 Última modificación: {modificado}\n💾 Tamaño: {tam} bytes"
    )

def salir():
    ventana.destroy()

# --- INTERFAZ ---
ventana = tk.Tk()
ventana.title("Simulador FAT - Administración avanzada")
ventana.geometry("1000x550")
ventana.configure(bg="#202020")

frame_izq = tk.Frame(ventana, bg="#202020")
frame_izq.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
frame_der = tk.Frame(ventana, bg="#202020")
frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

tk.Label(frame_izq, text="Archivos", fg="white", bg="#202020", font=("Arial", 13)).pack()
lista_archivos = tk.Listbox(frame_izq, width=40, height=15, bg="#303030", fg="white", font=("Arial", 10))
lista_archivos.pack(pady=10)
lista_archivos.bind("<<ListboxSelect>>", mostrar_metadata)  # <--- mostrar metadatos al seleccionar

lbl_metadata = tk.Label(frame_izq, text="Selecciona un archivo para ver sus metadatos", bg="#202020", fg="#a0a0a0", justify="left", font=("Arial", 10))
lbl_metadata.pack(pady=5)

tk.Label(frame_izq, text="Papelera", fg="white", bg="#202020", font=("Arial", 13)).pack()
lista_papelera = tk.Listbox(frame_izq, width=40, height=10, bg="#303030", fg="white", font=("Arial", 10))
lista_papelera.pack(pady=10)

botones = [
    ("Iniciar Sesión", login_usuario),
    ("Crear Archivo", crear_archivo_ui),
    ("Abrir Archivo", abrir_archivo),
    ("Modificar Archivo", modificar_archivo_ui),
    ("Eliminar Archivo", eliminar_archivo_ui),
    ("Recuperar Archivo", recuperar_archivo),
    ("Vaciar Papelera", vaciar_papelera_ui),
    ("Crear Usuario", crear_usuario_ui),
    ("Asignar Permisos", asignar_permiso_ui),
]
for i, (texto, cmd) in enumerate(botones):
    b = tk.Button(frame_der, text=texto, command=cmd, width=25, height=2)
    b.grid(row=i, column=0, pady=5)
    if texto == "Crear Usuario": boton_crear_usuario = b
    elif texto == "Asignar Permisos": boton_asignar_permiso = b
    elif texto == "Recuperar Archivo": boton_recuperar = b

boton_salir = tk.Button(frame_der, text="Salir", command=salir, width=25, height=2, bg="#a83232", fg="white")
boton_salir.grid(row=len(botones), column=0, pady=10)

actualizar_visibilidad_botones()
refrescar_listas()
ventana.mainloop()

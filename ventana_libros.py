import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class DialogoLibro(Gtk.Dialog):
    """
    Ventana modal para añadir o editar libros.
    Incluye un Gtk.Scale para la valoración del 1 al 5.
    """

    def __init__(self, parent, titulo, db, datos=None):
        super().__init__(title=titulo, transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.set_default_size(400, 350)
        self.db = db

        box = self.get_content_area()
        box.set_spacing(10)

        # --- Entradas de datos ---
        self.et = Gtk.Entry(placeholder_text="Título del libro")

        # ComboBox para Autores
        self.ma = Gtk.ListStore(int, str)
        self.cb = Gtk.ComboBox(model=self.ma)
        ren = Gtk.CellRendererText()
        self.cb.pack_start(ren, True)
        self.cb.add_attribute(ren, "text", 1)

        for a in db.consultaSenParametros("SELECT id_autor, nombre FROM autores"):
            self.ma.append([a[0], a[1]])

        # --- Gtk.Scale (Slider) para valoración ---
        # Definimos el rango de 1 a 5 con saltos de 1
        adj = Gtk.Adjustment(value=1, lower=1, upper=5, step_increment=1, page_increment=1, page_size=0)
        self.slider_nota = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
        self.slider_nota.set_digits(0)  # No mostrar decimales
        self.slider_nota.set_value_pos(Gtk.PositionType.RIGHT)  # Mostrar valor a la derecha
        self.slider_nota.set_hexpand(True)

        self.ch = Gtk.CheckButton(label="¿Marcar como leído?")

        # Layout con Grid
        grid = Gtk.Grid(row_spacing=15, column_spacing=10, border_width=15)
        grid.attach(Gtk.Label(label="Título:"), 0, 0, 1, 1)
        grid.attach(self.et, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label="Autor:"), 0, 1, 1, 1)
        grid.attach(self.cb, 1, 1, 1, 1)
        grid.attach(Gtk.Label(label="Puntuación:"), 0, 2, 1, 1)
        grid.attach(self.slider_nota, 1, 2, 1, 1)
        grid.attach(self.ch, 1, 3, 2, 1)

        box.add(grid)

        # Cargar datos si es edición
        if datos:
            # datos[1] es título, datos[3] es valoración, datos[4] es leido
            self.et.set_text(datos[1])
            self.slider_nota.set_value(datos[3])
            self.ch.set_active(bool(datos[4]))
            # Seleccionar autor correspondiente
            for i, fila in enumerate(self.ma):
                if fila[0] == datos[5]:  # datos[5] es el ID_autor oculto
                    self.cb.set_active(i)
                    break

        self.show_all()

    def get_datos(self):
        """Retorna la tupla de datos procesada del formulario."""
        it = self.cb.get_active_iter()
        ida = self.ma.get_value(it, 0) if it else None
        return (
            self.et.get_text(),
            ida,
            int(self.slider_nota.get_value()),
            1 if self.ch.get_active() else 0
        )


class VentanaLibros(Gtk.Window):
    """
    Ventana de gestión de libros con persistencia.
    """

    def __init__(self, db, main_win):
        super().__init__(title="Gestión de Libros")
        self.db, self.main_win = db, main_win
        self.set_default_size(700, 450)
        self.connect("delete-event", self.on_delete_event)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, border_width=10)
        self.add(vbox)

        # Modelo del TreeView
        self.modelo = Gtk.ListStore(int, str, str, int, str, int)
        self.tree = Gtk.TreeView(model=self.modelo)

        columnas = ["ID", "Título", "Autor", "Nota", "Leído"]
        for i, c in enumerate(columnas):
            ren = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(c, ren, text=i)
            self.tree.append_column(col)

        sc = Gtk.ScrolledWindow()
        sc.add(self.tree)
        vbox.pack_start(sc, True, True, 0)

        # Botonera
        hb = Gtk.ButtonBox(spacing=10, layout_style=Gtk.ButtonBoxStyle.CENTER)
        self.btn_add = Gtk.Button(label="Añadir Libro")
        self.btn_edit = Gtk.Button(label="Editar Seleccionado")
        self.btn_del = Gtk.Button(label="Eliminar")
        btn_v = Gtk.Button(label="Volver al Menú")

        # 1. Desactivar botones inicialmente
        self.btn_edit.set_sensitive(False)
        self.btn_del.set_sensitive(False)

        # 2. Conectar la señal de selección
        seleccion = self.tree.get_selection()
        seleccion.connect("changed", self.on_seleccion_cambiada)

        for b in [self.btn_add, self.btn_edit, self.btn_del, btn_v]: hb.add(b)
        vbox.pack_start(hb, False, False, 0)

        # Eventos
        self.btn_add.connect("clicked", self.on_add_clicked)
        self.btn_edit.connect("clicked", self.on_edit_clicked)
        self.btn_del.connect("clicked", self.on_delete_clicked)
        btn_v.connect("clicked", self.on_volver_clicked)

        self.show_all()
        self.hide()

    def actualizar_listado(self):
        """Refresca los datos de la tabla convirtiendo los 1/0 en texto."""
        self.modelo.clear()
        sql = """SELECT l.id_libro, l.titulo, a.nombre, l.valoracion, l.leido, l.id_autor
                 FROM libros l \
                          JOIN autores a ON l.id_autor = a.id_autor"""

        for f in self.db.consultaSenParametros(sql):
            # Convertimos la lista a una lista mutable de Python para modificar el valor
            fila_procesada = list(f)

            # fila_procesada[4] es el valor de 'leido' (0 o 1)
            if fila_procesada[4] == 1:
                fila_procesada[4] = "Leído"
            else:
                fila_procesada[4] = "Pendiente"

            # Añadimos la fila ya procesada al modelo del TreeView
            self.modelo.append(fila_procesada)

    def on_add_clicked(self, w):
        d = DialogoLibro(self, "Añadir Nuevo Libro", self.db)

        while True:
            response = d.run()
            if response == Gtk.ResponseType.OK:
                titulo, id_autor, nota, leido = d.get_datos()

                if not titulo.strip():
                    self.mostrar_error("El título del libro no puede estar vacío.")
                elif id_autor is None:
                    self.mostrar_error("Debes seleccionar un autor de la lista.")
                else:
                    # Datos correctos: Guardamos y salimos
                    self.db.engadeRexistro("INSERT INTO libros(titulo, id_autor, valoracion, leido) VALUES(?,?,?,?)",
                                           titulo, id_autor, nota, leido)
                    self.actualizar_listado()
                    break
            else:
                # Cancelar o cerrar ventana
                break

        d.destroy()

    def on_edit_clicked(self, w):
        mod, it = self.tree.get_selection().get_selected()
        if it:
            # Pasamos la fila completa al diálogo para que cargue los datos
            d = DialogoLibro(self, "Editar Libro", self.db, mod[it])

            while True:
                response = d.run()
                if response == Gtk.ResponseType.OK:
                    titulo, id_autor, nota, leido = d.get_datos()

                    # VALIDACIÓN DOBLE
                    if not titulo.strip():
                        self.mostrar_error("El título no puede quedar vacío.")
                    elif id_autor is None:
                        self.mostrar_error("Debe haber un autor seleccionado.")
                    else:
                        # Todo correcto, actualizamos usando el ID (mod[it][0])
                        self.db.actualizaRexistro(
                            "UPDATE libros SET titulo=?, id_autor=?, valoracion=?, leido=? WHERE id_libro=?",
                            titulo, id_autor, nota, leido, mod[it][0]
                        )
                        self.actualizar_listado()
                        break
                else:
                    break  # Cancelar
            d.destroy()

    def on_delete_clicked(self, w):
        mod, it = self.tree.get_selection().get_selected()
        if it:
            confirm = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.QUESTION,
                                        buttons=Gtk.ButtonsType.YES_NO, text="¿Eliminar libro?")
            confirm.format_secondary_text(f"Se borrará '{mod[it][1]}' de la base de datos.")
            res = confirm.run()
            confirm.destroy()

            if res == Gtk.ResponseType.YES:
                self.db.borraRexistro("DELETE FROM libros WHERE id_libro=?", mod[it][0])
                self.actualizar_listado()

    def mostrar_error(self, mensaje):
        dialogo = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.WARNING,
                                    buttons=Gtk.ButtonsType.OK, text="Atención")
        dialogo.format_secondary_text(mensaje)
        dialogo.run()
        dialogo.destroy()

    def on_delete_event(self, w, e):
        self.on_volver_clicked()
        return True

    def on_volver_clicked(self, w=None):
        self.hide()
        self.main_win.show()

    def on_seleccion_cambiada(self, seleccion):
        """Habilita o deshabilita botones según si hay algo seleccionado."""
        modelo, iterador = seleccion.get_selected()
        hay_seleccion = iterador is not None
        self.btn_edit.set_sensitive(hay_seleccion)
        self.btn_del.set_sensitive(hay_seleccion)
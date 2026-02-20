import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class DialogoAutor(Gtk.Dialog):
    def __init__(self, parent, titulo, nombre="", nac="", bio=""):
        super().__init__(title=titulo, transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        box = self.get_content_area()
        box.set_spacing(10)
        box.set_border_width(10)

        self.en = Gtk.Entry(text=nombre, placeholder_text="Nombre")
        self.ena = Gtk.Entry(text=nac, placeholder_text="Nacionalidad")
        self.tv = Gtk.TextView()
        self.tv.get_buffer().set_text(bio)

        for w in [Gtk.Label(label="Nombre:"), self.en, Gtk.Label(label="Nacionalidad:"), self.ena,
                  Gtk.Label(label="Bio:"), self.tv]:
            box.pack_start(w, True, True, 0)
        self.show_all()

    def get_datos(self):
        b = self.tv.get_buffer()
        return (self.en.get_text(), self.ena.get_text(), b.get_text(b.get_start_iter(), b.get_end_iter(), True))


class VentanaAutores(Gtk.Window):
    def __init__(self, db, main_win):
        super().__init__(title="Gestión de Autores")
        self.db, self.main_win = db, main_win
        self.set_default_size(500, 400)
        self.connect("delete-event", self.on_delete_event)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, border_width=10)
        self.add(vbox)

        self.modelo = Gtk.ListStore(int, str, str, str)
        self.tree = Gtk.TreeView(model=self.modelo)
        for i, c in enumerate(["ID", "Nombre", "Nacionalidad", "Bio"]):
            self.tree.append_column(Gtk.TreeViewColumn(c, Gtk.CellRendererText(), text=i))

        sc = Gtk.ScrolledWindow()
        sc.add(self.tree)
        vbox.pack_start(sc, True, True, 0)

        hb = Gtk.ButtonBox(spacing=10)
        self.btn_add = Gtk.Button(label="Añadir")
        self.btn_edit = Gtk.Button(label="Editar")
        self.btn_del = Gtk.Button(label="Eliminar")
        btn_v = Gtk.Button(label="Volver")

        # 1. Desactivar botones inicialmente
        self.btn_edit.set_sensitive(False)
        self.btn_del.set_sensitive(False)

        # 2. Conectar la señal de selección
        seleccion = self.tree.get_selection()
        seleccion.connect("changed", self.on_seleccion_cambiada)

        for b in [self.btn_add, self.btn_edit, self.btn_del, btn_v]: hb.add(b)
        vbox.pack_start(hb, False, False, 0)

        self.btn_add.connect("clicked", self.on_add_clicked)
        self.btn_edit.connect("clicked", self.on_edit_clicked)
        self.btn_del.connect("clicked", self.on_delete_clicked)
        btn_v.connect("clicked", self.on_volver_clicked)

        self.show_all()
        self.hide()

    def actualizar_listado(self):
        self.modelo.clear()
        for f in self.db.consultaSenParametros("SELECT * FROM autores"):
            self.modelo.append(list(f))

    def on_add_clicked(self, w):
        d = DialogoAutor(self, "Nuevo Autor")

        # Bucle para mantener el diálogo abierto hasta que los datos sean correctos o cancele
        while True:
            response = d.run()
            if response == Gtk.ResponseType.OK:
                datos = d.get_datos()
                if datos[0].strip():  # Si el nombre es válido
                    self.db.engadeRexistro("INSERT INTO autores(nombre, nacionalidad, biografia) VALUES(?,?,?)", *datos)
                    self.actualizar_listado()
                    break  # Salimos del bucle y cerramos
                else:
                    self.mostrar_error("El nombre del autor es obligatorio.")
                    # Al no haber 'break', el bucle vuelve a d.run() y la ventana sigue ahí
            else:
                break  # El usuario pulsó cancelar o cerró la ventana

        d.destroy()

    def on_edit_clicked(self, w):
        mod, it = self.tree.get_selection().get_selected()
        if it:
            # Creamos el diálogo con los datos actuales
            d = DialogoAutor(self, "Editar Autor", mod[it][1], mod[it][2], mod[it][3])

            while True:
                response = d.run()
                if response == Gtk.ResponseType.OK:
                    datos_nuevos = d.get_datos()
                    # VALIDACIÓN: Nombre no vacío
                    if datos_nuevos[0].strip():
                        self.db.actualizaRexistro(
                            "UPDATE autores SET nombre=?, nacionalidad=?, biografia=? WHERE id_autor=?",
                            *datos_nuevos, mod[it][0]
                        )
                        self.actualizar_listado()
                        break  # Datos correctos, cerramos
                    else:
                        self.mostrar_error("El nombre no puede quedar vacío al editar.")
                else:
                    break  # Cancelar
            d.destroy()

    def on_delete_clicked(self, w):
        mod, it = self.tree.get_selection().get_selected()
        if it:
            # CONFIRMACIÓN DE BORRADO
            confirm = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.QUESTION,
                                        buttons=Gtk.ButtonsType.YES_NO, text="¿Seguro que desea eliminar este autor?")
            confirm.format_secondary_text("Se eliminarán también todos los libros asociados a este autor.")
            res = confirm.run()
            confirm.destroy()

            if res == Gtk.ResponseType.YES:
                self.db.borraRexistro("DELETE FROM autores WHERE id_autor=?", mod[it][0])
                self.actualizar_listado()

    def mostrar_error(self, mensaje):
        """Muestra un diálogo de aviso al usuario."""
        dialogo = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.ERROR,
                                    buttons=Gtk.ButtonsType.OK, text="Error en los datos")
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
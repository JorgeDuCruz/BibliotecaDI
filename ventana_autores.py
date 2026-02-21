import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class DialogoAutor(Gtk.Dialog):
    """
    Ventana de diálogo modal para la creación y edición de autores.

    Esta clase genera un formulario con campos para el nombre, nacionalidad
    y biografía de un autor.
    """

    def __init__(self, parent, titulo, nombre="", nac="", bio=""):
        """
        Inicializa el diálogo de autor.

        :param parent: Ventana que actúa como padre del diálogo.
        :type parent: Gtk.Window
        :param titulo: Título de la ventana del diálogo.
        :type titulo: str
        :param nombre: Nombre predefinido (para edición), por defecto "".
        :param nac: Nacionalidad predefinida (para edición), por defecto "".
        :param bio: Biografía predefinida (para edición), por defecto "".
        """
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
                  Gtk.Label(label="Biografía:"), self.tv]:
            box.pack_start(w, True, True, 0)
        self.show_all()

    def get_datos(self):
        """
        Recupera la información introducida en los campos del formulario.

        :return: Tupla con el nombre, nacionalidad y contenido del búfer de texto.
        :rtype: tuple
        """
        b = self.tv.get_buffer()
        return (self.en.get_text(), self.ena.get_text(), b.get_text(b.get_start_iter(), b.get_end_iter(), True))


class VentanaAutores(Gtk.Window):
    """
    Ventana encargada de la gestión integral de autores.

    Permite listar autores mediante un TreeView, añadirlos, editarlos
    y eliminarlos con confirmación previa.
    """

    def __init__(self, db, main_win):
        """
        Inicializa la ventana de gestión de autores.

        :param db: Instancia de conexión a la base de datos.
        :type db: ConexionBD
        :param main_win: Referencia a la ventana principal para la navegación.
        :type main_win: VentanaSeleccion
        """
        super().__init__(title="Gestión de Autores")
        self.db, self.main_win = db, main_win
        self.set_default_size(500, 400)
        self.connect("delete-event", self.on_delete_event)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, border_width=10)
        self.add(vbox)

        self.modelo = Gtk.ListStore(int, str, str, str)
        self.tree = Gtk.TreeView(model=self.modelo)
        for i, c in enumerate(["ID", "Nombre", "Nacionalidad", "Biografía"]):
            self.tree.append_column(Gtk.TreeViewColumn(c, Gtk.CellRendererText(), text=i))

        sc = Gtk.ScrolledWindow()
        sc.add(self.tree)
        vbox.pack_start(sc, True, True, 0)

        hb = Gtk.ButtonBox(spacing=10)
        self.btn_add = Gtk.Button(label="Añadir")
        self.btn_edit = Gtk.Button(label="Editar")
        self.btn_del = Gtk.Button(label="Eliminar")
        btn_v = Gtk.Button(label="Volver")

        # Configuración inicial de sensibilidad
        self.btn_edit.set_sensitive(False)
        self.btn_del.set_sensitive(False)

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
        """
        Consulta la base de datos y refresca el contenido del TreeView.
        """
        self.modelo.clear()
        for f in self.db.consultaSenParametros("SELECT * FROM autores"):
            self.modelo.append(list(f))

    def on_add_clicked(self, w):
        """
        Gestiona la lógica para añadir un nuevo autor.

        Mantiene el diálogo abierto mediante un bucle hasta que la validación sea
        correcta o el usuario cancele la operación.
        """
        d = DialogoAutor(self, "Nuevo Autor")

        while True:
            response = d.run()
            if response == Gtk.ResponseType.OK:
                datos = d.get_datos()
                if datos[0].strip():
                    self.db.engadeRexistro("INSERT INTO autores(nombre, nacionalidad, biografia) VALUES(?,?,?)", *datos)
                    self.actualizar_listado()
                    break
                else:
                    self.mostrar_error("El nombre del autor es obligatorio.")
            else:
                break

        d.destroy()

    def on_edit_clicked(self, w):
        """
        Gestiona la edición de un autor seleccionado.

        Valida que los campos obligatorios no se dejen vacíos durante la edición.
        """
        mod, it = self.tree.get_selection().get_selected()
        if it:
            d = DialogoAutor(self, "Editar Autor", mod[it][1], mod[it][2], mod[it][3])

            while True:
                response = d.run()
                if response == Gtk.ResponseType.OK:
                    datos_nuevos = d.get_datos()
                    if datos_nuevos[0].strip():
                        self.db.actualizaRexistro(
                            "UPDATE autores SET nombre=?, nacionalidad=?, biografia=? WHERE id_autor=?",
                            *datos_nuevos, mod[it][0]
                        )
                        self.actualizar_listado()
                        break
                    else:
                        self.mostrar_error("El nombre no puede quedar vacío al editar.")
                else:
                    break
            d.destroy()

    def on_delete_clicked(self, w):
        """
        Gestiona la eliminación de un autor tras confirmación del usuario.

        Muestra un diálogo de advertencia informando sobre el borrado en cascada.
        """
        mod, it = self.tree.get_selection().get_selected()
        if it:
            confirm = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.QUESTION,
                                        buttons=Gtk.ButtonsType.YES_NO, text="¿Seguro que desea eliminar este autor?")
            confirm.format_secondary_text("Se eliminarán también todos los libros asociados a este autor.")
            res = confirm.run()
            confirm.destroy()

            if res == Gtk.ResponseType.YES:
                self.db.borraRexistro("DELETE FROM autores WHERE id_autor=?", mod[it][0])
                self.actualizar_listado()

    def mostrar_error(self, mensaje):
        """
        Muestra un diálogo de error con un mensaje personalizado.

        :param mensaje: Texto que se mostrará en el cuerpo del error.
        :type mensaje: str
        """
        dialogo = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.ERROR,
                                    buttons=Gtk.ButtonsType.OK, text="Error en los datos")
        dialogo.format_secondary_text(mensaje)
        dialogo.run()
        dialogo.destroy()

    def on_delete_event(self, w, e):
        """
        Intervención del evento de cierre de ventana (botón X).

        Impide la destrucción del objeto y vuelve al menú principal.
        """
        self.on_volver_clicked()
        return True

    def on_volver_clicked(self, w=None):
        """
        Oculta la ventana actual y muestra la ventana principal.
        """
        self.hide()
        self.main_win.show()

    def on_seleccion_cambiada(self, seleccion):
        """
        Controlador de la señal 'changed' de la selección del TreeView.

        Habilita o deshabilita los botones Editar y Eliminar según la selección.
        """
        modelo, iterador = seleccion.get_selected()
        hay_seleccion = iterador is not None
        self.btn_edit.set_sensitive(hay_seleccion)
        self.btn_del.set_sensitive(hay_seleccion)
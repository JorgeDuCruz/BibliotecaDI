import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from ventana_autores import VentanaAutores
from ventana_libros import VentanaLibros


class VentanaSeleccion(Gtk.Window):
    def __init__(self, db):
        super().__init__(title="Menú Principal")
        self.set_default_size(300, 200)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.db = db

        # Instancias persistentes
        self.v_autores = VentanaAutores(self.db, self)
        self.v_libros = VentanaLibros(self.db, self)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, border_width=20)
        self.add(vbox)

        btn_a = Gtk.Button(label="Gestión de Autores")
        btn_a.connect("clicked", lambda x: self.abrir(self.v_autores))

        btn_l = Gtk.Button(label="Gestión de Libros")
        btn_l.connect("clicked", lambda x: self.abrir(self.v_libros))

        btn_s = Gtk.Button(label="Salir")
        btn_s.connect("clicked", Gtk.main_quit)

        for b in [btn_a, btn_l, btn_s]: vbox.pack_start(b, True, True, 0)
        self.connect("destroy", Gtk.main_quit)
        self.show_all()

    def abrir(self, ventana):
        self.hide()
        ventana.actualizar_listado()
        ventana.present()
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from ventana_autores import VentanaAutores
from ventana_libros import VentanaLibros


class VentanaSeleccion(Gtk.Window):
    """
    Ventana de menú principal que sirve como orquestador de la aplicación.

    Esta clase permite al usuario navegar entre la gestión de autores y la
    gestión de libros. Utiliza un sistema de ventanas persistentes para
    evitar la recreación constante de objetos y mejorar el rendimiento.
    """

    def __init__(self, db):
        """
        Inicializa la ventana de selección y prepara las subventanas.

        :param db: Instancia de la clase ConexionBD para la gestión de datos.
        :type db: ConexionBD
        """
        super().__init__(title="Menú Principal")
        self.set_default_size(300, 200)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.db = db

        # Instancias persistentes: Se crean una sola vez al inicio
        self.v_autores = VentanaAutores(self.db, self)
        self.v_libros = VentanaLibros(self.db, self)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, border_width=20)
        self.add(vbox)

        # Botón para abrir la sección de autores
        btn_a = Gtk.Button(label="Gestión de Autores")
        btn_a.connect("clicked", lambda x: self.abrir(self.v_autores))

        # Botón para abrir la sección de libros
        btn_l = Gtk.Button(label="Gestión de Libros")
        btn_l.connect("clicked", lambda x: self.abrir(self.v_libros))

        # Botón para cerrar la aplicación
        btn_s = Gtk.Button(label="Salir")
        btn_s.connect("clicked", Gtk.main_quit)

        # Empaquetado de botones
        for b in [btn_a, btn_l, btn_s]:
            vbox.pack_start(b, True, True, 0)

        self.connect("destroy", Gtk.main_quit)
        self.show_all()

    def abrir(self, ventana):
        """
        Gestiona la transición entre el menú principal y las ventanas secundarias.

        Oculta la ventana de selección, refresca los datos de la base de datos
        en la ventana destino y la presenta al usuario.

        :param ventana: Instancia de la ventana que se desea mostrar.
        :type ventana: Gtk.Window
        """
        self.hide()
        ventana.actualizar_listado()
        ventana.present()
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from Codigo.conexionBD import ConexionBD
from Codigo.ventana_seleccion import VentanaSeleccion

class AplicacionBiblioteca:
    """
    Clase principal que orquestra el inicio de la aplicación de biblioteca.

    Esta clase se encarga de establecer la conexión inicial con la base de datos,
    asegurar que la estructura de tablas exista y lanzar la primera ventana
    de la interfaz de usuario (VentanaSeleccion).
    """

    def __init__(self):
        """
        Inicializa la instancia de la aplicación.

        Configura la conexión a la base de datos SQLite 'biblioteca.db',
        instancia el cursor necesario para las operaciones y muestra la
        ventana principal de selección de gestión.
        """
        # Obtener la ruta absoluta de la carpeta donde está este archivo main.py
        ruta_directorio = os.path.dirname(os.path.abspath(__file__))
        ruta_db = os.path.join(ruta_directorio, "biblioteca.db")

        # 1. Configurar conexión a la base de datos
        self.db = ConexionBD(ruta_db)
        self.db.conectaBD()
        self.db.creaCursor()
        self.db.crearTablas()

        # 2. Lanzar la ventana de selección
        self.ventana_inicio = VentanaSeleccion(self.db)
        self.ventana_inicio.show_all()

    def ejecutar(self):
        """
        Inicia el bucle de eventos principal de GTK.

        Este método mantiene la aplicación en ejecución y a la espera de
        interacciones por parte del usuario hasta que se cierre la ventana principal.
        """
        Gtk.main()

def main():
    """Punto de entrada para el comando de terminal."""
    app = AplicacionBiblioteca()
    app.ejecutar()

if __name__ == "__main__":
    main()
import sqlite3 as dbapi

class ConexionBD:
    """
    Clase para gestionar la conexión y operaciones CRUD en una base de datos SQLite
    orientada a una biblioteca de libros y sus autores.
    """

    def __init__(self, rutaBd):
        """
        Inicializa las propiedades de la conexión.

        :param rutaBd: Ruta del archivo de la base de datos (ej: 'biblioteca.db').
        """
        self.rutaBd = rutaBd
        self.conexion = None
        self.cursor = None

    def conectaBD(self):
        """
        Crea la conexión con la base de datos SQLite y habilita el soporte
        para claves foráneas.
        """
        try:
            if self.conexion is None:
                self.conexion = dbapi.connect(self.rutaBd)
                # Habilitamos explícitamente el soporte de claves foráneas en SQLite
                self.conexion.execute("PRAGMA foreign_keys = ON")
                print(f"Conexión establecida con {self.rutaBd}")
        except dbapi.StandardError as e:
            print(f"Error al conectar con la base de datos: {e}")

    def creaCursor(self):
        """
        Crea el objeto cursor necesario para ejecutar sentencias SQL.
        """
        try:
            if self.conexion and self.cursor is None:
                self.cursor = self.conexion.cursor()
                print("Cursor preparado.")
        except dbapi.Error as e:
            print(f"Error al crear el cursor: {e}")

    def crearTablas(self):
        """
        Crea las tablas 'autores' y 'libros' estableciendo una relación 1:N.
        Un autor puede tener muchos libros, pero un libro pertenece a un solo autor.
        """
        # Tabla de Autores
        sql_autores = """
        CREATE TABLE IF NOT EXISTS autores (
            id_autor INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            nacionalidad TEXT,
            biografia TEXT
        )
        """
        # Tabla de Libros (con Foreign Key)
        sql_libros = """
        CREATE TABLE IF NOT EXISTS libros (
            id_libro INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            id_autor INTEGER NOT NULL,
            valoracion INTEGER CHECK(valoracion BETWEEN 1 AND 5),
            leido INTEGER DEFAULT 0,
            FOREIGN KEY (id_autor) REFERENCES autores (id_autor) ON DELETE CASCADE
        )
        """
        try:
            self.cursor.execute(sql_autores)
            self.cursor.execute(sql_libros)
            self.conexion.commit()
            print("Tablas de Autores y Libros creadas correctamente.")
        except dbapi.DatabaseError as e:
            print(f"Error al crear las tablas: {e}")

    def consultaSenParametros(self, consultaSQL):
        """
        Ejecuta una consulta SQL de selección sin parámetros.

        :param consultaSQL: Sentencia SQL a ejecutar.
        :return: Lista de tuplas con los registros.
        """
        try:
            self.cursor.execute(consultaSQL)
            return self.cursor.fetchall()
        except dbapi.DatabaseError as e:
            print(f"Error en consulta: {e}")
            return []

    def consultaConParametros(self, consultaSQL, *parametros):
        """
        Ejecuta una consulta SQL de selección utilizando parámetros.

        :param consultaSQL: Sentencia SQL con marcadores '?'.
        :param parametros: Valores para la consulta.
        :return: Lista de tuplas con los resultados.
        """
        try:
            self.cursor.execute(consultaSQL, parametros)
            return self.cursor.fetchall()
        except dbapi.DatabaseError as e:
            print(f"Error en consulta parametrizada: {e}")
            return []

    def engadeRexistro(self, insertSQL, *parametros):
        """
        Inserta un nuevo registro (Libro o Autor) en la base de datos.

        :param insertSQL: Sentencia INSERT con marcadores '?'.
        :param parametros: Datos a insertar.
        """
        try:
            self.cursor.execute(insertSQL, parametros)
            self.conexion.commit()
            print("Inserción completada.")
        except dbapi.DatabaseError as e:
            print(f"Error en la inserción: {e}")

    def actualizaRexistro(self, updateSQL, *parametros):
        """
        Actualiza un registro existente mediante su ID.

        :param updateSQL: Sentencia UPDATE con marcadores '?'.
        :param parametros: Nuevos valores incluyendo el ID al final.
        """
        try:
            self.cursor.execute(updateSQL, parametros)
            self.conexion.commit()
            print("Actualización completada.")
        except dbapi.DatabaseError as e:
            print(f"Error en la actualización: {e}")

    def borraRexistro(self, borraSQL, *parametros):
        """
        Elimina un registro. Si se borra un autor, se borrarán sus libros
        en cascada si así se configuró en la tabla.

        :param borraSQL: Sentencia DELETE con marcador para el ID.
        :param parametros: ID del registro.
        """
        try:
            self.cursor.execute(borraSQL, parametros)
            self.conexion.commit()
            print("Registro eliminado.")
        except dbapi.DatabaseError as e:
            print(f"Error al borrar registro: {e}")

    def pechaBD(self):
        """
        Cierra la conexión y el cursor.
        """
        if self.cursor:
            self.cursor.close()
        if self.conexion:
            self.conexion.close()
        print("Base de datos cerrada.")
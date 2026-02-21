import sqlite3 as dbapi


class ConexionBD:
    """
    Clase para gestionar la conexión y operaciones CRUD en una base de datos SQLite.

    Esta clase está orientada a la gestión de una biblioteca, manejando las tablas
    de libros y sus autores, asegurando la integridad referencial mediante claves foráneas.
    """

    def __init__(self, rutaBd):
        """
        Inicializa las propiedades de la conexión.

        :param rutaBd: Ruta física o nombre del archivo de la base de datos (ej: 'biblioteca.db').
        :type rutaBd: str
        """
        self.rutaBd = rutaBd
        self.conexion = None
        self.cursor = None

    def conectaBD(self):
        """
        Crea la conexión con la base de datos SQLite y habilita el soporte para claves foráneas.

        Utiliza el comando PRAGMA para asegurar que las relaciones ON DELETE CASCADE
        funcionen correctamente en el motor SQLite.
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

        Requiere que la conexión haya sido establecida previamente mediante conectaBD().
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
        La tabla libros incluye restricciones de validación para la puntuación.
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

            # --- Insertar autor por defecto ---
            # Comprobamos si hay algún autor en la tabla
            self.cursor.execute("SELECT COUNT(*) FROM autores")
            cantidad = self.cursor.fetchone()[0]

            if cantidad == 0:
                autor_defecto = ("Autor Desconocido", "N/A", "Autor creado por el sistema.")
                self.cursor.execute("INSERT INTO autores (nombre, nacionalidad, biografia) VALUES (?, ?, ?)",
                                    autor_defecto)
                print("Autor por defecto creado correctamente.")

            self.conexion.commit()
            print("Tablas de Autores y Libros creadas correctamente.")
        except dbapi.DatabaseError as e:
            print(f"Error al crear las tablas: {e}")

    def consultaSenParametros(self, consultaSQL):
        """
        Ejecuta una consulta SQL de selección sin parámetros.

        :param consultaSQL: Sentencia SQL (SELECT) a ejecutar.
        :type consultaSQL: str
        :return: Lista de tuplas con los registros resultantes.
        :rtype: list
        """
        try:
            self.cursor.execute(consultaSQL)
            return self.cursor.fetchall()
        except dbapi.DatabaseError as e:
            print(f"Error en consulta: {e}")
            return []

    def consultaConParametros(self, consultaSQL, *parametros):
        """
        Ejecuta una consulta SQL de selección utilizando parámetros de seguridad.

        :param consultaSQL: Sentencia SQL con marcadores de posición '?'.
        :type consultaSQL: str
        :param parametros: Valores para filtrar la consulta.
        :return: Lista de tuplas con los resultados filtrados.
        :rtype: list
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
        :type insertSQL: str
        :param parametros: Datos del registro a insertar.
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
        :type updateSQL: str
        :param parametros: Nuevos valores incluyendo el ID al final para la cláusula WHERE.
        """
        try:
            self.cursor.execute(updateSQL, parametros)
            self.conexion.commit()
            print("Actualización completada.")
        except dbapi.DatabaseError as e:
            print(f"Error en la actualización: {e}")

    def borraRexistro(self, borraSQL, *parametros):
        """
        Elimina un registro de la base de datos.

        Si se borra un autor, se borrarán sus libros en cascada automáticamente
        gracias a la configuración de la clave foránea.

        :param borraSQL: Sentencia DELETE con marcador para el ID.
        :type borraSQL: str
        :param parametros: ID del registro a eliminar.
        """
        try:
            self.cursor.execute(borraSQL, parametros)
            self.conexion.commit()
            print("Registro eliminado.")
        except dbapi.DatabaseError as e:
            print(f"Error al borrar registro: {e}")

    def pechaBD(self):
        """
        Realiza el cierre seguro del cursor y de la conexión con la base de datos.
        """
        if self.cursor:
            self.cursor.close()
        if self.conexion:
            self.conexion.close()
        print("Base de datos cerrada.")
Manual de Usuario
=================

Bienvenido al manual de **Biblioteca DI**. Esta guía te ayudará a dar tus primeros pasos con la aplicación.

.. warning::
   Asegúrate de tener instalada la librería GTK 3 en tu sistema antes de iniciar.

Instalación y Arranque
----------------------

Una vez instalado el paquete, puedes iniciar la aplicación desde cualquier terminal escribiendo:

.. code-block:: bash

   biblioteca-di

Gestión de la Aplicación
------------------------

1. Selección de Módulo
~~~~~~~~~~~~~~~~~~~~~~
Al abrir el programa, verás la **Ventana de Selección**. Aquí puedes elegir entre:

* **Gestión de Libros**: Para añadir, editar o borrar libros.
* **Gestión de Autores**: Para administrar la base de datos de escritores.

.. note::
   Esta ventana es la unica que cierra el programa.
   Si cierras otras ventas del programa volveras automáticamente a esta.

2. Trabajar con Libros
~~~~~~~~~~~~~~~~~~~~~~
En la ventana de libros podrás:

* **Añadir**: Rellena los campos y pulsa "Guardar".
* **Editar**: Selecciona un elemento de la lista y pulsa el botón "Editar".
* **Borrar**: Selecciona un elemento de la lista y pulsa el botón "Eliminar".

3. Trabajar con Autores
~~~~~~~~~~~~~~~~~~~~~~~
En la ventana de autores podrás:

* **Añadir**: Rellena los campos y pulsa "Guardar".
* **Editar**: Selecciona un elemento de la lista y pulsa el botón "Editar".
* **Borrar**: Selecciona un elemento de la lista y pulsa el botón "Eliminar".

4. Base de Datos
~~~~~~~~~~~~~~~~
La aplicación utiliza un archivo local llamado ``biblioteca.db``. No borres este archivo, ya que contiene toda la información guardada.

.. note::
   Si es la primera vez que abres la app, las tablas se crearán automáticamente.

.. note::
   La base de datos esta vinculada a la carpeta donde se ejecute el comando de inicio.
   Asegurate de siempre iniciar el programa en la misma carpeta.
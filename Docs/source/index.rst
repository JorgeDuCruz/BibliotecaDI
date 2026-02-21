.. Biblioteca DI documentation master file

Bienvenido a la documentación de Biblioteca DI
==============================================

.. image:: https://cdn-icons-png.flaticon.com/512/2232/2232688.png
   :width: 150
   :align: center
   :alt: Logo Biblioteca

Esta es la documentación técnica de la aplicación **Biblioteca DI**, una herramienta
desarrollada en Python utilizando **GTK 3** para la gestión integral de autores y sus
colecciones de libros.

Características principales
---------------------------
* **Gestión de Autores**: Registro de información biográfica y nacionalidad.
* **Catálogo de Libros**: Control de lecturas, valoraciones y vinculación con autores.
* **Persistencia**: Base de datos SQLite3 con integridad referencial.

.. toctree::
   :maxdepth: 2
   :caption: Guía de Referencia Técnica:

   Manual
   Codigo

Búsqueda y navegación
=====================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`




Dependencias del Proyecto
-------------------------

A continuación se detallan las librerías necesarias para el funcionamiento del sistema:

.. literalinclude:: ../../requirements.txt
   :language: text
   :caption: Archivo requirements.txt oficial
   :linenos:


Requisitos del Sistema
----------------------
Para instalar las dependencias necesarias para ejecutar este proyecto y compilar su documentación, cree un archivo .txt
con las depencias anteriores y luego ejecute:

.. code-block:: bash

   pip install -r requirements.txt
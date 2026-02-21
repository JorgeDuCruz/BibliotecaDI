from setuptools import setup, find_packages

setup(
    name="biblioteca-di-JorgeDC",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "PyGObject>=3.36.0",
    ],
    entry_points={
        'console_scripts': [
            # Esto crea el comando de terminal
            # 'comando = carpeta.archivo:funcion_principal'
            'biblioteca-di=Codigo.main:main',
        ],
    },
    author="Tu Nombre",
    description="Sistema de gestión de biblioteca con GTK3",
)
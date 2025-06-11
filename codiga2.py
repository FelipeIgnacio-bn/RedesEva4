# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from restconf_funciones import (
    obtener_info_dispositivo,
    obtener_estado_interfaces,
    configurar_interfaz,
    eliminar_interfaz,
)


app = Flask(__name__)
# Esta clave es necesaria para que Flask pueda mostrar mensajes de 'flash' al usuario.
# Puedes cambiarla por cualquier cadena de texto que desees.
app.secret_key = 'cisco123!_restconf_key'

@app.route('/')
def index():
    """
    Ruta principal que muestra el dashboard.
    Obtiene los datos del router y los pasa a la plantilla HTML.
    """
    info_dispositivo = obtener_info_dispositivo()
    interfaces = obtener_estado_interfaces()
    return render_template('index.html', info=info_dispositivo, interfaces=interfaces)

@app.route('/add_interface', methods=['POST'])
def add_interface_route():
    nombre = request.form['nombre']
    tipo_iana = request.form['tipo_iana']
    descripcion = request.form['descripcion']
    ip = request.form['ip']
    mascara = request.form['mascara']
    
    if configurar_interfaz(nombre, tipo_iana, descripcion, ip, mascara):
        flash(f"Interfaz {nombre} creada exitosamente.", "success")
    else:
        flash(f"Error al crear la interfaz {nombre}.", "danger")

    return redirect(url_for('index'))


@app.route('/delete_interface', methods=['POST'])
def delete_interface_route():
    nombre = request.form['nombre']

    if eliminar_interfaz(nombre):
        flash(f"Interfaz {nombre} eliminada exitosamente.", "success")
    else:
        flash(f"Error al eliminar la interfaz {nombre}.", "danger")

    return redirect(url_for('index'))

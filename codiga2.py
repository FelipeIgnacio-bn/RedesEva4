# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from restconf_funciones import (
    obtener_info_dispositivo,
    obtener_estado_interfaces,
    configurar_loopback,
    eliminar_loopback,
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

@app.route('/add_loopback', methods=['POST'])
def add_loopback_route():
    """
    Ruta para manejar la creación de una loopback desde el formulario web.
    """
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    ip = request.form['ip']
    mascara = request.form['mascara']
    
    if configurar_loopback(nombre, descripcion, ip, mascara):
        flash(f"Interfaz {nombre} creada exitosamente.", "success")
    else:
        flash(f"Error al crear la interfaz {nombre}. Revisa la consola para más detalles.", "danger")
        
    return redirect(url_for('index'))

@app.route('/delete_loopback', methods=['POST'])
def delete_loopback_route():
    """
    Ruta para manejar la eliminación de una loopback desde el formulario web.
    """
    nombre = request.form['nombre']
    
    if eliminar_loopback(nombre):
        flash(f"Interfaz {nombre} eliminada exitosamente.", "success")
    else:
        flash(f"Error al eliminar la interfaz {nombre}. Verifica que el nombre exista.", "danger")
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ejecuta la aplicación en modo de depuración para ver los errores fácilmente en el navegador.
    # host='0.0.0.0' permite acceder desde otras máquinas en la misma red.
    app.run(debug=True, host='0.0.0.0', port=5000)
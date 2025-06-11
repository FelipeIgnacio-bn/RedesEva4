# restconf_funciones.py

import requests
import json
from requests.auth import HTTPBasicAuth
from config import ROUTER_IP, ROUTER_USERNAME, ROUTER_PASSWORD, RESTCONF_PORT

# Deshabilitar advertencias de certificados SSL no confiables
# En un entorno de producción, deberías manejar los certificados correctamente.
try:
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
except AttributeError:
    # Manejar versiones más antiguas de 'requests' que podrían no tener esta estructura
    pass

def obtener_info_dispositivo():
    """
    Obtiene y devuelve información básica del dispositivo (hostname y versión).
    Esta es la función que el error indica que falta.
    """
    url = f"https://{ROUTER_IP}:{RESTCONF_PORT}/restconf/data/Cisco-IOS-XE-native:native?fields=hostname;version"
    headers = {"Accept": "application/yang-data+json"}
    try:
        response = requests.get(url, headers=headers, auth=HTTPBasicAuth(ROUTER_USERNAME, ROUTER_PASSWORD), verify=False, timeout=10)
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP (4xx o 5xx)
        data = response.json()
        return data.get("Cisco-IOS-XE-native:native", {})
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener info del dispositivo: {e}")
        return None

def obtener_estado_interfaces():
    """Obtiene y devuelve el estado de las interfaces."""
    url = f"https://{ROUTER_IP}:{RESTCONF_PORT}/restconf/data/ietf-interfaces:interfaces-state"
    headers = {"Accept": "application/yang-data+json"}
    try:
        response = requests.get(url, headers=headers, auth=HTTPBasicAuth(ROUTER_USERNAME, ROUTER_PASSWORD), verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Asegurarse de devolver una lista, incluso si está vacía
        return data.get("ietf-interfaces:interfaces-state", {}).get("interface", [])
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener estado de interfaces: {e}")
        return []
def seleccionar_interfaz():
    tipos = {
        "1": "softwareLoopback",
        "2": "ethernetCsmacd",  # para GigabitEthernet/FastEthernet
    }

    print("Selecciona el tipo de interfaz:")
    print("1. Loopback")
    print("2. Ethernet (GigabitEthernet/FastEthernet)")

    opcion = input("Opción: ").strip()
    tipo_iana = tipos.get(opcion)
    
    if not tipo_iana:
        print("Tipo no válido.")
        return None, None, None

    prefijo = "Loopback" if opcion == "1" else input("Prefijo de interfaz (ej: GigabitEthernet, FastEthernet): ").strip()
    numero = input("Número de interfaz (ej: 0, 0/0): ").strip()
    nombre = f"{prefijo}{numero}"

    return nombre, tipo_iana, prefijo
    
def configurar_interfaz(nombre, tipo_iana, descripcion, ip, mascara):
    """Configura una interfaz genérica por RESTCONF"""
    url = f"https://{ROUTER_IP}:{RESTCONF_PORT}/restconf/data/ietf-interfaces:interfaces"
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json"
    }

    payload = {
        "ietf-interfaces:interface": {
            "name": nombre,
            "description": descripcion,
            "type": f"iana-if-type:{tipo_iana}",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": ip,
                        "netmask": mascara
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(
            url, headers=headers, auth=HTTPBasicAuth(ROUTER_USERNAME, ROUTER_PASSWORD),
            data=json.dumps(payload), verify=False, timeout=10
        )
        if response.status_code == 201:
            print(f"Interfaz '{nombre}' creada exitosamente.")
            return True
        else:
            print(f"Error al crear interfaz: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return False
def eliminar_interfaz():
    nombre = input("Nombre de la interfaz a eliminar (ej: Loopback1, GigabitEthernet0/0): ").strip()
    url = f"https://{ROUTER_IP}:{RESTCONF_PORT}/restconf/data/ietf-interfaces:interfaces/interface={nombre}"
    headers = {"Accept": "application/yang-data+json"}

    try:
        response = requests.delete(
            url, headers=headers, auth=HTTPBasicAuth(ROUTER_USERNAME, ROUTER_PASSWORD), verify=False, timeout=10
        )
        if response.status_code == 204:
            print(f"Interfaz '{nombre}' eliminada exitosamente.")
            return True
        else:
            print(f"Error al eliminar: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return False

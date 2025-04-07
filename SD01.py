import socket
import threading
import time
import sys
from datetime import datetime

# === Configuración del nodo ===
if len(sys.argv) < 2:
    print("Uso: python SD01.py <puerto_propio> <puerto_peer_1> <puerto_peer_2> ...")
    sys.exit(1)

HOST = 'localhost'
PORT = int(sys.argv[1])  # Se pasa como argumento el puerto de este nodo
peers = [int(p) for p in sys.argv[2:]]  # Lista de puertos de los demás nodos

log_filename = f'log_nodo_{PORT}.txt'

def log_message(message):
    with open(log_filename, 'a') as f:
        f.write(message + '\n')

def get_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# === Servidor para recibir mensajes ===
def receiver():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[Nodo {PORT}] Esperando conexiones...")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_connection, args=(conn,)).start()

def handle_connection(conn):
    with conn:
        data = conn.recv(1024).decode()
        if data:
            print(f"[Nodo {PORT}] Mensaje recibido: {data}")
            log_message(f"Recibido: {data}")
            # Enviar respuesta automática
            response = f"ACK del nodo {PORT} a las {get_time()}"
            conn.sendall(response.encode())
            log_message(f"Enviado: {response}")

# === Cliente para enviar mensajes ===
def sender():
    while True:
        msg = input(f"[Nodo {PORT}] Escribe un mensaje: ")
        timestamp = get_time()
        full_msg = f"Mensaje desde nodo {PORT} a las {timestamp}: {msg}"
        for peer_port in peers:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((HOST, peer_port))
                    s.sendall(full_msg.encode())
                    response = s.recv(1024).decode()
                    print(f"[Nodo {PORT}] Respuesta de nodo {peer_port}: {response}")
                    log_message(f"Enviado a nodo {peer_port}: {full_msg}")
                    log_message(f"Respuesta de nodo {peer_port}: {response}")
            except ConnectionRefusedError:
                print(f"[Nodo {PORT}] No se pudo conectar con nodo {peer_port}")

# === Main ===
if __name__ == '__main__':
    print(f"Inicializando nodo en puerto {PORT}. Conectando con {peers}")
    threading.Thread(target=receiver, daemon=True).start()
    sender()  # El hilo principal se queda en modo envío

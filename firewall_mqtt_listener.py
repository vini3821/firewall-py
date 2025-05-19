import paho.mqtt.client as mqtt
import subprocess
import os
import re

# Configurações do broker MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "firewall/block_ip"

# Regex para validar IPs recebidos
IP_REGEX = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")

# Lista para armazenar IPs já bloqueados (evita duplicatas)
blocked_ips = set()

def block_ip(ip):
    if ip in blocked_ips:
        print(f"[INFO] IP já bloqueado: {ip}")
        return

    try:
        print(f"[FIREWALL] Bloqueando IP: {ip}")
        subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True)
        blocked_ips.add(ip)
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Falha ao bloquear IP: {ip} → {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] Conectado ao broker")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"[MQTT] Falha ao conectar, código de retorno {rc}")

def on_message(client, userdata, msg):
    ip = msg.payload.decode("utf-8").strip()
    print(f"[MQTT] Mensagem recebida no tópico '{msg.topic}': {ip}")
    if IP_REGEX.match(ip):
        block_ip(ip)
    else:
        print(f"[AVISO] IP inválido recebido: {ip}")

def main():
    print("[INICIANDO] Firewall MQTT Listener")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"[ERRO] Não foi possível conectar ao broker MQTT: {e}")

if __name__ == "__main__":
    main()

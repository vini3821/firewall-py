import os
import time
import subprocess
from datetime import datetime
from flask import Flask, render_template_string, redirect, url_for

# Armazena MACs detectados
mac_list = {}

# Lista de MACs bloqueadas
blocked_macs = set()

# Função para buscar IP a partir do MAC (via ARP)
def get_ip_from_mac(mac):
    try:
        arp_table = subprocess.check_output("arp -a", shell=True).decode()
        for line in arp_table.splitlines():
            if mac.lower() in line.lower():
                return line.split()[1].strip("()")
    except Exception as e:
        print("Erro ARP:", e)
    return None

# Flask App para a interface
app = Flask(__name__)

# Página principal
@app.route('/')
def index():
    return render_template_string('''
    <h2>Dispositivos Detectados</h2>
    <table border=1>
        <tr><th>MAC</th><th>Última Vez Visto</th><th>Bloqueado</th><th>Ação</th></tr>
        {% for mac, seen in macs.items() %}
        <tr>
            <td>{{ mac }}</td>
            <td>{{ seen }}</td>
            <td>{{ "Sim" if mac in blocked else "Não" }}</td>
            <td>
                {% if mac not in blocked %}
                <a href="{{ url_for('block', mac=mac) }}">Bloquear</a>
                {% else %}
                <a href="{{ url_for('unblock', mac=mac) }}">Desbloquear</a>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </table>
    ''', macs=mac_list, blocked=blocked_macs)

# Rota para bloquear MAC
@app.route('/block/<mac>')
def block(mac):
    ip = get_ip_from_mac(mac)
    if ip:
        os.system(f"sudo iptables -A INPUT -s {ip} -j DROP")
        os.system(f"sudo iptables -A FORWARD -s {ip} -j DROP")
        print(f"[+] Bloqueado IP {ip} (MAC: {mac})")
        blocked_macs.add(mac)
    else:
        print(f"[-] Não foi possível encontrar IP para {mac}")
    return redirect(url_for('index'))

# Rota para desbloquear MAC
@app.route('/unblock/<mac>')
def unblock(mac):
    ip = get_ip_from_mac(mac)
    if ip:
        os.system(f"sudo iptables -D INPUT -s {ip} -j DROP")
        os.system(f"sudo iptables -D FORWARD -s {ip} -j DROP")
        print(f"[+] Desbloqueado IP {ip} (MAC: {mac})")
        blocked_macs.discard(mac)
    return redirect(url_for('index'))

# Script para escutar serial (roda em paralelo)
def listen_serial():
    import serial
    ser = serial.Serial('/dev/ttyUSB0', 115200)
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            mac_list[line] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Inicializa sistema
if __name__ == '__main__':
    import threading
    threading.Thread(target=listen_serial, daemon=True).start()
    print("[*] Web interface iniciando em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000)

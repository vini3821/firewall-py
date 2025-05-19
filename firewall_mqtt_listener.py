import serial
import paho.mqtt.client as mqtt

# Configurações
serial_port = '/dev/ttyUSB0'  # Ou /dev/ttyAMA0 dependendo do ESP
baud_rate = 115200
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic = "esp32/sniffer"

# Inicializa Serial
ser = serial.Serial(serial_port, baud_rate)

# Inicializa MQTT
client = mqtt.Client()
client.connect(mqtt_broker, mqtt_port, 60)

print("Escutando MACs do ESP32...")

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        print("MAC recebido:", line)
        client.publish(mqtt_topic, line)
except KeyboardInterrupt:
    print("Encerrando...")
    ser.close()

from paho.mqtt.client import Client

MQTT_SERVER = "broker.hivemq.com"

def main():
    client = Client()
    client.connect(MQTT_SERVER)

if __name__ == "__main__":
    main()
from paho.mqtt.client import Client
import signal

MQTT_SERVER = "broker.hivemq.com"
MY_TOPIC = "asm/hello"

def sigint(client):   
    def signal_handler(signal, frame):
        client.disconnect()

    signal.signal(signal.SIGINT, signal_handler)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        msg = input("Enter your message: ")
        client.publish(MY_TOPIC, msg)

def on_publish(client, userdata, mid):
    msg = input("Enter your message: ")
    client.publish(MY_TOPIC, msg)

def main():
    client = Client()
    sigint(client)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(MQTT_SERVER)
    client.loop_forever()

if __name__ == "__main__":
    main()
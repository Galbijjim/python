from paho.mqtt.client import Client
import signal

MQTT_SERVER = "broker.hivemq.com"
TOPIC_HELLO = "asm/hello"

def sigint(client):   
    def signal_handler(signal, frame):
        client.disconnect()

    signal.signal(signal.SIGINT, signal_handler)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC_HELLO)   

def on_message(client, userdata, msg):
    print(msg.topic + " " + msg.payload.decode())

def main():   
    client = Client()
    sigint(client)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER)
    client.loop_forever()

if __name__ == "__main__":
    main()
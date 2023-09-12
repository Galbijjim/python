from paho.mqtt.client import Client

mqtt_server = "broker.hivemq.com"
topic = "test/topic"

def put_data(client):
    data = input("Enter your message: ")
    client.publish(topic, data)

def connect_mqtt(client, userdata, flags, rc):
    if rc == 0:
        print("Connected with result code "+str(rc))
        client.subscribe(topic)
        put_data(client)

def publish_mqtt(client, userdata, mid):
    put_data(client)

def message_received(client, userdata, msg):
    print(msg.topic, "->", msg.payload.decode())

def main():
    client = Client()
    client.on_connect = connect_mqtt
    client.on_publish = publish_mqtt
    client.on_message = message_received
    client.connect(mqtt_server)
    client.loop_forever()

if __name__ == "__main__":
    main()
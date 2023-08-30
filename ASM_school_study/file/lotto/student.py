from paho.mqtt.client import Client

MQTT_SERVER = "broker.hivemq.com"

STUDENT_ID = "2307"

TOPIC_LOTTO_SUB = "asm/hxx/lotto/" + STUDENT_ID
TOPIC_LOTTO_PUB = "asm/hxx/lotto/pub"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected")
        client.subscribe(TOPIC_LOTTO_SUB) 

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed")
    client.publish(TOPIC_LOTTO_PUB, STUDENT_ID)

def on_publish(client, userdata, mid):
    print("Published")

def on_message(client, userdata, msg):
    print(msg.topic, msg.payload.decode()) 
    client.disconnect()

def on_disconnect(client, userdata, rc):
    print("Disconnected")

def main():
    client = Client()
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_publish = on_publish
    client.on_message = on_message
    client.on_disconnect = on_disconnect 

    client.connect(MQTT_SERVER)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()

if __name__ == "__main__":
    main()
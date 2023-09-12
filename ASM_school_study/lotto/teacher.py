from paho.mqtt.client import Client
import random

MQTT_SERVER = "broker.hivemq.com"

TOPIC_LOTTO_SUB = "asm/+/lotto/pub" 
TOPIC_LOTTO_PUB = "asm/"

f = None
student_id = None
lotto = None

def on_connect(client, userdata, flags, rc):
    global f

    if rc == 0:
        print("Connected")
        client.subscribe(TOPIC_LOTTO_SUB)
        f = open("result.txt", '+a')

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed")

def on_publish(client, userdata, mid):
    print("Published")
    result = f"{student_id} {lotto}\n"
    print(result, end='')
    f.write(result) 

def on_message(client, userdata, msg):
    global student_id, lotto

    your_string = msg.topic.split("/")[1]

    student_id = msg.payload.decode()
    lotto = str(random.sample(range(1, 46), 6))

    #client.publish(TOPIC_LOTTO_PUB + your_string + "/lotto/" + student_id, lotto)

    new_topic = f"{TOPIC_LOTTO_PUB}{your_string}/lotto/{student_id}"
    client.publish(new_topic, lotto)

def main():
    client = Client()
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_publish = on_publish
    client.on_message = on_message

    client.connect(MQTT_SERVER)
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()
        f.close()

if __name__ == "__main__":
    main()
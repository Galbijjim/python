from paho.mqtt.client import Client

MQTT_SERVER = "broker.hivemq.com"

#1: 학번을 문자열로 입력하세요.
STUDENT_ID = "2307"

TOPIC_LOTTO_SUB = "asm/lotto/" + STUDENT_ID
TOPIC_LOTTO_PUB = "asm/lotto/pub"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("연결됨!")
        #2: 로또 구독 토픽을 브로커에 등록하는 코드를 작성하세요.
        client.subscribe(TOPIC_LOTTO_SUB, qos=1)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed")
    #3 로또 구독 요청 토픽과 학번을 페이로드로 메시지를 발행하는 코드를 작성하세요.
    client.publish(TOPIC_LOTTO_PUB, STUDENT_ID, qos=1)

def on_publish(client, userdata, mid):
    print("Published")


def on_message(client, userdata, msg):
    print(msg.topic, msg.payload.decode()) 

    #4: 브로커 연결을 종료하는 코드를 작성하세요.
    client.disconnect()

def on_disconnect(client, userdata, rc):
    print("연결종료!")

def main():
    client = Client()
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_publish = on_publish
    client.on_message = on_message
    client.on_disconnect = on_disconnect


    #5: MQTT 클라이언트 객체에 콜백을 등록하는 코드를 작성하세요.

    client.connect(MQTT_SERVER)

    #6 메시지 루프를 실행하는 코드를 작성하세요.
    client.loop_forever()

if __name__ == "__main__":
    main()
import os
import json
import urllib.request
import googlemaps
import logging


def __search_sauna(place: str):
    API_KEY = os.environ['API_KEY']
    client = googlemaps.Client(API_KEY)
    geocode_result = client.geocode(place)  # 位置情報を検索
    loc = geocode_result[0]['geometry']['location']  # 軽度・緯度の情報のみ取り出す
    place_result = client.places_nearby(
        location=loc, radius=800, keyword='サウナ', type='spa', language='ja')  # 半径800m以内のサウナの情報を取得
    sauna_list = [place['name'] for place in place_result['results']]
    return sauna_list


def lambda_handler(event, context):

    # 環境変数を参照
    TOKEN = os.environ['TOKEN']
    for message_event in json.loads(event['body'])['events']:
        place = str(message_event['message']['text'])
        sauna_list = __search_sauna(place)
        messages = []
        if len(sauna_list) == 0:
            messages.append({
                "type": "text",
                "text": 'sorry...近くのサウナが見つかりませんでした。',
            })
        else:
            for sauna in sauna_list:
                messages.append({
                    "type": "text",
                    "text": sauna,
                })
        url = 'https://api.line.me/v2/bot/message/reply'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + TOKEN
        }
        body = {
            'replyToken': message_event['replyToken'],
            'messages': messages
        }

        req = urllib.request.Request(url, data=json.dumps(
            body).encode('utf-8'), method='POST', headers=headers)
        try:
            with urllib.request.urlopen(req) as res:
                logging.info(res.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            logging.error(err.code)
            logging.error(err.reason)
        except urllib.error.URLError as err:
            logging.error(err.reason)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

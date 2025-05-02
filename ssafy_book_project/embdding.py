# -- coding: utf-8 --
import numpy as np
import http.client
import json

class CompletionExecutor:
    def __init__(self, host, api_key, request_id): 
        self._host = host
        self._api_key = api_key
        self._request_id = request_id

    def _send_request(self, completion_request):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': self._api_key,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id
        }

        conn = http.client.HTTPSConnection(self._host)
        conn.request('POST', '/testapp/v1/api-tools/embedding/v2', json.dumps(completion_request), headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode(encoding='utf-8'))
        conn.close()
        return result

    def execute(self, completion_request):
        res = self._send_request(completion_request)
        if res['status']['code'] == '20000':
            return res['result']['embedding']
        else:
            return f"Error: {res['status']['message']}"

if __name__ == '__main__': 
    completion_executor = CompletionExecutor(
        host='clovastudio.stream.ntruss.com',
        api_key='Bearer nv-ae40927d2265442b8b8754c8db76f7a9r2Rp',  # Bearer api_key
        request_id='cb74c8fb916a4ebbba73c47fe99e8c83'
    )

    request_data = {
        "text": "2025 롤드컵 우승은 디플러스 기아"
    }

    response_text = completion_executor.execute(request_data)
    print("입력 문장:", request_data["text"])
    print("임베딩 결과:", len(response_text))

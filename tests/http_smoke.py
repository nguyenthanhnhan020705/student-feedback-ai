"""Optional HTTP smoke against a running app without models."""

import argparse

import httpx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8000')
    args = parser.parse_args()
    with httpx.Client(base_url=args.url, timeout=10) as client:
        for path in ('/', '/static/style.css', '/static/app.js', '/docs', '/openapi.json'):
            response = client.get(path)
            assert response.status_code == 200, (path, response.status_code)
        health = client.get('/api/health').json()
        assert health == {'status': 'setup_required', 'models_loaded': {'sentiment': False, 'topic': False}}, health
        assert client.get('/api/metrics').json()['available'] is False
        assert client.post('/api/predict', json={'text': 'Nội dung kiểm thử HTTP'}).status_code == 503
        assert client.post('/api/predict', json={'text': '   '}).status_code == 422
        assert client.post('/api/predict-batch', files={'file': ('valid.csv', b'text\ninput', 'text/csv')}).status_code == 503
        assert client.post('/api/predict-batch', files={'file': ('invalid.csv', b'wrong\ninput', 'text/csv')}).status_code == 422
    print('HTTP smoke PASS: frontend, static, docs, OpenAPI, health, metrics, 503 and validation.')


if __name__ == '__main__':
    main()

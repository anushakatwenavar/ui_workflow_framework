from urllib.parse import urlparse
import time

class RequestLogger:
    def __init__(self, base_url):
        self.base_url = base_url
        self.recorded_requests = []
        self.auth_token = None

    def log_request(self, request):
        parsed_url = urlparse(request.url)
        base_domain = urlparse(self.base_url).netloc
        if base_domain not in parsed_url.netloc:
            return
        skip = ['.css', '.png', '.jpg', '.ico', '.woff', '.js']
        if any(ext in request.url.lower() for ext in skip):
            return

        req = {
            'method': request.method,
            'url': request.url,
            'path': parsed_url.path or '/',
            'query': parsed_url.query,
            'headers': dict(request.headers),
            'post_data': request.post_data if request.method == 'POST' else None,
            'timestamp': time.time(),
        }
        self.recorded_requests.append(req)

    def log_response(self, response):
        try:
            if 'application/json' in response.headers.get('content-type', ''):
                body = response.json()
                for key in ['token', 'auth_token', 'jwt', 'access_token']:
                    if key in body:
                        self.auth_token = body[key]
                        print(f"🔑 Found token: {key}")
                        break
        except Exception:
            pass

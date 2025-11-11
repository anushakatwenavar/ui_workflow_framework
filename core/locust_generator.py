import os, json, re
from datetime import datetime

class LocustGenerator:
    def __init__(self, base_url, recorded_requests, cookies, auth_token):
        self.base_url = base_url
        self.recorded_requests = recorded_requests
        self.cookies = cookies
        self.auth_token = auth_token

    def generate(self, output_file='reports/generated_scripts/load_test.py'):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        print(f"\n Generating Locust script: {output_file}")

        unique_reqs = self._deduplicate_requests()
        script = self._build_header() + self._build_class(unique_reqs)

        with open(output_file, 'w') as f:
            f.write(script)
        print(f" Locust script generated successfully at {output_file}")

    def _deduplicate_requests(self):
        seen = set()
        unique = []
        for req in self.recorded_requests:
            key = f"{req['method']}:{req['path']}"
            if req['method'] == 'GET' and key in seen:
                continue
            seen.add(key)
            unique.append(req)
        return unique

    def _build_header(self):
        cookie_dict = {c['name']: c['value'] for c in self.cookies}
        return f'''"""
Auto-generated Locust Load Test Script
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Base URL: {self.base_url}
"""
from locust import HttpUser, task, between, SequentialTaskSet
import json

COOKIES = {json.dumps(cookie_dict, indent=4)}
AUTH_TOKEN = {repr(self.auth_token)}

'''

    def _build_class(self, requests):
        tasks = ""
        for idx, req in enumerate(requests, 1):
            path = req['path'] or '/'
            method = req['method']
            clean = re.sub(r'[^a-zA-Z0-9_]', '_', path.strip('/')) or 'root'
            task_name = f"task_{idx}_{method.lower()}_{clean}"
            tasks += f'''
    @task
    def {task_name}(self):
        self.client.{method.lower()}("{path}")
'''
        return f'''
class UserWorkflow(SequentialTaskSet):
    def on_start(self):
        for n, v in COOKIES.items():
            self.client.cookies.set(n, v)
    {tasks}

class WebsiteUser(HttpUser):
    tasks = [UserWorkflow]
    wait_time = between(1, 3)
'''

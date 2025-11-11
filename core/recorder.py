from core.playwright_manager import PlaywrightManager
from core.request_logger import RequestLogger
from core.locust_generator import LocustGenerator
from urllib.parse import urlparse
import time

class WorkflowRecorder:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.cookies = []

    def record_workflow(self, login_url=None, username_selector=None, password_selector=None, submit_selector=None):
        manager = PlaywrightManager()
        p, browser, context, page = manager.launch()
        logger = RequestLogger(self.base_url)
        context.on('request', logger.log_request)
        context.on('response', logger.log_response)

        login_page = login_url or f"{self.base_url}/login"
        print(f" Navigating to {login_page}")
        page.goto(login_page, wait_until='networkidle')

        #  Wait a bit for dynamic UI to render (Vue/React delay)
        page.wait_for_timeout(2500)

        # Wait for any input to appear to ensure DOM is ready
        try:
            page.wait_for_selector("input", timeout=5000)
        except:
            print(" Inputs did not appear in time. Proceeding anyway...")

        # --- auto login
        print(" Detecting login fields...")
        if not username_selector:
            username_selector = self._find_element(
                page,
                [
                    'input[name="email"]',
                    'input[name="username"]',
                    '#email',
                    'input[placeholder*="Email" i]',
                    'input[type="text"]'
                ]
            )

        if not password_selector:
            password_selector = self._find_element(
                page,
                [
                    'input[name="password"]',
                    '#password',
                    'input[placeholder*="Password" i]'
                ]
            )

        if not submit_selector:
            submit_selector = self._find_element(
                page,
                [
                    'button[type="submit"]',
                    'button:has-text("Login")',
                    'button:has-text("Sign in")',
                    'button:has-text("Log in")',
                ]
            )

        #  Fill and submit
        if username_selector and password_selector:
            print(" Logging in automatically...")
            try:
                page.fill(username_selector, self.username)
                page.fill(password_selector, self.password)
            except:
                # fallback to manual typing (if it's a custom input)
                page.click(username_selector)
                page.keyboard.type(self.username)
                page.click(password_selector)
                page.keyboard.type(self.password)

            if submit_selector:
                print(f" Submitting login form via {submit_selector}")
                page.click(submit_selector)
                page.wait_for_load_state('networkidle', timeout=15000)
                print(" Login successful!")
            else:
                print(" Submit button not found. Please press Enter manually in browser.")
        else:
            print(" Could not detect login fields. Log in manually.")
            input("Press Enter when logged in...")

        #  Save cookies
        self.cookies = context.cookies()
        print(f" Saved {len(self.cookies)} cookies")

        print("\n Now perform your user actions. Close browser when done.")
        try:
            page.wait_for_event('close', timeout=0)
        except KeyboardInterrupt:
            print("\n Recording interrupted manually. Closing browser...")
        finally:
            browser.close()
            p.stop()

        print(f"\n Captured {len(logger.recorded_requests)} requests")
        return logger.recorded_requests, self.cookies, logger.auth_token

    def _find_element(self, page, selectors):
        """Try each selector and return the first visible one"""
        for s in selectors:
            try:
                el = page.query_selector(s)
                if el and el.is_visible():
                    print(f"✓ Found selector: {s}")
                    return s
            except:
                continue
        return None

    def generate_locust_script(self, requests, cookies, token, filename):
        generator = LocustGenerator(self.base_url, requests, cookies, token)
        generator.generate(filename)

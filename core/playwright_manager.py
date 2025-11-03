from playwright.sync_api import sync_playwright

class PlaywrightManager:
    def __init__(self, headless=False, slow_mo=100):
        self.headless = headless
        self.slow_mo = slow_mo

    def launch(self):
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        return p, browser, context, page

import sys
import time
from playwright.sync_api import sync_playwright

def check_and_wake(url):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking status of: {url}")
    try:
        with sync_playwright() as p:
            # Launch chromium headlessly
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1280, "height": 720})
            page = context.new_page()
            
            # Navigate with a timeout of 30 seconds
            page.goto(url, timeout=30000)
            
            # Wait for either the main app selector or the sleep notification container
            time.sleep(3) 
            
            # Check for the Streamlit Community Cloud sleep button
            # Usually contains the text "Yes, get this app back up!"
            button_selector = "button:has-text('Yes, get this app back up!')"
            sleep_text_selector = "text='This app has gone to sleep due to inactivity'"
            
            is_asleep = page.is_visible(sleep_text_selector) or page.is_visible(button_selector)
            
            if is_asleep:
                print("Detecting sleep state: App is hibernating. Attempting to wake it up...")
                
                # Double check button selector and click
                btn = page.query_selector(button_selector)
                if btn:
                    btn.click()
                    print("Clicked wake-up button. Waiting for engine to initialize...")
                    time.sleep(8)  # wait for rebuild/start
                    print("Wake up signal sent successfully.")
                else:
                    print("Error: Detected sleep text, but couldn't locate the wake-up button.")
            else:
                # App is awake. Check for header element or page load
                title = page.title()
                print(f"Detecting active state: App is awake. Page title: '{title}'")
                
            browser.close()
    except Exception as e:
        print(f"Uptime monitor check failed: {e}")

if __name__ == "__main__":
    # Get target URL from args, default to localhost
    target_url = "http://localhost:8501"
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
        
    check_and_wake(target_url)

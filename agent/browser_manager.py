"""
Browser Manager untuk Autonomous Agent
"""
import asyncio
import os
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from agent.models import BrowserState

class BrowserManager:
    """Manager untuk browser automation menggunakan Playwright"""
    
    def __init__(self, headless: bool = True, browser_type: str = "chromium"):
        self.headless = headless
        self.browser_type = browser_type
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.current_state = BrowserState()
    
    async def initialize(self) -> bool:
        """Initialize browser"""
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser
            if self.browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-gpu'
                    ]
                )
            elif self.browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(headless=self.headless)
            elif self.browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(headless=self.headless)
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")
            
            # Create context
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set default timeout
            self.page.set_default_timeout(30000)
            
            return True
        except Exception as e:
            print(f"Failed to initialize browser: {e}")
            return False
    
    async def close(self):
        """Close browser dan cleanup"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"Error closing browser: {e}")
    
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate ke URL"""
        try:
            if not self.page:
                raise Exception("Browser not initialized")
            
            await self.page.goto(url, wait_until="domcontentloaded")
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            
            # Update state
            self.current_state.current_url = self.page.url
            self.current_state.page_title = await self.page.title()
            
            return {
                "success": True,
                "url": self.current_state.current_url,
                "title": self.current_state.page_title
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def click_element(self, selector: str) -> Dict[str, Any]:
        """Click element berdasarkan selector"""
        try:
            if not self.page:
                raise Exception("Browser not initialized")
            
            # Wait for element
            await self.page.wait_for_selector(selector, timeout=10000)
            
            # Click element
            await self.page.click(selector)
            
            # Wait for potential page changes
            await asyncio.sleep(1)
            
            # Update current URL in case of navigation
            self.current_state.current_url = self.page.url
            
            return {
                "success": True,
                "message": f"Clicked element: {selector}",
                "current_url": self.current_state.current_url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def type_text(self, selector: str, text: str) -> Dict[str, Any]:
        """Type text ke input field"""
        try:
            if not self.page:
                raise Exception("Browser not initialized")
            
            # Wait for element
            await self.page.wait_for_selector(selector, timeout=10000)
            
            # Clear and type
            await self.page.fill(selector, text)
            
            return {
                "success": True,
                "message": f"Typed text into {selector}",
                "text": text
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_page_content(self) -> Dict[str, Any]:
        """Get current page content"""
        try:
            if not self.page:
                raise Exception("Browser not initialized")
            
            content = await self.page.content()
            title = await self.page.title()
            url = self.page.url
            
            return {
                "success": True,
                "content": content,
                "title": title,
                "url": url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def take_screenshot(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Take screenshot dari current page"""
        try:
            if not self.page:
                raise Exception("Browser not initialized")
            
            if not path:
                path = f"/app/screenshots/screenshot_{int(asyncio.get_event_loop().time())}.png"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            await self.page.screenshot(path=path, full_page=True)
            
            self.current_state.screenshot_path = path
            
            return {
                "success": True,
                "screenshot_path": path
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def wait_for_element(self, selector: str, timeout: int = 10000) -> Dict[str, Any]:
        """Wait for element to appear"""
        try:
            if not self.page:
                raise Exception("Browser not initialized")
            
            await self.page.wait_for_selector(selector, timeout=timeout)
            
            return {
                "success": True,
                "message": f"Element {selector} appeared"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_javascript(self, script: str) -> Dict[str, Any]:
        """Execute JavaScript di page"""
        try:
            if not self.page:
                raise Exception("Browser not initialized")
            
            result = await self.page.evaluate(script)
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_current_state(self) -> BrowserState:
        """Get current browser state"""
        return self.current_state
    
    async def get_interactive_elements(self) -> Dict[str, Any]:
        """Get interactive elements dari current page"""
        try:
            if not self.page:
                raise Exception("Browser not initialized")
            
            # JavaScript untuk get interactive elements
            script = """
            () => {
                const elements = [];
                
                // Get buttons
                document.querySelectorAll('button, input[type="button"], input[type="submit"]').forEach((el, index) => {
                    const text = el.textContent.trim() || el.value || '';
                    if (text) {
                        elements.push({
                            type: 'button',
                            text: text,
                            selector: `button:nth-of-type(${index + 1})`,
                            tagName: el.tagName.toLowerCase()
                        });
                    }
                });
                
                // Get links
                document.querySelectorAll('a[href]').forEach((el, index) => {
                    const text = el.textContent.trim();
                    if (text) {
                        elements.push({
                            type: 'link',
                            text: text,
                            href: el.href,
                            selector: `a:nth-of-type(${index + 1})`,
                            tagName: el.tagName.toLowerCase()
                        });
                    }
                });
                
                // Get input fields
                document.querySelectorAll('input, textarea').forEach((el, index) => {
                    elements.push({
                        type: 'input',
                        inputType: el.type || 'text',
                        placeholder: el.placeholder || '',
                        name: el.name || '',
                        selector: `${el.tagName.toLowerCase()}:nth-of-type(${index + 1})`,
                        tagName: el.tagName.toLowerCase()
                    });
                });
                
                return elements.slice(0, 20); // Limit to first 20 elements
            }
            """
            
            elements = await self.page.evaluate(script)
            
            return {
                "success": True,
                "elements": elements
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


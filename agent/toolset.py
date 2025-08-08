"""
Toolset untuk Autonomous Agent
"""
import asyncio
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup

class Tool(ABC):
    """Abstract base class untuk tools"""
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool dengan parameters"""
        pass

class BrowserTool(Tool):
    """Base class untuk browser-related tools"""
    
    def __init__(self, browser: Optional[Browser] = None, page: Optional[Page] = None):
        self.browser = browser
        self.page = page

class NavigateTool(BrowserTool):
    """Tool untuk navigate ke URL"""
    
    async def execute(self, url: str, **kwargs) -> Dict[str, Any]:
        """Navigate ke URL yang diberikan"""
        try:
            if not self.page:
                raise Exception("Browser page not initialized")
            
            await self.page.goto(url, wait_until="domcontentloaded")
            
            # Wait for page to load
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            
            current_url = self.page.url
            title = await self.page.title()
            
            return {
                "success": True,
                "result": {
                    "current_url": current_url,
                    "title": title,
                    "message": f"Successfully navigated to {current_url}"
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class ClickTool(BrowserTool):
    """Tool untuk click element"""
    
    async def execute(self, selector: str, **kwargs) -> Dict[str, Any]:
        """Click element berdasarkan CSS selector atau XPath"""
        try:
            if not self.page:
                raise Exception("Browser page not initialized")
            
            # Wait for element to be visible
            await self.page.wait_for_selector(selector, timeout=10000)
            
            # Click element
            await self.page.click(selector)
            
            # Wait a bit for any page changes
            await asyncio.sleep(1)
            
            return {
                "success": True,
                "result": {
                    "message": f"Successfully clicked element: {selector}",
                    "current_url": self.page.url
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class TypeTool(BrowserTool):
    """Tool untuk type text ke input field"""
    
    async def execute(self, selector: str, text: str, **kwargs) -> Dict[str, Any]:
        """Type text ke input field"""
        try:
            if not self.page:
                raise Exception("Browser page not initialized")
            
            # Wait for element to be visible
            await self.page.wait_for_selector(selector, timeout=10000)
            
            # Clear existing text and type new text
            await self.page.fill(selector, text)
            
            return {
                "success": True,
                "result": {
                    "message": f"Successfully typed text into {selector}",
                    "text": text
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class ReadDOMTool(BrowserTool):
    """Tool untuk read DOM dari current page"""
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Read dan summarize DOM dari current page"""
        try:
            if not self.page:
                raise Exception("Browser page not initialized")
            
            # Get page content
            content = await self.page.content()
            current_url = self.page.url
            title = await self.page.title()
            
            # Parse dengan BeautifulSoup untuk summarization
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script dan style tags
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text_content = soup.get_text()
            
            # Get interactive elements
            interactive_elements = []
            
            # Find buttons
            buttons = soup.find_all(['button', 'input[type="button"]', 'input[type="submit"]'])
            for btn in buttons[:10]:  # Limit to first 10
                text = btn.get_text(strip=True) or btn.get('value', '')
                if text:
                    interactive_elements.append({
                        "type": "button",
                        "text": text,
                        "selector": self._generate_selector(btn)
                    })
            
            # Find links
            links = soup.find_all('a', href=True)
            for link in links[:10]:  # Limit to first 10
                text = link.get_text(strip=True)
                if text:
                    interactive_elements.append({
                        "type": "link",
                        "text": text,
                        "href": link['href'],
                        "selector": self._generate_selector(link)
                    })
            
            # Find input fields
            inputs = soup.find_all(['input', 'textarea'])
            for inp in inputs[:10]:  # Limit to first 10
                input_type = inp.get('type', 'text')
                placeholder = inp.get('placeholder', '')
                name = inp.get('name', '')
                interactive_elements.append({
                    "type": f"input_{input_type}",
                    "placeholder": placeholder,
                    "name": name,
                    "selector": self._generate_selector(inp)
                })
            
            # Create summary
            summary = {
                "url": current_url,
                "title": title,
                "text_preview": text_content[:500] + "..." if len(text_content) > 500 else text_content,
                "interactive_elements": interactive_elements,
                "total_text_length": len(text_content)
            }
            
            return {
                "success": True,
                "result": summary
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_selector(self, element) -> str:
        """Generate CSS selector untuk element"""
        # Simple selector generation
        tag = element.name
        
        # Try ID first
        if element.get('id'):
            return f"#{element['id']}"
        
        # Try class
        if element.get('class'):
            classes = ' '.join(element['class'])
            return f"{tag}.{classes.replace(' ', '.')}"
        
        # Try name
        if element.get('name'):
            return f"{tag}[name='{element['name']}']"
        
        # Fallback to tag
        return tag

class WaitTool(Tool):
    """Tool untuk wait/delay"""
    
    async def execute(self, seconds: float = 1.0, **kwargs) -> Dict[str, Any]:
        """Wait untuk specified seconds"""
        try:
            await asyncio.sleep(seconds)
            return {
                "success": True,
                "result": {
                    "message": f"Waited for {seconds} seconds"
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class Toolset:
    """Container untuk semua tools"""
    
    def __init__(self, browser: Optional[Browser] = None, page: Optional[Page] = None):
        self.browser = browser
        self.page = page
        
        # Initialize tools
        self.tools = {
            "navigate": NavigateTool(browser, page),
            "click": ClickTool(browser, page),
            "type": TypeTool(browser, page),
            "read_dom": ReadDOMTool(browser, page),
            "wait": WaitTool()
        }
    
    def update_browser_context(self, browser: Browser, page: Page):
        """Update browser context untuk semua browser tools"""
        self.browser = browser
        self.page = page
        
        for tool_name, tool in self.tools.items():
            if isinstance(tool, BrowserTool):
                tool.browser = browser
                tool.page = page
    
    async def execute_tool(self, tool_name: str, **parameters) -> Dict[str, Any]:
        """Execute tool dengan nama dan parameters"""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
        
        tool = self.tools[tool_name]
        return await tool.execute(**parameters)
    
    def get_available_tools(self) -> Dict[str, str]:
        """Get list of available tools"""
        return {
            "navigate": "Navigate to a URL",
            "click": "Click element by CSS selector or XPath",
            "type": "Type text into input field",
            "read_dom": "Read current page DOM",
            "wait": "Wait for specified seconds"
        }


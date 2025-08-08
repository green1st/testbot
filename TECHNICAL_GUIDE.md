# Technical Guide - Autonomous Agent System

Panduan teknis mendalam untuk memahami implementasi dan arsitektur sistem agent otomatis.

## 🏗️ Arsitektur Detail

### 1. Agent Orchestrator

`AgentOrchestrator` adalah komponen utama yang mengelola siklus perencanaan-eksekusi-observasi:

```python
class AgentOrchestrator:
    def __init__(self, llm_provider="openai", browser_type="chromium", headless=True):
        self.llm = create_llm_interface(llm_provider)
        self.browser_manager = BrowserManager(headless, browser_type)
        self.toolset = Toolset()
    
    async def execute_task(self, request: AgentRequest) -> AgentResponse:
        # Main loop: Planning -> Execution -> Observation
        for step in range(request.max_iterations):
            observation = await self._get_current_observation()
            planning = await self._plan_next_action(goal, observation, history)
            result = await self._execute_tool_call(planning)
            
            if await self._is_goal_achieved(goal, observation):
                break
```

### 2. LLM Interface

Abstraksi untuk berbagai provider LLM:

```python
class LLMInterface(ABC):
    @abstractmethod
    async def plan_next_action(self, goal: str, current_state: str, history: List[str]) -> Dict[str, Any]:
        pass

class OpenAIInterface(LLMInterface):
    async def plan_next_action(self, goal, current_state, history):
        prompt = f"""
        GOAL: {goal}
        CURRENT STATE: {current_state}
        HISTORY: {history}
        
        Choose next action from: navigate, click, type, read_dom, wait
        Respond in JSON format with reasoning and parameters.
        """
        return await self.generate_response(prompt)
```

### 3. Browser Manager

Mengelola instance browser dan operasi automation:

```python
class BrowserManager:
    async def initialize(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        self.page = await self.browser.new_page()
    
    async def navigate(self, url: str):
        await self.page.goto(url, wait_until="domcontentloaded")
        return {"success": True, "url": self.page.url}
```

### 4. Toolset System

Kumpulan tools yang dapat dipanggil oleh LLM:

```python
class Toolset:
    def __init__(self, browser, page):
        self.tools = {
            "navigate": NavigateTool(browser, page),
            "click": ClickTool(browser, page),
            "type": TypeTool(browser, page),
            "read_dom": ReadDOMTool(browser, page),
            "wait": WaitTool()
        }
    
    async def execute_tool(self, tool_name: str, **parameters):
        return await self.tools[tool_name].execute(**parameters)
```

## 🔄 Loop Perencanaan-Eksekusi-Observasi

### Fase 1: Observasi (Observation)

```python
async def _get_current_observation(self) -> str:
    # Ambil DOM content
    dom_result = await self.toolset.execute_tool("read_dom")
    
    # Ringkas informasi penting
    observation = f"""
    Current URL: {result['url']}
    Page Title: {result['title']}
    Interactive Elements: {result['interactive_elements'][:5]}
    """
    return observation
```

### Fase 2: Perencanaan (Planning)

```python
async def _plan_next_action(self, goal, current_state, history):
    prompt = f"""
    Anda adalah autonomous agent. 
    GOAL: {goal}
    CURRENT STATE: {current_state}
    HISTORY: {history}
    
    Pilih action selanjutnya dan berikan reasoning.
    Format JSON: {{"reasoning": "...", "tool_name": "...", "parameters": {{}}}}
    """
    
    return await self.llm.generate_response(prompt)
```

### Fase 3: Eksekusi (Execution)

```python
async def _execute_tool_call(self, tool_call):
    return await self.toolset.execute_tool(
        tool_call.tool_name,
        **tool_call.parameters
    )
```

## 🛠️ Tool Implementation

### NavigateTool

```python
class NavigateTool(BrowserTool):
    async def execute(self, url: str, **kwargs):
        await self.page.goto(url, wait_until="domcontentloaded")
        await self.page.wait_for_load_state("networkidle", timeout=10000)
        
        return {
            "success": True,
            "result": {
                "current_url": self.page.url,
                "title": await self.page.title()
            }
        }
```

### ReadDOMTool

```python
class ReadDOMTool(BrowserTool):
    async def execute(self, **kwargs):
        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove noise
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract interactive elements
        interactive_elements = []
        
        # Buttons
        for btn in soup.find_all(['button', 'input[type="button"]'])[:10]:
            interactive_elements.append({
                "type": "button",
                "text": btn.get_text(strip=True),
                "selector": self._generate_selector(btn)
            })
        
        return {
            "success": True,
            "result": {
                "url": self.page.url,
                "title": await self.page.title(),
                "interactive_elements": interactive_elements,
                "text_preview": soup.get_text()[:500]
            }
        }
```

## 🐳 Docker Configuration

### Dockerfile Breakdown

```dockerfile
FROM ubuntu:22.04

# System dependencies untuk browser
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-pip \
    xvfb \              # Virtual display
    libnss3 \           # Browser dependencies
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libgbm1 \
    libasound2

# Install Node.js untuk Playwright
RUN curl -fsSL https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-x64.tar.xz | \
    tar -xJ -C /usr/local --strip-components=1

# Python dependencies
COPY requirements.txt .
RUN python3.11 -m pip install -r requirements.txt

# Install Playwright browsers
RUN python3.11 -m playwright install chromium
RUN python3.11 -m playwright install-deps

# Security: non-root user
RUN useradd -m -u 1000 agent
USER agent
```

### Docker Compose Configuration

```yaml
version: '3.8'
services:
  autonomous-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    security_opt:
      - seccomp:unconfined  # Untuk browser
    shm_size: 2gb          # Shared memory untuk browser
```

## 🔒 Security Considerations

### 1. Sandbox Isolation

- Container berjalan dengan user non-root
- Network access terbatas melalui Docker networking
- File system access terisolasi
- Resource limits (CPU, memory) dapat dikonfigurasi

### 2. API Security

```python
# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/agent/execute")
@limiter.limit("5/minute")  # Max 5 requests per minute
async def execute_agent_task(request: AgentRequest):
    pass
```

### 3. Input Validation

```python
class AgentRequest(BaseModel):
    goal: str = Field(..., max_length=1000)
    max_iterations: int = Field(default=10, ge=1, le=50)
    timeout: int = Field(default=300, ge=30, le=1800)
```

## 📊 Monitoring & Logging

### Structured Logging

```python
import logging
import json

class StructuredLogger:
    def __init__(self):
        self.logger = logging.getLogger("autonomous_agent")
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def log_step(self, step_number, tool_name, success, duration):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "step": step_number,
            "tool": tool_name,
            "success": success,
            "duration_ms": duration * 1000
        }
        self.logger.info(json.dumps(log_data))
```

### Metrics Collection

```python
class MetricsCollector:
    def __init__(self):
        self.metrics = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "average_steps": 0,
            "tool_usage": defaultdict(int)
        }
    
    def record_task_completion(self, response: AgentResponse):
        self.metrics["total_tasks"] += 1
        if response.status == "completed":
            self.metrics["successful_tasks"] += 1
        
        for step in response.steps:
            self.metrics["tool_usage"][step.tool_call.tool_name] += 1
```

## 🚀 Performance Optimization

### 1. Browser Optimization

```python
# Disable images untuk faster loading
await self.context.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort())

# Set viewport size
await self.context.set_viewport_size({"width": 1280, "height": 720})

# Configure timeouts
self.page.set_default_timeout(30000)
self.page.set_default_navigation_timeout(30000)
```

### 2. LLM Response Caching

```python
from functools import lru_cache
import hashlib

class CachedLLMInterface:
    def __init__(self, base_interface):
        self.base = base_interface
        self.cache = {}
    
    async def plan_next_action(self, goal, current_state, history):
        # Create cache key
        cache_key = hashlib.md5(
            f"{goal}:{current_state}:{str(history)}".encode()
        ).hexdigest()
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = await self.base.plan_next_action(goal, current_state, history)
        self.cache[cache_key] = result
        return result
```

### 3. Concurrent Task Execution

```python
import asyncio
from asyncio import Semaphore

class ConcurrentOrchestrator:
    def __init__(self, max_concurrent=3):
        self.semaphore = Semaphore(max_concurrent)
        self.active_tasks = {}
    
    async def execute_task(self, request: AgentRequest):
        async with self.semaphore:
            return await self._execute_single_task(request)
```

## 🧪 Testing Strategy

### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_navigate_tool():
    # Mock browser page
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.url = "https://example.com"
    mock_page.title = AsyncMock(return_value="Example")
    
    # Test tool
    tool = NavigateTool(None, mock_page)
    result = await tool.execute(url="https://example.com")
    
    assert result["success"] is True
    assert result["result"]["current_url"] == "https://example.com"
    mock_page.goto.assert_called_once()
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_agent_workflow():
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    request = AgentRequest(
        goal="Navigate to example.com",
        max_iterations=3
    )
    
    response = await orchestrator.execute_task(request)
    
    assert response.status in ["completed", "failed"]
    assert len(response.steps) > 0
    
    await orchestrator.cleanup()
```

## 🔧 Customization & Extension

### Adding New Tools

```python
class CustomTool(Tool):
    async def execute(self, **kwargs):
        # Custom implementation
        return {"success": True, "result": "Custom action completed"}

# Register tool
toolset.tools["custom_action"] = CustomTool()
```

### Custom LLM Provider

```python
class CustomLLMInterface(LLMInterface):
    async def generate_response(self, prompt, context=None):
        # Custom LLM implementation
        pass
    
    async def plan_next_action(self, goal, current_state, history):
        # Custom planning logic
        pass
```

### Plugin System

```python
class PluginManager:
    def __init__(self):
        self.plugins = []
    
    def register_plugin(self, plugin):
        self.plugins.append(plugin)
    
    async def execute_hooks(self, hook_name, *args, **kwargs):
        for plugin in self.plugins:
            if hasattr(plugin, hook_name):
                await getattr(plugin, hook_name)(*args, **kwargs)
```

## 📈 Scaling Considerations

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  autonomous-agent:
    build: .
    deploy:
      replicas: 3
    environment:
      - INSTANCE_ID=${HOSTNAME}
  
  nginx:
    image: nginx
    ports:
      - "80:80"
    depends_on:
      - autonomous-agent
```

### Resource Management

```python
# Resource limits dalam Docker
services:
  autonomous-agent:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

Panduan teknis ini memberikan pemahaman mendalam tentang implementasi sistem agent otomatis, dari arsitektur hingga optimisasi dan scaling.


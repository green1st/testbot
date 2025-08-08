"""
Demo script untuk Autonomous Agent
"""
import asyncio
import os
from agent.orchestrator import AgentOrchestrator
from agent.models import AgentRequest

async def demo_web_search():
    """Demo: Search di Google dan baca hasil"""
    print("=== DEMO: Web Search ===")
    
    # Set dummy API key
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "dummy-key"
    
    orchestrator = AgentOrchestrator(headless=False)  # Non-headless untuk demo
    
    try:
        await orchestrator.initialize()
        
        request = AgentRequest(
            goal="Navigate to Google and search for 'autonomous agent'",
            max_iterations=5
        )
        
        response = await orchestrator.execute_task(request)
        
        print(f"\\nDemo Result:")
        print(f"Status: {response.status}")
        print(f"Steps: {len(response.steps)}")
        print(f"Time: {response.execution_time:.2f}s")
        
        return response
        
    finally:
        await orchestrator.cleanup()

async def demo_form_filling():
    """Demo: Fill form di website"""
    print("\\n=== DEMO: Form Filling ===")
    
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "dummy-key"
    
    orchestrator = AgentOrchestrator(headless=False)
    
    try:
        await orchestrator.initialize()
        
        request = AgentRequest(
            goal="Navigate to httpbin.org/forms/post and fill the form with sample data",
            max_iterations=8
        )
        
        response = await orchestrator.execute_task(request)
        
        print(f"\\nDemo Result:")
        print(f"Status: {response.status}")
        print(f"Steps: {len(response.steps)}")
        print(f"Time: {response.execution_time:.2f}s")
        
        return response
        
    finally:
        await orchestrator.cleanup()

async def demo_simple_navigation():
    """Demo sederhana: Navigate ke website dan baca content"""
    print("=== DEMO: Simple Navigation ===")
    
    from agent.browser_manager import BrowserManager
    
    browser_manager = BrowserManager(headless=False)
    
    try:
        print("1. Initializing browser...")
        await browser_manager.initialize()
        
        print("2. Navigating to example.com...")
        result = await browser_manager.navigate("https://example.com")
        print(f"   Result: {result.get('title', 'No title')}")
        
        print("3. Taking screenshot...")
        screenshot_result = await browser_manager.take_screenshot("/tmp/demo_screenshot.png")
        if screenshot_result.get('success'):
            print(f"   Screenshot saved: {screenshot_result.get('screenshot_path')}")
        
        print("4. Getting interactive elements...")
        elements_result = await browser_manager.get_interactive_elements()
        if elements_result.get('success'):
            elements = elements_result.get('elements', [])
            print(f"   Found {len(elements)} interactive elements")
            for i, element in enumerate(elements[:3]):  # Show first 3
                print(f"     {i+1}. {element.get('type')}: {element.get('text', element.get('placeholder', 'N/A'))}")
        
        print("5. Waiting 3 seconds for demo...")
        await asyncio.sleep(3)
        
        print("✅ Simple navigation demo completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    
    finally:
        await browser_manager.close()

async def main():
    """Main demo function"""
    print("🤖 Autonomous Agent Demo")
    print("=" * 50)
    
    demos = [
        ("Simple Navigation", demo_simple_navigation),
        # ("Web Search", demo_web_search),  # Commented out karena butuh API key
        # ("Form Filling", demo_form_filling)  # Commented out karena butuh API key
    ]
    
    for demo_name, demo_func in demos:
        print(f"\\n🚀 Running {demo_name} Demo...")
        try:
            await demo_func()
            print(f"✅ {demo_name} demo completed successfully!")
        except Exception as e:
            print(f"❌ {demo_name} demo failed: {e}")
        
        print("\\n" + "-" * 50)
    
    print("\\n🎉 All demos completed!")
    print("\\nNote: For full LLM-powered demos, set OPENAI_API_KEY environment variable.")

if __name__ == "__main__":
    asyncio.run(main())


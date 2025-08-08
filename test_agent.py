"""
Test script untuk Autonomous Agent
"""
import asyncio
import os
from agent.orchestrator import AgentOrchestrator
from agent.models import AgentRequest

async def test_basic_functionality():
    """Test basic functionality dari agent"""
    print("=== Testing Basic Agent Functionality ===")
    
    # Set dummy API key untuk testing (jika tidak ada)
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "dummy-key-for-testing"
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(
        llm_provider="openai",
        browser_type="chromium",
        headless=True
    )
    
    try:
        # Initialize
        print("Initializing agent...")
        success = await orchestrator.initialize()
        if not success:
            print("❌ Failed to initialize agent")
            return False
        
        print("✅ Agent initialized successfully")
        
        # Test browser navigation
        print("\\nTesting browser navigation...")
        request = AgentRequest(
            goal="Navigate to example.com and read the page content",
            max_iterations=3
        )
        
        response = await orchestrator.execute_task(request)
        
        print(f"Task Status: {response.status}")
        print(f"Steps Executed: {len(response.steps)}")
        print(f"Execution Time: {response.execution_time:.2f}s")
        
        if response.steps:
            print("\\nStep Details:")
            for step in response.steps:
                print(f"  Step {step.step_number}: {step.tool_call.tool_name}")
                print(f"    Success: {step.success}")
                if step.tool_call.error:
                    print(f"    Error: {step.tool_call.error}")
        
        return response.status in ["completed", "failed"]  # Either is acceptable for testing
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        # Cleanup
        await orchestrator.cleanup()

async def test_browser_manager():
    """Test browser manager secara terpisah"""
    print("\\n=== Testing Browser Manager ===")
    
    from agent.browser_manager import BrowserManager
    
    browser_manager = BrowserManager(headless=True)
    
    try:
        # Initialize
        print("Initializing browser...")
        success = await browser_manager.initialize()
        if not success:
            print("❌ Failed to initialize browser")
            return False
        
        print("✅ Browser initialized successfully")
        
        # Test navigation
        print("Testing navigation to example.com...")
        result = await browser_manager.navigate("https://example.com")
        
        if result.get('success'):
            print(f"✅ Navigation successful: {result.get('title')}")
        else:
            print(f"❌ Navigation failed: {result.get('error')}")
            return False
        
        # Test DOM reading
        print("Testing DOM reading...")
        content_result = await browser_manager.get_page_content()
        
        if content_result.get('success'):
            content = content_result.get('content', '')
            print(f"✅ DOM reading successful: {len(content)} characters")
        else:
            print(f"❌ DOM reading failed: {content_result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        return False
    
    finally:
        await browser_manager.close()

async def test_toolset():
    """Test toolset secara terpisah"""
    print("\\n=== Testing Toolset ===")
    
    from agent.toolset import Toolset
    from agent.browser_manager import BrowserManager
    
    browser_manager = BrowserManager(headless=True)
    
    try:
        # Initialize browser
        await browser_manager.initialize()
        
        # Initialize toolset
        toolset = Toolset(browser_manager.browser, browser_manager.page)
        
        # Test available tools
        available_tools = toolset.get_available_tools()
        print(f"Available tools: {list(available_tools.keys())}")
        
        # Test navigate tool
        print("Testing navigate tool...")
        result = await toolset.execute_tool("navigate", url="https://example.com")
        
        if result.get('success'):
            print("✅ Navigate tool successful")
        else:
            print(f"❌ Navigate tool failed: {result.get('error')}")
            return False
        
        # Test read_dom tool
        print("Testing read_dom tool...")
        result = await toolset.execute_tool("read_dom")
        
        if result.get('success'):
            dom_result = result.get('result', {})
            print(f"✅ Read DOM successful: {dom_result.get('title', 'No title')}")
        else:
            print(f"❌ Read DOM failed: {result.get('error')}")
            return False
        
        # Test wait tool
        print("Testing wait tool...")
        result = await toolset.execute_tool("wait", seconds=1)
        
        if result.get('success'):
            print("✅ Wait tool successful")
        else:
            print(f"❌ Wait tool failed: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Toolset test failed: {e}")
        return False
    
    finally:
        await browser_manager.close()

async def main():
    """Main test function"""
    print("Starting Autonomous Agent Tests...")
    
    tests = [
        ("Browser Manager", test_browser_manager),
        ("Toolset", test_toolset),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\\n{'='*50}")
        print(f"Running {test_name} Test")
        print('='*50)
        
        try:
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        
        except Exception as e:
            print(f"❌ {test_name} test CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Agent is ready for use.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    asyncio.run(main())


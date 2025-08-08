"""
Agent Orchestrator - Main loop untuk perencanaan-eksekusi-observasi
"""
import asyncio
import time
import uuid
from typing import Dict, Any, List, Optional
from agent.models import AgentRequest, AgentResponse, AgentStep, ToolCall, BrowserState
from agent.llm_interface import create_llm_interface, LLMInterface
from agent.browser_manager import BrowserManager
from agent.toolset import Toolset

class AgentOrchestrator:
    """Main orchestrator untuk autonomous agent"""
    
    def __init__(self, llm_provider: str = "openai", browser_type: str = "chromium", headless: bool = True):
        self.llm_provider = llm_provider
        self.browser_type = browser_type
        self.headless = headless
        
        # Components
        self.llm: Optional[LLMInterface] = None
        self.browser_manager: Optional[BrowserManager] = None
        self.toolset: Optional[Toolset] = None
        
        # State
        self.current_task: Optional[AgentRequest] = None
        self.current_response: Optional[AgentResponse] = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize semua components"""
        try:
            # Initialize LLM
            self.llm = create_llm_interface(self.llm_provider)
            
            # Initialize browser
            self.browser_manager = BrowserManager(
                headless=self.headless,
                browser_type=self.browser_type
            )
            await self.browser_manager.initialize()
            
            # Initialize toolset
            self.toolset = Toolset(
                browser=self.browser_manager.browser,
                page=self.browser_manager.page
            )
            
            print("Agent orchestrator initialized successfully")
            return True
        except Exception as e:
            print(f"Failed to initialize agent orchestrator: {e}")
            return False
    
    async def execute_task(self, request: AgentRequest) -> AgentResponse:
        """Execute agent task dengan planning-execution-observation loop"""
        task_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Initialize response
        response = AgentResponse(
            task_id=task_id,
            goal=request.goal,
            status="running",
            steps=[]
        )
        
        self.current_task = request
        self.current_response = response
        self.is_running = True
        
        try:
            # Main agent loop
            for step_number in range(1, request.max_iterations + 1):
                if not self.is_running:
                    response.status = "stopped"
                    break
                
                print(f"\\n=== Step {step_number} ===")
                
                # 1. OBSERVATION - Get current state
                observation = await self._get_current_observation()
                print(f"Observation: {observation[:200]}...")
                
                # 2. PLANNING - LLM decides next action
                planning_result = await self._plan_next_action(
                    goal=request.goal,
                    current_state=observation,
                    history=[step.planning for step in response.steps]
                )
                print(f"Planning: {planning_result.get('reasoning', 'No reasoning provided')}")
                
                # 3. EXECUTION - Execute planned action
                tool_call = ToolCall(
                    tool_name=planning_result.get('tool_name', 'wait'),
                    parameters=planning_result.get('parameters', {})
                )
                
                execution_result = await self._execute_tool_call(tool_call)
                tool_call.result = execution_result.get('result')
                tool_call.error = execution_result.get('error')
                
                print(f"Execution: {tool_call.tool_name} -> {'Success' if execution_result.get('success') else 'Failed'}")
                
                # 4. Create step record
                step = AgentStep(
                    step_number=step_number,
                    planning=planning_result.get('reasoning', ''),
                    tool_call=tool_call,
                    observation=observation,
                    success=execution_result.get('success', False)
                )
                
                response.steps.append(step)
                
                # 5. Check if goal achieved atau error
                if await self._is_goal_achieved(request.goal, observation):
                    response.status = "completed"
                    response.final_result = "Goal achieved successfully"
                    break
                
                if not step.success:
                    # Try to recover atau continue
                    print(f"Step failed: {tool_call.error}")
                    if step_number >= 3:  # Stop after 3 consecutive failures
                        response.status = "failed"
                        response.error = f"Multiple failures: {tool_call.error}"
                        break
                
                # Small delay between steps
                await asyncio.sleep(1)
            
            # If loop completed without achieving goal
            if response.status == "running":
                response.status = "completed"
                response.final_result = f"Completed {len(response.steps)} steps"
            
        except Exception as e:
            response.status = "failed"
            response.error = str(e)
            print(f"Task execution failed: {e}")
        
        finally:
            response.execution_time = time.time() - start_time
            self.is_running = False
            self.current_task = None
            self.current_response = None
        
        return response
    
    async def _get_current_observation(self) -> str:
        """Get current state observation"""
        try:
            if not self.browser_manager or not self.browser_manager.page:
                return "Browser not initialized"
            
            # Get page content summary
            dom_result = await self.toolset.execute_tool("read_dom")
            
            if dom_result.get('success'):
                result = dom_result['result']
                observation = f"""
Current URL: {result.get('url', 'Unknown')}
Page Title: {result.get('title', 'Unknown')}
Page Content Preview: {result.get('text_preview', 'No content')}

Interactive Elements:
"""
                for element in result.get('interactive_elements', [])[:5]:  # Limit to 5 elements
                    observation += f"- {element.get('type', 'unknown')}: {element.get('text', element.get('placeholder', 'N/A'))}\\n"
                
                return observation.strip()
            else:
                return f"Failed to read DOM: {dom_result.get('error', 'Unknown error')}"
        
        except Exception as e:
            return f"Error getting observation: {str(e)}"
    
    async def _plan_next_action(self, goal: str, current_state: str, history: List[str]) -> Dict[str, Any]:
        """Plan next action menggunakan LLM"""
        try:
            if not self.llm:
                raise Exception("LLM not initialized")
            
            return await self.llm.plan_next_action(goal, current_state, history)
        
        except Exception as e:
            print(f"Planning failed: {e}")
            # Fallback action
            return {
                "reasoning": f"Planning failed: {str(e)}. Waiting.",
                "tool_name": "wait",
                "parameters": {"seconds": 2},
                "expected_outcome": "Wait and retry"
            }
    
    async def _execute_tool_call(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Execute tool call"""
        try:
            if not self.toolset:
                raise Exception("Toolset not initialized")
            
            return await self.toolset.execute_tool(
                tool_call.tool_name,
                **tool_call.parameters
            )
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _is_goal_achieved(self, goal: str, current_observation: str) -> bool:
        """Check if goal is achieved menggunakan LLM"""
        try:
            if not self.llm:
                return False
            
            prompt = f"""
Goal: {goal}

Current State:
{current_observation}

Has the goal been achieved? Respond with only "YES" or "NO".
"""
            
            response = await self.llm.generate_response(prompt)
            return "YES" in response.upper()
        
        except Exception as e:
            print(f"Goal check failed: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "is_running": self.is_running,
            "current_task": self.current_task.goal if self.current_task else None,
            "current_step": len(self.current_response.steps) if self.current_response else 0,
            "browser_initialized": self.browser_manager is not None,
            "llm_initialized": self.llm is not None
        }
    
    async def stop_current_task(self) -> Dict[str, Any]:
        """Stop current running task"""
        if self.is_running:
            self.is_running = False
            return {"message": "Task stopped successfully"}
        else:
            return {"message": "No task is currently running"}
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.browser_manager:
                await self.browser_manager.close()
            print("Agent orchestrator cleaned up successfully")
        except Exception as e:
            print(f"Cleanup error: {e}")


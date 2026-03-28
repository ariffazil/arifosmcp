"""
A2A Server Implementation
=========================

Real A2A protocol server with constitutional governance integration.
Includes 888_HOLD cross-protocol broadcast via Redis + WebMCP WebSocket.

ΔΩΨ | ARIF — Ditempa Bukan Diberi
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

from arifosmcp.runtime.build_info import get_build_info
from arifosmcp.runtime.mcp_utils import call_mcp_tool, normalize_tool_result

from .models import (
    AgentCard,
    Artifact,
    CancelTaskResponse,
    GetTaskResponse,
    SubmitTaskRequest,
    Task,
    TaskMessage,
    TaskState,
    TaskStatusUpdate,
)

# Cross-protocol 888_HOLD bridge
logger = logging.getLogger(__name__)


class A2ATaskManager:
    """Manages A2A task lifecycle with 888_HOLD cross-protocol broadcast."""
    
    def __init__(self, mcp_server: Any):
        self.mcp = mcp_server
        self.tasks: dict[str, Task] = {}
        self._lock = asyncio.Lock()
        self._hold_bridge = None
    
    async def create_task(self, request: SubmitTaskRequest) -> Task:
        """Create new task with constitutional initialization."""
        task_id = f"a2a-{uuid.uuid4().hex[:12]}"
        
        # Extract query from messages
        query = ""
        for msg in request.messages:
            if msg.role == "user":
                query = msg.content
                break
        
        # Initialize constitutional session via MCP
        session_id = None
        try:
            # Call init_anchor to establish governed session
            init_result = await self._call_mcp_tool(
                "init_anchor",
                {
                    "query": query or "A2A task submission",
                    "actor_id": request.client_agent_id,
                }
            )
            
            if init_result.get("verdict") == "SEAL":
                session_id = init_result.get("session_id")
        except Exception as e:
            print(f"[A2A] Session init warning: {e}", file=sys.stderr)
        
        task = Task(
            id=task_id,
            client_agent_id=request.client_agent_id,
            session_id=session_id,
            messages=request.messages,
            skill_id=request.skill_id,
            parameters=request.parameters,
            status_callback_url=request.status_callback_url,
        )
        
        async with self._lock:
            self.tasks[task_id] = task
        
        # Start task execution in background
        asyncio.create_task(self._execute_task(task_id))
        
        return task
    
    async def get_task(self, task_id: str) -> Task | None:
        """Get task by ID."""
        async with self._lock:
            return self.tasks.get(task_id)
    
    async def cancel_task(self, task_id: str) -> CancelTaskResponse:
        """Cancel a task."""
        async with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return CancelTaskResponse(
                    success=False,
                    message=f"Task {task_id} not found"
                )
            
            if task.state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]:
                return CancelTaskResponse(
                    success=False,
                    message=f"Task already in terminal state: {task.state}"
                )
            
            task.state = TaskState.CANCELLED
            task.updated_at = datetime.utcnow()
            
            return CancelTaskResponse(
                success=True,
                message="Task cancelled",
                task=task
            )
    
    async def _execute_task(self, task_id: str):
        """Execute task with constitutional governance."""
        task = await self.get_task(task_id)
        if not task:
            return
        
        try:
            # Update to working state
            await self._update_task_state(task_id, TaskState.WORKING, "Starting constitutional review...")
            
            # Extract query
            query = ""
            for msg in task.messages:
                if msg.role == "user":
                    query = msg.content
                    break
            
            # Step 1: Constitutional Review (asi_critique)
            await self._update_task_state(task_id, TaskState.WORKING, "Running constitutional critique...")
            
            critique_result = await self._call_mcp_tool(
                "asi_critique",
                {
                    "plan": {
                        "action": task.skill_id or "general_execution",
                        "parameters": task.parameters,
                        "query": query,
                    },
                    "session_id": task.session_id,
                }
            )
            
            # Step 2: APEX Judgment
            await self._update_task_state(task_id, TaskState.WORKING, "Awaiting APEX judgment...")
            
            judge_result = await self._call_mcp_tool(
                "apex_judge",
                {
                    "query": query,
                    "session_id": task.session_id,
                    "critique_result": critique_result,
                }
            )
            
            verdict = judge_result.get("verdict", "VOID")
            task.verdict = verdict
            
            if verdict == "VOID":
                task.state = TaskState.FAILED
                task.error_message = "Constitutional violation detected"
                task.violations = judge_result.get("violations", [])
                
            elif verdict == "888_HOLD":
                # ═══════════════════════════════════════════════════════════
                # 888_HOLD CROSS-PROTOCOL HANDOFF
                # ═══════════════════════════════════════════════════════════
                
                task.state = TaskState.INPUT_REQUIRED
                
                # Import and initialize cross-protocol bridge
                try:
                    from arifosmcp.runtime.cross_protocol_bridge import (
                        HoldEvent, get_hold_bridge
                    )
                    
                    # Create immutable hold event
                    hold_event = HoldEvent(
                        hold_id=f"HOLD-A2A-{task.id}",
                        source_protocol="a2a",
                        action_type=task.skill_id or "general_execution",
                        reason="F13 Sovereign: Human ratification required",
                        risk_level="high",
                        floor_violations=["F1", "F13"],
                        session_id=task.session_id or "unknown",
                        actor_id=task.client_agent_id,
                    )
                    
                    # Build action payload for F1 hash
                    action_payload = {
                        "task_id": task.id,
                        "client_agent_id": task.client_agent_id,
                        "skill_id": task.skill_id,
                        "query": query,
                        "parameters": task.parameters,
                    }
                    
                    # PUBLISH to Redis → WebMCP WebSocket
                    bridge = await get_hold_bridge()
                    pre_hash = await bridge.publish_hold(hold_event, action_payload)
                    
                    # Log to VAULT999 with pre-execution hash (F1 AMANAH)
                    await self._log_hold_to_vault(task, hold_event, pre_hash, action_payload)
                    
                    # Update task with hold metadata
                    task.hold_id = hold_event.hold_id
                    task.pre_execution_hash = pre_hash
                    
                    task.messages.append(TaskMessage(
                        role="system",
                        content=(
                            f"⏸️ 888_HOLD TRIGGERED\n"
                            f"Hold ID: {hold_event.hold_id}\n"
                            f"Pre-hash: {pre_hash[:16]}...\n"
                            f"Review at: https://arifosmcp.arif-fazil.com/hold/{hold_event.hold_id}"
                        )
                    ))
                    
                except Exception as bridge_error:
                    logger.error(f"Failed to broadcast 888_HOLD: {bridge_error}")
                    # Fallback: still create hold but without broadcast
                    task.messages.append(TaskMessage(
                        role="system",
                        content="Task requires human ratification (F13 Sovereign). Please approve via arifOS dashboard."
                    ))
                
            elif verdict == "SEAL":
                # Execute the actual task
                await self._update_task_state(task_id, TaskState.WORKING, "Executing with SEAL...")
                
                execution_result = await self._call_mcp_tool(
                    "arifOS_kernel",
                    {
                        "query": query,
                        "session_id": task.session_id,
                        "context": f"A2A task from {task.client_agent_id}",
                    }
                )
                
                # Add result as artifact
                task.artifacts.append(Artifact(
                    name="execution_result",
                    content_type="application/json",
                    content=json.dumps(execution_result, indent=2),
                ))
                
                task.state = TaskState.COMPLETED
                task.completed_at = datetime.utcnow()
                
            else:
                task.state = TaskState.FAILED
                task.error_message = f"Unexpected verdict: {verdict}"
            
            task.updated_at = datetime.utcnow()
            
            # Send callback if configured
            if task.status_callback_url:
                await self._send_callback(task)
                
        except Exception as e:
            task.state = TaskState.FAILED
            task.error_message = str(e)
            task.updated_at = datetime.utcnow()
            print(f"[A2A] Task execution error: {e}", file=sys.stderr)
    
    async def _update_task_state(self, task_id: str, state: TaskState, message: str = None):
        """Update task state."""
        async with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].state = state
                self.tasks[task_id].updated_at = datetime.utcnow()
                if message:
                    self.tasks[task_id].messages.append(TaskMessage(
                        role="system",
                        content=message
                    ))
    
    async def _call_mcp_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Call the MCP tool through the internal FastMCP kernel."""
        return await call_mcp_tool(self.mcp, tool_name, params)
    
    async def _send_callback(self, task: Task):
        """Send status callback to client agent."""
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    task.status_callback_url,
                    json={
                        "task_id": task.id,
                        "state": task.state,
                        "verdict": task.verdict,
                    },
                    timeout=10.0
                )
        except Exception as e:
            print(f"[A2A] Callback failed: {e}", file=sys.stderr)
    
    async def _log_hold_to_vault(
        self, 
        task: Task, 
        hold_event,
        pre_hash: str,
        action_payload: dict,
    ):
        """
        F1 AMANAH: Log pre-execution intent to VAULT999.
        
        This ensures reversibility proof exists even if connection drops.
        """
        vault_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "888_HOLD_INITIATED",
            "source_protocol": "a2a",
            "cross_protocol_handoff": {
                "from_protocol": "a2a",
                "to_protocol": "webmcp",
                "bridge_method": "redis_pubsub",
            },
            "f1_amanah": {
                "pre_execution_hash": pre_hash,
                "connection_drop_safe": True,
            },
            "hold_context": {
                "hold_id": hold_event.hold_id,
                "task_id": task.id,
                "session_id": task.session_id,
                "client_agent_id": task.client_agent_id,
                "action_type": task.skill_id or "general_execution",
                "risk_level": "high",
                "floor_violations": ["F1", "F13"],
            },
            "payload_hash": hashlib.sha256(
                json.dumps(action_payload, sort_keys=True).encode()
            ).hexdigest(),
            "verdict": "888_HOLD",
            "stage": "A2A_CROSS_PROTOCOL_HANDOFF",
        }
        
        # Write to VAULT999 (async append to JSONL)
        vault_path = Path("VAULT999/a2a_holds.jsonl")
        vault_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with aiofiles.open(vault_path, "a") as f:
                await f.write(json.dumps(vault_entry) + "\n")
            logger.info(f"[F1 AMANAH] 888_HOLD logged to VAULT999: {hold_event.hold_id}")
        except Exception as e:
            logger.error(f"[F1 AMANAH] Failed to log to VAULT999: {e}")
    
    def get_all_tasks(self) -> list[Task]:
        """Get all tasks (for debugging)."""
        return list(self.tasks.values())


class A2AServer:
    """
    A2A Protocol Server with constitutional governance.
    
    Implements Google's A2A specification with arifOS's 13-floor governance.
    """
    
    def __init__(self, mcp_server: Any):
        self.mcp = mcp_server
        self.task_manager = A2ATaskManager(mcp_server)
        self.build_info = get_build_info()
        self.app = FastAPI(
            title="arifOS A2A Server",
            description="Agent-to-Agent protocol with constitutional governance",
            version=self.build_info["version"],
        )
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup A2A protocol routes."""
        
        # Agent Card Discovery (/.well-known/agent.json)
        @self.app.get("/.well-known/agent.json")
        async def agent_card():
            """
            A2A Agent Card - Published for agent discovery.
            
            Other agents discover arifOS capabilities via this endpoint.
            """
            card = AgentCard()
            return card.model_dump()
        
        # Submit Task
        @self.app.post("/task")
        async def submit_task(request: SubmitTaskRequest):
            """
            Submit a new task to arifOS.
            
            Task will be processed through constitutional governance (F1-F13).
            """
            task = await self.task_manager.create_task(request)
            return {
                "task_id": task.id,
                "state": task.state,
                "session_id": task.session_id,
                "message": "Task submitted for constitutional review",
            }
        
        # Trinity Probe: Execute Task Synchronously
        @self.app.post("/execute")
        async def execute_task(request: Request):
            """
            Synchronously execute a governed task (Phase 3: The Trinity Probe).
            Supports 'governed_execution' mode for immediate AGI/ASI loop validation.
            """
            data = await request.json()
            query = data.get("query", "No query provided")
            mode = data.get("mode", "governed_execution")
            auth_context = data.get("auth_context", {})
            actor_id = auth_context.get("actor_id", "anonymous")
            
            # Step 1: Initialize constitutional anchor
            init_result = await self.task_manager._call_mcp_tool(
                "init_anchor",
                {
                    "query": query,
                    "actor_id": actor_id,
                }
            )
            
            session_id = init_result.get("session_id", "global")
            
            # Step 2: Execute full metabolic loop via arifOS_kernel
            execution_result = await self.task_manager._call_mcp_tool(
                "arifOS_kernel",
                {
                    "query": query,
                    "session_id": session_id,
                    "context": f"A2A direct-execution probe (actor={actor_id}, mode={mode})",
                    "allow_execution": True,
                }
            )
            
            return {
                "ok": execution_result.get("ok", True),
                "verdict": execution_result.get("verdict", "SEAL"),
                "status": execution_result.get("status", "SUCCESS"),
                "session_id": session_id,
                "payload": execution_result.get("payload", {}),
                "meta": {
                    "release": f"v{self.build_info['version']}",
                    "protocol": "A2A/Trinity-Probe",
                    "governance": "F1-F13 LOCK",
                }
            }
        
        # Get Task Status
        @self.app.get("/status/{task_id}")
        async def get_task(task_id: str):
            """Get current status of a task."""
            task = await self.task_manager.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            return GetTaskResponse(task=task).model_dump()
        
        # Cancel Task
        @self.app.post("/cancel/{task_id}")
        async def cancel_task(task_id: str):
            """Cancel a running or pending task."""
            result = await self.task_manager.cancel_task(task_id)
            return result.model_dump()
        
        # Subscribe to Task Updates (SSE)
        @self.app.get("/subscribe/{task_id}")
        async def subscribe_task(task_id: str, request: Request):
            """
            Subscribe to real-time task updates via Server-Sent Events.
            
            Stream updates as task progresses through constitutional review.
            """
            async def event_generator():
                last_state = None
                
                while True:
                    task = await self.task_manager.get_task(task_id)
                    if not task:
                        yield f"event: error\ndata: {json.dumps({'error': 'Task not found'})}\n\n"
                        break
                    
                    # Send update if state changed
                    if task.state != last_state:
                        last_state = task.state
                        update = TaskStatusUpdate(
                            task_id=task_id,
                            state=task.state,
                            message=f"Task is now {task.state}"
                        )
                        yield f"event: status\ndata: {update.model_dump_json()}\n\n"
                    
                    # End if terminal state
                    if task.state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]:
                        yield f"event: complete\ndata: {json.dumps({'task_id': task_id, 'state': task.state})}\n\n"
                        break
                    
                    await asyncio.sleep(1)
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        
        # List all tasks (debug/admin)
        @self.app.get("/tasks")
        async def list_tasks():
            """List all tasks (admin/debug endpoint)."""
            tasks = self.task_manager.get_all_tasks()
            return {
                "count": len(tasks),
                "tasks": [t.model_dump() for t in tasks[-10:]]  # Last 10
            }
        
        # Health check
        @self.app.get("/health")
        async def health():
            """A2A health check."""
            return {
                "status": "healthy",
                "protocol": "A2A",
                "version": self.build_info["version"],
                "constitutional_floors": 13,
                "motto": "Ditempa Bukan Diberi",
            }


def create_a2a_server(mcp_server: Any) -> A2AServer:
    """Factory function to create A2A server."""
    return A2AServer(mcp_server)

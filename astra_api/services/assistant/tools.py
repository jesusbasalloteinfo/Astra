"""
ASTRA - Automated Smart Telescope Remote Assistant
Copyright (C) 2026 Jesus Basallote

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
Infrastructure for defining and executing assistant tools in astra_api.
"""
import inspect
import json
import asyncio
from typing import Callable, Any, Dict, Type
from pydantic import BaseModel, Field, ValidationError
from functools import partial
from .models import BaseToolResponse

class CurriedTool:
    """
    Represents an AI assistant tool with metadata and execution logic.

    Supports partial application of arguments, automatic schema generation for LLMs,
    and safe execution of both synchronous and asynchronous functions.

    Attributes:
        name (str): The name of the tool as seen by the LLM.
        description (str): A description of what the tool does.
        args_model (Type[BaseModel]): Pydantic model for argument validation.
        func (Callable): The function to execute.
        frontend_action (bool): Whether this tool triggers a specific action in the UI.
        frontend_only (bool): If True, the tool is a stub that only triggers UI actions.
    """
    def __init__(self, name: str, description: str, args_model: Type[BaseModel], func: Callable = None, frontend_action: bool = False, frontend_only: bool = False):
        """
        Initializes the CurriedTool.

        Args:
            name (str): Tool name.
            description (str): Tool description.
            args_model (Type[BaseModel]): Pydantic model class for arguments.
            func (Callable, optional): The implementation function.
            frontend_action (bool): UI trigger flag.
            frontend_only (bool): Stub tool flag.
        """
        self.name = name
        self.description = description
        self.args_model = args_model
        self.func = func
        self.frontend_action = frontend_action
        self.frontend_only = frontend_only

    def get_openai_tool_schema(self) -> Dict[str, Any]:
        """
        Generates the OpenAI-compatible tool schema.

        Returns:
            Dict[str, Any]: The tool definition schema.
        """
        schema = self.args_model.model_json_schema()
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": schema,
            }
        }

    async def execute(self, arguments_json: str) -> BaseToolResponse:
        """
        Validates arguments and executes the tool function asynchronously.

        Handles argument validation via Pydantic and ensures thread-safe execution
        of synchronous functions using asyncio.to_thread.

        Args:
            arguments_json (str): The raw JSON string of arguments from the LLM.

        Returns:
            BaseToolResponse: The result of the tool execution.
        """
        try:
            validated_args = self.args_model.model_validate_json(arguments_json or "{}")
        except ValidationError as e:
            return BaseToolResponse(status="error", message="Validation Error", data=e.errors())
        except Exception as e:
            return BaseToolResponse(status="error", message=f"Invalid arguments format: {str(e)}")
        
        if self.frontend_only:
            return BaseToolResponse(
                status="success",
                message="Action dispatched to UI",
                frontend_action=True
            )
        
        try:
            # Check if the target function is async
            target_func = self.func.func if isinstance(self.func, partial) else self.func
            
            if inspect.iscoroutinefunction(target_func):
                # Execute as a native async
                raw_result = await self.func(**validated_args.model_dump())
            else:
                # For synchronous functions, run them in a separate thread to prevent
                # blocking the main async event loop.
                raw_result = await asyncio.to_thread(self.func, **validated_args.model_dump())
                
            if isinstance(raw_result, BaseToolResponse):
                # Do not wrap the response if is already a tool response
                return raw_result
            return BaseToolResponse(status="success", data=raw_result, frontend_action=self.frontend_action)
        except Exception as e:
            return BaseToolResponse(status="error", message=f"Tool execution failed: {str(e)}")


class EmptyArgs(BaseModel):
    """Placeholder for tools that require no arguments."""
    pass

import inspect
import json
import asyncio
from typing import Callable, Any, Dict, Type
from pydantic import BaseModel, Field, ValidationError
from functools import partial
from .models import BaseToolResponse

class CurriedTool:
    """
    A class that represents an assistant tool with or without partial arguments
    """
    def __init__(self, name: str, description: str, args_model: Type[BaseModel], func: Callable = None, frontend_action: bool = False, frontend_only: bool = False):
        self.name = name
        self.description = description
        self.args_model = args_model
        self.func = func
        self.frontend_action = frontend_action
        self.frontend_only = frontend_only

    def get_openai_tool_schema(self) -> Dict[str, Any]:
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
        """ Execute a toolcall with the arguments with async response """
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
    pass

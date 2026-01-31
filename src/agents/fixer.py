import os
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.utils.logger import log_experiment, ActionType
from src.tools.files import write_file
from src.agents.base import BaseAgent
from src.config import DEFAULT_MODEL_NAME

class FixerAgent(BaseAgent):
    """
    Expert AI agent responsible for autonomous code refactoring and bug fixing.
    Uses LLM-based reasoning to apply specific implementation plans to existing source code.
    """
    
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        super().__init__(model_name)
        self.agent_name = "Fixer_Agent"
        
    def _sanitize_output(self, raw_code: str) -> str:
        """
        Removes markdown code blocks and extraneous whitespace from the LLM response.
        Attempts to extract JSON object if present.
        """
        import re
        
        # 1. Try to find a specific JSON code block
        json_block_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_code, re.DOTALL)
        if json_block_match:
            return json_block_match.group(1)

        # 2. Try to find any code block that looks like JSON
        code_block_match = re.search(r'```(?:\w+)?\s*(\{.*?\})\s*```', raw_code, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1)
            
        # 3. Fallback: Identify the outer-most JSON-like structure in the raw text
        # This regex matches the first opening brace and the last closing brace
        # It's a heuristic but works well if the model includes text before/after
        match = re.search(r'\{.*\}', raw_code, re.DOTALL)
        if match:
            return match.group(0)

        # 4. Final fallback: just strip standard markdown codes if mostly code
        code = raw_code.strip()
        if code.startswith("```"):
            # Find the end of the first line (language identifier)
            first_newline = code.find('\n')
            if first_newline != -1:
                code = code[first_newline+1:]
        
        if code.endswith("```"):
            code = code[:-3]
        
        return code.strip()
    
    def fix(self, file_path: str, code_content: str, plan: str, error_context: Optional[str] = None) -> str:
        """
        Analyzes code and applies the refactoring plan using structured prompt engineering.
        """
        import json
        
        system_prompt = (
            "You are a Senior Python Expert Developer (The Fixer).\n"
            "Your mission is to rewrite the provided Python code based on a specific plan.\n\n"
            "CRITICAL RULES:\n"
            "1. You MUST output a valid JSON object where keys are filenames and values are the file content.\n"
            "   Example: {{ 'filename.py': '...code...', 'test_filename.py': '...test code...' }}\n"
            "2. Never include markdown backticks (```) or conversational text outside the JSON structure.\n"
            "3. If the code contains invalid syntax, fix it.\n"
            "4. Ensure the code is production-ready and maintains existing functionality unless the plan states otherwise.\n"
            "5. Follow the provided plan exactly. If the plan asks for tests, create a separate test file.\n"
            
        )

        # Escaping curly braces to prevent LangChain parsing issues
        escaped_code = code_content.replace("{", "{{").replace("}", "}}")
        escaped_plan = plan.replace("{", "{{").replace("}", "}}")

        user_message = (
            f"TARGET FILE: {os.path.basename(file_path)}\n\n"
            f"### ORIGINAL SOURCE CODE ###\n{escaped_code}\n\n"
            f"### REFACTORING PLAN ###\n{escaped_plan}"
        )

        if error_context:
            escaped_error = error_context.replace("{", "{{").replace("}", "}}")
            user_message += f"\n\n### PREVIOUS ERRORS TO RESOLVE ###\n{escaped_error}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_message)
        ])

        # Execution via LangChain
        chain = prompt | self.llm
        response = self.invoke_with_delay(chain, {})
        
        # Clean and validate the output
        cleaned_response = self._sanitize_output(response.content)
        
        try:
            files_to_write = json.loads(cleaned_response)
        except json.JSONDecodeError:
            # Fallback for legacy single-file output or malformed JSON
            print("⚠️ Warning: LLM did not return valid JSON. Assuming single file output.")
            files_to_write = {os.path.basename(file_path): cleaned_response}
        
        final_main_code = ""
        
        # Persistence: Write the improved code to the disk
        for filename, content in files_to_write.items():
            # Security check: Ensure filename contains no path traversal
            if ".." in filename or "/" in filename or "\\" in filename:
                print(f"❌ Security Warning: Skipping file with invalid name: {filename}")
                continue
                
            full_path = os.path.join(os.path.dirname(file_path), filename)
            write_file(full_path, content)
            
            if filename == os.path.basename(file_path):
                final_main_code = content

        # Mandatory Experiment Logging
        log_experiment(
            agent_name=self.agent_name,
            model_used=self.model_name,
            action=ActionType.FIX,
            details={
                "file_fixed": os.path.basename(file_path),
                "files_created": list(files_to_write.keys()),
                "plan_length": len(plan),
                "success_status": "applied_to_filesystem",
                "input_prompt": system_prompt + "\n\n" + user_message, # FIXED: Added mandatory field
                "output_response": cleaned_response # FIXED: Added mandatory field
            },
            status="SUCCESS"
        )
        
        # Return the content of the main file to keep state consistent
        return final_main_code if final_main_code else code_content
import google.generativeai as genai
from typing import Optional, List, Dict, Any
from loguru import logger
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from core.config import settings


class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-2.0-flash"
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            logger.warning("Gemini API key not configured")
            self.model = None
    
    async def chat_with_document(
        self,
        document_text: str,
        question: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Chat with a document using Gemini API
        """
        if not self.model:
            raise ValueError("Gemini API not configured")
        
        try:
            # Create system prompt for document chat
            system_prompt = f"""
            You are an AI assistant helping students understand and learn from documents. 
            You have access to the following document content:
            
            {document_text[:8000]}...
            
            Please answer questions about this document accurately and helpfully.
            If the question cannot be answered from the document content, politely say so.
            Provide clear, educational responses that help the student learn.
            """
            
            # Build conversation context
            conversation_parts = [system_prompt]
            
            # Add chat history if provided
            if chat_history:
                for msg in chat_history[-10:]:  # Keep last 10 messages for context
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        conversation_parts.append(f"Student: {content}")
                    else:
                        conversation_parts.append(f"Assistant: {content}")
            
            # Add current question
            conversation_parts.append(f"Student: {question}")
            
            full_prompt = "\n\n".join(conversation_parts)
            
            # Generate response using thread executor for async compatibility
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                self._generate_response,
                full_prompt
            )
            
            return {
                "response": response.text,
                "success": True,
                "model_used": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Error in document chat: {str(e)}")
            return {
                "response": "I'm sorry, I encountered an error while processing your question. Please try again.",
                "success": False,
                "error": str(e)
            }
    
    def _generate_response(self, prompt: str):
        """Synchronous wrapper for model generation"""
        return self.model.generate_content(prompt)
    
    async def extract_document_summary(self, document_text: str) -> Dict[str, Any]:
        """
        Extract a summary of the document using Gemini
        """
        if not self.model:
            raise ValueError("Gemini API not configured")
        
        try:
            prompt = f"""
            Please provide a concise summary of the following document. 
            Include the main topics, key points, and any important concepts:
            
            {document_text[:10000]}
            
            Summary:
            """
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                self._generate_response,
                prompt
            )
            
            return {
                "summary": response.text,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {
                "summary": "Unable to generate summary",
                "success": False,
                "error": str(e)
            }
    
    async def suggest_study_questions(self, document_text: str) -> Dict[str, Any]:
        """
        Generate study questions based on document content
        """
        if not self.model:
            raise ValueError("Gemini API not configured")
        
        try:
            prompt = f"""
            Based on the following document content, generate 5-7 thoughtful study questions 
            that would help a student understand and remember the key concepts.
            
            Document content:
            {document_text[:8000]}
            
            Please format as a numbered list of questions:
            """
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                self._generate_response,
                prompt
            )
            
            return {
                "questions": response.text,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating study questions: {str(e)}")
            return {
                "questions": "Unable to generate study questions",
                "success": False,
                "error": str(e)
            }
    
    async def generate_mind_map(self, document_text: str) -> Dict[str, Any]:
        """
        Generate a mind map structure based on document content
        """
        if not self.model:
            raise ValueError("Gemini API not configured")
        
        try:
            prompt = f"""
            Based on the following document content, create a hierarchical mind map structure.
            
            Document content:
            {document_text[:10000]}
            
            Please return the mind map as a JSON structure with the following format:
            {{
                "title": "Main Topic/Document Title",
                "children": [
                    {{
                        "name": "Main Topic 1",
                        "children": [
                            {{
                                "name": "Subtopic 1.1",
                                "children": [
                                    {{"name": "Detail 1.1.1"}},
                                    {{"name": "Detail 1.1.2"}}
                                ]
                            }},
                            {{
                                "name": "Subtopic 1.2",
                                "children": [
                                    {{"name": "Detail 1.2.1"}}
                                ]
                            }}
                        ]
                    }},
                    {{
                        "name": "Main Topic 2",
                        "children": [
                            {{"name": "Subtopic 2.1"}},
                            {{"name": "Subtopic 2.2"}}
                        ]
                    }}
                ]
            }}
            
            Make sure to:
            1. Identify the main themes and topics from the document
            2. Create logical hierarchical relationships
            3. Include key concepts, facts, and details
            4. Keep node names concise but descriptive
            5. Create 3-5 levels of hierarchy where appropriate
            6. Return ONLY the JSON structure, no additional text
            """
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                self._generate_response,
                prompt
            )
            
            # Try to parse the JSON response
            import json
            import re
            
            # Clean the response text - remove markdown code blocks if present
            response_text = response.text.strip()
            
            # Remove markdown code blocks
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            elif response_text.startswith('```'):
                response_text = response_text[3:]   # Remove ```
            
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove closing ```
            
            response_text = response_text.strip()
            
            try:
                mind_map_data = json.loads(response_text)
                return {
                    "mind_map": mind_map_data,
                    "success": True
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, return a structured error
                logger.warning(f"Failed to parse mind map JSON: {response.text[:200]}")
                return {
                    "mind_map": {
                        "title": "Mind Map Generation Error",
                        "children": [
                            {
                                "name": "Unable to generate structured mind map",
                                "children": [
                                    {"name": "The AI response could not be parsed as JSON"},
                                    {"name": "Please try again or contact support"}
                                ]
                            }
                        ]
                    },
                    "success": False,
                    "error": "Failed to parse AI response as JSON"
                }
            
        except Exception as e:
            logger.error(f"Error generating mind map: {str(e)}")
            return {
                "mind_map": {
                    "title": "Error",
                    "children": [
                        {
                            "name": "Unable to generate mind map",
                            "children": [
                                {"name": "An error occurred during generation"}
                            ]
                        }
                    ]
                },
                "success": False,
                "error": str(e)
            }


# Global instance
gemini_service = GeminiService()
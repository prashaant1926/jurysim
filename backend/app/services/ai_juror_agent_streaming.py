"""
AI Juror Agent with DeepSeek streaming support
"""
from openai import OpenAI
from typing import List, Dict, Any, Optional, Callable, AsyncGenerator
import asyncio
import json
from datetime import datetime
from app.models.deliberation import (
    JurorPersona, JurorStatement, Vote, VerdictChoice, 
    DeliberationPhase, DeliberationCase
)
from app.services.ai_juror_agent import AIJurorAgent
import logging
from colorama import Fore, Back, Style, init

# Initialize colorama for colored terminal output
init()

logger = logging.getLogger(__name__)


class StreamingAIJurorAgent(AIJurorAgent):
    """Enhanced AI Juror Agent with streaming support"""
    
    async def generate_statement_streaming(
        self, 
        phase: DeliberationPhase,
        previous_statements: List[JurorStatement],
        prompt_addition: Optional[str] = None,
        on_token: Optional[Callable[[str], None]] = None
    ) -> JurorStatement:
        """Generate a statement with streaming tokens"""
        
        # Build conversation context
        messages = self._build_conversation_context(phase, previous_statements, prompt_addition)
        
        # Print to terminal
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🤖 DEEPSEEK API CALL - {self.persona.name} (Juror {self.persona.juror_id}){Style.RESET_ALL}")
        print(f"{Fore.CYAN}Phase: {phase.value}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        
        # Show prompt preview
        if prompt_addition:
            print(f"{Fore.GREEN}Prompt: {prompt_addition[:100]}...{Style.RESET_ALL}")
        
        try:
            # Create messages for DeepSeek
            deepseek_messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": messages[-1]["content"]}
            ]
            
            # Determine max tokens based on phase
            max_tokens = 150
            if phase == DeliberationPhase.OPENING:
                max_tokens = 200
            elif phase == DeliberationPhase.DISCUSSION:
                max_tokens = 80
            
            print(f"{Fore.MAGENTA}Requesting {max_tokens} tokens...{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Response: {Style.RESET_ALL}", end='', flush=True)
            
            # Create streaming response
            stream = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=deepseek_messages,
                max_tokens=max_tokens,
                temperature=0.8,
                stream=True
            )
            
            # Collect the full response while streaming
            full_content = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_content += token
                    
                    # Print to terminal with color
                    print(f"{Fore.WHITE}{token}{Style.RESET_ALL}", end='', flush=True)
                    
                    # Send to callback if provided
                    if on_token:
                        on_token(token)
                    
                    # Small delay to simulate natural typing
                    await asyncio.sleep(0.01)
            
            print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
            
            # Ensure proper sentence ending
            content = full_content.strip()
            if content and not content.rstrip().endswith(('.', '!', '?')):
                last_period = content.rfind('.')
                last_exclaim = content.rfind('!')
                last_question = content.rfind('?')
                last_complete = max(last_period, last_exclaim, last_question)
                
                if last_complete > 0:
                    content = content[:last_complete + 1]
                else:
                    content = content.rstrip() + "..."
            
            # Record in conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": content,
                "phase": phase.value,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Determine sentiment
            sentiment = self._determine_sentiment(content)
            
            statement = JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content=content,
                sentiment=sentiment
            )
            
            # Record in full transcript
            self.full_transcript.append({
                "type": "statement",
                "timestamp": datetime.utcnow().isoformat(),
                "juror_id": self.persona.juror_id,
                "juror_name": self.persona.name,
                "phase": phase.value,
                "content": content,
                "sentiment": sentiment,
                "previous_statements": [s.dict() for s in previous_statements[-3:]]
            })
            
            # Write to transcript file
            self._append_to_transcript(
                "STATEMENT",
                content,
                {"Phase": phase.value, "Sentiment": sentiment}
            )
            
            return statement
            
        except Exception as e:
            print(f"\n{Fore.RED}Error generating statement: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Error generating statement for {self.persona.name}: {str(e)}")
            
            # Return a fallback statement
            fallback = self._get_fallback_statement(phase)
            return JurorStatement(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                phase=phase,
                content=fallback,
                sentiment="neutral"
            )
    
    async def cast_vote_streaming(
        self, 
        round_number: int,
        previous_votes: Optional[List[Vote]] = None,
        recent_discussion: Optional[List[JurorStatement]] = None,
        on_token: Optional[Callable[[str], None]] = None
    ) -> Vote:
        """Cast a vote with streaming reasoning"""
        
        print(f"\n{Fore.YELLOW}🗳️  VOTE REQUEST - {self.persona.name}{Style.RESET_ALL}")
        
        # Build vote prompt (same as parent)
        vote_prompt = self._build_vote_prompt(round_number, previous_votes, recent_discussion)
        
        try:
            deepseek_messages = [
                {"role": "system", "content": self.system_prompt + "\n\nYou must respond with valid JSON only."},
                {"role": "user", "content": vote_prompt}
            ]
            
            print(f"{Fore.MAGENTA}Generating vote...{Style.RESET_ALL}")
            
            # For votes, we can't stream JSON easily, so use regular call
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=deepseek_messages,
                max_tokens=250,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            vote_data = json.loads(response.choices[0].message.content)
            
            # Display the vote
            print(f"{Fore.GREEN}Vote: {vote_data['verdict'].upper()}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Confidence: {vote_data['confidence']}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Reasoning: {vote_data['reasoning']}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
            
            vote = Vote(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                verdict=VerdictChoice(vote_data["verdict"]),
                confidence=float(vote_data["confidence"]),
                reasoning=vote_data["reasoning"],
                round_number=round_number
            )
            
            return vote
            
        except Exception as e:
            print(f"\n{Fore.RED}Error casting vote: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Error in vote for {self.persona.name}: {str(e)}")
            
            # Default vote
            return Vote(
                juror_id=self.persona.juror_id,
                juror_name=self.persona.name,
                verdict=VerdictChoice.UNDECIDED,
                confidence=0.5,
                reasoning="I need more time to consider the evidence.",
                round_number=round_number
            )
    
    def _build_vote_prompt(self, round_number, previous_votes, recent_discussion):
        """Build the voting prompt (extracted from parent class)"""
        # Similar to parent class cast_vote method
        discussion_context = ""
        if recent_discussion:
            discussion_context = "\n\nRecent discussion points:\n"
            for stmt in recent_discussion[-10:]:
                discussion_context += f"- {stmt.juror_name}: {stmt.content[:150]}...\n"
        
        vote_prompt = f"""Based on the deliberation so far, how would this person vote?

Consider:
1. Your initial assessment of the evidence
2. The points raised during discussion
3. Whether compelling new arguments were made
4. Your personality traits and decision-making approach

{discussion_context}

For round {round_number}, assess if the discussion has raised new doubts or strengthened your conviction.

Respond in this exact JSON format:
{{
  "verdict": "guilty" or "not_guilty" or "undecided",
  "confidence": 0.0 to 1.0,
  "reasoning": "2-3 sentence explanation"
}}"""
        
        return vote_prompt
import openai
import os
from dotenv import load_dotenv

## Load environment variables
load_dotenv()

class AuraHealthChatbot:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.conversation_history = []
    
    def get_response(self, user_message):
        ## Add system prompt for mental health context
        system_prompt = """You are Aura, a compassionate mental health support chatbot for students. 
        Your role is to:
        - Listen empathetically to students' concerns
        - Provide supportive and encouraging responses
        - Offer practical coping strategies
        - Encourage professional help when needed
        - Never provide medical diagnoses
        - Be warm, understanding, and non-judgmental
        
        Always prioritize the student's wellbeing and safety."""
        
        ## Prepare messages for API
        messages = [{"role": "system", "content": system_prompt}]
        
        ## Add conversation history
        for msg in self.conversation_history:
            messages.append(msg)
        
        ## Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            bot_response = response.choices[0].message.content
            
            ## Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            
            ## Keep only last 10 exchanges to manage token limits
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return bot_response
            
        except Exception as e:
            return f"I'm sorry, I'm having trouble responding right now. Error: {str(e)}"

## Create chatbot instance
aura_bot = AuraHealthChatbot()

def chat_with_aura(message):
    return aura_bot.get_response(message)

## Test function to verify everything works
def test_chatbot():
    """Test function to verify the chatbot is working"""
    try:
        test_message = "Hello, I'm feeling anxious about my studies."
        response = chat_with_aura(test_message)
        return f"✅ Chatbot test successful! Response: {response[:100]}..."
    except Exception as e:
        return f"❌ Chatbot test failed: {str(e)}"

## Initialize and test when script runs
if __name__ == "__main__":
    print("Initializing Aura Health Chatbot...")
    try:
        ## Test if the chatbot works
        result = test_chatbot()
        print(result)
    except Exception as e:
        print(f"Error during initialization: {e}")



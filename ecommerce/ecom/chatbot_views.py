from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
import uuid
from datetime import datetime
from .models import ChatSession, ChatMessage, ChatbotKnowledge, Customer
from django.db.models import Q
import re


class ChatbotService:
    """Service class to handle chatbot logic and responses"""
    
    def __init__(self):
        self.default_responses = {
            'greeting': [
                "Hello! Welcome to WorksTeamWear! I'm here to help you with any questions about our products, orders, or services. How can I assist you today?",
                "Hi there! I'm your WorksTeamWear assistant. I can help you with product information, ordering, account questions, and more. What would you like to know?"
            ],
            'goodbye': [
                "Thank you for chatting with WorksTeamWear! If you need any more help, feel free to ask. Have a great day!",
                "Goodbye! Don't hesitate to reach out if you have more questions. Happy shopping at WorksTeamWear!"
            ],
            'default': [
                "I'm here to help! Could you please provide more details about what you're looking for? I can assist with:\n• Product information and availability\n• Order status and tracking\n• Account management\n• Shipping and delivery\n• Payment methods\n• Product customization\n• Returns and refunds",
                "I'd be happy to help you with that! For the best assistance, could you tell me more about:\n• What specific product you're interested in?\n• If you need help with an existing order?\n• Account or payment questions?\n• Information about our customization services?"
            ]
        }
    
    def get_response(self, user_message, session_id=None):
        """Generate appropriate response based on user message"""
        user_message_lower = user_message.lower().strip()
        
        # Check for greeting patterns
        if self._is_greeting(user_message_lower):
            return self._get_random_response('greeting')
        
        # Check for goodbye patterns
        if self._is_goodbye(user_message_lower):
            return self._get_random_response('goodbye')
        
        # Search knowledge base for relevant response
        knowledge_response = self._search_knowledge_base(user_message_lower)
        if knowledge_response:
            return knowledge_response
        
        # Check for specific patterns and provide contextual responses
        contextual_response = self._get_contextual_response(user_message_lower)
        if contextual_response:
            return contextual_response
        
        # Default response
        return self._get_random_response('default')
    
    def _is_greeting(self, message):
        greeting_patterns = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
        return any(pattern in message for pattern in greeting_patterns)
    
    def _is_goodbye(self, message):
        goodbye_patterns = ['bye', 'goodbye', 'see you', 'thanks', 'thank you', 'that\'s all', 'done']
        return any(pattern in message for pattern in goodbye_patterns)
    
    def _search_knowledge_base(self, message):
        """Search the knowledge base for relevant responses"""
        try:
            knowledge_items = ChatbotKnowledge.objects.filter(is_active=True)
            
            for item in knowledge_items:
                keywords = item.get_keywords_list()
                if any(keyword in message for keyword in keywords):
                    return item.answer
            
            return None
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return None
    
    def _get_contextual_response(self, message):
        """Provide contextual responses based on message content"""
        
        # Order-related queries
        if any(word in message for word in ['order', 'track', 'delivery', 'shipping']):
            return "I can help you with order-related questions! To track your order, you'll need your order reference number. You can find this in your email confirmation or by logging into your account and checking 'My Orders'. If you need specific help with an order, please provide your order reference number."
        
        # Product-related queries
        if any(word in message for word in ['product', 'jersey', 'shirt', 'size', 'color', 'design']):
            return "I'd be happy to help you with our products! We offer custom jerseys and teamwear in various sizes (XS, S, M, L, XL) and colors. You can browse our product catalog on the main page, or use our AI Designer tool to create custom designs. What specific product information are you looking for?"
        
        # Account-related queries
        if any(word in message for word in ['account', 'login', 'register', 'profile', 'password']):
            return "For account-related help: You can create an account by clicking 'Sign Up' in the top menu. If you're having trouble logging in, make sure you're using the correct email and password. You can reset your password using the 'Forgot Password' link on the login page. Need help with your profile information? You can update it in the 'My Profile' section after logging in."
        
        # Payment-related queries
        if any(word in message for word in ['payment', 'pay', 'gcash', 'cod', 'cash on delivery']):
            return "We accept multiple payment methods for your convenience: Cash on Delivery (COD) and GCash. You can select your preferred payment method during checkout. For COD orders, you'll pay when your order is delivered. For GCash payments, you'll be redirected to complete the payment securely."
        
        # Customization queries
        if any(word in message for word in ['custom', 'design', 'personalize', 'ai designer']):
            return "Our AI Designer tool lets you create custom jersey designs! You can access it from the main menu. The tool allows you to choose colors, add text, select patterns, and create unique designs for your team. You can also upload your own images or logos. Would you like me to guide you through the customization process?"
        
        return None
    
    def _get_random_response(self, response_type):
        """Get a random response from the specified type"""
        import random
        responses = self.default_responses.get(response_type, self.default_responses['default'])
        return random.choice(responses)


@csrf_exempt
@require_http_methods(["POST"])
def chat_message(request):
    """Handle incoming chat messages"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get customer instance if user is authenticated
        customer_instance = None
        if request.user.is_authenticated:
            try:
                customer_instance = Customer.objects.get(user=request.user)
            except Customer.DoesNotExist:
                customer_instance = None
        
        # Get or create chat session
        chat_session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={
                'customer': customer_instance,
                'is_active': True
            }
        )
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=chat_session,
            message_type='user',
            content=message
        )
        
        # Generate bot response
        chatbot_service = ChatbotService()
        bot_response = chatbot_service.get_response(message, session_id)
        
        # Save bot response
        bot_message = ChatMessage.objects.create(
            session=chat_session,
            message_type='bot',
            content=bot_response
        )
        
        return JsonResponse({
            'success': True,
            'session_id': session_id,
            'response': bot_response,
            'timestamp': bot_message.timestamp.isoformat()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def chat_history(request):
    """Get chat history for a session"""
    try:
        session_id = request.GET.get('session_id')
        
        if not session_id:
            return JsonResponse({'error': 'Session ID is required'}, status=400)
        
        try:
            chat_session = ChatSession.objects.get(session_id=session_id)
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Chat session not found'}, status=404)
        
        messages = chat_session.messages.all()
        
        message_data = []
        for msg in messages:
            message_data.append({
                'type': msg.message_type,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'session_id': session_id,
            'messages': message_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def chat_feedback(request):
    """Handle user feedback on bot responses"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        message_id = data.get('message_id')
        is_helpful = data.get('is_helpful')
        
        if not all([session_id, message_id, is_helpful is not None]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        try:
            chat_session = ChatSession.objects.get(session_id=session_id)
            message = chat_session.messages.get(id=message_id, message_type='bot')
            message.is_helpful = is_helpful
            message.save()
            
            return JsonResponse({'success': True})
            
        except (ChatSession.DoesNotExist, ChatMessage.DoesNotExist):
            return JsonResponse({'error': 'Session or message not found'}, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def chatbot_widget(request):
    """Render the chatbot widget template"""
    return render(request, 'ecom/chatbot_widget.html')
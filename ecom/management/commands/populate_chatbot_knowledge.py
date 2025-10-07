from django.core.management.base import BaseCommand
from ecom.models import ChatbotKnowledge

class Command(BaseCommand):
    help = 'Populate chatbot knowledge base with website-specific help content'

    def handle(self, *args, **options):
        # Clear existing knowledge base
        ChatbotKnowledge.objects.all().delete()
        
        knowledge_data = [
            {
                'category': 'Account',
                'question': 'How do I create an account?',
                'answer': 'To create an account, click on "Sign Up" in the top navigation, fill in your details including name, email, and password, then click "Create Account". You\'ll receive a confirmation email.',
                'keywords': 'signup, register, create account, new user'
            },
            {
                'category': 'Account',
                'question': 'How do I log in?',
                'answer': 'Click "Login" in the top navigation, enter your email and password, then click "Sign In". If you forgot your password, use the "Forgot Password" link.',
                'keywords': 'login, sign in, password, forgot password'
            },
            {
                'category': 'Shopping',
                'question': 'How do I add items to my cart?',
                'answer': 'Browse our products, click on any item to view details, select your size and quantity, then click "Add to Cart". You can view your cart by clicking the cart icon.',
                'keywords': 'add to cart, shopping, buy, purchase'
            },
            {
                'category': 'Shopping',
                'question': 'How do I place an order?',
                'answer': 'Add items to your cart, click the cart icon, review your items, click "Checkout", fill in your shipping address, select payment method, and confirm your order.',
                'keywords': 'order, checkout, place order, buy'
            },
            {
                'category': 'Orders',
                'question': 'How can I track my order?',
                'answer': 'Log into your account and go to "My Orders" to view all your orders and their current status. You can see if your order is pending, processing, shipped, or delivered.',
                'keywords': 'track order, order status, my orders, delivery'
            },
            {
                'category': 'Orders',
                'question': 'Can I cancel my order?',
                'answer': 'You can cancel your order if it\'s still in "Pending" status. Go to "My Orders", find your order, and click "Cancel Order". Once shipped, orders cannot be cancelled.',
                'keywords': 'cancel order, cancel, refund'
            },
            {
                'category': 'Products',
                'question': 'What products do you sell?',
                'answer': 'We specialize in custom team wear including jerseys, uniforms, and sports apparel. We offer jersey customization with 3D preview, AI-powered design tools, and various customization options.',
                'keywords': 'products, jerseys, team wear, custom, uniforms'
            },
            {
                'category': 'Customization',
                'question': 'How do I customize a jersey?',
                'answer': 'Go to "Jersey Customizer" from the main menu. You can use our 3D customizer, advanced designer, or AI-powered design tool to create custom jerseys with your preferred colors, patterns, and text.',
                'keywords': 'customize, jersey customizer, 3d, design, ai designer'
            },
            {
                'category': 'Payment',
                'question': 'What payment methods do you accept?',
                'answer': 'We accept various payment methods including GCash and other secure payment options. You can select your preferred payment method during checkout.',
                'keywords': 'payment, gcash, pay, payment methods'
            },
            {
                'category': 'Shipping',
                'question': 'How much is shipping?',
                'answer': 'Shipping fees vary based on your location within the Philippines. The exact shipping cost will be calculated and displayed during checkout based on your delivery address.',
                'keywords': 'shipping, delivery, shipping fee, cost'
            },
            {
                'category': 'Account',
                'question': 'How do I update my profile?',
                'answer': 'Log into your account, go to "My Profile" or "Edit Profile" to update your personal information, contact details, and addresses.',
                'keywords': 'profile, edit profile, update information'
            },
            {
                'category': 'Features',
                'question': 'What is the wishlist feature?',
                'answer': 'The wishlist allows you to save products you\'re interested in for later. Click the heart icon on any product to add it to your wishlist. Access your wishlist from your account menu.',
                'keywords': 'wishlist, save products, favorites'
            },
            {
                'category': 'Support',
                'question': 'How can I contact customer support?',
                'answer': 'You can contact us through the "Contact Us" page, send feedback through the feedback form, or reach out via our social media channels (Facebook and Instagram).',
                'keywords': 'contact, support, help, feedback, customer service'
            },
            {
                'category': 'Navigation',
                'question': 'How do I search for products?',
                'answer': 'Use the search bar in the top navigation to search for specific products. You can also browse by categories or use filters to find what you\'re looking for.',
                'keywords': 'search, find products, browse, filter'
            },
            {
                'category': 'Technical',
                'question': 'The website is not working properly',
                'answer': 'Try refreshing the page, clearing your browser cache, or using a different browser. If the problem persists, please contact our support team through the Contact Us page.',
                'keywords': 'technical issue, not working, error, bug, problem'
            }
        ]
        
        created_count = 0
        for data in knowledge_data:
            ChatbotKnowledge.objects.create(**data)
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} knowledge base entries'
            )
        )
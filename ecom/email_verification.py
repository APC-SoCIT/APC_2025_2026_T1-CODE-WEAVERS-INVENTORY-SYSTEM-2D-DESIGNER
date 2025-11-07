from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from urllib.parse import urljoin
import uuid
from .models import EmailVerification


def send_verification_email(user, request):
    """Send verification email to user"""
    try:
        # Get or create email verification record
        email_verification, created = EmailVerification.objects.get_or_create(
            user=user,
            defaults={'verification_token': uuid.uuid4()}
        )
        
        # If not created and not verified, generate new token and reset issuance time
        if not created and not email_verification.is_verified:
            email_verification.verification_token = uuid.uuid4()
            # Reset created_at to mark new token issuance time for expiry window
            email_verification.created_at = timezone.now()
            email_verification.save()
        
        # Build verification URL
        path = reverse('verify_email', kwargs={'token': email_verification.verification_token})
        base = getattr(settings, 'PUBLIC_BASE_URL', '')
        if base:
            base = base.rstrip('/') + '/'
            verification_url = urljoin(base, path.lstrip('/'))
        else:
            verification_url = request.build_absolute_uri(path)
        
        # Prepare email content
        context = {
            'user': user,
            'verification_url': verification_url,
            'site_name': 'WorksTeamWear'
        }
        
        html_message = render_to_string('ecom/email/verification_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject='Verify Your Email Address',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"✅ Verification email sent successfully to {user.email}")
        return True
    except Exception as e:
        print(f"❌ Error sending verification email: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_email_view(request, token):
    """Verify email using token; show error page when invalid/expired"""
    email_verification = EmailVerification.objects.filter(verification_token=token).first()

    if not email_verification:
        # Invalid token: show error page with link to resend
        return render(request, 'ecom/verification_expired.html', {
            'email': None,
            'invalid': True,
        })

    if email_verification.is_verified:
        # Already verified: show success page, avoid leaking messages to login
        return render(request, 'ecom/verification_success.html', {
            'email': email_verification.user.email,
            'already_verified': True,
        })

    if email_verification.is_token_expired():
        # Expired token: show error page with user's email and resend link
        return render(request, 'ecom/verification_expired.html', {
            'email': email_verification.user.email,
            'invalid': False,
        })

    # Verify the email and show dedicated success page (no messages on login)
    email_verification.verify_email()
    return render(request, 'ecom/verification_success.html', {
        'email': email_verification.user.email,
        'already_verified': False,
    })


def resend_verification_view(request):
    """Resend verification email"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Please provide your email address.')
            return render(request, 'ecom/resend_verification.html', {'prefill_email': request.GET.get('email', '')})
        
        # Handle duplicate emails gracefully
        users_qs = User.objects.filter(email__iexact=email).order_by('-date_joined')
        if not users_qs.exists():
            messages.error(request, 'No account found with this email address.')
            return render(request, 'ecom/resend_verification.html', {'prefill_email': email})

        if users_qs.count() > 1:
            messages.warning(request, 'Multiple accounts use this email. Sending verification to the newest account.')

        user = users_qs.first()

        # Get or create verification record
        email_verification, _ = EmailVerification.objects.get_or_create(user=user)

        if email_verification.is_verified:
            messages.info(request, 'This email is already verified. You can log in now.')
            return redirect('customerlogin')

        # Send new verification email
        if send_verification_email(user, request):
            messages.success(request, 'Verification email sent successfully! Please check your inbox.')
        else:
            messages.error(request, 'Failed to send verification email. Please try again.')

        return render(request, 'ecom/resend_verification.html', {'prefill_email': email})
    
    # Prefill from query param if provided
    return render(request, 'ecom/resend_verification.html', {'prefill_email': request.GET.get('email', '')})


@csrf_exempt
def check_verification_status(request):
    """AJAX endpoint to check email verification status"""
    if request.method == 'GET' and request.user.is_authenticated:
        try:
            email_verification = EmailVerification.objects.get(user=request.user)
            # Compute expiry info (5 minutes window)
            expiry_seconds = 300
            expiry_time = email_verification.created_at + timedelta(seconds=expiry_seconds)
            now = timezone.now()
            is_expired = (not email_verification.is_verified) and (now > expiry_time)
            seconds_left = max(0, int((expiry_time - now).total_seconds()))

            return JsonResponse({
                'is_verified': email_verification.is_verified,
                'verified_at': email_verification.verified_at.isoformat() if email_verification.verified_at else None,
                'created_at': email_verification.created_at.isoformat() if email_verification.created_at else None,
                'is_expired': is_expired,
                'seconds_left': seconds_left
            })
        except EmailVerification.DoesNotExist:
            return JsonResponse({'is_verified': False, 'verified_at': None})
    
    return JsonResponse({'error': 'Unauthorized'}, status=401)


def verification_required_view(request):
    """View to show when email verification is required"""
    if request.user.is_authenticated:
        try:
            email_verification = EmailVerification.objects.get(user=request.user)
            if email_verification.is_verified:
                return redirect('home')
        except EmailVerification.DoesNotExist:
            pass
    
    return render(request, 'ecom/verification_required.html')

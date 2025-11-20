"""
OTP (One-Time Password) utilities for password reset
"""
import random
import string
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import logging

logger = logging.getLogger('smart_task_manager')


def generate_otp(length=6):
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(email, otp):
    """Send OTP via email"""
    try:
        subject = 'Password Reset OTP - Smart Task Manager'
        message = f"""
Hello,

You have requested to reset your password. Your One-Time Password (OTP) is:

{otp}

This OTP is valid for 10 minutes.

If you did not request this, please ignore this email.

Best regards,
Smart Task Manager Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"OTP email sent successfully to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {str(e)}")
        return False


def send_otp_sms(phone_number, otp):
    """
    Send OTP via SMS using Twilio or any SMS provider
    For now, this is a placeholder - you need to configure your SMS provider
    """
    try:
        # SMS sending implementation would go here
        # Example with Twilio:
        # from twilio.rest import Client
        # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        # message = client.messages.create(
        #     body=f'Your password reset OTP is: {otp}. Valid for 10 minutes.',
        #     from_=settings.TWILIO_PHONE_NUMBER,
        #     to=phone_number
        # )
        
        logger.info(f"OTP SMS would be sent to {phone_number}: {otp}")
        # For development, just log the OTP
        print(f"📱 SMS OTP for {phone_number}: {otp}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP SMS to {phone_number}: {str(e)}")
        return False


def store_otp(identifier, otp, otp_type='email'):
    """
    Store OTP in cache with 10 minute expiry
    identifier: email or phone number
    """
    cache_key = f"password_reset_otp_{otp_type}_{identifier}"
    cache.set(cache_key, otp, timeout=600)  # 10 minutes
    logger.info(f"OTP stored for {identifier} ({otp_type})")


def verify_otp(identifier, otp, otp_type='email'):
    """
    Verify OTP from cache
    """
    cache_key = f"password_reset_otp_{otp_type}_{identifier}"
    stored_otp = cache.get(cache_key)
    
    if stored_otp is None:
        logger.warning(f"OTP expired or not found for {identifier}")
        return False
    
    if stored_otp == otp:
        # OTP is valid, delete it so it can't be reused
        cache.delete(cache_key)
        logger.info(f"OTP verified successfully for {identifier}")
        return True
    
    logger.warning(f"Invalid OTP attempt for {identifier}")
    return False


def create_reset_token(user_id):
    """
    Create a password reset token and store it in cache
    """
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    cache_key = f"password_reset_token_{token}"
    cache.set(cache_key, user_id, timeout=1800)  # 30 minutes
    logger.info(f"Password reset token created for user {user_id}")
    return token


def verify_reset_token(token):
    """
    Verify password reset token and return user_id
    """
    cache_key = f"password_reset_token_{token}"
    user_id = cache.get(cache_key)
    
    if user_id is None:
        logger.warning(f"Password reset token expired or invalid")
        return None
    
    return user_id


def delete_reset_token(token):
    """
    Delete password reset token after use
    """
    cache_key = f"password_reset_token_{token}"
    cache.delete(cache_key)

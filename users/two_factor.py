"""
Two-Factor Authentication Models and Utilities
"""
from django.db import models
from django.contrib.auth import get_user_model
import pyotp
import qrcode
from io import BytesIO
import base64

User = get_user_model()


class TwoFactorAuth(models.Model):
    """Two-factor authentication settings for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor')
    secret_key = models.CharField(max_length=32, unique=True)
    is_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Two-Factor Authentication'
        verbose_name_plural = 'Two-Factor Authentications'
    
    def __str__(self):
        return f"2FA for {self.user.email}"
    
    @classmethod
    def generate_secret(cls):
        """Generate a new secret key"""
        return pyotp.random_base32()
    
    def get_totp_uri(self):
        """Get TOTP URI for QR code"""
        return pyotp.totp.TOTP(self.secret_key).provisioning_uri(
            name=self.user.email,
            issuer_name='Smart Task Manager'
        )
    
    def get_qr_code(self):
        """Generate QR code as base64 image"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.get_totp_uri())
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_token(self, token):
        """Verify TOTP token"""
        totp = pyotp.TOTP(self.secret_key)
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self, count=10):
        """Generate backup codes"""
        import secrets
        codes = [secrets.token_hex(4).upper() for _ in range(count)]
        self.backup_codes = codes
        self.save()
        return codes
    
    def use_backup_code(self, code):
        """Use a backup code (one-time use)"""
        code = code.upper()
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        return False


class LoginAttempt(models.Model):
    """Track login attempts for security monitoring"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['email', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        status = 'Success' if self.success else 'Failed'
        return f"{status} login attempt for {self.email} from {self.ip_address}"


class SessionManagement(models.Model):
    """Track active user sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_name = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-last_activity']
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'
    
    def __str__(self):
        return f"Session for {self.user.email} from {self.ip_address}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

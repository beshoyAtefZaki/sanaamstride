import frappe
from frappe import _
import jwt
from datetime import datetime, timedelta

def authenticate_user(username, password):
    """
    Authenticates user and returns JWT token if successful
    """
    try:
        # Validate login
        frappe.local.login_manager.authenticate(username, password)
        frappe.local.login_manager.post_login()

        # Get user details
        user = frappe.get_doc('User', frappe.session.user)
        
        # Generate JWT token
        expiry = datetime.utcnow() + timedelta(days=1)
        token = generate_jwt_token(user.name, expiry)
        
        # Get user roles
        roles = [role.role for role in user.roles]
        
        return {
            "message": "Login successful",
            "success": True,
            "access_token": token,
            "user": {
                "name": user.name,
                "full_name": user.full_name,
                "roles": roles
            },
            "expires_at": expiry.isoformat()
        }
        
    except frappe.AuthenticationError:
        frappe.throw(_("Invalid username or password"))
    except Exception as e:
        frappe.throw(_("Authentication failed: {0}").format(str(e)))

def generate_jwt_token(user, expiry):
    """
    Generates a JWT token for the user
    """
    try:
        # Get the secret key from Frappe configuration
        secret_key = frappe.get_conf().get('jwt_secret') or 'your_secret_key_here'
        
        payload = {
            'user': user,
            'exp': expiry,
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token
        
    except Exception as e:
        frappe.throw(_("Token generation failed: {0}").format(str(e)))

def verify_token(token):
    """
    Verifies the JWT token
    """
    try:
        secret_key = frappe.get_conf().get('jwt_secret') or 'your_secret_key_here'
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        frappe.throw(_("Token has expired"))
    except jwt.InvalidTokenError:
        frappe.throw(_("Invalid token"))
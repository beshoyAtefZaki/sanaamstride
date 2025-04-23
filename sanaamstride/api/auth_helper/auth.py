import frappe
from frappe import _
import jwt
from datetime import datetime, timedelta
import base64 
def authenticate_user(username, password):
    """
    Authenticates user and returns JWT token if successful
    """
    try:
        # Validate login
        frappe.local.login_manager.authenticate(username, password)
        frappe.local.login_manager.post_login()

        # Get user details
        api_generate = generate_keys(frappe.session.user)
        user = frappe.get_doc('User', frappe.session.user)
        token_key =  user.api_key + ":" + api_generate
        token_key_decode = base64.b64encode(token_key.encode()).decode('utf-8')
        auth_token = f"Basic {token_key_decode}"
        frappe.local.response['auth_token'] = auth_token
        
    
    
    except frappe.AuthenticationError:
        frappe.throw(_("Invalid username or password"))
    except Exception as e:
        frappe.throw(_("Authentication failed: {0}").format(str(e)))


def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.save( ignore_permissions=True)
    return api_secret
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
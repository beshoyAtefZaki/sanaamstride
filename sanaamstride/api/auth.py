import frappe
from sanaamstride.api.auth_helper.auth import authenticate_user

@frappe.whitelist(allow_guest=True)
def login():
    """
    Login endpoint that accepts user credentials and returns an access token
    Request body should contain:
    {
        "usr": "username@example.com",
        "pwd": "password"
    }
    """
    try:
        username = frappe.request.form.get('usr')
        password = frappe.request.form.get('pwd')
        
        if not username or not password:
            frappe.throw('Username and password are required')
            
        return authenticate_user(username, password)
        
    except Exception as e:
        frappe.local.response.http_status_code = 401
        return {"message": str(e), "success": False}
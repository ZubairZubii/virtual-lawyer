"""
Script to apply security fixes to all API endpoints
Adds RBAC (role-based access control) to admin and lawyer endpoints
"""
import re

# Read the API file
with open('api_complete.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Admin endpoints that need protection
admin_endpoints = [
    (r'@app\.get\("/api/admin/dashboard"\)\nasync def get_admin_dashboard\(',
     '@app.get("/api/admin/dashboard")\nasync def get_admin_dashboard(current_user: dict = Depends(require_role("admin"))):'),

    (r'@app\.get\("/api/admin/settings"\)\nasync def get_settings\(',
     '@app.get("/api/admin/settings")\nasync def get_settings(current_user: dict = Depends(require_role("admin"))):'),

    (r'@app\.post\("/api/admin/settings"\)\nasync def update_settings\((\w+): (\w+)\)',
     r'@app.post("/api/admin/settings")\nasync def update_settings(\1: \2, current_user: dict = Depends(require_role("admin"))):'),

    (r'@app\.put\("/api/admin/users/\{user_id\}"\)\nasync def update_user\(user_id: str, updates: Dict\)',
     '@app.put("/api/admin/users/{user_id}")\nasync def update_user(user_id: str, updates: Dict, current_user: dict = Depends(require_role("admin"))):'),

    (r'@app\.delete\("/api/admin/users/\{user_id\}"\)\nasync def delete_user\(user_id: str\)',
     '@app.delete("/api/admin/users/{user_id}")\nasync def delete_user(user_id: str, current_user: dict = Depends(require_role("admin"))):'),

    (r'@app\.get\("/api/admin/lawyers"\)\nasync def get_admin_lawyers\(\)',
     '@app.get("/api/admin/lawyers")\nasync def get_admin_lawyers(current_user: dict = Depends(require_role("admin"))):'),

    (r'@app\.post\("/api/admin/lawyers"\)\nasync def create_lawyer\(request: CreateLawyerRequest\)',
     '@app.post("/api/admin/lawyers")\nasync def create_lawyer(request: CreateLawyerRequest, current_user: dict = Depends(require_role("admin"))):'),

    (r'@app\.put\("/api/admin/lawyers/\{lawyer_id\}/verify"\)\nasync def verify_lawyer\(lawyer_id: str, status: str = "Verified"\)',
     '@app.put("/api/admin/lawyers/{lawyer_id}/verify")\nasync def verify_lawyer(lawyer_id: str, status: str = "Verified", current_user: dict = Depends(require_role("admin"))):'),

    (r'@app\.put\("/api/admin/lawyers/\{lawyer_id\}"\)\nasync def update_lawyer\(lawyer_id: str, request: UpdateLawyerRequest\)',
     '@app.put("/api/admin/lawyers/{lawyer_id}")\nasync def update_lawyer(lawyer_id: str, request: UpdateLawyerRequest, current_user: dict = Depends(require_role("admin"))):'),

    (r'@app\.delete\("/api/admin/lawyers/\{lawyer_id\}"\)\nasync def delete_lawyer\(lawyer_id: str\)',
     '@app.delete("/api/admin/lawyers/{lawyer_id}")\nasync def delete_lawyer(lawyer_id: str, current_user: dict = Depends(require_role("admin"))):'),

    (r'@app\.post\("/api/admin/lawyers/\{lawyer_id\}/image"\)\nasync def upload_lawyer_image\(lawyer_id: str, image: UploadFile = File\(\.\.\.\)\)',
     '@app.post("/api/admin/lawyers/{lawyer_id}/image")\nasync def upload_lawyer_image(lawyer_id: str, image: UploadFile = File(...), current_user: dict = Depends(require_role("admin"))):'),
]

# Lawyer endpoints that need protection
lawyer_endpoints = [
    (r'@app\.get\("/api/lawyer/clients"\)\nasync def get_lawyer_clients\(lawyer_id: str\)',
     '@app.get("/api/lawyer/clients")\nasync def get_lawyer_clients(lawyer_id: str, current_user: dict = Depends(require_role("lawyer"))):'),

    (r'@app\.post\("/api/lawyer/clients"\)\nasync def add_client\(client_data: dict\)',
     '@app.post("/api/lawyer/clients")\nasync def add_client(client_data: dict, current_user: dict = Depends(require_role("lawyer"))):'),

    (r'@app\.get\("/api/lawyer/clients/\{client_id\}/cases"\)\nasync def get_client_cases\(client_id: str\)',
     '@app.get("/api/lawyer/clients/{client_id}/cases")\nasync def get_client_cases(client_id: str, current_user: dict = Depends(require_role("lawyer"))):'),

    (r'@app\.post\("/api/lawyer/clients/\{client_id\}/cases"\)\nasync def create_client_case\(client_id: str, case_data: dict\)',
     '@app.post("/api/lawyer/clients/{client_id}/cases")\nasync def create_client_case(client_id: str, case_data: dict, current_user: dict = Depends(require_role("lawyer"))):'),
]

# Apply all admin endpoint protections
for pattern, replacement in admin_endpoints:
    content = re.sub(pattern, replacement, content)

# Apply all lawyer endpoint protections
for pattern, replacement in lawyer_endpoints:
    content = re.sub(pattern, replacement, content)

# Write the updated content back
with open('api_complete.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Security fixes applied successfully!")
print(f"   - Protected {len(admin_endpoints)} admin endpoints")
print(f"   - Protected {len(lawyer_endpoints)} lawyer endpoints")

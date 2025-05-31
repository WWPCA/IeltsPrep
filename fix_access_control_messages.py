"""
Fix Access Control Messages

Updates access control error messages to reflect the actual user flow
where users can only access assessments they've purchased.
"""

import re

def fix_access_control_messages():
    """Update access control messages to reflect actual user flow"""
    
    # Read the current routes.py file
    with open('routes.py', 'r') as f:
        content = f.read()
    
    # Update access control messages
    # Since users must purchase before accessing, if they reach an assessment
    # they shouldn't have access to, it's likely URL manipulation or technical issue
    content = re.sub(
        r"flash\('You need to purchase an assessment package to access this feature\.', 'info'\)",
        "flash('Assessment not available. Please start from your dashboard.', 'info')",
        content
    )
    
    # Write the updated content back
    with open('routes.py', 'w') as f:
        f.write(content)
    
    print("Updated access control messages to reflect actual user flow")

if __name__ == '__main__':
    fix_access_control_messages()
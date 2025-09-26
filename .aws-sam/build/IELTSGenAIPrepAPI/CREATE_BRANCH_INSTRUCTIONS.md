# Simple Branch Creation Instructions

## Option 1: Look for "Shell" or "Terminal" 
- Look in the left sidebar for a "Shell" or "Terminal" button
- Click it to open a new terminal
- Type: `git checkout -b production-recaptcha-fix`

## Option 2: Use Git Interface Branch Dropdown
- In the Git tab, look for a dropdown that says "main"
- Click on it and look for "Create new branch" or similar
- Name it: `production-recaptcha-fix`

## Option 3: Manual Branch Creation
If you find a command prompt anywhere, just type:
```bash
git checkout -b production-recaptcha-fix
```

Then go back to Git tab and commit your changes.

## What This Does:
- Creates a new branch with your current production code
- Includes the reCAPTCHA fix and all working features
- Allows you to push this specific version to GitHub
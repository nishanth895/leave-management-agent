# ============================================
# Leave Management Agent - GitHub Push Script
# ============================================
# Step 1: Replace YOUR_GITHUB_USERNAME with your actual GitHub username
# Step 2: Replace YOUR_REPO_NAME with your repository name (e.g., leave-management-agent)
# Step 3: Run this script in PowerShell

$GITHUB_USERNAME = "YOUR_GITHUB_USERNAME"   # <-- Change this!
$REPO_NAME = "leave-management-agent"        # <-- Change this if different!

# Initialize Git
git init

# Configure Git (change to your email & name)
git config user.email "your@email.com"       # <-- Change this!
git config user.name "Your Name"             # <-- Change this!

# Add all files
git add .

# First commit
git commit -m "Initial commit: Leave Management Agent"

# Set main branch
git branch -M main

# Link to GitHub repo
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# Push to GitHub
git push -u origin main

Write-Host ""
Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host "🔗 Your repo: https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Cyan

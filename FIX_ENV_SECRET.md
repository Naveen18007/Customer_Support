# 🔒 Fix: Remove .env File from Git History

GitHub blocked your push because a `.env` file with API keys was committed. Here's how to fix it:

## ⚠️ **CRITICAL: Remove .env from Git History**

The `.env` file contains sensitive API keys and should NEVER be in git history.

## 🔧 **Solution: Remove .env from Git**

### **Step 1: Remove Lock File**
```powershell
# Remove git lock file
Remove-Item .git/index.lock -ErrorAction SilentlyContinue
```

### **Step 2: Remove .env from Git Tracking**
```powershell
# Remove .env from git (but keep local file)
git rm --cached .env

# Verify .env is in .gitignore (it already is)
cat .gitignore | Select-String ".env"
```

### **Step 3: Commit the Removal**
```powershell
git add .gitignore
git commit -m "chore: Remove .env file from git tracking"
```

### **Step 4: Remove from Git History (IMPORTANT)**

Since `.env` was already pushed, you need to remove it from history:

**Option A: Using git filter-branch (Recommended)**
```powershell
# Remove .env from all commits
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env" --prune-empty --tag-name-filter cat -- --all

# Force garbage collection
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**Option B: Using BFG Repo-Cleaner (Easier)**
1. Download BFG: https://rtyley.github.io/bfg-repo-cleaner/
2. Run:
```powershell
java -jar bfg.jar --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**Option C: Interactive Rebase (If only recent commits)**
```powershell
# Find the commit that added .env
git log --all --full-history -- .env

# Interactive rebase (replace N with number of commits)
git rebase -i HEAD~N

# In the editor, change 'pick' to 'edit' for commits with .env
# Then run:
git rm --cached .env
git commit --amend --no-edit
git rebase --continue
```

### **Step 5: Force Push (After Removing from History)**
```powershell
# ⚠️ WARNING: This rewrites history
git push origin main --force
```

## 🛡️ **Verify .env is Protected**

### **Check .gitignore**
Make sure `.env` is in `.gitignore`:
```powershell
cat .gitignore
```

Should see:
```
.env
.env.local
.env.*.local
```

### **Verify .env is NOT Tracked**
```powershell
git ls-files | Select-String ".env"
```

Should return **nothing** (empty).

### **Check if .env Exists Locally**
```powershell
Test-Path .env
```

Should return `True` (file exists locally but not in git).

## 📝 **Create .env.example Template**

Create a template file for others (without real keys):

```powershell
# Create .env.example
@"
GROQ_API_KEY=your_groq_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
FROM_EMAIL=your_email@gmail.com
TEAMS_WEBHOOK_URL=your_teams_webhook_url_here
LOG_LEVEL=INFO
"@ | Out-File -FilePath .env.example -Encoding utf8

# Add to git
git add .env.example
git commit -m "docs: Add .env.example template"
```

## ✅ **Quick Fix Commands**

Run these commands in order:

```powershell
# 1. Remove lock file
Remove-Item .git/index.lock -ErrorAction SilentlyContinue

# 2. Remove .env from git
git rm --cached .env

# 3. Commit removal
git commit -m "chore: Remove .env from git tracking"

# 4. Remove from history (choose one method above)

# 5. Force push
git push origin main --force
```

## 🔐 **Security Best Practices**

1. ✅ **Never commit `.env`** - Always in `.gitignore`
2. ✅ **Use `.env.example`** - Template without real keys
3. ✅ **Rotate API keys** - If exposed, regenerate them
4. ✅ **Use GitHub Secrets** - For CI/CD pipelines
5. ✅ **Review commits** - Before pushing, check what's included

## 🚨 **If API Keys Were Exposed**

If your API keys were already pushed to GitHub:

1. **Immediately regenerate all API keys:**
   - Groq API Key
   - Supabase Keys
   - SMTP Credentials
   - Teams Webhook URL

2. **Update your local `.env` file** with new keys

3. **Remove from git history** (steps above)

4. **Monitor for unauthorized access**

## 📋 **Complete Checklist**

- [ ] Remove `.env` from git tracking
- [ ] Remove `.env` from git history
- [ ] Verify `.gitignore` includes `.env`
- [ ] Create `.env.example` template
- [ ] Regenerate exposed API keys
- [ ] Update local `.env` with new keys
- [ ] Force push cleaned history
- [ ] Verify push succeeds

---

**After fixing, your push should succeed!** 🚀

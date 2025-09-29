# Branch Protection Setup Instructions

## 🛡️ Required Status Checks for CI/CD Pipeline

To complete the CI/CD setup, configure these branch protection rules for the `main` branch:

### **1. Go to Repository Settings**
- Navigate to: `https://github.com/WWFCA/IeltsPrep/settings/branch_protection_rules`
- Click "Add rule" or edit existing rule for `main` branch

### **2. Configure Protection Rules**

#### **Basic Settings:**
- ✅ **Branch name pattern**: `main`
- ✅ **Restrict pushes that create files larger than**: 100 MB
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: 1
  - ✅ Dismiss stale PR approvals when new commits are pushed
  - ✅ Require review from code owners (if CODEOWNERS file exists)

#### **Status Checks (CRITICAL):**
- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**

**Required Status Checks to Add:**
1. `Python Tests`
2. `Android Build Verification` 
3. `iOS Build Verification`

#### **Additional Protection:**
- ✅ **Require conversation resolution before merging**
- ✅ **Include administrators** (applies rules to admins too)
- ✅ **Allow force pushes**: ❌ (disabled)
- ✅ **Allow deletions**: ❌ (disabled)

### **3. Result**
After setup:
- 🚫 **No direct pushes to main** allowed
- ✅ **All changes must go through PRs**
- ✅ **All tests must pass** before merge
- ✅ **Both Android APK and iOS builds** must succeed
- ✅ **Python tests with Flask server** must pass

## 🔄 **Developer Workflow**
1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit
3. Push branch: `git push origin feature/my-feature`
4. Create Pull Request to `main`
5. **CI automatically runs**: Python tests + Android build + iOS build
6. **Only merge if all tests pass** ✅

This ensures broken code never reaches production!
# Security Scanning & Release Approval Setup

## Overview
This document explains the security scanning and release approval process implemented in the CI/CD pipeline.

## Security Scanning Components

### 1. SAST (Static Application Security Testing)
- **Tool**: Bandit
- **Runs on**: Every push, PR
- **Checks**: Python code vulnerabilities, security anti-patterns
- **Location**: `.github/workflows/comprehensive-tests.yml`

### 2. Dependency Vulnerability Scanning
- **Tools**: pip-audit, npm audit, Safety
- **Runs on**: Every push, PR, before builds
- **Checks**: Known vulnerabilities in dependencies
- **Location**: Multiple workflows

### 3. Secret Scanning
- **Tool**: TruffleHog
- **Runs on**: Every push, PR
- **Checks**: Hardcoded secrets, API keys, credentials
- **Location**: `.github/workflows/comprehensive-tests.yml`

## Release Approval Process

### Automated Build (Draft Release)
1. Code pushed to `main` branch
2. Security scans run automatically
3. Android/iOS builds execute with signing
4. **Release created as DRAFT** (not public)
5. Artifacts stored securely

### Manual Approval Required
To publish a release:

1. **Go to Actions** → **Production Release Approval**
2. **Click "Run workflow"**
3. **Enter**:
   - Release version (e.g., `v123`)
   - Platform (android/ios/both)
4. **Workflow requires approval** (via GitHub Environment protection)
5. **Authorized approver** reviews and approves
6. **Release published** to GitHub

### GitHub Environment Setup

Create a `production-release` environment:

```bash
# In GitHub repository settings:
1. Go to Settings → Environments
2. Click "New environment"
3. Name: "production-release"
4. Add protection rules:
   - Required reviewers: [Your team members]
   - Wait timer: 0 minutes (optional: add delay)
5. Save protection rules
```

### Who Can Approve Releases?
Configure in: **Settings → Environments → production-release → Required reviewers**

Add team members who should approve production releases.

## Security Best Practices

### Never Auto-Publish
- Releases are created as **drafts** by default
- Manual approval required for publication
- Prevents accidental exposure of signed binaries

### Artifact Retention
- **Debug builds**: 14 days
- **Release builds**: 90 days  
- **Security reports**: 90 days

### Secret Management
- All secrets stored in GitHub Secrets
- Never committed to repository
- Rotated regularly (recommended: every 90 days)

## CI/CD Pipeline Flow

```
┌─────────────────┐
│  Code Push      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Security Scans  │ ◄─── Bandit, pip-audit, TruffleHog
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Integration     │ ◄─── LocalStack, pytest
│ Tests           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Build APK/IPA   │ ◄─── Signed with production keys
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DRAFT Release   │ ◄─── NOT publicly accessible
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Manual Approval │ ◄─── Required reviewer approval
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PUBLIC Release  │ ◄─── Published to GitHub
└─────────────────┘
```

## Compliance Checklist

Before approving a release:

- [ ] Security scans passed (no critical/high vulnerabilities)
- [ ] Integration tests passed (100% success)
- [ ] Build artifacts verified and signed
- [ ] Release notes reviewed and accurate
- [ ] App Store/Google Play compliance verified
- [ ] Privacy policy and terms up to date
- [ ] Version number follows semantic versioning

## Troubleshooting

### Release Workflow Fails
Check security scanning job logs for specific failures.

### Can't Find Draft Release
Releases are in: **Releases** → Filter by **Draft**

### Approval Not Working
Verify `production-release` environment exists with required reviewers configured.

## Support

For questions about the CI/CD pipeline:
- Review workflow files in `.github/workflows/`
- Check test logs in GitHub Actions
- Contact: DevOps team

# IELTS GenAI Prep Admin Guide

This document provides instructions for setting up and using the administrative interface for the IELTS GenAI Prep platform.

## Setting Up Admin Access

### Creating an Admin User

To create an admin user or elevate an existing user to admin status, use the provided script:

```bash
python create_admin_user.py <username> <email> <password>
```

For example:
```bash
python create_admin_user.py admin admin@example.com securepassword123
```

This will either:
1. Create a new user with admin privileges, or
2. Update an existing user to have admin privileges

### Accessing the Admin Dashboard

Once you have admin credentials:

1. Log in to the platform with your admin username and password
2. Navigate to `/admin` in your browser (e.g., https://yoursite.com/admin)
3. You'll see the admin dashboard with various monitoring options

## Admin Dashboard Features

The admin dashboard provides comprehensive monitoring and management capabilities:

### Connection Issues Monitoring

- **Path**: `/admin/connection-issues`
- **Purpose**: Track and resolve user connection problems during assessments
- **Features**:
  - Filter by date, location, assessment type, and user
  - View detailed connection information (browser, device, network quality)
  - Mark issues as resolved with resolution notes

### API Issues Monitoring

- **Path**: `/admin/api-issues`
- **Purpose**: Monitor external API service issues (AWS Bedrock, OpenAI, etc.)
- **Features**:
  - Track API errors by service, endpoint, and error type
  - View request/response data for debugging
  - Monitor API performance metrics

### Authentication Issues Monitoring

- **Path**: `/admin/auth-issues`
- **Purpose**: Track login issues and detect suspicious activity
- **Features**:
  - Monitor failed login attempts and success rates
  - View geographic distribution of login attempts
  - Identify suspicious login patterns

### Performance Reports

- **Path**: `/admin/connection-issues-report` (and others)
- **Purpose**: View aggregate statistics and trends
- **Features**:
  - Visual charts of issue frequency and distribution
  - Regional analysis of connection problems
  - Success/failure rate metrics

## Using the System Monitoring Tools

### Filtering Data

All monitoring interfaces include powerful filtering capabilities:
- **Date Range**: Filter by specific time periods
- **Issue Type**: Focus on specific types of problems
- **User/Location**: Filter by specific users or geographic regions

### Resolving Issues

1. From any issue list, click "View Details" on a specific issue
2. Review the detailed information about the problem
3. If the issue is resolved, use the "Mark as Resolved" button
4. Add optional resolution notes for future reference

### Generating Demo Data (Development Only)

For testing the admin interface, you can generate sample issue data:

```bash
python setup_issue_tracking.py
```

This will create sample connection, API, and authentication issues with realistic patterns for testing the interface.

## Security Considerations

- Admin access should be granted only to authorized personnel
- Regular password rotation is recommended for admin accounts
- Admin actions are logged for accountability
- Be cautious when viewing user data, respecting privacy regulations
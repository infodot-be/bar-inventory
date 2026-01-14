# Security Documentation

## Overview

This document outlines the security measures implemented in the Bar Inventory Management System and provides guidance for maintaining a secure deployment.

## Security Vulnerabilities Fixed

### 1. ✅ HTTPS/SSL Security
**Issue:** No enforcement of HTTPS connections in production.

**Fix:** Added comprehensive SSL/TLS security settings:
- `SECURE_SSL_REDIRECT`: Forces HTTPS for all connections
- `SESSION_COOKIE_SECURE`: Ensures session cookies only sent over HTTPS
- `CSRF_COOKIE_SECURE`: Ensures CSRF tokens only sent over HTTPS
- `SECURE_PROXY_SSL_HEADER`: Properly handles HTTPS behind reverse proxies
- `SECURE_HSTS_SECONDS`: HTTP Strict Transport Security for 1 year
- `SECURE_HSTS_INCLUDE_SUBDOMAINS`: Extends HSTS to all subdomains
- `SECURE_HSTS_PRELOAD`: Enables HSTS preload list inclusion

**Configuration:** Set via environment variables in WSGI file (see DEPLOY.md)

### 2. ✅ Cookie Security
**Issue:** Cookies were not protected against XSS and CSRF attacks.

**Fix:** Enhanced cookie security:
- `SESSION_COOKIE_HTTPONLY = True`: Prevents JavaScript access to session cookies
- `CSRF_COOKIE_HTTPONLY = True`: Protects CSRF tokens from JavaScript
- `SESSION_COOKIE_SAMESITE = 'Lax'`: Prevents CSRF via same-site cookie policy
- `CSRF_COOKIE_SAMESITE = 'Lax'`: Additional CSRF protection

**Impact:** Significantly reduces XSS and CSRF attack surface

### 3. ✅ Clickjacking Protection
**Issue:** Application could be embedded in iframes by malicious sites.

**Fix:** Added `X_FRAME_OPTIONS = 'DENY'`

**Impact:** Prevents clickjacking attacks by disallowing iframe embedding

### 4. ✅ Content Type Sniffing
**Issue:** Browsers could misinterpret content types.

**Fix:** Added `SECURE_CONTENT_TYPE_NOSNIFF = True`

**Impact:** Forces browsers to respect declared content types

### 5. ✅ CSRF Trusted Origins
**Issue:** Cross-origin POST requests could be rejected even from legitimate sources.

**Fix:** Added `CSRF_TRUSTED_ORIGINS` configuration

**Configuration:** Set via environment variable (comma-separated HTTPS URLs)

### 6. ✅ Sensitive Settings in Environment Variables
**Issue:** `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` were hardcoded.

**Fix:** All sensitive settings now read from environment variables:
- `SECRET_KEY`: Must be set in production
- `DEBUG`: Defaults to True (dev), must be set to False (prod)
- `ALLOWED_HOSTS`: Must specify allowed domains in production

**Impact:** Keeps secrets out of version control

### 7. ✅ Authentication/Authorization Gaps
**Issue:** Stock modification endpoints lacked proper authentication and authorization checks.

**Fix:** Added comprehensive checks to all endpoints:
- `update_stock()`: Requires authentication + location authorization
- `quick_adjust()`: Requires authentication + location authorization
- `save_count()`: Requires authentication + location authorization
- Non-staff users can only modify their assigned location

**Impact:** Prevents unauthorized stock modifications

### 8. ✅ Token Login Security
**Issue:** Token-based authentication lacked validation and logging.

**Fix:** Enhanced token security:
- Tokens expire after 1 hour (PASSWORD_RESET_TIMEOUT)
- Tokens invalidated if user is deactivated
- Added `is_active` check during token validation
- Inactive users cannot receive tokens
- All token generation and usage logged
- Failed login attempts logged for monitoring

**Impact:** Reduces risk of token abuse and provides audit trail

### 9. ✅ Missing Authentication Checks
**Issue:** `generate_token_link()` didn't verify authentication.

**Fix:** Added authentication check before staff permission check

**Impact:** Prevents unauthenticated access attempts

### 10. ✅ Logging and Monitoring
**Issue:** No logging of security-relevant events.

**Fix:** Added logging for:
- Successful token logins
- Failed token login attempts
- Token generation by staff
- Unauthorized token generation attempts

**Impact:** Enables detection of suspicious activity and security audits

## Current Security Posture

### ✅ Implemented Protections

1. **Authentication & Authorization**
   - Token-based authentication with expiration
   - Role-based access control (staff vs. location users)
   - Per-location authorization checks
   - Session-based authentication for admin

2. **Data Protection**
   - HTTPS enforcement in production
   - Secure cookie flags (HttpOnly, Secure, SameSite)
   - SQL injection protection (Django ORM)
   - XSS protection (Django template auto-escaping)

3. **Request Security**
   - CSRF protection on all POST requests
   - Trusted origins configuration
   - HTTP method restrictions (@require_http_methods)
   - Clickjacking protection

4. **Configuration Security**
   - Secrets in environment variables
   - Production-ready security headers
   - Strong password validation
   - Debug mode disabled in production

5. **Audit & Monitoring**
   - Authentication event logging
   - Failed access attempt logging
   - Token generation audit trail

### Remaining Considerations

1. **Rate Limiting** ⚠️
   - **Status:** Not implemented
   - **Risk:** Brute force attacks on login/token endpoints
   - **Recommendation:** Implement django-ratelimit or similar
   - **Priority:** Medium (PythonAnywhere has some built-in protection)

2. **Password Reset Timeout** ⚠️
   - **Status:** Uses Django default (1 hour)
   - **Recommendation:** Consider reducing for higher security environments
   - **Configuration:** Add `PASSWORD_RESET_TIMEOUT = 3600` in settings.py

3. **Account Lockout** ⚠️
   - **Status:** Not implemented
   - **Risk:** Unlimited login attempts possible
   - **Recommendation:** Implement django-axes for automatic lockout
   - **Priority:** Medium

4. **Two-Factor Authentication** ⚠️
   - **Status:** Not implemented
   - **Risk:** Single factor authentication only
   - **Recommendation:** Consider django-otp for admin accounts
   - **Priority:** Low (for internal bar inventory system)

5. **File Upload Validation** ✅
   - **Status:** N/A - No file uploads in current implementation
   - **Note:** If adding file uploads (e.g., import), use secure_filename()

6. **API Rate Limiting** ⚠️
   - **Status:** Not implemented for HTMX endpoints
   - **Risk:** Potential abuse of stock update endpoints
   - **Recommendation:** Add rate limiting to update_stock, quick_adjust
   - **Priority:** Low (requires authentication + authorization already)

## Environment Variables Reference

### Required for Production

```bash
# Core Django settings
SECRET_KEY='generate-at-https://djecrety.ir/'
DEBUG='False'
ALLOWED_HOSTS='yourdomain.com,www.yourdomain.com'

# HTTPS/SSL Security
SESSION_COOKIE_SECURE='True'
CSRF_COOKIE_SECURE='True'
SECURE_SSL_REDIRECT='True'
SECURE_HSTS_SECONDS='31536000'  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS='True'
SECURE_HSTS_PRELOAD='True'

# CSRF Protection
CSRF_TRUSTED_ORIGINS='https://yourdomain.com,https://www.yourdomain.com'

# Database (if using MySQL)
DJANGO_ENV='prod'
DB_HOST='your-mysql-host'
DB_NAME='your_database'
DB_USER='your_user'
DB_PASSWORD='secure-password'
DB_PORT='3306'
```

### Optional Settings

```bash
# Token expiration (default 3600 seconds = 1 hour)
PASSWORD_RESET_TIMEOUT='3600'
```

## Security Best Practices

### For Administrators

1. **Use Strong Passwords**
   - Minimum 12 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Use password manager

2. **Protect Token Links**
   - Share token links securely (not via email if possible)
   - Tokens expire after 1 hour
   - Generate new tokens if compromised

3. **Monitor Logs**
   - Check error logs regularly for failed login attempts
   - Review token generation audit trail
   - Investigate suspicious patterns

4. **Keep Software Updated**
   - Regularly update Django and dependencies
   - Monitor security advisories
   - Apply security patches promptly

5. **Backup Regularly**
   - Automated daily backups
   - Store backups securely
   - Test restoration procedures

### For Deployment

1. **Never Commit Secrets**
   - Use environment variables
   - Add .env files to .gitignore
   - Rotate secrets if accidentally committed

2. **Use HTTPS Everywhere**
   - Force HTTPS redirects
   - Use HSTS headers
   - Verify SSL certificate validity

3. **Minimal Permissions**
   - Database user should have minimum required permissions
   - File system permissions should be restrictive
   - Run application as non-root user

4. **Network Security**
   - Use firewalls to restrict access
   - Whitelist IP addresses if possible
   - Use VPN for administrative access

## Incident Response

### If a Security Issue is Discovered

1. **Immediate Actions**
   - Document the issue with details
   - Assess the scope and impact
   - Isolate affected systems if necessary

2. **Containment**
   - Disable compromised accounts
   - Rotate all secrets (SECRET_KEY, passwords, tokens)
   - Review logs for unauthorized access

3. **Investigation**
   - Check authentication logs
   - Review database for unauthorized changes
   - Identify entry point and affected data

4. **Remediation**
   - Apply security patches
   - Fix vulnerabilities
   - Restore from backups if needed

5. **Prevention**
   - Update security documentation
   - Implement additional controls
   - Train users on lessons learned

## Security Audit Checklist

Run this checklist before production deployment and quarterly thereafter:

- [ ] All environment variables set correctly in WSGI
- [ ] DEBUG set to False in production
- [ ] Unique SECRET_KEY generated and set
- [ ] ALLOWED_HOSTS configured with actual domains only
- [ ] All HTTPS security settings enabled
- [ ] CSRF_TRUSTED_ORIGINS includes all domains with https://
- [ ] Admin accounts use strong passwords
- [ ] Inactive user accounts have been disabled
- [ ] All dependencies are up to date
- [ ] Backup system is functional and tested
- [ ] Logs are being collected and monitored
- [ ] Token links are shared securely
- [ ] Database credentials are secure and not default values
- [ ] No sensitive data in version control
- [ ] SSL certificate is valid and not expiring soon

## Reporting Security Issues

If you discover a security vulnerability, please:

1. **DO NOT** open a public GitHub issue
2. Contact the system administrator directly
3. Provide detailed information about the vulnerability
4. Allow reasonable time for fixes before disclosure

## References

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [PythonAnywhere Security](https://help.pythonanywhere.com/pages/security/)

## Last Updated

January 14, 2026

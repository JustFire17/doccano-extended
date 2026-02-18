# 🔒 Security Guidelines

## Reporting Security Issues

If you discover a security vulnerability, please **DO NOT** create a public issue. Instead:

1. Email us at: [your-email@example.com]
2. Include detailed information about the vulnerability
3. Allow us reasonable time to address the issue before public disclosure

We take security seriously and will respond promptly to all reports.

---

## Security Checklist Before Deployment

### ✅ Essential (Must Do)

- [ ] **Change default admin password** immediately after installation
- [ ] **Set strong `SECRET_KEY`** - Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- [ ] **Set `DEBUG=False`** in production
- [ ] **Configure `ALLOWED_HOSTS`** with your domain(s) only
- [ ] **Configure `CORS_ALLOWED_ORIGINS`** with your frontend URL(s) only
- [ ] **Enable HTTPS** and set `SESSION_COOKIE_SECURE=True` and `CSRF_COOKIE_SECURE=True`
- [ ] **Remove `.env` file from git** - Never commit secrets!
- [ ] **Use PostgreSQL** instead of SQLite for production
- [ ] **Set up regular database backups**

### ✅ Recommended

- [ ] **Enable HTTP Strict Transport Security (HSTS)**
- [ ] **Use strong database passwords** (16+ characters, mixed)
- [ ] **Configure proper file permissions** on server (700 for sensitive files)
- [ ] **Set up firewall rules** (only allow ports 80, 443, and SSH)
- [ ] **Enable security headers** in Nginx/Apache
- [ ] **Implement rate limiting** for API endpoints
- [ ] **Use environment-based configuration** (separate dev/staging/prod)
- [ ] **Keep dependencies updated** (`poetry update`, `npm update`)
- [ ] **Enable logging and monitoring**
- [ ] **Set up automated security scanning** (e.g., Dependabot)

### ✅ Advanced

- [ ] **Implement Two-Factor Authentication (2FA)**
- [ ] **Use a Web Application Firewall (WAF)**
- [ ] **Set up intrusion detection**
- [ ] **Encrypt sensitive data at rest**
- [ ] **Implement audit logging**
- [ ] **Use a secrets management service** (AWS Secrets Manager, HashiCorp Vault)
- [ ] **Conduct regular security audits**
- [ ] **Set up automated backups with encryption**

---

## Environment Variables Security

### Never Commit These to Git

```bash
SECRET_KEY=...
DATABASE_URL=...
ADMIN_PASSWORD=...
EMAIL_HOST_PASSWORD=...
AWS_SECRET_ACCESS_KEY=...
OAUTH_*_SECRET=...
```

### How to Generate Secure Keys

```bash
# Django SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Random password
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use OpenSSL
openssl rand -base64 32
```

---

## Password Policy Recommendations

### For Admin Accounts
- Minimum 16 characters
- Mix of uppercase, lowercase, numbers, symbols
- Avoid common words or patterns
- Change every 90 days
- Don't reuse passwords

### For User Accounts
- Minimum 12 characters
- Enforce complexity requirements
- Implement password history (prevent reuse)
- Offer 2FA option

---

## Database Security

### PostgreSQL Configuration

```sql
-- Create user with limited privileges
CREATE USER doccano_app WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE doccano TO doccano_app;
GRANT USAGE ON SCHEMA public TO doccano_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO doccano_app;

-- Don't use superuser for application
```

### Connection Security
```bash
# Use SSL for database connections
DATABASE_URL=postgres://user:pass@host:5432/dbname?sslmode=require

# Restrict database access by IP
# Edit pg_hba.conf to allow only application server
```

---

## Web Server Security Headers

### Nginx Configuration

```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# Hide nginx version
server_tokens off;

# Disable unwanted HTTP methods
if ($request_method !~ ^(GET|HEAD|POST|PUT|PATCH|DELETE|OPTIONS)$ ) {
    return 405;
}
```

---

## HTTPS Configuration

### Let's Encrypt (Free SSL)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal (cron)
0 0 * * * certbot renew --quiet
```

### SSL Best Practices

```nginx
# Use modern TLS protocols only
ssl_protocols TLSv1.2 TLSv1.3;

# Use strong ciphers
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers on;

# OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
```

---

## Application Security

### Django Security Settings

```python
# Production settings
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']

# Security middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    ...
]

# Cookie security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Input Validation

- All user inputs are validated through Django forms and serializers
- SQL injection prevented by using Django ORM
- XSS prevention through template auto-escaping
- CSRF protection enabled by default

### File Upload Security

```python
# Limit file sizes
MAX_UPLOAD_SIZE = 1073741824  # 1GB

# Validate file types
ENABLE_FILE_TYPE_CHECK = True

# Store uploads outside web root
MEDIA_ROOT = '/var/app/media'  # Not in public directory
```

---

## API Security

### Authentication
- Token-based authentication required for all API endpoints
- Session authentication for web interface
- Optional: OAuth2 for SSO integration

### Rate Limiting

```python
# Install: pip install django-ratelimit
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h')
def api_view(request):
    ...
```

### API Best Practices
- Use HTTPS for all API requests
- Implement proper authorization checks
- Sanitize error messages (don't leak sensitive info)
- Log all API access for audit trails

---

## Monitoring & Logging

### What to Log

```python
import logging
logger = logging.getLogger(__name__)

# Security events
- Failed login attempts
- Permission denied errors
- Suspicious activities
- Configuration changes
- File uploads
- Data exports

# Don't log
- Passwords
- Tokens
- Session IDs
- Personal data (GDPR compliance)
```

### Recommended Tools
- **Sentry** - Error tracking
- **Prometheus** - Metrics monitoring
- **Grafana** - Visualization
- **ELK Stack** - Log aggregation

---

## Backup & Disaster Recovery

### Backup Strategy

```bash
# Daily database backups
0 2 * * * /usr/local/bin/backup_database.sh

# Weekly media backups
0 3 * * 0 /usr/local/bin/backup_media.sh

# Store backups off-site (AWS S3, etc.)
```

### Backup Script Example

```bash
#!/bin/bash
# backup_database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="doccano"

# Dump database
pg_dump $DB_NAME > "$BACKUP_DIR/db_$DATE.sql"

# Compress
gzip "$BACKUP_DIR/db_$DATE.sql"

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/db_$DATE.sql.gz" s3://your-bucket/backups/

# Delete old backups (keep 30 days)
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
```

---

## Compliance

### GDPR Considerations

If processing EU citizens' data:
- Implement data export functionality
- Provide data deletion capabilities
- Log consent for data processing
- Encrypt personal data
- Implement "right to be forgotten"
- Keep data processing records

### Data Retention

```python
# Configure data retention policies
from datetime import timedelta

# Delete old audit logs
AUDIT_LOG_RETENTION = timedelta(days=90)

# Anonymize old annotations
ANNOTATION_RETENTION = timedelta(days=365)
```

---

## Incident Response

### If a Security Breach Occurs

1. **Immediate Actions**
   - Isolate affected systems
   - Change all passwords and tokens
   - Revoke compromised credentials
   - Enable maintenance mode

2. **Investigation**
   - Review logs for attack vector
   - Identify compromised data
   - Document timeline of events
   - Assess damage

3. **Remediation**
   - Patch vulnerabilities
   - Restore from clean backups if needed
   - Implement additional security measures
   - Update security policies

4. **Communication**
   - Notify affected users
   - Report to authorities if required (GDPR)
   - Document lessons learned
   - Update security procedures

---

## Security Updates

### Stay Updated

```bash
# Check for security updates
cd backend
poetry show --outdated

cd ../frontend
npm audit

# Update dependencies
poetry update
npm update
```

### Subscribe to Security Advisories
- Django security mailing list
- npm security advisories
- GitHub Dependabot alerts
- CVE databases

---

## Third-Party Dependencies

### Before Adding a Dependency

- Check package reputation and maintainers
- Review recent updates and activity
- Check for known vulnerabilities
- Evaluate alternatives
- Read the code if critical

### Tools for Security Scanning

```bash
# Python
pip install safety
safety check

# Node.js
npm audit
npm audit fix

# Docker
docker scan your-image:tag
```

---

## Contact

For security-related questions or to report vulnerabilities:
- Email: [security@yourdomain.com]
- PGP Key: [link to public key]

---

**Last Updated**: February 2026
**Review Schedule**: Quarterly

# Known Issues and Resolutions

This document tracks issues encountered during development and their resolutions.

## Python/Pip Issues

### Issue #1: Pip Cache Directory Permissions
**Date**: 2025-11-18
**Severity**: Low (Warning only)
**Description**:
```
WARNING: The directory '/root/.cache/pip' or its parent directory is not owned or is not writable by the current user.
```

**Impact**: Pip cache is disabled, which may slow down package installations but doesn't break functionality.

**Resolution**:
- For production, use a virtual environment: `python3 -m venv venv`
- If running as root, use `sudo -H pip install` to fix permissions
- Current workaround: Ignore warning as it doesn't affect functionality

**Status**: Documented - Not critical for development

---

## FastAPI Issues

### Issue #2: Trailing Slash Redirects (307)
**Date**: 2025-11-18
**Severity**: Low
**Description**:
API endpoints without trailing slashes return 307 Temporary Redirect.

**Impact**: curl/fetch requests need to follow redirects or include trailing slash.

**Resolution**:
- Always include trailing slash in API calls: `/api/v1/companies/`
- Or configure client to follow redirects automatically

**Status**: Documented - Expected FastAPI behavior

---

## Database Issues

*No issues reported*

---

## Frontend Issues

*Not yet implemented*

---

## Future Improvements

1. Add proper virtual environment setup instructions
2. Create Docker container for consistent environment
3. Add API client library with proper URL handling
4. Implement automated testing for all endpoints

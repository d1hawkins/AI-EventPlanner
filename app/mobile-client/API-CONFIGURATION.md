# API Configuration Guide

## 🌐 Connecting to Azure Backend

The mobile client is now configured to connect to the Azure-hosted backend services.

### Current Configuration

**Azure Backend URL**: `https://ai-event-planner-saas-py.azurewebsites.net/api`

This is configured via environment variables in the `.env` file.

---

## 📝 Environment Setup

### 1. Environment File

The `.env` file in the mobile-client directory contains:

```env
VITE_API_BASE_URL=https://ai-event-planner-saas-py.azurewebsites.net/api
```

### 2. API Client Configuration

The API client (`src/api/client.js`) automatically reads this environment variable:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
```

### 3. How It Works

1. **Environment Variable** - Vite loads `VITE_API_BASE_URL` from `.env`
2. **API Client** - Axios uses this as the base URL for all requests
3. **Interceptors** - Automatically add auth tokens and tenant IDs
4. **Error Handling** - Centralized error handling for all API calls

---

## 🔄 Switching Between Environments

### Use Azure Backend (Production)

Edit `.env`:
```env
VITE_API_BASE_URL=https://ai-event-planner-saas-py.azurewebsites.net/api
```

### Use Local Backend (Development)

Edit `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### Use Custom Backend

Edit `.env`:
```env
VITE_API_BASE_URL=https://your-custom-backend.com/api
```

**Important**: Restart the dev server after changing `.env`:
```bash
npm run dev
```

---

## 🔐 Authentication & Headers

### Automatic Headers

The API client automatically adds:

1. **Authorization**: `Bearer {token}` (from localStorage)
2. **X-Tenant-ID**: `{organizationId}` (from localStorage)
3. **Content-Type**: `application/json`

### Token Storage

- **authToken** - JWT authentication token
- **organizationId** - Tenant ID for multi-tenant support
- **user** - User profile data

### How Authentication Works

```
1. User logs in → receives JWT token
2. Token saved to localStorage.authToken
3. API client reads token from localStorage
4. Token added to Authorization header automatically
5. All API requests include the token
6. On 401 error → clear storage and redirect to login
```

---

## 📡 API Endpoints

All endpoints are relative to the base URL. Examples:

### Events
```
GET    /events           - List all events
GET    /events/:id       - Get event details
POST   /events           - Create new event
PUT    /events/:id       - Update event
DELETE /events/:id       - Delete event
```

### Dashboard
```
GET    /dashboard/stats            - Get statistics
GET    /dashboard/activity         - Get recent activity
GET    /dashboard/upcoming-events  - Get upcoming events
```

### Team
```
GET    /team/members          - List team members
POST   /team/invite           - Invite new member
PUT    /team/members/:id/role - Update member role
DELETE /team/members/:id      - Remove member
GET    /team/invites          - List pending invites
```

### Subscription
```
GET    /subscription                 - Get current subscription
GET    /subscription/usage           - Get usage metrics
GET    /subscription/billing-history - Get billing history
GET    /subscription/plans           - List available plans
POST   /subscription/upgrade         - Upgrade plan
POST   /subscription/downgrade       - Downgrade plan
DELETE /subscription                 - Cancel subscription
```

---

## 🛠️ Development Tools

### API Request Logging

In development mode, all API requests and responses are logged to the console:

```
🔗 API Base URL: https://ai-event-planner-saas-py.azurewebsites.net/api
[API Request] GET /events
[API Response] GET /events {...data}
```

### Error Logging

Detailed error information is logged in development:

```
[API Error] 404 Resource not found
[API Error] 401 Unauthorized
[API Error] 500 Server error
```

### Disable Logging in Production

Set in environment:
```env
VITE_ENV=production
```

The API client checks `import.meta.env.DEV` and only logs in development mode.

---

## 🚨 Troubleshooting

### Problem: API requests failing

**Check:**
1. Is the backend URL correct in `.env`?
2. Is the Azure backend running? Test: `curl https://ai-event-planner-saas-py.azurewebsites.net/health`
3. Did you restart the dev server after changing `.env`?
4. Are CORS headers configured on the backend?

### Problem: 401 Unauthorized errors

**Check:**
1. Is the user logged in?
2. Is the auth token in localStorage? (Check dev tools → Application → Local Storage)
3. Has the token expired?
4. Is the token format correct? (`Bearer {token}`)

### Problem: CORS errors

**Solution:**
The backend must allow requests from your frontend origin. Check Azure App Service CORS settings:

```bash
az webapp cors add \
  --resource-group ai-event-planner-rg \
  --name ai-event-planner-saas-py \
  --allowed-origins "http://localhost:5173" "https://your-frontend-domain.com"
```

### Problem: 404 Not Found on API routes

**Check:**
1. Is the endpoint path correct?
2. Is the base URL correct? (should end with `/api`)
3. Is the backend deployed correctly?

---

## ✅ Verification

To verify the configuration is working:

1. **Start the dev server:**
   ```bash
   npm run dev
   ```

2. **Check the console:**
   You should see:
   ```
   🔗 API Base URL: https://ai-event-planner-saas-py.azurewebsites.net/api
   ```

3. **Open the app:**
   Navigate to `http://localhost:5173`

4. **Check Network tab:**
   - Open DevTools → Network
   - Interact with the app
   - You should see requests going to the Azure backend

5. **Test an API call:**
   ```javascript
   // In browser console
   fetch('https://ai-event-planner-saas-py.azurewebsites.net/api/health')
     .then(r => r.json())
     .then(console.log)
   ```

---

## 🔒 Security Notes

1. **Never commit `.env` files** - Already excluded in `.gitignore`
2. **Use HTTPS in production** - Azure provides this automatically
3. **Rotate tokens regularly** - Implement token refresh
4. **Validate tokens on backend** - Don't trust client-side validation
5. **Use environment-specific configs** - Different .env for dev/staging/prod

---

## 📚 Related Documentation

- [Phase 1 Implementation Plan](../../docs/PHASE-1-IMPLEMENTATION-PLAN.md)
- [Deployment Readiness](../../docs/DEPLOYMENT-READINESS.md)
- [Azure Deployment Workflow](../../.github/workflows/azure-deploy.yml)

---

**Last Updated**: 2024-12-05
**Status**: ✅ Configured and Ready
**Backend**: Azure App Service (ai-event-planner-saas-py)

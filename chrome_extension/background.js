/**
 * Background service worker for Chrome extension
 * Handles authentication and API communication
 */

class GoogleAdsAIAssistant {
    constructor() {
        this.API_BASE = 'https://your-api-domain.com/api/v1';
        this.currentUser = null;
    }

    async authenticateUser() {
        try {
            // Use Chrome Identity API for OAuth
            const authResult = await chrome.identity.getAuthToken({
                interactive: true,
                scopes: [
                    'https://www.googleapis.com/auth/adwords',
                    'openid',
                    'email',
                    'profile'
                ]
            });

            if (authResult.token) {
                // Get user info from Google
                const userInfo = await this.getUserInfo(authResult.token);
                
                // Authenticate with backend
                const backendAuth = await this.authenticateWithBackend(authResult.token, userInfo);
                
                // Store session data
                await chrome.storage.local.set({
                    'userToken': authResult.token,
                    'backendSession': backendAuth.session_id,
                    'userInfo': userInfo,
                    'googleAdsAccounts': backendAuth.google_ads_accounts || []
                });

                this.currentUser = userInfo;
                return true;
            }
        } catch (error) {
            console.error('Authentication failed:', error);
            return false;
        }
    }

    async getUserInfo(token) {
        const response = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return await response.json();
    }

    async authenticateWithBackend(googleToken, userInfo) {
        const response = await fetch(`${this.API_BASE}/auth/chrome-extension`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${googleToken}`
            },
            body: JSON.stringify({
                userInfo: userInfo,
                extensionId: chrome.runtime.id
            })
        });

        if (!response.ok) {
            throw new Error('Backend authentication failed');
        }

        return await response.json();
    }

    async callAPI(endpoint, method = 'GET', data = null) {
        const storage = await chrome.storage.local.get(['userToken', 'backendSession']);
        
        const response = await fetch(`${this.API_BASE}${endpoint}`, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${storage.userToken}`,
                'X-Session-ID': storage.backendSession
            },
            body: data ? JSON.stringify(data) : null
        });

        return await response.json();
    }
}

// Initialize service
const assistant = new GoogleAdsAIAssistant();

// Message listener for content script communication
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'authenticate') {
        assistant.authenticateUser().then(sendResponse);
        return true; // Keep message channel open
    }
    
    if (request.action === 'callAI') {
        assistant.callAPI('/agents/contextual-assist', 'POST', {
            message: request.message,
            context: request.context
        }).then(sendResponse);
        return true;
    }
});
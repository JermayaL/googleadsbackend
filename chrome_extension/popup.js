/**
 * Popup functionality for Chrome extension
 */

class PopupManager {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    async init() {
        // Check if user is already authenticated
        const storage = await chrome.storage.local.get(['userInfo', 'userToken']);
        
        if (storage.userInfo && storage.userToken) {
            this.showMainSection(storage.userInfo);
            await this.loadUserStats();
        } else {
            this.showAuthSection();
        }
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Login button
        document.getElementById('login-btn').addEventListener('click', async () => {
            await this.handleLogin();
        });

        // Logout button
        document.getElementById('logout-btn').addEventListener('click', async () => {
            await this.handleLogout();
        });

        // Action buttons
        document.getElementById('analyze-page-btn').addEventListener('click', async () => {
            await this.analyzePage();
        });

        document.getElementById('open-chat-btn').addEventListener('click', () => {
            this.openChat();
        });

        document.getElementById('quick-optimize-btn').addEventListener('click', async () => {
            await this.quickOptimize();
        });
    }

    showAuthSection() {
        document.getElementById('auth-section').classList.remove('hidden');
        document.getElementById('main-section').classList.add('hidden');
        document.getElementById('loading-section').classList.add('hidden');
    }

    showMainSection(userInfo) {
        document.getElementById('auth-section').classList.add('hidden');
        document.getElementById('main-section').classList.remove('hidden');
        document.getElementById('loading-section').classList.add('hidden');

        // Update user info
        document.getElementById('user-name').textContent = userInfo.name || 'User';
        document.getElementById('user-email').textContent = userInfo.email || '';
        
        if (userInfo.picture) {
            document.getElementById('user-avatar').src = userInfo.picture;
        }
    }

    showLoadingSection() {
        document.getElementById('auth-section').classList.add('hidden');
        document.getElementById('main-section').classList.add('hidden');
        document.getElementById('loading-section').classList.remove('hidden');
    }

    async handleLogin() {
        try {
            this.showLoadingSection();
            
            const success = await chrome.runtime.sendMessage({
                action: 'authenticate'
            });

            if (success) {
                const storage = await chrome.storage.local.get(['userInfo']);
                this.showMainSection(storage.userInfo);
                await this.loadUserStats();
            } else {
                this.showAuthSection();
                this.showError('Authentication failed. Please try again.');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showAuthSection();
            this.showError('Authentication failed. Please try again.');
        }
    }

    async handleLogout() {
        try {
            await chrome.storage.local.clear();
            this.showAuthSection();
        } catch (error) {
            console.error('Logout error:', error);
        }
    }

    async loadUserStats() {
        try {
            const response = await chrome.runtime.sendMessage({
                action: 'callAPI',
                endpoint: '/users/usage',
                method: 'GET'
            });

            if (response.api_calls !== undefined) {
                document.getElementById('ai-generations').textContent = response.ai_generations || 0;
            }

            // Load connected accounts
            const accountsResponse = await chrome.runtime.sendMessage({
                action: 'callAPI',
                endpoint: '/google-ads/accounts',
                method: 'GET'
            });

            if (accountsResponse.accounts) {
                document.getElementById('accounts-count').textContent = accountsResponse.accounts.length;
            }

        } catch (error) {
            console.error('Error loading user stats:', error);
        }
    }

    async analyzePage() {
        try {
            // Get current tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (!tab.url.includes('ads.google.com')) {
                this.showError('Please navigate to Google Ads to use this feature.');
                return;
            }

            this.showLoadingSection();

            // Send message to content script to analyze page
            const response = await chrome.tabs.sendMessage(tab.id, {
                action: 'analyzePage'
            });

            this.showMainSection(this.currentUser);
            
            if (response && response.suggestions) {
                this.updateSuggestions(response.suggestions);
            }

        } catch (error) {
            console.error('Error analyzing page:', error);
            this.showError('Failed to analyze page. Make sure you\'re on a Google Ads page.');
            this.showMainSection(this.currentUser);
        }
    }

    openChat() {
        // Send message to content script to open chat
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            chrome.tabs.sendMessage(tabs[0].id, {
                action: 'openChat'
            });
            window.close(); // Close popup
        });
    }

    async quickOptimize() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (!tab.url.includes('ads.google.com')) {
                this.showError('Please navigate to Google Ads to use this feature.');
                return;
            }

            this.showLoadingSection();

            // Send quick optimize request
            const response = await chrome.tabs.sendMessage(tab.id, {
                action: 'quickOptimize'
            });

            this.showMainSection(this.currentUser);
            
            if (response && response.optimizations) {
                this.showOptimizations(response.optimizations);
            }

        } catch (error) {
            console.error('Error during quick optimize:', error);
            this.showError('Failed to optimize. Please try again.');
            this.showMainSection(this.currentUser);
        }
    }

    updateSuggestions(suggestions) {
        const suggestionsList = document.getElementById('suggestions-list');
        suggestionsList.innerHTML = '';

        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.innerHTML = `
                <span class="suggestion-text">${suggestion}</span>
                <button class="apply-btn" onclick="this.applySuggestion('${suggestion}')">Apply</button>
            `;
            suggestionsList.appendChild(item);
        });
    }

    showOptimizations(optimizations) {
        // Show optimization results (simplified)
        const suggestionsList = document.getElementById('suggestions-list');
        suggestionsList.innerHTML = `
            <div class="optimization-result">
                <h4>✅ Quick Optimization Complete</h4>
                <p>${optimizations.summary || 'Optimizations applied successfully'}</p>
            </div>
        `;
    }

    showError(message) {
        // Simple error display (in a real app, you'd want better error handling)
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);

        setTimeout(() => {
            errorDiv.remove();
        }, 3000);
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PopupManager();
});
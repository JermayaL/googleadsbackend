/**
 * Content script that injects AI assistant into Google Ads pages
 */

class GoogleAdsPageAssistant {
    constructor() {
        this.init();
    }

    async init() {
        if (this.isGoogleAdsPage()) {
            await this.injectAIAssistant();
            await this.setupEventListeners();
        }
    }

    isGoogleAdsPage() {
        return window.location.hostname === 'ads.google.com';
    }

    async injectAIAssistant() {
        // Create floating AI assistant widget
        const aiWidget = document.createElement('div');
        aiWidget.id = 'google-ads-ai-assistant';
        aiWidget.innerHTML = `
            <div class="ai-assistant-container">
                <div class="ai-header">
                    <h3>🤖 AI Assistant</h3>
                    <button id="ai-toggle">💬</button>
                </div>
                <div class="ai-chat" id="ai-chat" style="display: none;">
                    <div class="ai-messages" id="ai-messages"></div>
                    <div class="ai-suggestions" id="ai-suggestions"></div>
                    <div class="ai-input-container">
                        <input type="text" id="ai-input" placeholder="Ask AI about this campaign...">
                        <button id="ai-send">Send</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(aiWidget);
        
        // Show contextual suggestions
        await this.showContextualSuggestions();
    }

    async setupEventListeners() {
        document.getElementById('ai-toggle').addEventListener('click', () => {
            const chat = document.getElementById('ai-chat');
            chat.style.display = chat.style.display === 'none' ? 'block' : 'none';
        });

        document.getElementById('ai-send').addEventListener('click', () => {
            this.handleUserMessage();
        });

        document.getElementById('ai-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleUserMessage();
            }
        });
    }

    async handleUserMessage() {
        const input = document.getElementById('ai-input');
        const message = input.value.trim();
        if (!message) return;

        input.value = '';
        this.addMessageToChat('user', message);

        // Get current page context
        const context = this.extractPageContext();

        // Send to backend AI
        try {
            const response = await chrome.runtime.sendMessage({
                action: 'callAI',
                message: message,
                context: context
            });

            this.addMessageToChat('ai', response.response || 'Sorry, I encountered an error.');
        } catch (error) {
            this.addMessageToChat('ai', 'Sorry, I encountered an error. Please try again.');
        }
    }

    extractPageContext() {
        const url = window.location.href;
        const context = {
            page_type: this.detectPageType(url),
            account_id: this.extractAccountId(url),
            campaign_id: this.extractCampaignId(url),
            current_data: this.scrapeCurrentPageData()
        };

        return context;
    }

    detectPageType(url) {
        if (url.includes('/campaigns')) return 'campaigns';
        if (url.includes('/keywords')) return 'keywords';
        if (url.includes('/ads')) return 'ads';
        if (url.includes('/extensions')) return 'extensions';
        return 'overview';
    }

    extractAccountId(url) {
        const match = url.match(/\/accounts\/(\d+)/);
        return match ? match[1] : null;
    }

    extractCampaignId(url) {
        const match = url.match(/\/campaigns\/(\d+)/);
        return match ? match[1] : null;
    }

    scrapeCurrentPageData() {
        const data = {};
        
        // Extract campaign name
        const campaignElement = document.querySelector('[data-test-id*="campaign"]');
        if (campaignElement) {
            data.campaign_name = campaignElement.textContent?.trim();
        }

        // Extract performance metrics
        const metricElements = document.querySelectorAll('[data-test-id*="metric"]');
        metricElements.forEach(element => {
            const label = element.querySelector('.label')?.textContent;
            const value = element.querySelector('.value')?.textContent;
            if (label && value) {
                data[label.toLowerCase().replace(/\s+/g, '_')] = value;
            }
        });

        return data;
    }

    async showContextualSuggestions() {
        const context = this.extractPageContext();
        
        // Get AI suggestions based on current page
        try {
            const response = await chrome.runtime.sendMessage({
                action: 'callAI',
                message: 'Analyze this page and provide optimization suggestions',
                context: context
            });

            const suggestionsContainer = document.getElementById('ai-suggestions');
            if (response.suggestions) {
                suggestionsContainer.innerHTML = `
                    <div class="suggestions-title">💡 AI Suggestions:</div>
                    ${response.suggestions.map(s => `<div class="suggestion">${s}</div>`).join('')}
                `;
            }
        } catch (error) {
            console.error('Failed to get suggestions:', error);
        }
    }

    addMessageToChat(sender, message) {
        const messagesContainer = document.getElementById('ai-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `ai-message ai-message-${sender}`;
        messageDiv.textContent = message;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new GoogleAdsPageAssistant();
    });
} else {
    new GoogleAdsPageAssistant();
}
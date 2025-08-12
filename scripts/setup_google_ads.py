"""
Google Ads API setup script
"""

import os
from google.ads.googleads.client import GoogleAdsClient

def setup_google_ads_credentials():
    """Setup Google Ads API credentials"""
    
    print("Google Ads API Setup:")
    print("1. Apply for Google Ads API access: https://developers.google.com/google-ads/api/docs/first-call/dev-token")
    print("2. Create OAuth2 credentials in Google Cloud Console")
    print("3. Get your developer token")
    print("4. Generate refresh token")
    
    config_template = """
# Google Ads API Configuration Template
[GOOGLE_ADS]
developer_token = YOUR_DEVELOPER_TOKEN
client_id = YOUR_CLIENT_ID.apps.googleusercontent.com
client_secret = YOUR_CLIENT_SECRET
refresh_token = YOUR_REFRESH_TOKEN
login_customer_id = YOUR_MCC_CUSTOMER_ID (optional)
use_proto_plus = True
"""
    
    print("\nConfiguration template:")
    print(config_template)

def generate_refresh_token():
    """Generate refresh token for Google Ads API"""
    
    script = """
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow

def get_refresh_token():
    # OAuth 2.0 configuration
    client_config = {
        "web": {
            "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
            "client_secret": "YOUR_CLIENT_SECRET",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/callback"]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=["https://www.googleapis.com/auth/adwords"]
    )
    flow.redirect_uri = "http://localhost:8080/callback"
    
    # Get authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')
    print(f"Visit this URL to authorize: {auth_url}")
    
    # Get authorization code from user
    auth_code = input("Enter the authorization code: ")
    
    # Exchange code for tokens
    flow.fetch_token(code=auth_code)
    
    credentials = flow.credentials
    print(f"Refresh token: {credentials.refresh_token}")

if __name__ == "__main__":
    get_refresh_token()
"""
    
    print("Refresh token generation script:")
    print(script)

def test_google_ads_connection():
    """Test Google Ads API connection"""
    
    try:
        # This would test the actual connection
        # For now, just show what to test
        
        test_script = """
from google.ads.googleads.client import GoogleAdsClient

def test_connection():
    client = GoogleAdsClient.load_from_env()
    
    # Test getting accessible customers
    customer_service = client.get_service("CustomerService")
    accessible_customers = customer_service.list_accessible_customers()
    
    print("Accessible customers:")
    for customer in accessible_customers.results:
        print(f"  - {customer.resource_name}")
    
    # Test basic query
    if accessible_customers.results:
        customer_id = accessible_customers.results[0].resource_name.split('/')[-1]
        
        ga_service = client.get_service("GoogleAdsService")
        query = '''
            SELECT campaign.id, campaign.name
            FROM campaign
            LIMIT 5
        '''
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        print(f"\\nCampaigns for customer {customer_id}:")
        for row in response:
            print(f"  - {row.campaign.name} (ID: {row.campaign.id})")

if __name__ == "__main__":
    test_connection()
"""
        
        print("Connection test script:")
        print(test_script)
        
    except Exception as e:
        print(f"Error in connection test: {e}")

if __name__ == "__main__":
    print("🔗 Google Ads API Setup Script")
    print("=" * 50)
    
    setup_google_ads_credentials()
    print("\n" + "=" * 50)
    
    generate_refresh_token()
    print("\n" + "=" * 50)
    
    test_google_ads_connection()
    print("\n✅ Google Ads setup complete!")
"""
Deployment script for Google Cloud Run
"""

import os
import subprocess
import json

def build_and_deploy():
    """Build and deploy to Google Cloud Run"""
    
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
    
    service_name = "google-ads-ai-api"
    region = "us-central1"
    
    print(f"🚀 Deploying {service_name} to Google Cloud Run...")
    
    # Build container
    print("📦 Building container...")
    build_cmd = [
        "gcloud", "builds", "submit",
        "--tag", f"gcr.io/{project_id}/{service_name}",
        "."
    ]
    
    result = subprocess.run(build_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Build failed: {result.stderr}")
    
    print("✅ Container built successfully")
    
    # Deploy to Cloud Run
    print("🚀 Deploying to Cloud Run...")
    deploy_cmd = [
        "gcloud", "run", "deploy", service_name,
        "--image", f"gcr.io/{project_id}/{service_name}",
        "--platform", "managed",
        "--region", region,
        "--allow-unauthenticated",
        "--memory", "1Gi",
        "--cpu", "1",
        "--max-instances", "100",
        "--set-env-vars", f"GOOGLE_CLOUD_PROJECT={project_id}"
    ]
    
    result = subprocess.run(deploy_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Deployment failed: {result.stderr}")
    
    print("✅ Deployed to Cloud Run successfully")
    
    # Get service URL
    url_cmd = [
        "gcloud", "run", "services", "describe", service_name,
        "--platform", "managed",
        "--region", region,
        "--format", "value(status.url)"
    ]
    
    result = subprocess.run(url_cmd, capture_output=True, text=True)
    service_url = result.stdout.strip()
    
    print(f"🌐 Service URL: {service_url}")
    print(f"📖 API Docs: {service_url}/docs")
    
    return service_url

def setup_custom_domain():
    """Setup custom domain for Cloud Run service"""
    
    print("🌐 Custom Domain Setup:")
    print("1. Add your domain to Cloud Run")
    print("2. Verify domain ownership")
    print("3. Map domain to service")
    print("4. Update DNS records")
    
    commands = [
        "gcloud run domain-mappings create --service=google-ads-ai-api --domain=your-domain.com --region=us-central1",
        "gcloud run domain-mappings list"
    ]
    
    print("\nCommands to run:")
    for cmd in commands:
        print(f"  {cmd}")

def setup_https_certificate():
    """Setup SSL certificate"""
    
    print("🔒 SSL Certificate Setup:")
    print("Google Cloud Run automatically provides SSL certificates for mapped domains")
    print("Your API will be available at: https://your-domain.com")

if __name__ == "__main__":
    print("🚀 Google Ads AI System Deployment")
    print("=" * 50)
    
    try:
        service_url = build_and_deploy()
        print("\n" + "=" * 50)
        
        setup_custom_domain()
        print("\n" + "=" * 50)
        
        setup_https_certificate()
        print("\n✅ Deployment complete!")
        
        print(f"\n🎉 Your Google Ads AI System is live at: {service_url}")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
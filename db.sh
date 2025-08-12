#!/bin/bash

# Fix Remaining Issues - App Engine and Project Configuration
# The Firestore database was created successfully!

PROJECT_ID="lateral-layout-465711-e1"
REGION="us-central1"

echo "🔧 Fixing Remaining GCP Issues"
echo "=============================="
echo "Project: $PROJECT_ID"
echo

# Step 1: Fix project configuration issue
echo "1. Fixing project configuration..."
echo "Current project configuration:"
gcloud config list project

echo
echo "Setting correct project..."
gcloud config set project "$PROJECT_ID"

echo
echo "Verifying project is set correctly:"
gcloud config get-value project

echo
echo "Checking if you have access to the correct project:"
gcloud projects describe "$PROJECT_ID"

echo
# Step 2: Enable App Engine Admin API for the correct project
echo "2. Enabling App Engine Admin API..."
gcloud services enable appengine.googleapis.com --project="$PROJECT_ID"

echo
# Step 3: Try creating App Engine again
echo "3. Creating App Engine application..."
echo "This may take 2-5 minutes..."
gcloud app create --region="$REGION" --quiet --project="$PROJECT_ID"

echo
# Step 4: Verify everything is working
echo "4. Verifying setup..."

echo "Checking App Engine:"
if gcloud app describe --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "✅ App Engine is now accessible"
else
    echo "❌ App Engine still not accessible"
fi

echo
echo "Checking Firestore:"
if gcloud firestore databases describe --database="(default)" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "✅ Firestore is accessible"
else
    echo "❌ Firestore not accessible"
fi

echo
echo "Checking service account:"
SA_EMAIL="google-ads-ai-backend@$PROJECT_ID.iam.gserviceaccount.com"
if gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "✅ Service account exists"
else
    echo "❌ Service account not found"
fi

echo
echo "Checking service account key file:"
if [ -f "firebase-service-account.json" ]; then
    echo "✅ Service account key file exists"
else
    echo "❌ Service account key file missing"
fi

echo
echo "5. Testing Firebase connection..."
echo "Running Python test script..."
python test_firebase.py

echo
echo "🎉 Setup verification complete!"
echo
echo "Next steps:"
echo "1. If all tests passed, start your app: python main.py"
echo "2. Test health endpoint: curl http://localhost:8000/health"
echo "3. Open UI in browser: http://localhost:8000"
echo
echo "Console links:"
echo "• App Engine: https://console.cloud.google.com/appengine?project=$PROJECT_ID"
echo "• Firestore: https://console.cloud.google.com/firestore/databases?project=$PROJECT_ID"
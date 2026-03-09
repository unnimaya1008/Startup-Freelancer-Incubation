# accounts/supabase_helper.py

import os
from datetime import datetime
from supabase import create_client
from django.conf import settings

def get_supabase_client():
    """Create and return Supabase client"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def upload_to_supabase(file, folder="uploads"):
    try:
        supabase = get_supabase_client()
        # Generate unique filename with timestamp
        filename = f"{folder}/{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.name}"

        # Upload file to Supabase bucket
        result = supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
            filename,
            file.read(),
            filetype=file.content_type  # ✅ include MIME type
        )

        # Check for errors
        if isinstance(result, dict) and result.get('error'):
            print(f"❌ Supabase Upload Failed: {result['error']}")
            return None

        # Get public URL
        public_url_data = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(filename)
        public_url = public_url_data.get('publicURL')
        print("Uploaded file URL:", public_url)


        if not public_url:
            print("⚠️ Supabase Upload Warning: No public URL returned")
            return None

        print("✅ File uploaded successfully:", public_url)
        return public_url

    except Exception as e:
        print("🚨 Supabase Upload Exception:", e)
        return None

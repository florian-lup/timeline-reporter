"""Centralized configuration for Cloudflare R2 CDN storage system.

This module contains all settings and configuration data
related to Cloudflare R2 object storage and CDN.
"""

from .settings import (
    CLOUDFLARE_ACCOUNT_ID,
    CLOUDFLARE_R2_ACCESS_KEY,
    CLOUDFLARE_R2_BUCKET,
    CLOUDFLARE_R2_CUSTOM_DOMAIN,
    CLOUDFLARE_R2_SECRET_KEY,
)

# ---------------------------------------------------------------------------
# CDN Configuration
# ---------------------------------------------------------------------------
CDN_CACHE_CONTROL: str = "public, max-age=31536000"  # 1 year cache
CDN_ENABLE_COMPRESSION: bool = True

# ---------------------------------------------------------------------------
# File Storage Configuration
# ---------------------------------------------------------------------------
STORAGE_PATH_PREFIX: str = "podcasts"  # Prefix for all audio files in bucket
AUDIO_FILE_METADATA = {
    "generated-by": "timeline-reporter",
    "content-category": "podcast-audio",
}

# ---------------------------------------------------------------------------
# Content Type Mapping
# ---------------------------------------------------------------------------
AUDIO_CONTENT_TYPE_MAP = {
    "mp3": "audio/mpeg",
    "aac": "audio/aac", 
    "wav": "audio/wav",
    "ogg": "audio/ogg",
    "flac": "audio/flac",
    "opus": "audio/opus",
}

# Default content type fallback
DEFAULT_AUDIO_CONTENT_TYPE: str = "audio/mpeg"

# ---------------------------------------------------------------------------
# R2 Client Configuration
# ---------------------------------------------------------------------------
R2_ENDPOINT_URL_TEMPLATE: str = "https://{account_id}.r2.cloudflarestorage.com"
R2_CDN_URL_TEMPLATE: str = "https://{bucket_name}.{account_id}.r2.dev"
R2_SIGNATURE_VERSION: str = "s3v4"
R2_REGION: str = "auto" 
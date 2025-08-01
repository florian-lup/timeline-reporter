"""Cloudflare R2 client for CDN-powered audio storage."""

from __future__ import annotations

import uuid

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from config import (
    AUDIO_CONTENT_TYPE_MAP,
    AUDIO_FILE_METADATA,
    CDN_CACHE_CONTROL,
    CLOUDFLARE_ACCOUNT_ID,
    CLOUDFLARE_R2_ACCESS_KEY,
    CLOUDFLARE_R2_BUCKET,
    CLOUDFLARE_R2_CUSTOM_DOMAIN,
    CLOUDFLARE_R2_SECRET_KEY,
    DEFAULT_AUDIO_CONTENT_TYPE,
    R2_CDN_URL_TEMPLATE,
    R2_ENDPOINT_URL_TEMPLATE,
    R2_REGION,
    R2_SIGNATURE_VERSION,
    STORAGE_PATH_PREFIX,
)
from config.audio_config import AUDIO_FORMAT
from utils import logger


class CloudflareR2Client:
    """Client for uploading audio files to Cloudflare R2 with built-in CDN."""

    def __init__(
        self,
        account_id: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket_name: str | None = None,
    ):
        """Initialize R2 client using S3-compatible API.

        Args:
            account_id: Cloudflare account ID (defaults to config)
            access_key: R2 access key (defaults to config)
            secret_key: R2 secret key (defaults to config)
            bucket_name: R2 bucket name (defaults to config)
        """
        # Use provided values or fallback to configuration
        self.account_id = account_id or CLOUDFLARE_ACCOUNT_ID
        self.access_key = access_key or CLOUDFLARE_R2_ACCESS_KEY
        self.secret_key = secret_key or CLOUDFLARE_R2_SECRET_KEY
        self.bucket_name = bucket_name or CLOUDFLARE_R2_BUCKET

        if not all([self.account_id, self.access_key, self.secret_key]):
            raise ValueError(
                "Missing Cloudflare R2 credentials. Set environment variables:\n"
                "- CLOUDFLARE_ACCOUNT_ID\n"
                "- CLOUDFLARE_R2_ACCESS_KEY\n"
                "- CLOUDFLARE_R2_SECRET_KEY"
            )

        # Initialize S3-compatible client for R2
        endpoint_url = R2_ENDPOINT_URL_TEMPLATE.format(account_id=self.account_id)
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version=R2_SIGNATURE_VERSION),
            region_name=R2_REGION,
        )

        # CDN domain for public access - use custom domain if available
        if CLOUDFLARE_R2_CUSTOM_DOMAIN:
            self.cdn_domain = f"https://{CLOUDFLARE_R2_CUSTOM_DOMAIN}"
        else:
            self.cdn_domain = R2_CDN_URL_TEMPLATE.format(bucket_name=self.bucket_name, account_id=self.account_id)

        logger.info("✓ Cloudflare R2 client initialized: %s", self.bucket_name)

    def _get_content_type(self, audio_format: str) -> str:
        """Get the correct MIME content type for the audio format."""
        return AUDIO_CONTENT_TYPE_MAP.get(audio_format.lower(), DEFAULT_AUDIO_CONTENT_TYPE)

    def upload_audio(self, audio_bytes: bytes, podcast_id: str | None = None) -> str:
        """Upload audio file to R2 and return CDN URL.

        Args:
            audio_bytes: Raw audio file data
            podcast_id: Unique identifier for the podcast (auto-generated if None)

        Returns:
            CDN URL for the uploaded audio file
        """
        if podcast_id is None:
            podcast_id = str(uuid.uuid4())

        # Use the configured audio format for file extension and content type
        file_extension = AUDIO_FORMAT
        content_type = self._get_content_type(AUDIO_FORMAT)

        key = f"{STORAGE_PATH_PREFIX}/{podcast_id}.{file_extension}"

        # Prepare metadata combining config defaults with specific values
        metadata = AUDIO_FILE_METADATA.copy()
        metadata.update({"format": AUDIO_FORMAT, "podcast-id": podcast_id})

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=audio_bytes,
                ContentType=content_type,
                CacheControl=CDN_CACHE_CONTROL,
                Metadata=metadata,
            )

            cdn_url = f"{self.cdn_domain}/{key}"
            file_size_mb = len(audio_bytes) / (1024 * 1024)

            logger.info(
                "  ✓ Audio uploaded to R2 CDN: %.1f MB (%s format)",
                file_size_mb,
                AUDIO_FORMAT.upper(),
            )
            logger.info("  🔗 CDN URL: %s", cdn_url)

            return cdn_url

        except ClientError as e:
            logger.error("Failed to upload audio to R2: %s", e)
            raise RuntimeError(f"R2 upload failed: {e}") from e

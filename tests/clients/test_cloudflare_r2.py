"""Tests for the Cloudflare R2 client."""

from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from clients.cloudflare_r2 import CloudflareR2Client


@pytest.fixture
def mock_boto3_client():
    """Mock the boto3 client for testing."""
    with patch("clients.cloudflare_r2.boto3.client") as mock_client:
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        yield mock_s3


@pytest.fixture
def r2_client(mock_boto3_client):
    """Create a CloudflareR2Client instance with mocked dependencies."""
    return CloudflareR2Client(
        account_id="test-account",
        access_key="test-access-key",
        secret_key="test-secret-key",
        bucket_name="test-bucket",
    )


def test_init_with_credentials():
    """Test initialization with explicit credentials."""
    with patch("clients.cloudflare_r2.boto3.client") as mock_client:
        client = CloudflareR2Client(
            account_id="test-account",
            access_key="test-access-key",
            secret_key="test-secret-key",
            bucket_name="test-bucket",
        )

        assert client.account_id == "test-account"
        assert client.access_key == "test-access-key"
        assert client.secret_key == "test-secret-key"
        assert client.bucket_name == "test-bucket"

        # Verify boto3 client was initialized correctly
        mock_client.assert_called_once()


def test_init_missing_credentials():
    """Test initialization fails with missing credentials."""
    with (
        patch("clients.cloudflare_r2.CLOUDFLARE_ACCOUNT_ID", None),
        patch("clients.cloudflare_r2.CLOUDFLARE_R2_ACCESS_KEY", None),
        patch("clients.cloudflare_r2.CLOUDFLARE_R2_SECRET_KEY", None),
    ):
        with pytest.raises(ValueError) as excinfo:
            CloudflareR2Client()

        assert "Missing Cloudflare R2 credentials" in str(excinfo.value)


def test_init_with_custom_domain():
    """Test initialization with custom domain."""
    with (
        patch("clients.cloudflare_r2.boto3.client"),
        patch("clients.cloudflare_r2.CLOUDFLARE_R2_CUSTOM_DOMAIN", "custom.example.com"),
    ):
        client = CloudflareR2Client(
            account_id="test-account", access_key="test-access-key", secret_key="test-secret-key"
        )

        assert client.cdn_domain == "https://custom.example.com"


def test_init_without_custom_domain():
    """Test initialization without custom domain."""
    with (
        patch("clients.cloudflare_r2.boto3.client"),
        patch("clients.cloudflare_r2.CLOUDFLARE_R2_CUSTOM_DOMAIN", ""),
        patch(
            "clients.cloudflare_r2.R2_CDN_URL_TEMPLATE",
            "https://{bucket_name}.{account_id}.test-cdn.com",
        ),
    ):
        client = CloudflareR2Client(
            account_id="test-account",
            access_key="test-access-key",
            secret_key="test-secret-key",
            bucket_name="test-bucket",
        )

        assert client.cdn_domain == "https://test-bucket.test-account.test-cdn.com"


def test_get_content_type(r2_client):
    """Test the _get_content_type method."""
    with (
        patch(
            "clients.cloudflare_r2.AUDIO_CONTENT_TYPE_MAP",
            {"mp3": "audio/mpeg", "ogg": "audio/ogg"},
        ),
        patch("clients.cloudflare_r2.DEFAULT_AUDIO_CONTENT_TYPE", "audio/mpeg"),
    ):
        assert r2_client._get_content_type("mp3") == "audio/mpeg"
        assert r2_client._get_content_type("ogg") == "audio/ogg"
        assert r2_client._get_content_type("unknown") == "audio/mpeg"


def test_upload_audio_success(r2_client, mock_boto3_client):
    """Test successful audio upload."""
    # Mock the uuid
    test_uuid = "test-uuid-12345"
    with patch("uuid.uuid4", return_value=test_uuid):
        # Audio test data
        audio_bytes = b"test audio data"

        # Test the upload
        with (
            patch("clients.cloudflare_r2.STORAGE_PATH_PREFIX", "podcasts"),
            patch("clients.cloudflare_r2.AUDIO_FORMAT", "mp3"),
            patch("clients.cloudflare_r2.AUDIO_FILE_METADATA", {"test": "metadata"}),
            patch("clients.cloudflare_r2.CDN_CACHE_CONTROL", "max-age=3600"),
        ):
            cdn_url = r2_client.upload_audio(audio_bytes)

            # Verify the upload
            mock_boto3_client.put_object.assert_called_once()
            args = mock_boto3_client.put_object.call_args[1]
            assert args["Bucket"] == "test-bucket"
            assert args["Key"] == f"podcasts/{test_uuid}.mp3"
            assert args["Body"] == audio_bytes

            # Check the returned URL
            assert cdn_url == f"{r2_client.cdn_domain}/podcasts/{test_uuid}.mp3"


def test_upload_audio_with_podcast_id(r2_client, mock_boto3_client):
    """Test upload with specified podcast ID."""
    audio_bytes = b"test audio data"
    podcast_id = "custom-podcast-id"

    with (
        patch("clients.cloudflare_r2.STORAGE_PATH_PREFIX", "podcasts"),
        patch("clients.cloudflare_r2.AUDIO_FORMAT", "mp3"),
        patch("clients.cloudflare_r2.AUDIO_FILE_METADATA", {"test": "metadata"}),
        patch("clients.cloudflare_r2.CDN_CACHE_CONTROL", "max-age=3600"),
    ):
        cdn_url = r2_client.upload_audio(audio_bytes, podcast_id=podcast_id)

        # Verify the upload used the custom ID
        args = mock_boto3_client.put_object.call_args[1]
        assert args["Key"] == f"podcasts/{podcast_id}.mp3"
        assert cdn_url == f"{r2_client.cdn_domain}/podcasts/{podcast_id}.mp3"


def test_upload_audio_error(r2_client, mock_boto3_client):
    """Test error handling during upload."""
    # Set up the mock to raise an error
    error = ClientError(
        {"Error": {"Code": "TestError", "Message": "Test error message"}}, "put_object"
    )
    mock_boto3_client.put_object.side_effect = error

    # Test that the error is propagated correctly
    with pytest.raises(RuntimeError) as excinfo:
        r2_client.upload_audio(b"test audio data")

    assert "R2 upload failed" in str(excinfo.value)

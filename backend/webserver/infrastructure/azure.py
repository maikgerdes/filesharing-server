from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse
import os

from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
from django.core.files.uploadedfile import InMemoryUploadedFile
from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


@lru_cache(maxsize=1)
def _load_azure_config():
    load_dotenv(ENV_PATH, override=True)

    client_id = os.environ["AZURE_CLIENT_ID"]
    tenant_id = os.environ["AZURE_TENANT_ID"]
    client_secret = os.environ["AZURE_CLIENT_SECRET"]
    vault_url = os.environ["AZURE_VAULT_URL"]
    container_name = os.environ["AZURE_CONTAINER_NAME"]
    storage_account_url = os.environ["AZURE_STORAGE_URL"]

    parsed_vault_url = urlparse(vault_url)
    if parsed_vault_url.scheme != "https":
        raise ValueError(
            "AZURE_VAULT_URL must be an https URL for Key Vault authentication; "
            f"got: {vault_url!r}"
        )

    credentials = ClientSecretCredential(
        client_id=client_id,
        client_secret=client_secret,
        tenant_id=tenant_id,
    )

    return {
        "vault_url": vault_url,
        "container_name": container_name,
        "storage_account_url": storage_account_url,
        "credentials": credentials,
    }

def keyvault_conn():
    config = _load_azure_config()
    secret_name = "Maik"
    secret_client = SecretClient(vault_url=config["vault_url"], credential=config["credentials"])

    secret = secret_client.get_secret(secret_name)
    print("The secret value is :" + secret.value)


def upload_blob(file_path: InMemoryUploadedFile, blob_name: str) -> str:
    config = _load_azure_config()
    blob_service_client = BlobServiceClient(
        account_url=config["storage_account_url"],
        credential=config["credentials"],
    )
    blob_client = blob_service_client.get_blob_client(container=config["container_name"], blob=blob_name)
    if hasattr(file_path, "seek"):
        file_path.seek(0)
    blob_client.upload_blob(file_path, overwrite=True)
    return blob_client.url


if __name__ == "__main__":
    test_file_path = Path(__file__).resolve().parents[1] / "test.docx"
    with open(test_file_path, "rb") as file_handle:
        uploaded_file = InMemoryUploadedFile(
            file=file_handle,
            field_name="file",
            name=test_file_path.name,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size=test_file_path.stat().st_size,
            charset=None,
        )
        print(upload_blob(uploaded_file, test_file_path.name))

# Fetch the latest version of a secret from GCP Secret Manager.
# Returns a decoded string by default, or a parsed dict/list if as_json=True.


import json
from functools import lru_cache
from typing import Any

from google.cloud import secretmanager

from config import DEFAULT_GAE_PROJECT


@lru_cache(maxsize=1)
def _secretmanager_client() -> secretmanager.SecretManagerServiceClient:
    return secretmanager.SecretManagerServiceClient()


def fetch_secret(
    name: str,
    *,
    project: str = DEFAULT_GAE_PROJECT,
    as_json: bool = False,
) -> Any:

    client = _secretmanager_client()
    version_path = f"projects/{project}/secrets/{name}/versions/latest"
    raw = client.access_secret_version(name=version_path).payload.data.decode("UTF-8")
    return json.loads(raw) if as_json else raw
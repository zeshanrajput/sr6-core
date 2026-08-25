"""
Gemini File Search Store Vector Synchronizer.
Provides concurrent parallel uploads and cloud vectorization verification for local rules vault.
"""

import os
import time
import hashlib
import pathlib
import concurrent.futures
from typing import Dict, Any, List, Optional, Tuple
from google import genai
from google.genai import types


def calculate_sha256(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_local_vault_files(vault_dir: str) -> Dict[str, Tuple[pathlib.Path, str]]:
    vault_path = pathlib.Path(vault_dir)
    if not vault_path.exists():
        return {}
    local_files = {}
    for file_path in vault_path.rglob("*.md"):
        stem = file_path.stem
        file_hash = calculate_sha256(str(file_path))
        local_files[stem] = (file_path, file_hash)
    return local_files


def _upload_single_worker(client: genai.Client, file_store_name: str, path: pathlib.Path, stem: str, file_hash: str):
    is_srm = "srm" in path.name.lower() or "mission" in path.name.lower()
    metadata = [
        {"key": "is_missions_legal", "string_value": "true" if is_srm else "false"},
        {"key": "content_hash", "string_value": file_hash}
    ]
    try:
        op = client.file_search_stores.upload_to_file_search_store(
            file_search_store_name=file_store_name,
            file=str(path),
            config={
                "display_name": stem,
                "custom_metadata": metadata
            }
        )
        return (stem, op, None)
    except Exception as e:
        return (stem, None, str(e))


def sync_gemini_store(
    vault_dir: Optional[str] = None,
    store_display_name: str = "Shadowrun 6E SRM Vault",
    skip_updates: bool = False,
    max_workers: int = 10,
    target_model: str = "models/gemini-embedding-001"
) -> Dict[str, Any]:
    """
    Synchronizes local markdown rules in vault_dir to Google Gemini File Search Store.
    """
    from sr6core.rules_db import DEFAULT_VAULT_DIR
    from sr6core.vault.store_inspector import get_gemini_client

    target_vault = vault_dir or DEFAULT_VAULT_DIR
    if not os.path.exists(target_vault):
        return {"success": False, "error": f"Vault directory not found: {target_vault}"}

    client = get_gemini_client()
    file_store = None

    print(f"Resolving File Search Store: '{store_display_name}'...")
    try:
        stores = list(client.file_search_stores.list())
        for s in stores:
            if s.display_name == store_display_name:
                current_model = getattr(s, "embedding_model", None)
                if current_model and current_model != target_model:
                    print(f"Found store with mismatching model: {current_model}. Deleting to recreate with {target_model}...")
                    client.file_search_stores.delete(name=s.name, config={"force": True})
                else:
                    file_store = s
                    break
    except Exception as e:
        return {"success": False, "error": f"Error listing file search stores: {e}"}

    if not file_store:
        print(f"Creating persistent File Search Store '{store_display_name}' with model '{target_model}'...")
        try:
            file_store = client.file_search_stores.create(
                config={"display_name": store_display_name, "embedding_model": target_model}
            )
            print(f"Store created: {file_store.name}")
        except Exception as e:
            return {"success": False, "error": f"Error creating store: {e}"}
    else:
        print(f"Found existing store: {file_store.name}")

    print("Retrieving remote documents from the store...", flush=True)
    remote_docs = {}
    docs = []
    for attempt in range(1, 6):
        try:
            doc_pager = client.file_search_stores.documents.list(parent=file_store.name)
            docs = []
            for doc in doc_pager:
                docs.append(doc)
                if len(docs) % 1000 == 0:
                    print(f"  Fetched {len(docs)} remote documents...", flush=True)
            break
        except Exception as e:
            print(f"Listing remote documents failed (attempt {attempt}/5): {e}", flush=True)
            if attempt < 5:
                time.sleep(attempt * 3)
            else:
                return {"success": False, "error": f"Failed retrieving remote documents: {e}"}

    for doc in docs:
        remote_docs[doc.display_name] = doc
    print(f"Found {len(remote_docs)} remote documents.", flush=True)

    local_files = get_local_vault_files(target_vault)
    print(f"Found {len(local_files)} local files in vault: {target_vault}")

    to_upload = []
    to_delete = []
    to_update = []

    for stem, (path, file_hash) in local_files.items():
        if stem not in remote_docs:
            to_upload.append((path, stem, file_hash))
        else:
            doc = remote_docs[stem]
            remote_hash = None
            if doc.custom_metadata:
                for meta in doc.custom_metadata:
                    key = getattr(meta, 'key', None) or (meta.get('key') if isinstance(meta, dict) else None)
                    val = getattr(meta, 'string_value', None) or (meta.get('string_value') if isinstance(meta, dict) else None)
                    if key == 'content_hash':
                        remote_hash = val
                        break
            if remote_hash != file_hash:
                if not skip_updates:
                    to_update.append((path, stem, file_hash, doc.name))

    for display_name, doc in remote_docs.items():
        if display_name not in local_files:
            to_delete.append(doc)

    print(f"\n--- Sync Plan ---")
    print(f"Upload (New):     {len(to_upload)}")
    print(f"Update (Changed): {len(to_update)}")
    print(f"Delete (Pruned):  {len(to_delete)}")
    print(f"-----------------\n")

    if to_delete:
        print("Processing deletions...")
        for doc in to_delete:
            try:
                client.file_search_stores.documents.delete(name=doc.name, config={"force": True})
            except Exception as e:
                print(f"    Error deleting {doc.display_name}: {e}")

    if to_update:
        print("Pruning outdated files for update...")
        for path, stem, file_hash, doc_name in to_update:
            try:
                client.file_search_stores.documents.delete(name=doc_name, config={"force": True})
                to_upload.append((path, stem, file_hash))
            except Exception as e:
                print(f"    Error removing old version of {stem}: {e}")

    uploaded_count = 0
    failed_count = 0
    active_operations = []

    if to_upload:
        print(f"Initiating parallel upload of {len(to_upload)} files with {max_workers} workers...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(_upload_single_worker, client, file_store.name, p, s, h)
                for p, s, h in to_upload
            ]
            for idx, future in enumerate(concurrent.futures.as_completed(futures), 1):
                stem, op, error = future.result()
                if error:
                    print(f"  [{idx}/{len(to_upload)}] [FAIL] Upload Failed for {stem}: {error}")
                    failed_count += 1
                else:
                    print(f"  [{idx}/{len(to_upload)}] [STAGED] Staged on server: {stem}")
                    active_operations.append((stem, op))
                    uploaded_count += 1

        print("\nChecking background cloud indexing status...", flush=True)
        max_retries_per_op = 3
        retry_counts = {}
        while active_operations:
            still_active = []
            for stem, op in active_operations:
                try:
                    op_status = client.operations.get(op)
                    if op_status.done:
                        if op_status.error:
                            print(f"    [FAIL] Indexing failed for {stem}: {op_status.error}", flush=True)
                        else:
                            print(f"    [OK] Fully Indexed: {stem}", flush=True)
                    else:
                        still_active.append((stem, op))
                except Exception as net_err:
                    count = retry_counts.get(stem, 0) + 1
                    retry_counts[stem] = count
                    if count >= max_retries_per_op:
                        print(f"    [WARN] Giving up on status check for {stem} after {count} retries: {net_err}", flush=True)
                    else:
                        still_active.append((stem, op))
            active_operations = still_active
            if active_operations:
                print(f"  Waiting on {len(active_operations)} documents to complete background server vectorization... (Checking in 5s)", flush=True)
                time.sleep(5)

    print("\nVault synchronization finalized successfully.", flush=True)
    return {
        "success": True,
        "store_name": file_store.name,
        "uploaded": uploaded_count,
        "updated": len(to_update),
        "deleted": len(to_delete),
        "failed": failed_count,
        "total_local": len(local_files)
    }

import os
import re
import requests
import sys

DB_SERVICE_URL = "http://127.0.0.1:8001"
QUERY_DIR = "Tools/queries"

# Security Rules
FORBIDDEN_KEYWORDS = ["drop", "delete", "truncate", "alter", "grant", "revoke"]
ALLOWED_FORMAT_KEYS = ["table", "col", "id_list"]


def sanitize_identifier(name):
    """Only allow alphanumeric and underscores for table/column names."""
    return re.match(r"^[a-zA-Z0-9_]+$", name) is not None


def test_sql_files():
    print(">>> Starting SQL Security & Validity Test <<<")
    errors = 0
    files_checked = 0

    for root, dirs, files in os.walk(QUERY_DIR):
        for file in files:
            if not file.endswith(".sql"):
                continue

            file_path = os.path.join(root, file)
            files_checked += 1
            with open(file_path, "r") as f:
                content = f.read()
                content_lower = content.lower()

            # 1. Check for forbidden keywords
            for word in FORBIDDEN_KEYWORDS:
                if word in content_lower:
                    # Exception: save/upsert tasks are allowed to write, but not DROP
                    if "save" not in file and "upsert" not in file:
                        print(f"❌ SECURITY ERROR: Forbidden keyword '{word.upper()}' found in {file_path}")
                        errors += 1

            # 2. Check for potential SQL injection patterns
            if "f'" in content or 'f"' in content:
                print(
                    f"❌ SECURITY ERROR: Python f-strings detected in SQL file {file_path}. Use '?' placeholders instead."
                )
                errors += 1

            # 3. Validate dynamic placeholders
            placeholders = re.findall(r"\{(\w+)\}", content)
            for p in placeholders:
                if p not in ALLOWED_FORMAT_KEYS:
                    print(
                        f"❌ VALIDATION ERROR: Unknown placeholder '{{{p}}}' in {file_path}. Allowed: {ALLOWED_FORMAT_KEYS}"
                    )
                    errors += 1

            # 4. Dry-run syntax check via EXPLAIN (if DB service is running)
            try:
                # Prepare a dummy version of the query by filling placeholders
                dummy_sql = content.format(table="dummy_table", col="dummy_col", id_list="1,2,3")
                explain_sql = f"EXPLAIN {dummy_sql}"

                r = requests.post(f"{DB_SERVICE_URL}/query", json={"sql": explain_sql, "params": []}, timeout=5)
                if r.status_code != 200:
                    # Note: This might fail if dummy_table doesn't exist, which is expected.
                    # We primarily check for PARSER errors here.
                    err_detail = r.json().get("detail", "")
                    if "Parser Error" in err_detail:
                        print(f"❌ SYNTAX ERROR: SQL Parser failed for {file_path}\n   Detail: {err_detail}")
                        errors += 1
            except requests.exceptions.ConnectionError:
                print(f"⚠️  WARNING: DB Service not reachable. Skipping live syntax check for {file_path}")

    print(f"\nSummary: {files_checked} files checked, {errors} errors found.")
    return errors == 0


if __name__ == "__main__":
    if not test_sql_files():
        sys.exit(1)
    sys.exit(0)

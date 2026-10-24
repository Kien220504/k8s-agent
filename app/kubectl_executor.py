import json
import subprocess

ALLOWED_COMMANDS = {"get", "logs"}

class KubectlError(Exception):
    """Kubectl ERROR."""

def run_kubectl(args: list[str], timeout: int = 15) -> str:
    if not args or args[0] not in ALLOWED_COMMANDS:
        raise KubectlError(f"Invalid command(s): {args[:1]}")
    
    result = subprocess.run(
        ["kubectl", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if result.returncode != 0:
        raise KubectlError(result.stderr.strip())
    
    return result.stdout

def kubectl_json(args: list[str]) -> dict:
    return json.loads(run_kubectl([*args, "-o", "json"]))
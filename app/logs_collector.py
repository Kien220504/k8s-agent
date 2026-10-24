from .kubectl_executor import KubectlError, run_kubectl

def collect_logs(pod: str, namespace: str = "default", tail: int = 50) -> dict:
    logs = {}

    try:
        logs["current"] = run_kubectl(["logs", pod, "-n", namespace, f"--tail={tail}"])
    except KubectlError as e:
        logs["current"] = f"(Unable to retrieve logs: {e})"

    try:
        logs["previous"] = run_kubectl(["logs", pod, "-n", namespace, f"--tail={tail}", "--previous"])
    except KubectlError as e:
        logs["previous"] = f"(Unable to retrieve logs: {e})"

    return logs
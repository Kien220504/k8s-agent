from .kubectl_executor import kubectl_json

NORMAL_WAITING = {"ContainerCreating", "PodInitializing"}

def inspect_pods(namespace: str = "default") -> list[dict]:
    data = kubectl_json(["get", "pods", "-n", namespace])
    pods = []
    for pod in data["items"]:
        status = pod.get("status", {})
        info = {
            "name": pod["metadata"]["name"],
            "phase": status.get("phase"),
            "failed_conditions": [
                {
                    "type": c.get("type"),
                    "reason": c.get("reason"),
                    "message": c.get("message"),
                }
                for c in status.get("conditions", [])
                if c.get("status") == "False"
            ],
            "containers": [],
        }
        for cs in status.get("containerStatuses", []):
            waiting = cs.get("state", {}).get("waiting") or {}
            terminated = cs.get("lastState", {}).get("terminated") or {}
            info["containers"].append(
                {
                    "name": cs["name"],
                    "restart_count": cs.get("restartCount", 0),
                    "waiting_reason": waiting.get("reason"),
                    "waiting_message": waiting.get("message"),
                    "last_terminated_reason": terminated.get("reason"),
                    "last_terminated_exticode": terminated.get("exitCode"),
                }
            )
        pods.append(info)
    return pods

def is_unhealthy(pod: dict) -> bool:
    if pod["phase"] in ("Pending", "Failed"):
        return True
    return any(
        c["waiting_reason"] not in (None, *NORMAL_WAITING) or c["last_terminated_reason"]
        for c in pod["containers"]
    )
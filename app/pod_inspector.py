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
            "spec_containers": [
                {
                    "name": c["name"],
                    "image": c.get("image"),
                    "command": c.get("command"),
                    "args": c.get("args"),
                    "env_names": [e["name"] for e in c.get("env", [])],
                    "resources": c.get("resources", {}),
                }
                for c in pod.get("spec", {}).get("containers", [])
            ],
            "owners": [
                {"kind": o.get("kind"), "name": o.get("name")}
                for o in pod["metadata"].get("ownerReferences", [])
            ],
        }
        for cs in status.get("containerStatuses", []):
            waiting = cs.get("state", {}).get("waiting") or {}
            terminated = cs.get("lastState", {}).get("terminated") or {}
            info["containers"].append(
                {
                    "name": cs["name"],
                    "ready": cs.get("ready", False),
                    "restart_count": cs.get("restartCount", 0),
                    "waiting_reason": waiting.get("reason"),
                    "waiting_message": waiting.get("message"),
                    "last_terminated_reason": terminated.get("reason"),
                    "last_exit_code": terminated.get("exitCode"),
                }
            )
        pods.append(info)
    return pods

def is_unhealthy(pod: dict) -> bool:
    if pod["phase"] == "Succeeded":
        return False
    if pod["phase"] == "Failed":
        return True
    if any(c["reason"] == "Unschedulable" for c in pod["failed_conditions"]):
        return True
    return any(
        not c["ready"] and c["waiting_reason"] not in NORMAL_WAITING
        for c in pod["containers"]
    )
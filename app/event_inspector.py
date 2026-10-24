from .kubectl_executor import KubectlError, kubectl_json

def collect_events(pod: str, namespace: str = "default", limit: int = 15) -> list[dict]:
    data = kubectl_json(
        ["get", "events", "-n", namespace, "--field-selector", f"involvedObject.name={pod}"]
    )
    items = sorted(
        data["items"],
        key=lambda e: e.get("lastTimestamp") or e.get("eventTime") or "",
    )
    return [
        {
            "type": e.get("type"),
            "reason" :e.get("reason"),
            "message": e.get("message"),
            "count": e.get("count"),
        }
        for e in items
    ][-limit:]

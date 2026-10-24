from fastapi import FastAPI, HTTPException, Query

from .event_inspector import collect_events
from .kubectl_executor import KubectlError
from .logs_collector import collect_logs
from .pod_inspector import inspect_pods, is_unhealthy

NAME_PATTERN = r"^[a-z0-9]([-a-z0-9.]*[a-z0-9])?$"

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/pods")
def list_pods(namespace: str = Query("default", pattern=NAME_PATTERN, max_length=63)):
    try:
        return inspect_pods(namespace)
    except KubectlError as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.get("/evidence")
def evidence(namespace: str = Query("default", pattern=NAME_PATTERN, max_length=63)):
    try:
        pods = []
        for p in inspect_pods(namespace):
            if is_unhealthy(p):
                pods.append(
                    {
                        "pod": p,
                        "logs": collect_logs(p["name"], namespace),
                        "events": collect_events(p["name"], namespace),
                    }
                )
        return pods
    except KubectlError as e:
        raise HTTPException(status_code=502, detail=str(e))
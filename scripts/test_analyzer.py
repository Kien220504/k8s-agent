import yaml

from app.ai_analyzer import AnalysisError, analyze
from app.event_inspector import collect_events
from app.logs_collector import collect_logs
from app.pod_inspector import inspect_pods, is_unhealthy

EXPECTED = {
    "bad-image": "ImagePullBackOff",
    "crash-loop": "CrashLoopBackOff",
    "crash-loop-2": "CrashLoopBackOff",
    "oom-demo": "OOMKilled",
    "pending-demo": "Pending",
}

correct = 0
total = 0

for pod in inspect_pods():
    if not is_unhealthy(pod):
        continue
    evidence = {
        "pod": pod,
        "logs": collect_logs(pod["name"]),
        "events": collect_events(pod["name"]),
    }
    total += 1
    try:
        result = analyze(evidence)
    except AnalysisError as e:
        print(f"--- {pod['name']} | ERROR: {e}")
        continue
    expected = EXPECTED.get(pod["name"])
    ok = result.category == expected
    correct += ok
    print(f"--- {pod['name']} | model: {result.model}")
    print(f"    True/False     : {'TRUE' if ok else 'FALSE'} (AI: {result.category}, expected: {expected})")
    print(f"    Confidence     : {result.confidence}%")
    print(f"    Root cause     : {result.root_cause}")
    print(f"    Evidence       : {result.evidence_used}")
    print(f"  Fix command(s)   : {result.fix_commands}")
    print(f"  Corrected YAML   :\n{result.corrected_manifest}")

    try:
        yaml.safe_load(result.corrected_manifest) if result.corrected_manifest else None
        yaml_ok = "valid" if result.corrected_manifest else "invalid"
    except yaml.YAMLError:
        yaml_ok = "SYNTAX ERROR"
    print(f"  YAML checking    : {yaml_ok}")

print(f"RESULT: {correct}/{total}")
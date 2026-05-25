import json
import urllib.request

url = "https://nyquist.app/simuladorlego/healthz"
with urllib.request.urlopen(url, timeout=15) as r:
    data = json.loads(r.read().decode("utf-8"))

print("status:", data.get("status"))
print("session_backend:", data.get("session_manager", {}).get("session_backend"))
print("mirror_driver:", data.get("session_manager", {}).get("metadata_mirror", {}).get("driver"))
print("mirror_enabled:", data.get("session_manager", {}).get("metadata_mirror", {}).get("enabled"))
print("degraded_to_memory:", data.get("session_manager", {}).get("degraded_to_memory"))
print("redis_enabled:", data.get("redis", {}).get("enabled"))
print("JSON:", json.dumps(data, ensure_ascii=False))
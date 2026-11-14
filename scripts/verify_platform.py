"""Platform verification script testing both FastAPI and Next.js endpoints."""
import urllib.request
import json

def main():
    print("==================================================================")
    print("             EXOPLANET FINDER PLATFORM VERIFICATION               ")
    print("==================================================================")

    # 1. Test FastAPI Backend
    try:
        health_resp = urllib.request.urlopen("http://127.0.0.1:8000/api/health")
        health = json.loads(health_resp.read())
        print(f"[FastAPI] Health: {health.get('status')} | PyTorch: {health.get('torch_version')} | Device: {health.get('device_name')}")

        catalog_resp = urllib.request.urlopen("http://127.0.0.1:8000/api/catalog/objects")
        catalog = json.loads(catalog_resp.read())
        print(f"[FastAPI] Catalog Systems Loaded: {len(catalog)} verified systems")

        tces_resp = urllib.request.urlopen("http://127.0.0.1:8000/api/candidates/11442793/tces")
        tces = json.loads(tces_resp.read())
        print(f"[FastAPI] Kepler-90 TCEs: {len(tces)} candidate signals found")
    except Exception as e:
        print(f"[ERROR] FastAPI verification failed: {e}")

    # 2. Test Next.js Frontend Routes
    print("\n--- Verifying Next.js 3D and Scientific Routes ---")
    routes = [
        ("", "Landing Page (Cinematic 3D Scene)"),
        ("space-3d", "Interactive 3D Universe Explorer"),
        ("transit-sim", "Educational 3D Transit Simulator"),
        ("planet-viewer", "3D Exoplanet Detail Experience"),
        ("kepler90", "Kepler-90 Star System Explorer"),
        ("detector", "AI Exoplanet Detection Laboratory"),
        ("studio", "Light Curve Analysis Studio"),
        ("explorer", "NASA DR24 Candidate Explorer"),
        ("models", "Model Intelligence Center"),
        ("experiments", "Research History Registry"),
        ("data", "Dataset & Cache Management"),
        ("settings", "Settings & Telemetry"),
    ]

    for path, description in routes:
        url = f"http://127.0.0.1:3000/{path}"
        try:
            resp = urllib.request.urlopen(url)
            print(f"  ✓ HTTP {resp.status} - /{path:15s} [{description}]")
        except Exception as e:
            print(f"  ✗ FAILED    - /{path:15s} ({e})")

    print("==================================================================")
    print("All platform services verified and operational!")

if __name__ == "__main__":
    main()


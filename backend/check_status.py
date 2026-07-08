"""Quick check of document + analysis status."""
import httpx

c = httpx.Client(base_url="http://127.0.0.1:8000", timeout=30)
r = c.post("/api/auth/login", json={"email": "test@finauditor.com", "password": "secret123"})
tok = r.json()["accessToken"]
h = {"Authorization": f"Bearer {tok}"}

r = c.get("/api/documents", headers=h)
docs = r.json()
print("docs:", len(docs))
for d in docs:
    print(f"  id={d['id']} status={d['status']} analysisId={d.get('analysisId')}")

if docs:
    doc_id = docs[0]["id"]
    r2 = c.get(f"/api/analysis/by-document/{doc_id}", headers=h)
    print(f"analysis by doc {doc_id}: status={r2.status_code}")
    if r2.status_code == 200:
        a = r2.json()
        print("  risks:", len(a.get("risks", [])))
    else:
        print("  body:", r2.text[:200])

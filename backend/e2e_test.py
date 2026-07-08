"""End-to-end integration test against the running server."""
import sys
import time

import httpx

BASE = "http://127.0.0.1:8000"


def main():
    c = httpx.Client(base_url=BASE, timeout=60)

    # Login
    r = c.post("/api/auth/login", json={"email": "test@finauditor.com", "password": "secret123"})
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    tok = r.json()["accessToken"]
    print(f"[OK] login -> user={r.json()['user']['email']}")
    auth = {"Authorization": f"Bearer {tok}"}

    # Upload
    file_path = "tests/fixtures/sample_rsbu.xlsx"
    with open(file_path, "rb") as f:
        r = c.post(
            "/api/documents/upload",
            headers=auth,
            files={"file": ("sample_rsbu.xlsx", f)},
            data={"template": "RSBU"},
        )
    assert r.status_code in (201, 200), f"upload failed: {r.status_code} {r.text}"
    doc = r.json()["document"]
    doc_id = doc["id"]
    print(f"[OK] upload -> docId={doc_id} status={doc['status']} analysisId={doc.get('analysisId')}")
    time.sleep(1)

    # Analysis
    r = c.get(f"/api/analysis/by-document/{doc_id}", headers=auth)
    assert r.status_code == 200, f"analysis fetch failed: {r.status_code} {r.text}"
    a = r.json()
    b = a["balanceSheet"]
    rat = a["ratios"]
    inc = a["incomeStatement"]
    print(f"[OK] analysis -> assets={b['totalAssets']} currentAssets={b['currentAssets']} equity={b['equity']}")
    print(f"     income   -> revenue={inc['revenue']} netProfit={inc['netProfit']}")
    print(f"     ratios   -> currentRatio={rat['currentRatio']} debtToEquity={rat['debtToEquity']} roa={rat['roa']}% roe={rat['roe']}%")
    print(f"     risks    -> {len(a['risks'])} found:")
    for risk in a["risks"]:
        print(f"        [{risk['level']}] {risk['title']}")

    # PDF report
    r = c.get(f"/api/analysis/{a['id']}/report", headers=auth)
    assert r.status_code == 200, f"PDF failed: {r.status_code} {r.text}"
    print(f"[OK] PDF report -> {len(r.content)} bytes, type={r.headers.get('content-type')}")

    # Chat with context
    r = c.post(
        "/api/chat",
        json={"message": "Как изменилась выручка?", "documentId": doc_id},
        headers=auth,
    )
    assert r.status_code == 200, f"chat failed: {r.status_code} {r.text}"
    chat = r.json()
    answer = chat["answer"]
    print(f"[OK] chat -> answer='{answer[:100]}...'")

    # Summary (dashboard)
    r = c.get("/api/analysis/summary", headers=auth)
    assert r.status_code == 200, f"summary failed: {r.status_code} {r.text}"
    s = r.json()
    print(f"[OK] dashboard summary -> docs={s['totalDocuments']} risks={s['totalRisks']} critical={s['criticalRisks']}")

    # Documents list
    r = c.get("/api/documents", headers=auth)
    docs = r.json()
    print(f"[OK] documents list -> {len(docs)} document(s)")

    print("\n=== ALL END-TO-END TESTS PASSED ===")


if __name__ == "__main__":
    sys.exit(main() or 0)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app

CASES = {
    "urgent-complaint": ("complaint", "high"),
    "gdpr-delete": ("gdpr_request", "normal"),
    "new-lead": ("lead", "normal"),
}


def main() -> None:
    client = TestClient(app)
    passed = 0
    rows = []
    for case, expected in CASES.items():
        payload = client.get(f"/v1/demo/{case}").json()["result"]
        actual = (payload["ticket_type"], payload["urgency"])
        ok = actual == expected
        passed += ok
        rows.append(f"| {case} | {expected[0]} / {expected[1]} | {actual[0]} / {actual[1]} | {'PASS' if ok else 'FAIL'} |")
    report = "# Triage evaluation\n\nThis is a small deterministic portfolio regression set, not a production accuracy claim.\n\n| Case | Expected | Actual | Result |\n|---|---|---|---|\n" + "\n".join(rows) + f"\n\n**Exact route match:** {passed}/{len(CASES)} ({passed / len(CASES):.0%})\n"
    output = Path("reports/latest-eval.md")
    output.parent.mkdir(exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()

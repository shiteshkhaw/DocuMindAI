import asyncio
import httpx
import random
import sys
import os
import json
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Generate a multi-page PDF with contradictions, placeholders, and requirement markers
def generate_contradictions_pdf(filename: str):
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Page 1
    c.drawString(100, 750, "Document for DocuMind Verification Audit - Page 1")
    c.drawString(100, 700, "Section 1: General Info")
    c.drawString(100, 680, "The active headcount is 5 members.")
    c.drawString(100, 660, "The project start date is 2023-01-01.")
    c.drawString(100, 640, "The total budget is $1,000,000.")
    c.drawString(100, 620, "The system shall encrypt all user data.")
    c.drawString(100, 600, "REQ-101: The system shall encrypt all user data.")
    c.drawString(100, 580, "The primary contractor is Microsoft.")
    
    # Pad Page 1 to ensure it exceeds chunk size (500 tokens)
    y = 560
    filler = "This is filler sentence to pad the document chunk size. We must ensure that the total length of page one exceeds five hundred tokens so it gets split. "
    for i in range(40):
        c.drawString(100, y, f"Page 1 filler sentence {i}: {filler[:60]}")
        y -= 12
        if y < 50:
            break
    c.showPage()
    
    # Page 2
    c.drawString(100, 750, "Document for DocuMind Verification Audit - Page 2")
    c.drawString(100, 700, "Section 2: Revisions")
    c.drawString(100, 680, "The active headcount is 4 members.")
    c.drawString(100, 660, "The project start date is 2023-03-01.")
    c.drawString(100, 640, "The total budget is $2,000,000.")
    c.drawString(100, 620, "The system shall not encrypt all user data.")
    c.drawString(100, 600, "See REQ-102 for security parameters.")
    c.drawString(100, 580, "The primary contractor is Google.")
    c.drawString(100, 560, "TODO: resolve these discrepancies prior to deployment.")
    
    # Pad Page 2
    y = 540
    for i in range(40):
        c.drawString(100, y, f"Page 2 filler sentence {i}: {filler[:60]}")
        y -= 12
        if y < 50:
            break
    c.showPage()
    
    c.save()

# Generate a PDF with 500+ repeated vague phrases
def generate_vague_pdf(filename: str):
    c = canvas.Canvas(filename, pagesize=letter)
    y = 750
    phrase = "It is possible that the system might be somewhat slow."
    c.drawString(100, y, "Document containing repeated vague terms:")
    y -= 20
    
    # Generate 520 lines of the vague phrase
    count = 0
    for i in range(520):
        c.drawString(100, y, f"{i+1}: {phrase}")
        y -= 15
        count += 1
        if y < 50:
            c.showPage()
            y = 750
            
    c.showPage()
    c.save()

async def run_audit():
    print("====================================================")
    print("      DOCUMIND AI COMMERCIAL VERIFICATION AUDIT     ")
    print("====================================================\n")
    
    # Unique suffix to avoid DB collisions
    suffix = str(random.randint(1000, 9999))
    email_a = f"usera_{suffix}@example.com"
    email_b = f"userb_{suffix}@example.com"
    password = "SuperPassword123!"
    
    evidence = {}
    failure_matrix = {
        "User Registration": {"tested": True, "passed": False, "failed": False, "evidence": ""},
        "User Login": {"tested": True, "passed": False, "failed": False, "evidence": ""},
        "Workspace Creation": {"tested": True, "passed": False, "failed": False, "evidence": ""},
        "Ownership Isolation": {"tested": True, "passed": False, "failed": False, "evidence": ""},
        "Document Upload": {"tested": True, "passed": False, "failed": False, "evidence": ""},
        "Ingestion Pipeline": {"tested": True, "passed": False, "failed": False, "evidence": ""},
        "Numeric Conflict Detection": {"tested": True, "passed": False, "failed": False, "evidence": ""},
        "Date Conflict Detection": {"tested": True, "passed": False, "failed": False, "evidence": ""},
        "Polarity Conflict Detection": {"tested": True, "passed": False, "failed": False, "evidence": ""},
        "Monetary Conflict Detection": {"tested": True, "passed": False, "failed": False, "evidence": ""},
        "Semantic Conflict Detection": {"tested": True, "passed": False, "failed": False, "evidence": ""},
        "Trust Score Verification": {"tested": True, "passed": False, "failed": False, "evidence": ""},
        "Ambiguity Deduplication": {"tested": True, "passed": False, "failed": False, "evidence": ""},
        "Concurrent Analysis (20 threads)": {"tested": True, "passed": False, "failed": False, "evidence": ""}
    }
    
    async with httpx.AsyncClient(timeout=90.0) as client:
        # 1. Register User A and User B
        print("1. Testing User Registration & Login...")
        r_signup_a = await client.post(f"{BASE_URL}/auth/signup", json={"name": "User A", "email": email_a, "password": password})
        r_signup_b = await client.post(f"{BASE_URL}/auth/signup", json={"name": "User B", "email": email_b, "password": password})
        
        evidence["Signup A Request"] = {"url": f"{BASE_URL}/auth/signup", "payload": {"name": "User A", "email": email_a}}
        evidence["Signup A Response"] = r_signup_a.json() if r_signup_a.status_code == 201 else r_signup_a.text
        
        if r_signup_a.status_code == 201 and r_signup_b.status_code == 201:
            print("  [PASS] User registration successful (201 Created)")
            failure_matrix["User Registration"]["passed"] = True
        else:
            print(f"  [FAIL] User registration failed: User A ({r_signup_a.status_code}), User B ({r_signup_b.status_code})")
            failure_matrix["User Registration"]["failed"] = True
            
        r_login_a = await client.post(f"{BASE_URL}/auth/login", json={"email": email_a, "password": password})
        r_login_b = await client.post(f"{BASE_URL}/auth/login", json={"email": email_b, "password": password})
        
        evidence["Login A Request"] = {"url": f"{BASE_URL}/auth/login", "payload": {"email": email_a}}
        evidence["Login A Response"] = r_login_a.json() if r_login_a.status_code == 200 else r_login_a.text
        
        if r_login_a.status_code == 200 and r_login_b.status_code == 200:
            print("  [PASS] User login successful (200 OK)")
            failure_matrix["User Login"]["passed"] = True
            token_a = r_login_a.json()["access_token"]
            token_b = r_login_b.json()["access_token"]
        else:
            print("  [FAIL] User login failed")
            failure_matrix["User Login"]["failed"] = True
            return
            
        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}
        
        # 2. Workspace Creation
        print("\n2. Testing Workspace Creation...")
        r_ws_a = await client.post(f"{BASE_URL}/workspaces", json={"name": "Workspace A"}, headers=headers_a)
        r_ws_b = await client.post(f"{BASE_URL}/workspaces", json={"name": "Workspace B"}, headers=headers_b)
        
        evidence["Create Workspace A Request"] = {"url": f"{BASE_URL}/workspaces", "payload": {"name": "Workspace A"}}
        evidence["Create Workspace A Response"] = r_ws_a.json()
        
        if r_ws_a.status_code == 201 and r_ws_b.status_code == 201:
            print("  [PASS] Workspaces created successfully")
            failure_matrix["Workspace Creation"]["passed"] = True
            ws_id_a = r_ws_a.json()["id"]
            ws_id_b = r_ws_b.json()["id"]
        else:
            print("  [FAIL] Workspace creation failed")
            failure_matrix["Workspace Creation"]["failed"] = True
            
        # 3. Ownership Isolation Check
        print("\n3. Testing Ownership Isolation...")
        # User A tries to list workspaces of User B (should not see them)
        r_list_ws_a = await client.get(f"{BASE_URL}/workspaces", headers=headers_a)
        workspaces_a = r_list_ws_a.json()
        user_b_ws_visible = any(w["id"] == ws_id_b for w in workspaces_a)
        
        # User A tries to patch User B's workspace (should fail)
        r_patch_b_ws = await client.patch(f"{BASE_URL}/workspaces/{ws_id_b}", json={"name": "Hacked"}, headers=headers_a)
        
        evidence["User A List Workspaces Response"] = workspaces_a
        evidence["User A Hack Workspace B Response"] = r_patch_b_ws.status_code
        
        if not user_b_ws_visible and r_patch_b_ws.status_code in (403, 404):
            print("  [PASS] Workspaces strictly isolated")
            failure_matrix["Ownership Isolation"]["passed"] = True
        else:
            print("  [FAIL] Workspace isolation breach!")
            failure_matrix["Ownership Isolation"]["failed"] = True

        # Generate files for upload
        pdf_filename = "audit_contradictions.pdf"
        generate_contradictions_pdf(pdf_filename)
        
        vague_filename = "audit_vague.pdf"
        generate_vague_pdf(vague_filename)
        
        # 4. Uploading Real Documents
        print("\n4. Testing Document Upload...")
        with open(pdf_filename, "rb") as f:
            files = {"file": (pdf_filename, f, "application/pdf")}
            r_upload = await client.post(f"{BASE_URL}/documents/upload", files=files, data={"workspace_id": ws_id_a}, headers=headers_a)
            
        evidence["Document Upload Request"] = {"url": f"{BASE_URL}/documents/upload", "filename": pdf_filename}
        evidence["Document Upload Response"] = r_upload.json()
        
        if r_upload.status_code == 201:
            print("  [PASS] Document uploaded successfully (201 Created)")
            failure_matrix["Document Upload"]["passed"] = True
            doc_id = r_upload.json()["id"]
        else:
            print(f"  [FAIL] Document upload failed: {r_upload.text}")
            failure_matrix["Document Upload"]["failed"] = True
            return
            
        # 5. Ingestion Pipeline
        print("\n5. Checking Ingestion Pipeline...")
        completed = False
        for i in range(15):
            r_doc = await client.get(f"{BASE_URL}/documents/{doc_id}", headers=headers_a)
            status = r_doc.json().get("status")
            print(f"  - Ingestion status (attempt {i+1}): {status}")
            if status == "COMPLETED":
                completed = True
                break
            if status == "FAILED":
                print(f"  [FAIL] Ingestion failed with error: {r_doc.json().get('error')}")
                break
            await asyncio.sleep(2)
            
        if completed:
            print("  [PASS] Document ingested completely")
            failure_matrix["Ingestion Pipeline"]["passed"] = True
        else:
            print("  [FAIL] Document ingestion timed out or failed")
            failure_matrix["Ingestion Pipeline"]["failed"] = True
            return

        # Double check document ownership isolation
        print("\nChecking Document Ownership Isolation...")
        r_doc_b_leak = await client.get(f"{BASE_URL}/documents/{doc_id}", headers=headers_b)
        r_analysis_b_leak = await client.get(f"{BASE_URL}/documents/{doc_id}/analysis", headers=headers_b)
        
        evidence["Leak Doc Response Code"] = r_doc_b_leak.status_code
        evidence["Leak Analysis Response Code"] = r_analysis_b_leak.status_code
        
        if r_doc_b_leak.status_code == 404 and r_analysis_b_leak.status_code == 404:
            print("  [PASS] Document and Analysis isolated successfully (404 Not Found for non-owner)")
        else:
            print("  [FAIL] Ownership isolation breached for document/analysis endpoints!")
            failure_matrix["Ownership Isolation"]["passed"] = False
            failure_matrix["Ownership Isolation"]["failed"] = True
            
        # 6. Fetch Analysis and Verify Contradictions
        print("\n6. Running Contradiction Detection Verification...")
        r_analysis = await client.get(f"{BASE_URL}/documents/{doc_id}/analysis", headers=headers_a)
        analysis_data = r_analysis.json()
        
        evidence["Analysis Response"] = analysis_data
        
        # Verify Contradictions
        entity_inconsistencies = analysis_data.get("entityInconsistencies", [])
        semantic_conflicts = analysis_data.get("semanticConflicts", [])
        
        print("\n--- Contradiction Detection Results ---")
        numeric_detected = False
        date_detected = False
        polarity_detected = False
        monetary_detected = False
        semantic_detected = False
        
        # We query the specific endpoint GET /documents/{id}/entity-conflicts to print out raw results
        r_entity_conflicts = await client.get(f"{BASE_URL}/documents/{doc_id}/entity-conflicts", headers=headers_a)
        raw_ent_conflicts = r_entity_conflicts.json()
        print(f"Raw Entity Conflicts count: {len(raw_ent_conflicts)}")
        for ec in raw_ent_conflicts:
            ent = str(ec.get("entity", "")).lower()
            vals = [str(v).lower() for v in (ec.get("values") or [ec.get("value_a", ""), ec.get("value_b", "")])]
            evidence_str = str(ec.get("evidence", "")).lower()
            
            if "headcount" in ent or "headcount" in evidence_str or ("5" in vals and "4" in vals):
                numeric_detected = True
            if "date" in ent or "date" in evidence_str or ("2023-01-01" in vals and "2023-03-01" in vals):
                date_detected = True
            if "budget" in ent or "budget" in evidence_str or ("$1,000,000" in vals or "1,000,000" in vals):
                monetary_detected = True
                
        # Polarity conflict matches requirements
        r_reqs = await client.get(f"{BASE_URL}/documents/{doc_id}/requirements", headers=headers_a)
        reqs_list = r_reqs.json()
        print(f"Requirements list count: {len(reqs_list)}")
        
        # We check semantic conflicts
        print(f"Semantic Conflicts count: {len(semantic_conflicts)}")
        for sc in semantic_conflicts:
            stmt_a = sc.get("statement_a", "").lower()
            stmt_b = sc.get("statement_b", "").lower()
            expl = sc.get("explanation", "").lower()
            ctype = sc.get("conflict_type", "").lower()
            
            if "encrypt" in stmt_a or "encrypt" in stmt_b or "polarity" in ctype:
                polarity_detected = True
            if "contractor" in stmt_a or "contractor" in stmt_b or "microsoft" in stmt_a or "google" in stmt_a:
                semantic_detected = True
                
        # Print results
        print(f"  * Numeric Conflict (5 vs 4 headcount): {'[PASS]' if numeric_detected else '[FAIL]'}")
        print(f"  * Date Conflict (2023-01-01 vs 2023-03-01): {'[PASS]' if date_detected else '[FAIL]'}")
        print(f"  * Polarity Conflict (shall encrypt vs shall not encrypt): {'[PASS]' if polarity_detected else '[FAIL]'}")
        print(f"  * Monetary Conflict ($1M vs $2M budget): {'[PASS]' if monetary_detected else '[FAIL]'}")
        print(f"  * Semantic Conflict (Microsoft vs Google contractor): {'[PASS]' if semantic_detected else '[FAIL]'}")
        
        failure_matrix["Numeric Conflict Detection"]["passed"] = numeric_detected
        failure_matrix["Numeric Conflict Detection"]["failed"] = not numeric_detected
        failure_matrix["Date Conflict Detection"]["passed"] = date_detected
        failure_matrix["Date Conflict Detection"]["failed"] = not date_detected
        failure_matrix["Polarity Conflict Detection"]["passed"] = polarity_detected
        failure_matrix["Polarity Conflict Detection"]["failed"] = not polarity_detected
        failure_matrix["Monetary Conflict Detection"]["passed"] = monetary_detected
        failure_matrix["Monetary Conflict Detection"]["failed"] = not monetary_detected
        failure_matrix["Semantic Conflict Detection"]["passed"] = semantic_detected
        failure_matrix["Semantic Conflict Detection"]["failed"] = not semantic_detected
        
        # 7. Trust Score Verification
        print("\n7. Trust Score Verification...")
        r_ts = await client.get(f"{BASE_URL}/documents/{doc_id}/trust-score", headers=headers_a)
        ts_data = r_ts.json()
        evidence["Trust Score Response"] = ts_data
        
        actual_score = ts_data.get("score")
        actual_breakdown = ts_data.get("breakdown", {})
        
        # Manually compute expected deductions
        # Component scores start at 100
        # 1. Contradictions score: 100 - sum(deductions)
        # Semantic conflicts:
        deducted_contr = 0
        for sc in semantic_conflicts:
            sev = sc.get("severity", "medium").lower()
            if sev == "critical":
                deducted_contr += 20.0
            elif sev == "high":
                deducted_contr += 12.0
            elif sev == "low":
                deducted_contr += 2.0
            else:
                deducted_contr += 6.0
        expected_contr_score = max(0.0, 100.0 - deducted_contr)
        
        # 2. References score: 100
        r_refs = await client.get(f"{BASE_URL}/documents/{doc_id}/references", headers=headers_a)
        refs_list = r_refs.json()
        deducted_refs = sum(8.0 for r in refs_list if r.get("status") == "BROKEN_REFERENCE")
        expected_ref_score = max(0.0, 100.0 - deducted_refs)
        
        # 3. Requirements score: 100
        deducted_reqs = 0.0
        for r in reqs_list:
            if r.get("status") == "MISSING":
                deducted_reqs += 12.0
            elif r.get("status") == "ORPHANED":
                deducted_reqs += 4.0
        expected_req_score = max(0.0, 100.0 - deducted_reqs)
        
        # 4. Entities score: 100
        deducted_ent = 0.0
        for ec in raw_ent_conflicts:
            sev = ec.get("severity", "medium").lower()
            if sev in ("critical", "high"):
                deducted_ent += 15.0
            elif sev == "low":
                deducted_ent += 3.0
            else:
                deducted_ent += 8.0
        expected_ent_score = max(0.0, 100.0 - deducted_ent)
        
        # 5. Ambiguities score: 100
        r_amb = await client.get(f"{BASE_URL}/documents/{doc_id}/ambiguities", headers=headers_a)
        amb_list = r_amb.json()
        deducted_amb = 0.0
        for amb in amb_list:
            sev = amb.get("severity", "low").lower()
            if sev == "high":
                deducted_amb += 8.0
            elif sev == "medium":
                deducted_amb += 4.0
            else:
                deducted_amb += 1.5
        expected_amb_score = max(0.0, 100.0 - deducted_amb)
        
        # 6. Completeness score: 100
        expected_comp_score = 100.0 - 8.0  # (one TODO placeholder)
        
        expected_score = (
            0.35 * expected_contr_score +
            0.20 * expected_ref_score +
            0.15 * expected_req_score +
            0.15 * expected_ent_score +
            0.10 * expected_amb_score +
            0.05 * expected_comp_score
        )
        expected_score = max(0.0, min(100.0, round(expected_score, 2)))
        
        print(f"  - Actual Trust Score: {actual_score}")
        print(f"  - Expected Trust Score (calculated): {expected_score}")
        print(f"  - Breakdown:")
        print(f"    * Contradiction Health: actual={actual_breakdown.get('contradiction_health')}, expected={expected_contr_score}")
        print(f"    * Reference Integrity: actual={actual_breakdown.get('reference_integrity')}, expected={expected_ref_score}")
        print(f"    * Requirement Traceability: actual={actual_breakdown.get('requirement_traceability')}, expected={expected_req_score}")
        print(f"    * Entity Consistency: actual={actual_breakdown.get('entity_consistency')}, expected={expected_ent_score}")
        print(f"    * Ambiguity Analysis: actual={actual_breakdown.get('ambiguity_analysis')}, expected={expected_amb_score}")
        print(f"    * Document Completeness: actual={actual_breakdown.get('document_completeness')}, expected={expected_comp_score}")
        
        if abs(actual_score - expected_score) < 1.0:
            print("  [PASS] Trust Score calculation verified successfully")
            failure_matrix["Trust Score Verification"]["passed"] = True
        else:
            print("  [FAIL] Trust Score mismatch!")
            failure_matrix["Trust Score Verification"]["failed"] = True

        # 8. Ambiguity Deduplication
        print("\n8. Testing Ambiguity Deduplication with 500+ repeated phrases...")
        with open(vague_filename, "rb") as f:
            files = {"file": (vague_filename, f, "application/pdf")}
            r_upload_vague = await client.post(f"{BASE_URL}/documents/upload", files=files, data={"workspace_id": ws_id_a}, headers=headers_a)
            
        if r_upload_vague.status_code == 201:
            vague_doc_id = r_upload_vague.json()["id"]
            # Wait for ingestion
            for _ in range(15):
                r_doc_v = await client.get(f"{BASE_URL}/documents/{vague_doc_id}", headers=headers_a)
                if r_doc_v.json().get("status") == "COMPLETED":
                    break
                await asyncio.sleep(2)
                
            r_vague_amb = await client.get(f"{BASE_URL}/documents/{vague_doc_id}/ambiguities", headers=headers_a)
            vague_ambs = r_vague_amb.json()
            evidence["Vague Document Ambiguities Count"] = len(vague_ambs)
            
            print(f"  - Extracted ambiguities count: {len(vague_ambs)}")
            if len(vague_ambs) < 15:
                print("  [PASS] Ambiguity deduplication verified (500+ repeated phrases deduplicated to clean subset)")
                failure_matrix["Ambiguity Deduplication"]["passed"] = True
            else:
                print("  [FAIL] Ambiguity list is not properly deduplicated!")
                failure_matrix["Ambiguity Deduplication"]["failed"] = True
        else:
            print("  [FAIL] Vague document upload failed")
            failure_matrix["Ambiguity Deduplication"]["failed"] = True
            
        # 9. Concurrent Analysis (20 simultaneous calls)
        print("\n9. Testing Concurrent Analysis by launching 20 calls simultaneously...")
        t0 = time.perf_counter()
        
        async def call_analysis_endpoint():
            res = await client.get(f"{BASE_URL}/documents/{doc_id}/analysis", headers=headers_a)
            return res.status_code
            
        tasks = [call_analysis_endpoint() for _ in range(20)]
        results = await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - t0
        
        evidence["Concurrent Status Codes"] = results
        evidence["Concurrent Latency Seconds"] = elapsed
        
        print(f"  - Handled 20 concurrent requests in {elapsed:.2f} seconds")
        print(f"  - Status codes returned: {dict((x, results.count(x)) for x in set(results))}")
        
        if all(code == 200 for code in results):
            print("  [PASS] Concurrent analysis successfully completed without DB locks or failures")
            failure_matrix["Concurrent Analysis (20 threads)"]["passed"] = True
        else:
            print("  [FAIL] Concurrent analysis encountered errors!")
            failure_matrix["Concurrent Analysis (20 threads)"]["failed"] = True
            
    # Cleanup files
    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)
    if os.path.exists(vague_filename):
        os.remove(vague_filename)
        
    # Write audit findings and evidence to json file
    with open("audit_evidence.json", "w") as f:
        json.dump(evidence, f, indent=2)
        
    print("\n====================================================")
    print("                AUDIT SUMMARY MATRIX                ")
    print("====================================================")
    print(f"{'Feature':<35} | {'Tested':<6} | {'Passed':<6} | {'Failed':<6}")
    print("-" * 65)
    passed_cnt = 0
    total_cnt = 0
    for feat, res in failure_matrix.items():
        total_cnt += 1
        p = "YES" if res["passed"] else "NO"
        f = "YES" if res["failed"] else "NO"
        if res["passed"]:
            passed_cnt += 1
        print(f"{feat:<35} | {'YES':<6} | {p:<6} | {f:<6}")
        
    readiness_score = int((passed_cnt / total_cnt) * 100)
    print(f"\nPRODUCTION READINESS SCORE: {readiness_score}/100")
    print("====================================================\n")

if __name__ == "__main__":
    asyncio.run(run_audit())

"""Seed MongoDB with Pakistan-focused sample data for Lawmate."""

from .repository import DEFAULT_ADMIN_SETTINGS, hash_password
from .database import get_collection


def seed_if_empty() -> None:
    admin_coll = get_collection("admin_users")
    settings_coll = get_collection("app_settings")
    citizens_coll = get_collection("citizens")
    lawyers_coll = get_collection("lawyers")
    cases_coll = get_collection("stored_cases")
    lawyer_clients_coll = get_collection("lawyer_client_rows")

    if admin_coll.count_documents({}) == 0:
        admin_coll.insert_one(
            {
                "id": "admin-1",
                "name": "Admin User",
                "email": "admin@lawmate.com",
                "password_hash": hash_password("admin123"),
            }
        )

    if settings_coll.find_one({"key": "admin_settings"}) is None:
        settings_coll.insert_one({"key": "admin_settings", "value": dict(DEFAULT_ADMIN_SETTINGS)})

    seed_password_hash = hash_password("demo123")

    citizens_seed = [
        {
            "id": "cit-001",
            "name": "Ali Raza",
            "email": "ali.raza@example.pk",
            "password_hash": seed_password_hash,
            "join_date": "2026-01-08",
            "status": "Active",
            "cases_involved": 2,
        },
        {
            "id": "cit-002",
            "name": "Ayesha Noor",
            "email": "ayesha.noor@example.pk",
            "password_hash": seed_password_hash,
            "join_date": "2026-02-11",
            "status": "Active",
            "cases_involved": 1,
        },
        {
            "id": "cit-003",
            "name": "Muhammad Hamza",
            "email": "hamza.khan@example.pk",
            "password_hash": seed_password_hash,
            "join_date": "2026-02-25",
            "status": "Pending",
            "cases_involved": 1,
        },
    ]
    for citizen in citizens_seed:
        if citizens_coll.find_one({"id": citizen["id"]}) is None:
            citizens_coll.insert_one(citizen)

    lawyers_seed = [
        {
            "id": "law-001",
            "name": "Adv. Sara Ahmed",
            "email": "sara.ahmed@lawmate.pk",
            "password_hash": seed_password_hash,
            "specialization": "Criminal Defense",
            "verification_status": "Verified",
            "cases_solved": 41,
            "win_rate": 84.0,
            "join_date": "2025-08-10",
            "location": "Lahore",
            "rating": 4.8,
            "reviews": 57,
            "specializations": ["Bail", "Trial", "Appeals"],
            "years_exp": 11,
            "cases": 28,
            "phone": "+92-300-1112233",
            "bio": "Criminal defense advocate focused on bail and trial strategy in Punjab courts.",
            "profile_image": "",
        },
        {
            "id": "law-002",
            "name": "Adv. Bilal Siddiqui",
            "email": "bilal.siddiqui@lawmate.pk",
            "password_hash": seed_password_hash,
            "specialization": "FIR & Investigation",
            "verification_status": "Verified",
            "cases_solved": 33,
            "win_rate": 79.0,
            "join_date": "2025-09-02",
            "location": "Karachi",
            "rating": 4.6,
            "reviews": 43,
            "specializations": ["FIR Quashment", "Police Procedure", "Cyber Crime"],
            "years_exp": 9,
            "cases": 23,
            "phone": "+92-301-5566778",
            "bio": "Handles FIR disputes and investigation-stage criminal matters in Sindh.",
            "profile_image": "",
        },
        {
            "id": "law-003",
            "name": "Adv. Hamna Tariq",
            "email": "hamna.tariq@lawmate.pk",
            "password_hash": seed_password_hash,
            "specialization": "Appellate Criminal Practice",
            "verification_status": "Verified",
            "cases_solved": 26,
            "win_rate": 81.0,
            "join_date": "2025-10-14",
            "location": "Islamabad",
            "rating": 4.7,
            "reviews": 31,
            "specializations": ["Appeals", "Constitutional Petitions", "Revision"],
            "years_exp": 8,
            "cases": 17,
            "phone": "+92-333-7788990",
            "bio": "Represents clients before Islamabad High Court in criminal appeals and revisions.",
            "profile_image": "",
        },
        {
            "id": "law-004",
            "name": "Adv. Usman Khalid",
            "email": "usman.khalid@lawmate.pk",
            "password_hash": seed_password_hash,
            "specialization": "Narcotics & Special Laws",
            "verification_status": "Pending",
            "cases_solved": 9,
            "win_rate": 68.0,
            "join_date": "2026-01-20",
            "location": "Peshawar",
            "rating": 4.2,
            "reviews": 10,
            "specializations": ["CNSA", "Special Courts", "Bail"],
            "years_exp": 5,
            "cases": 11,
            "phone": "+92-334-6655443",
            "bio": "Early-career advocate for special criminal statutes and narcotics defense.",
            "profile_image": "",
        },
    ]
    for lawyer in lawyers_seed:
        if lawyers_coll.find_one({"id": lawyer["id"]}) is None:
            lawyers_coll.insert_one(lawyer)

    cases_seed = [
                {
                    "id": "FIR/2026/0001",
                    "scope": "citizen",
                    "payload": {
                        "id": "FIR/2026/0001",
                        "case_type": "Bail Application",
                        "status": "Active",
                        "court": "Lahore High Court",
                        "judge": "Hon. Justice Ali Baqar Najafi",
                        "filing_date": "2026-03-05",
                        "next_hearing": "2026-05-12",
                        "documents_count": 5,
                        "progress": 55,
                        "assigned_lawyer": "Adv. Sara Ahmed",
                        "sections": ["PPC 302", "PPC 34"],
                        "police_station": "Model Town Police Station, Lahore",
                        "fir_number": "FIR/2026/0001",
                        "owner_citizen_id": "cit-001",
                    },
                },
                {
                    "id": "FIR/2026/0002",
                    "scope": "citizen",
                    "payload": {
                        "id": "FIR/2026/0002",
                        "case_type": "FIR Quashment",
                        "status": "Hearing Scheduled",
                        "court": "Sindh High Court, Karachi",
                        "judge": "Hon. Justice Salahuddin Panhwar",
                        "filing_date": "2026-03-14",
                        "next_hearing": "2026-05-18",
                        "documents_count": 4,
                        "progress": 42,
                        "assigned_lawyer": "Adv. Bilal Siddiqui",
                        "sections": ["PPC 420", "PPC 468"],
                        "police_station": "Gulshan-e-Iqbal Police Station, Karachi",
                        "fir_number": "FIR/2026/0002",
                        "owner_citizen_id": "cit-002",
                    },
                },
                {
                    "id": "FIR/2026/0003",
                    "scope": "citizen",
                    "payload": {
                        "id": "FIR/2026/0003",
                        "case_type": "Revision Petition",
                        "status": "Active",
                        "court": "Islamabad High Court",
                        "judge": "Hon. Justice Babar Sattar",
                        "filing_date": "2026-04-01",
                        "next_hearing": "2026-05-25",
                        "documents_count": 3,
                        "progress": 31,
                        "assigned_lawyer": "Adv. Hamna Tariq",
                        "sections": ["CrPC 439", "CrPC 561-A"],
                        "police_station": "Aabpara Police Station, Islamabad",
                        "fir_number": "FIR/2026/0003",
                        "owner_citizen_id": "cit-003",
                    },
                },
                {
                    "id": "C-2026-LHR-001",
                    "scope": "lawyer",
                    "payload": {
                        "id": "C-2026-LHR-001",
                        "case_type": "Bail Application",
                        "status": "Active",
                        "court": "Lahore High Court",
                        "judge": "Hon. Justice Syed Shahbaz Ali Rizvi",
                        "filing_date": "2026-03-03",
                        "next_hearing": "2026-05-10",
                        "documents_count": 6,
                        "progress": 64,
                        "priority": "High",
                        "client_name": "Ali Raza",
                        "deadline": "2026-05-10",
                        "hours_billed": 18,
                        "owner_lawyer_id": "law-001",
                    },
                },
                {
                    "id": "C-2026-KHI-001",
                    "scope": "lawyer",
                    "payload": {
                        "id": "C-2026-KHI-001",
                        "case_type": "FIR Quashment",
                        "status": "Hearing Scheduled",
                        "court": "Sindh High Court, Karachi",
                        "judge": "Hon. Justice Adnan Iqbal Chaudhry",
                        "filing_date": "2026-03-12",
                        "next_hearing": "2026-05-17",
                        "documents_count": 5,
                        "progress": 49,
                        "priority": "Medium",
                        "client_name": "Ayesha Noor",
                        "deadline": "2026-05-17",
                        "hours_billed": 14,
                        "owner_lawyer_id": "law-002",
                    },
                },
                {
                    "id": "C-2026-ISB-001",
                    "scope": "lawyer",
                    "payload": {
                        "id": "C-2026-ISB-001",
                        "case_type": "Criminal Appeal",
                        "status": "Active",
                        "court": "Islamabad High Court",
                        "judge": "Hon. Justice Mohsin Akhtar Kayani",
                        "filing_date": "2026-03-27",
                        "next_hearing": "2026-05-28",
                        "documents_count": 7,
                        "progress": 58,
                        "priority": "High",
                        "client_name": "Muhammad Hamza",
                        "deadline": "2026-05-28",
                        "hours_billed": 21,
                        "owner_lawyer_id": "law-003",
                    },
                },
            ]
    for case_doc in cases_seed:
        if cases_coll.find_one({"id": case_doc["id"]}) is None:
            cases_coll.insert_one(case_doc)

    lawyer_clients_seed = [
                {
                    "row_id": 1,
                    "lawyer_id": "law-001",
                    "client_id": "cli-lhr-001",
                    "payload": {
                        "lawyerId": "law-001",
                        "clientId": "cli-lhr-001",
                        "clientName": "Ali Raza",
                        "clientEmail": "ali.raza@example.pk",
                        "clientPhone": "+92-300-1122334",
                        "caseType": "Bail Application",
                        "status": "Active",
                        "activeCases": 1,
                        "totalCases": 1,
                        "caseId": "C-2026-LHR-001",
                        "firNumber": "FIR/2026/0001",
                        "court": "Lahore High Court",
                        "policeStation": "Model Town Police Station, Lahore",
                        "caseStage": "Post-Arrest Bail",
                        "riskLevel": "Medium",
                        "priority": "High",
                        "nextHearing": "2026-05-10",
                        "lastContactDate": "2026-04-20",
                        "assignedDate": "2026-03-03",
                        "outstandingAmount": 85000,
                        "notes": "Family wants urgent bail disposal before trial framing.",
                        "city": "Lahore",
                    },
                },
                {
                    "row_id": 2,
                    "lawyer_id": "law-002",
                    "client_id": "cli-khi-001",
                    "payload": {
                        "lawyerId": "law-002",
                        "clientId": "cli-khi-001",
                        "clientName": "Ayesha Noor",
                        "clientEmail": "ayesha.noor@example.pk",
                        "clientPhone": "+92-301-3344556",
                        "caseType": "FIR Quashment",
                        "status": "Active",
                        "activeCases": 1,
                        "totalCases": 1,
                        "caseId": "C-2026-KHI-001",
                        "firNumber": "FIR/2026/0002",
                        "court": "Sindh High Court, Karachi",
                        "policeStation": "Gulshan-e-Iqbal Police Station, Karachi",
                        "caseStage": "Constitutional Petition",
                        "riskLevel": "Low",
                        "priority": "Medium",
                        "nextHearing": "2026-05-17",
                        "lastContactDate": "2026-04-22",
                        "assignedDate": "2026-03-12",
                        "outstandingAmount": 65000,
                        "notes": "Need certified copies of FIR annexures before next date.",
                        "city": "Karachi",
                    },
                },
                {
                    "row_id": 3,
                    "lawyer_id": "law-003",
                    "client_id": "cli-isb-001",
                    "payload": {
                        "lawyerId": "law-003",
                        "clientId": "cli-isb-001",
                        "clientName": "Muhammad Hamza",
                        "clientEmail": "hamza.khan@example.pk",
                        "clientPhone": "+92-333-9988776",
                        "caseType": "Criminal Appeal",
                        "status": "Active",
                        "activeCases": 1,
                        "totalCases": 1,
                        "caseId": "C-2026-ISB-001",
                        "firNumber": "FIR/2026/0003",
                        "court": "Islamabad High Court",
                        "policeStation": "Aabpara Police Station, Islamabad",
                        "caseStage": "Appeal Hearing",
                        "riskLevel": "Medium",
                        "priority": "High",
                        "nextHearing": "2026-05-28",
                        "lastContactDate": "2026-04-24",
                        "assignedDate": "2026-03-27",
                        "outstandingAmount": 92000,
                        "notes": "Appellate paperbook prepared; argument notes under review.",
                        "city": "Islamabad",
                    },
                },
            ]
    for row in lawyer_clients_seed:
        if lawyer_clients_coll.find_one({"row_id": row["row_id"]}) is None:
            lawyer_clients_coll.insert_one(row)

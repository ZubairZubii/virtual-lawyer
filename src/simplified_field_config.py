"""
Simplified Field Configuration for Document Templates
Maps complex template fields to simple, layman-friendly fields
Only includes essential fields that users actually need to fill
"""

# Field type definitions for better UX
FIELD_TYPES = {
    'text': 'text',
    'textarea': 'textarea',
    'date': 'date',
    'email': 'email',
    'phone': 'tel',
}

# Simplified field mappings for each document category
# Format: {template_file: {simplified_field_key: {maps_to: [original_fields], label: str, type: str, required: bool, description: str}}}

SIMPLIFIED_FIELDS = {
    # Pre-arrest Bail (Anticipatory Bail)
    "Pre-arrest bail (anticipatory bail)": {
        "applicant_name": {
            "maps_to": ["NAME OF APPLICANT/PETITIONER", "PETITIONER'S NAME", "NAME"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name as it appears on your CNIC"
        },
        "father_husband_name": {
            "maps_to": ["FATHER/HUSBAND'S NAME"],
            "label": "Father's or Husband's Name",
            "type": "text",
            "required": True,
            "description": "Enter your father's or husband's full name"
        },
        "address": {
            "maps_to": ["FULL ADDRESS", "ADDRESS"],
            "label": "Your Complete Address",
            "type": "textarea",
            "required": True,
            "description": "Enter your full residential address with house number, street, area, and city"
        },
        "contact_number": {
            "maps_to": ["CONTACT NUMBER"],
            "label": "Mobile Number",
            "type": "phone",
            "required": True,
            "description": "Enter your mobile number (e.g., 0300-1234567)"
        },
        "fir_number": {
            "maps_to": ["FIR NUMBER"],
            "label": "FIR Number",
            "type": "text",
            "required": True,
            "description": "Enter the FIR number (e.g., 123/2024)"
        },
        "police_station": {
            "maps_to": ["NAME OF POLICE STATION"],
            "label": "Police Station Name",
            "type": "text",
            "required": True,
            "description": "Name of the police station where FIR was registered"
        },
        "city": {
            "maps_to": ["CITY", "DISTRICT"],
            "label": "City",
            "type": "text",
            "required": True,
            "description": "City where the case is registered"
        },
        "case_details": {
            "maps_to": ["SUMMARY OF ALLEGATIONS", "PROVIDE A CONCISE 2-3 SENTENCE SUMMARY OF THE ALLEGATIONS AS PER FIR"],
            "label": "Brief Description of the Case",
            "type": "textarea",
            "required": True,
            "description": "Briefly describe what the case is about in simple words (2-3 sentences)"
        },
        "fir_date": {
            "maps_to": ["DATE OF FIR"],
            "label": "Date when FIR was registered",
            "type": "date",
            "required": False,
            "description": "Select the date when the FIR was registered"
        }
    },

    # Post-arrest Bail
    "Post-arrest bail": {
        "applicant_name": {
            "maps_to": ["NAME OF APPLICANT/PETITIONER", "APPLICANT'S NAME", "NAME"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "father_husband_name": {
            "maps_to": ["FATHER/HUSBAND'S NAME"],
            "label": "Father's or Husband's Name",
            "type": "text",
            "required": True,
            "description": "Enter your father's or husband's full name"
        },
        "address": {
            "maps_to": ["FULL ADDRESS", "ADDRESS", "PERMANENT ADDRESS"],
            "label": "Your Complete Address",
            "type": "textarea",
            "required": True,
            "description": "Enter your full residential address"
        },
        "contact_number": {
            "maps_to": ["CONTACT NUMBER"],
            "label": "Mobile Number",
            "type": "phone",
            "required": True,
            "description": "Enter your mobile number"
        },
        "fir_number": {
            "maps_to": ["FIR NUMBER"],
            "label": "FIR Number",
            "type": "text",
            "required": True,
            "description": "Enter the FIR number"
        },
        "police_station": {
            "maps_to": ["NAME OF POLICE STATION"],
            "label": "Police Station Name",
            "type": "text",
            "required": True,
            "description": "Name of the police station"
        },
        "city": {
            "maps_to": ["CITY", "DISTRICT"],
            "label": "City",
            "type": "text",
            "required": True,
            "description": "City where case is registered"
        },
        "jail_name": {
            "maps_to": ["NAME OF JAIL", "PRISON"],
            "label": "Jail/Prison Name",
            "type": "text",
            "required": False,
            "description": "Name of jail where you are detained (if applicable)"
        },
        "arrest_date": {
            "maps_to": ["DATE OF ARREST"],
            "label": "Date of Arrest",
            "type": "date",
            "required": False,
            "description": "Date when you were arrested"
        },
        "case_details": {
            "maps_to": ["SUMMARY OF ALLEGATIONS", "BRIEF FACTS"],
            "label": "Brief Description of the Case",
            "type": "textarea",
            "required": True,
            "description": "Briefly describe the case in simple words"
        }
    },

    # FIR Complaint
    "FIR  Complaint Related": {
        "complainant_name": {
            "maps_to": ["NAME OF COMPLAINANT", "PETITIONER 1 NAME", "NAME OF PETITIONER 1"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "father_husband_name": {
            "maps_to": ["FATHER/HUSBAND'S NAME", "FATHER/HUSBAND'S NAME (FOR PETITIONER 1)"],
            "label": "Father's or Husband's Name",
            "type": "text",
            "required": True,
            "description": "Enter your father's or husband's full name"
        },
        "address": {
            "maps_to": ["PERMANENT ADDRESS", "CURRENT ADDRESS", "ADDRESS"],
            "label": "Your Complete Address",
            "type": "textarea",
            "required": True,
            "description": "Enter your full residential address"
        },
        "contact_number": {
            "maps_to": ["CONTACT NUMBER"],
            "label": "Mobile Number",
            "type": "phone",
            "required": True,
            "description": "Enter your mobile number"
        },
        "accused_name": {
            "maps_to": ["NAME OF ACCUSED", "RESPONDENT NAME"],
            "label": "Name of the Accused Person",
            "type": "text",
            "required": False,
            "description": "Name of the person you are filing complaint against"
        },
        "incident_details": {
            "maps_to": ["SUMMARY OF ALLEGATIONS", "PROVIDE A CONCISE, 2-3 SENTENCE SUMMARY OF THE ALLEGATION MADE IN THE FIR"],
            "label": "What Happened?",
            "type": "textarea",
            "required": True,
            "description": "Describe the incident in simple words - what happened, when, and where"
        },
        "incident_date": {
            "maps_to": ["DATE OF INCIDENT", "DATE OF ALLEGED INCIDENT"],
            "label": "When did this happen?",
            "type": "date",
            "required": False,
            "description": "Date when the incident occurred"
        },
        "incident_location": {
            "maps_to": ["LOCATION", "PLACE OF INCIDENT"],
            "label": "Where did this happen?",
            "type": "text",
            "required": False,
            "description": "Location or address where incident occurred"
        },
        "police_station": {
            "maps_to": ["NAME OF POLICE STATION"],
            "label": "Police Station",
            "type": "text",
            "required": True,
            "description": "Name of the police station where you want to file FIR"
        },
        "city": {
            "maps_to": ["CITY", "DISTRICT"],
            "label": "City",
            "type": "text",
            "required": True,
            "description": "City where incident occurred"
        }
    },

    # Legal Notices
    "Legal notices": {
        "sender_name": {
            "maps_to": ["NAME OF CLIENT", "NAME OF SENDER"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "sender_address": {
            "maps_to": ["ADDRESS OF CLIENT", "SENDER ADDRESS"],
            "label": "Your Complete Address",
            "type": "textarea",
            "required": True,
            "description": "Enter your full residential address"
        },
        "sender_contact": {
            "maps_to": ["CONTACT NUMBER"],
            "label": "Mobile Number",
            "type": "phone",
            "required": True,
            "description": "Enter your mobile number"
        },
        "recipient_name": {
            "maps_to": ["NAME OF RECIPIENT", "ADDRESSEE NAME"],
            "label": "Name of Person You're Sending Notice To",
            "type": "text",
            "required": True,
            "description": "Full name of the person/party you're sending this notice to"
        },
        "recipient_address": {
            "maps_to": ["ADDRESS OF RECIPIENT", "ADDRESSEE ADDRESS"],
            "label": "Their Complete Address",
            "type": "textarea",
            "required": True,
            "description": "Complete address of the recipient"
        },
        "issue_description": {
            "maps_to": ["DESCRIPTION OF ISSUE", "MATTER", "SUBJECT MATTER"],
            "label": "What is the Issue?",
            "type": "textarea",
            "required": True,
            "description": "Describe the issue or dispute in simple words"
        },
        "demand": {
            "maps_to": ["DEMAND", "RELIEF SOUGHT"],
            "label": "What do you want them to do?",
            "type": "textarea",
            "required": True,
            "description": "What action do you want the recipient to take? (e.g., return money, stop doing something, etc.)"
        },
        "deadline_days": {
            "maps_to": ["NUMBER OF DAYS", "TIME LIMIT"],
            "label": "Response Deadline (in days)",
            "type": "text",
            "required": False,
            "description": "How many days to give for response? (typically 7-15 days)"
        }
    },

    # Power of Attorney
    "Power of Attorney (Lawyer)": {
        "client_name": {
            "maps_to": ["NAME OF CLIENT", "PRINCIPAL NAME"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "client_father_name": {
            "maps_to": ["FATHER/HUSBAND'S NAME"],
            "label": "Father's or Husband's Name",
            "type": "text",
            "required": True,
            "description": "Enter your father's or husband's name"
        },
        "client_address": {
            "maps_to": ["ADDRESS OF CLIENT", "FULL ADDRESS"],
            "label": "Your Complete Address",
            "type": "textarea",
            "required": True,
            "description": "Enter your full residential address"
        },
        "client_cnic": {
            "maps_to": ["CNIC NUMBER", "CNIC"],
            "label": "Your CNIC Number",
            "type": "text",
            "required": True,
            "description": "Enter your 13-digit CNIC number (e.g., 12345-1234567-1)"
        },
        "lawyer_name": {
            "maps_to": ["NAME OF ADVOCATE", "LAWYER NAME"],
            "label": "Lawyer's Full Name",
            "type": "text",
            "required": True,
            "description": "Full name of the lawyer you're appointing"
        },
        "lawyer_license": {
            "maps_to": ["BAR COUNCIL NUMBER"],
            "label": "Lawyer's License Number",
            "type": "text",
            "required": False,
            "description": "Bar council enrollment number (if known)"
        },
        "case_reference": {
            "maps_to": ["CASE TITLE", "MATTER"],
            "label": "Case Details",
            "type": "textarea",
            "required": False,
            "description": "Brief description of the case/matter (optional)"
        }
    },

    # Affidavits
    "Affidavits": {
        "deponent_name": {
            "maps_to": ["NAME OF DEPONENT", "AFFIANT NAME"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "father_husband_name": {
            "maps_to": ["FATHER/HUSBAND'S NAME"],
            "label": "Father's or Husband's Name",
            "type": "text",
            "required": True,
            "description": "Enter your father's or husband's name"
        },
        "address": {
            "maps_to": ["FULL ADDRESS", "ADDRESS"],
            "label": "Your Complete Address",
            "type": "textarea",
            "required": True,
            "description": "Enter your full residential address"
        },
        "age": {
            "maps_to": ["AGE"],
            "label": "Your Age",
            "type": "text",
            "required": False,
            "description": "Enter your age in years"
        },
        "occupation": {
            "maps_to": ["OCCUPATION", "PROFESSION"],
            "label": "Your Occupation/Profession",
            "type": "text",
            "required": False,
            "description": "What do you do? (e.g., teacher, business, etc.)"
        },
        "affidavit_purpose": {
            "maps_to": ["PURPOSE", "SUBJECT MATTER"],
            "label": "Purpose of Affidavit",
            "type": "textarea",
            "required": True,
            "description": "Why are you making this affidavit? What is it for?"
        },
        "facts_statement": {
            "maps_to": ["FACTS", "STATEMENT", "CONTENTS"],
            "label": "Statement of Facts",
            "type": "textarea",
            "required": True,
            "description": "State the facts you want to declare under oath (keep it simple and truthful)"
        }
    },

    # Cyber Crime Bail
    "Cyber crime bail petition (special category)": {
        "applicant_name": {
            "maps_to": ["NAME OF APPLICANT/PETITIONER", "NAME"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "father_husband_name": {
            "maps_to": ["FATHER/HUSBAND'S NAME"],
            "label": "Father's or Husband's Name",
            "type": "text",
            "required": True,
            "description": "Enter your father's or husband's name"
        },
        "address": {
            "maps_to": ["FULL ADDRESS", "ADDRESS"],
            "label": "Your Complete Address",
            "type": "textarea",
            "required": True,
            "description": "Enter your full residential address"
        },
        "contact_number": {
            "maps_to": ["CONTACT NUMBER"],
            "label": "Mobile Number",
            "type": "phone",
            "required": True,
            "description": "Enter your mobile number"
        },
        "fir_number": {
            "maps_to": ["FIR NUMBER"],
            "label": "FIR Number",
            "type": "text",
            "required": True,
            "description": "Enter the FIR number"
        },
        "fia_circle": {
            "maps_to": ["FIA CIRCLE", "CYBER CRIME WING"],
            "label": "FIA Cyber Crime Circle",
            "type": "text",
            "required": True,
            "description": "Name of FIA circle (e.g., FIA Cyber Crime Circle Karachi)"
        },
        "city": {
            "maps_to": ["CITY", "DISTRICT"],
            "label": "City",
            "type": "text",
            "required": True,
            "description": "City where case is registered"
        },
        "case_details": {
            "maps_to": ["SUMMARY OF ALLEGATIONS", "BRIEF FACTS"],
            "label": "Brief Description of the Case",
            "type": "textarea",
            "required": True,
            "description": "Briefly describe the cyber crime allegation"
        }
    },

    # Consolidation of Cases
    "Consolidation of cases": {
        "applicant_name": {
            "maps_to": ["APPLICANT_NAME", "LAWYER_NAME"],
            "label": "Your Full Name (or Lawyer's Name)",
            "type": "text",
            "required": True,
            "description": "Enter your complete name or your lawyer's name"
        },
        "case_title": {
            "maps_to": ["CASE_TITLE", "CASE_TITLE_1", "CASE_TITLE_2", "CASE_TITLE_3", "SUBJECT_MATTER"],
            "label": "Case Title/Subject",
            "type": "text",
            "required": True,
            "description": "Title or subject matter of the case"
        },
        "court_name": {
            "maps_to": ["COURT_NAME", "COURT_NAME_1", "COURT_NAME_2", "COURT_NAME_3"],
            "label": "Court Name",
            "type": "text",
            "required": True,
            "description": "Name of the court (e.g., Sessions Court Karachi)"
        },
        "city": {
            "maps_to": ["CITY_DISTRICT", "LOCATION_1", "LOCATION_2", "LOCATION_3"],
            "label": "City/District",
            "type": "text",
            "required": True,
            "description": "City or district where court is located"
        },
        "hearing_date": {
            "maps_to": ["HEARING_DATE_1", "HEARING_DATE_2", "HEARING_DATE_3", "DOCUMENT_DATE"],
            "label": "Hearing Date",
            "type": "date",
            "required": False,
            "description": "Date of hearing or document date"
        },
        "enrollment_number": {
            "maps_to": ["ENROLLMENT_NUMBER"],
            "label": "Lawyer's Enrollment Number",
            "type": "text",
            "required": False,
            "description": "Bar council enrollment number (if applicable)"
        }
    },

    # Court & Case Management Applications
    "Court & Case Management Applications": {
        "applicant_name": {
            "maps_to": ["APPLICANT_NAME", "NAME OF APPLICANT"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "case_details": {
            "maps_to": ["CASE_TITLE", "SUBJECT_MATTER", "APPLICATION_PURPOSE"],
            "label": "What is your application about?",
            "type": "textarea",
            "required": True,
            "description": "Briefly describe the purpose of your application"
        },
        "court_name": {
            "maps_to": ["COURT_NAME"],
            "label": "Court Name",
            "type": "text",
            "required": True,
            "description": "Name of the court"
        },
        "city": {
            "maps_to": ["CITY_DISTRICT", "CITY"],
            "label": "City",
            "type": "text",
            "required": True,
            "description": "City where court is located"
        },
        "case_number": {
            "maps_to": ["CASE_NUMBER", "CASE NO"],
            "label": "Case Number",
            "type": "text",
            "required": False,
            "description": "Your case number (if you have one)"
        }
    },

    # Cancellation of Bail Applications
    "Cancellation of bail applications": {
        "applicant_name": {
            "maps_to": ["NAME OF APPLICANT", "COMPLAINANT NAME"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "accused_name": {
            "maps_to": ["NAME OF ACCUSED", "RESPONDENT NAME"],
            "label": "Name of the Accused (whose bail to cancel)",
            "type": "text",
            "required": True,
            "description": "Name of person whose bail you want cancelled"
        },
        "fir_number": {
            "maps_to": ["FIR NUMBER"],
            "label": "FIR Number",
            "type": "text",
            "required": True,
            "description": "FIR number of the case"
        },
        "city": {
            "maps_to": ["CITY", "DISTRICT"],
            "label": "City",
            "type": "text",
            "required": True,
            "description": "City where case is registered"
        },
        "reasons": {
            "maps_to": ["REASONS FOR CANCELLATION", "GROUNDS"],
            "label": "Why should bail be cancelled?",
            "type": "textarea",
            "required": True,
            "description": "Reasons why bail should be cancelled (e.g., threatening witnesses, absconding)"
        }
    },

    # Contempt of Court Petitions
    "Contempt of court petitions": {
        "petitioner_name": {
            "maps_to": ["NAME OF PETITIONER"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "respondent_name": {
            "maps_to": ["NAME OF RESPONDENT", "CONTEMNER NAME"],
            "label": "Name of Person in Contempt",
            "type": "text",
            "required": True,
            "description": "Name of the person who committed contempt"
        },
        "court_name": {
            "maps_to": ["COURT_NAME"],
            "label": "Court Name",
            "type": "text",
            "required": True,
            "description": "Name of the court"
        },
        "city": {
            "maps_to": ["CITY", "DISTRICT"],
            "label": "City",
            "type": "text",
            "required": True,
            "description": "City where court is located"
        },
        "contempt_details": {
            "maps_to": ["DETAILS OF CONTEMPT", "ACT OF CONTEMPT"],
            "label": "What happened?",
            "type": "textarea",
            "required": True,
            "description": "Describe the act of contempt - what did the person do?"
        }
    },

    # Article 199 Writ Petitions
    "Article 199 of Constitution Writ petitions for fundamental rights": {
        "petitioner_name": {
            "maps_to": ["NAME OF PETITIONER"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "address": {
            "maps_to": ["ADDRESS", "FULL ADDRESS"],
            "label": "Your Complete Address",
            "type": "textarea",
            "required": True,
            "description": "Enter your full residential address"
        },
        "respondent_name": {
            "maps_to": ["RESPONDENT NAME", "DEPARTMENT NAME"],
            "label": "Name of Respondent/Department",
            "type": "text",
            "required": True,
            "description": "Government department or official against whom petition is filed"
        },
        "city": {
            "maps_to": ["CITY"],
            "label": "City",
            "type": "text",
            "required": True,
            "description": "City where High Court is located"
        },
        "fundamental_right": {
            "maps_to": ["FUNDAMENTAL RIGHT VIOLATED", "ARTICLE NUMBER"],
            "label": "Which right was violated?",
            "type": "text",
            "required": True,
            "description": "Which fundamental right was violated? (e.g., Article 10A - Fair Trial)"
        },
        "violation_details": {
            "maps_to": ["DETAILS OF VIOLATION", "FACTS"],
            "label": "What happened?",
            "type": "textarea",
            "required": True,
            "description": "Describe how your fundamental right was violated"
        },
        "relief_sought": {
            "maps_to": ["RELIEF SOUGHT", "PRAYER"],
            "label": "What do you want the court to do?",
            "type": "textarea",
            "required": True,
            "description": "What relief/action do you want from the court?"
        }
    },

    # Recovery of Detained Property (491 CrPC)
    "Recovery of detained property (491 CrPC)": {
        "applicant_name": {
            "maps_to": ["NAME OF APPLICANT"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "address": {
            "maps_to": ["ADDRESS"],
            "label": "Your Complete Address",
            "type": "textarea",
            "required": True,
            "description": "Enter your full residential address"
        },
        "property_description": {
            "maps_to": ["DESCRIPTION OF PROPERTY", "PROPERTY DETAILS"],
            "label": "What property was detained?",
            "type": "textarea",
            "required": True,
            "description": "Describe the property that was detained by police"
        },
        "fir_number": {
            "maps_to": ["FIR NUMBER", "CASE NUMBER"],
            "label": "FIR/Case Number",
            "type": "text",
            "required": False,
            "description": "FIR or case number (if applicable)"
        },
        "police_station": {
            "maps_to": ["POLICE STATION", "NAME OF POLICE STATION"],
            "label": "Police Station",
            "type": "text",
            "required": True,
            "description": "Name of police station holding the property"
        },
        "city": {
            "maps_to": ["DISTRICT___CITY", "CITY"],
            "label": "City/District",
            "type": "text",
            "required": True,
            "description": "City or district"
        }
    },

    # Registration of Criminal Cases (22A-22B CrPC)
    "Registration of criminal cases under Sections 22A - 22B CrPC": {
        "complainant_name": {
            "maps_to": ["NAME OF COMPLAINANT"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "address": {
            "maps_to": ["ADDRESS"],
            "label": "Your Complete Address",
            "type": "textarea",
            "required": True,
            "description": "Enter your full residential address"
        },
        "incident_details": {
            "maps_to": ["DETAILS OF INCIDENT", "COMPLAINT DETAILS"],
            "label": "What happened?",
            "type": "textarea",
            "required": True,
            "description": "Describe the incident you want to register as FIR"
        },
        "police_station": {
            "maps_to": ["POLICE STATION"],
            "label": "Police Station",
            "type": "text",
            "required": True,
            "description": "Police station where you want to register the case"
        },
        "city": {
            "maps_to": ["DISTRICT___CITY", "CITY"],
            "label": "City/District",
            "type": "text",
            "required": True,
            "description": "City or district"
        },
        "refusal_date": {
            "maps_to": ["DATE OF REFUSAL"],
            "label": "When did police refuse to register FIR?",
            "type": "date",
            "required": False,
            "description": "Date when police refused to register your complaint"
        }
    },

    # Transfer of Case
    "Transfer of case": {
        "applicant_name": {
            "maps_to": ["NAME OF APPLICANT"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "case_number": {
            "maps_to": ["CASE NUMBER"],
            "label": "Case Number",
            "type": "text",
            "required": True,
            "description": "Current case number"
        },
        "current_court": {
            "maps_to": ["CURRENT COURT", "PRESENT COURT"],
            "label": "Current Court Name",
            "type": "text",
            "required": True,
            "description": "Name of court where case is currently pending"
        },
        "transfer_to_court": {
            "maps_to": ["TRANSFEREE COURT", "DESIRED COURT"],
            "label": "Transfer to Which Court?",
            "type": "text",
            "required": True,
            "description": "Name of court where you want case transferred"
        },
        "city": {
            "maps_to": ["CITY", "DISTRICT"],
            "label": "City",
            "type": "text",
            "required": True,
            "description": "City"
        },
        "reasons_for_transfer": {
            "maps_to": ["GROUNDS FOR TRANSFER", "REASONS"],
            "label": "Why should the case be transferred?",
            "type": "textarea",
            "required": True,
            "description": "Reasons for requesting transfer (e.g., bias, convenience)"
        }
    },

    # Legal Certificates
    "Legal certificates": {
        "applicant_name": {
            "maps_to": ["NAME OF APPLICANT"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "address": {
            "maps_to": ["ADDRESS"],
            "label": "Your Complete Address",
            "type": "textarea",
            "required": True,
            "description": "Enter your full residential address"
        },
        "certificate_type": {
            "maps_to": ["TYPE OF CERTIFICATE", "CERTIFICATE PURPOSE"],
            "label": "What type of certificate?",
            "type": "text",
            "required": True,
            "description": "Type of certificate needed (e.g., character certificate, domicile)"
        },
        "purpose": {
            "maps_to": ["PURPOSE", "REASON FOR CERTIFICATE"],
            "label": "Why do you need this certificate?",
            "type": "textarea",
            "required": True,
            "description": "Purpose for which certificate is needed"
        }
    },

    # Revision Petitions
    "Revision petitions (Section 476)": {
        "petitioner_name": {
            "maps_to": ["NAME OF PETITIONER", "REVISIONIST NAME"],
            "label": "Your Full Name",
            "type": "text",
            "required": True,
            "description": "Enter your complete name"
        },
        "father_husband_name": {
            "maps_to": ["FATHER/HUSBAND'S NAME"],
            "label": "Father's or Husband's Name",
            "type": "text",
            "required": True,
            "description": "Enter your father's or husband's name"
        },
        "address": {
            "maps_to": ["FULL ADDRESS", "ADDRESS"],
            "label": "Your Complete Address",
            "type": "textarea",
            "required": True,
            "description": "Enter your full residential address"
        },
        "contact_number": {
            "maps_to": ["CONTACT NUMBER"],
            "label": "Mobile Number",
            "type": "phone",
            "required": True,
            "description": "Enter your mobile number"
        },
        "case_number": {
            "maps_to": ["CASE NUMBER", "CASE NO"],
            "label": "Original Case Number",
            "type": "text",
            "required": True,
            "description": "The case number of the original trial"
        },
        "court_name": {
            "maps_to": ["NAME OF COURT", "TRIAL COURT"],
            "label": "Court Name",
            "type": "text",
            "required": True,
            "description": "Name of the court that gave the order"
        },
        "order_date": {
            "maps_to": ["DATE OF ORDER", "DATE OF JUDGMENT"],
            "label": "Date of Court Order",
            "type": "date",
            "required": True,
            "description": "Date when the court passed the order"
        },
        "grounds_for_revision": {
            "maps_to": ["GROUNDS", "GROUNDS FOR REVISION"],
            "label": "Why do you want revision?",
            "type": "textarea",
            "required": True,
            "description": "Explain in simple words why the court decision should be reviewed"
        }
    }
}

# Auto-fill values that can be derived or have sensible defaults
AUTO_FILL_VALUES = {
    "NAME OF HIGH COURT": "Lahore High Court",
    "YEAR": "2024",
    "BAR COUNCIL NUMBER": "[Lawyer's License Number]",
    "NAME OF ADVOCATE": "[Your Lawyer's Name]",
    "OFFICE ADDRESS": "[Lawyer's Office Address]",
    "EMAIL ADDRESS": "[Email Address]",

    # Fill common legal phrases
    "DOES / DO": "does",
    "HAS / HAS NOT": "has",
    "OR": "or",
    "and others": "",
    "Caste, if applicable": "",
    "City, if applicable": "",

    # Technical fields users shouldn't need to fill
    "ADD OTHER RESPONDENTS IF APPLICABLE": "",
    "ADD MORE PETITIONERS IF APPLICABLE": "",
    "ADD OTHER OFFICIAL RESPONDENTS IF APPLICABLE, E.G., \"THE PROVINCIAL INVESTIGATION BRANCH (PIB)\"": "",
    "APPLICABLE ONLY IF PREVIOUS BAIL WAS SOUGHT": "",

    # Default to common values
    "REJECTED / DISPOSED OF": "pending",
    "GRANTED / LISTED": "to be granted",
    "SETTLED / RESOLVED / WITHDRAWN": "pending resolution",
}

def get_simplified_fields(template_name: str):
    """
    Get simplified field configuration for a template

    Args:
        template_name: Name of the template file (without .docx)

    Returns:
        Dict of simplified fields with metadata
    """
    # Remove .docx extension if present
    template_name = template_name.replace('.docx', '')

    return SIMPLIFIED_FIELDS.get(template_name, {})

def map_simplified_to_original(template_name: str, simplified_data: dict):
    """
    Map simplified user input to original template placeholders

    Args:
        template_name: Name of the template
        simplified_data: Dict with simplified field keys and values

    Returns:
        Dict with original placeholder names and values
    """
    template_name = template_name.replace('.docx', '')
    config = SIMPLIFIED_FIELDS.get(template_name, {})

    result = {}

    # Map simplified fields to all their original field names
    for simple_key, value in simplified_data.items():
        if simple_key in config:
            field_config = config[simple_key]
            # Fill all mapped original fields with the same value
            for original_field in field_config.get('maps_to', []):
                result[original_field] = value

    # Add auto-fill values for fields user doesn't need to fill
    result.update(AUTO_FILL_VALUES)

    return result

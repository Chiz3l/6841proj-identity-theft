from typing import Dict, Any
from collections import Counter

class DocumentClassifier:
    def __init__(self):
        # categories and identifying words for each catagory
        self.categories = {
            "IDENTIFICATION": [
                "passport", "driver license", "identity", "date of birth", "dob", "address",
                "drivers license", "license number", "national id", "social security", "ssn", 
                "medicare", "full name", "surname", "given name", "citizenship", 
                "visa", "place of birth", "gender", "nationality", "expiry date", "issuing authority"
            ],
            "FINANCIAL": [
                "invoice", "bank statement", "tax return", "salary", "credit card", "payment", "amount due", "balance",
                "account number", "bsb", "iban", "swift", "routing number", "subtotal", 
                "tax", "gst", "vat", "total due", "receipt", "remittance", 
                "transaction", "billing", "payslip", "remuneration", "gross income", "net pay"
            ],
            "LEGAL": [
                "contract", "agreement", "confidential", "terms and conditions", "liability", "nda", "signature",
                "non-disclosure", "party", "parties", "governing law", "jurisdiction", 
                "indemnity", "termination", "clause", "statutory", "power of attorney", 
                "witness", "executed by", "hereby", "whereas", "dispute resolution"
            ],
            "TECHNICAL": [
                "source code", "architecture", "specification", "api", "database", "credentials", "config",
                "environment variable", "secret key", "api key", "access token", "bearer token", 
                "endpoint", "deployment", "infrastructure", "schema", "repository", 
                "git", "ssh key", "connection string", "payload", "framework", "documentation"
            ]
        }
    # classifies the document depending on the input text
    def classify(self, text):
        # preproccessing the text and setting up the classification tracker
        text_lower = text.lower()
        scores = {}
        for catagory in self.categories:
            scores[catagory] = 0
        keywords_found = []
        
        # this just blindly checks if any of the words in the catagories are contained in the document text
        for catagory, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[catagory] += 2
                    keywords_found.append(keyword)
                    
        keyword_counter = Counter(keywords_found)

        # Determine highest scoring category
        best_cat = max(scores, key=scores.get)
        max_score = scores[best_cat]
        
        category = best_cat if max_score >= 2 else "GENERAL_DOCUMENT"
        confidence = round(min(max_score / 10.0, 1.0), 2)

        return {
            "category": category,
            "confidence": confidence,
            "keyword_counter": keyword_counter,
            "char_count": len(text),
            "extracted_preview": text[:200].strip()
        }
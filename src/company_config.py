from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class CompanyConfig:
    name: str
    description: str
    industry: str
    website: str
    knowledge_base_urls: List[str]
    business_hours: Dict[str, Dict[str, str]]
    timezone: str
    support_email: str
    products_services: List[Dict[str, str]]
    faqs: List[Dict[str, str]]
    policies: Dict[str, str]
    greeting_message: str
    farewell_message: str
    escalation_message: str
    # Optional fields with defaults come last
    tone: str = "professional"  # professional, casual, friendly, formal
    phone_number: Optional[str] = None
    custom_instructions: Optional[str] = None
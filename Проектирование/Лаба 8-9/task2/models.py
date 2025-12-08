from dataclasses import dataclass

ESMI_TYPES = ["радио", "телевидение", "интернет"]
AUTHOR_ROLES = ["депутат", "корреспондент", "работник администрации", "журналист", "активист партии", "другое"]

@dataclass
class Author:
    id: int
    full_name: str
    role: str

@dataclass
class ESMIRecord:
    id: int
    esmi_type: str          # радио, телевидение, интернет
    channel: str
    date: str               # YYYY-MM-DD
    program: str            # название передачи
    topic: str
    author_id: int
    annotation: str
    notes: str
    duration_min: int
    rating: float

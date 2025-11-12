from typing import Optional
from app.models.language import Language

class LocalizationService:
    def __init__(self):
        # For now, simple implementation
        self.languages = {
            "en": {"name": "English", "direction": "ltr"},
            "es": {"name": "Spanish", "direction": "ltr"},
            "ar": {"name": "Arabic", "direction": "rtl"}
        }

    def get_language(self, code: str) -> Optional[Dict]:
        return self.languages.get(code)

    def is_rtl(self, code: str) -> bool:
        lang = self.get_language(code)
        return lang and lang["direction"] == "rtl"

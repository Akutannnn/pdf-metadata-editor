from __future__ import annotations
from dataclasses import dataclass, fields
from typing import Optional


@dataclass
class PDFMetadata:
    Title: Optional[str] = None
    Author: Optional[str] = None
    Subject: Optional[str] = None
    Keywords: Optional[str] = None
    Creator: Optional[str] = None
    Producer: Optional[str] = None
    CreationDate: Optional[str] = None
    ModDate: Optional[str] = None

    def to_dict(self) -> dict[str, Optional[str]]:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, Optional[str]]) -> PDFMetadata:
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})

    def copy(self) -> PDFMetadata:
        return PDFMetadata(**self.to_dict())

    def equals(self, other: PDFMetadata) -> bool:
        return self.to_dict() == other.to_dict()

    def display_value(self, key: str) -> str:
        val = getattr(self, key, None)
        return val if val is not None else ""

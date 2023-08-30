from dataclasses import dataclass
    
@dataclass
class Article:
    group: str
    title: str
    desc: str
    url: str
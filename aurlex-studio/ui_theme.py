"""Aurlex Studio visual theme and marketing UI helpers."""
AURLEX_PAGE_ACCENTS = {
    "IDEA": ("#7C3AED","#22D3EE"), "RESEARCH": ("#06B6D4","#34D399"),
    "FORMAT": ("#F59E0B","#F97316"), "STORY": ("#EC4899","#8B5CF6"),
    "ANIMATION": ("#EF4444","#F59E0B"), "VERIFY": ("#10B981","#06B6D4"),
    "PUBLISH": ("#F43F5E","#A855F7"),
}

def page_gradient(label):
    a,b=AURLEX_PAGE_ACCENTS.get(label,("#7C3AED","#22D3EE"))
    return f"linear-gradient(115deg,{a}22,rgba(12,17,35,.86) 48%,{b}20)"

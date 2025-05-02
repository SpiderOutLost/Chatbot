import spacy
nlp = spacy.load("ru_core_news_sm")

def extract_entities(text: str) -> dict:
    doc = nlp(text)
    return {
        label: [ent.text for ent in doc.ents if ent.label_ == label]
        for label in ["PER", "LOC", "DATE", "ORG"]
    }

def format_entities(entities: dict) -> str:
    parts = []
    for label, names in entities.items():
        if names:
            label_name = {
                "PER": "Люди",
                "LOC": "Места",
                "DATE": "Даты",
                "ORG": "Организации"
            }[label]
            parts.append(f"{label_name}: {', '.join(names)}")
    return "\n".join(parts) if parts else "Не удалось распознать сущности в тексте."
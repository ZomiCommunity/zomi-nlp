# zomi-nlp/zomi_nlp/native/ner.py
"""Rule-based Named Entity Recognition for Zomi language."""

from dataclasses import dataclass
from typing import Optional

from zomi_nlp.core.doc import ZomiDoc
from zomi_nlp.native.tokenizer import ZomiTokenizer


@dataclass
class Entity:
    """Named entity."""
    text: str
    type: str
    start: int
    end: int
    confidence: float = 1.0


class ZomiNER:
    """Rule-based Named Entity Recognition for Zomi.

    Entity types:
    - PERSON: People names (Pasian, Moses, David, Paulam)
    - PERSON_HONORIFIC: Titles (Pipa, Nu, Pa, Pi)
    - LOCATION: Places (leitang, Galilee, Jerusalem)
    - ORGANIZATION: Groups, institutions (sanginn, khopi)
    - DATE: Time references (tuni, zing, nisim)
    - NUMERIC: Numbers, quantities (khat, ni, thum)
    - GPE: Geo-political entities (Tedim, Falam, Kalay)
    """

    # Person names (common Zomi names)
    PERSON_NAMES: set[str] = {
        "Pasian", "Moses", "David", "Peter", "John", "James",
        "Joseph", "Abraham", "Isaac", "Jacob", "Samuel", "Elijah", "Jeremiah",
        "Isaiah", "Ezekiel", "Daniel", "Hosea", "Amos", "Jonah", "Malachi",
        "Zechariah", "Nehemiah", "Ezra", "Ruth", "Esther", "Hannah", "Mary",
        "Martha", "Lazarus", "Timothy", "Titus", "Silas", "Luke", "Mark",
        "Matthew", "Andrew", "Philip", "Thomas", "Simon", "Judas",
         "Paul",
    }

    # Personal honorifics (removed "Sian" as it was causing over-matching)
    PERSON_HONORIFICS: set[str] = {
        "Pipa", "Nu", "Pa", "Pi", "Pu", "Ukpi", "Lungal", "Tawng", "Khamtuan",
        "Pastor", "Evangelist", "Deacon", "Elder", "Teacher", "Dr", "Prof",
    }

    # Locations (places)
    LOCATIONS: set[str] = {
        "leitang", "Galilee", "Jerusalem", "Bethlehem", "Nazareth", "Capernaum",
        "Egypt", "Babylon", "Rome", "Judea", "Samaria", "Damascus", "Antioch",
        "Ephesus", "Corinth", "Thessalonica", "Philippi", "Colossae",
    }

    # GPE (Geo-political entities)
    GPE_NAMES: set[str] = {
        "Tedim", "Falam", "Kalay", "Mandalay", "Yangon", "Rangoon",
        "Churachandpur", "Imphal", "Lamka", "Moreh", "Mizoram", "Manipur",
        "Assam", "Nagaland", "Shillong", "Guwahati", "Silchar", "Aizawl",
        "Myanmar", "Burma", "India", "Bangladesh",
    }

    # Organizations
    ORGANIZATIONS: set[str] = {
        "sanginn", "khopi", "ZBC", "Zomi Baptist", "ZCC", "Zomi Christian",
        "ZRA", "Zomi Revolutionary", "ZYP", "Zomi Youth", "ZSU", "Zomi Students",
        "Zomi Council", "Zomi Congress", "Zomi National", "Zomi Innkuan",
    }

    # Date/time indicators
    DATE_INDICATORS: set[str] = {
        "tuni", "khawldal", "zing", "nisa", "nitak", "zingsang", "niphua",
        "kum", "tha", "ni", "khaw", "khawsim", "khawman",
    }

    # Numeric words
    NUMERIC_WORDS: set[str] = {
        "khat", "ni", "thum", "li", "nga", "guk", "sagi", "giat", "ku", "tam",
        "sawm", "sawl", "zale", "ng", "sen", "nua", "sa", "tua", "khua",
    }

    def __init__(self, tokenizer: Optional[ZomiTokenizer] = None):
        """Initialize rule-based NER."""
        self.tokenizer = tokenizer or ZomiTokenizer()

        # Merge location sets for easier lookup
        self.ALL_LOCATIONS: set[str] = self.LOCATIONS | self.GPE_NAMES

    def extract(self, text: str) -> list[Entity]:
        """Extract named entities from text."""
        tokens = self.tokenizer.tokenize(text)
        print(f"Tokens for NER: {tokens}")
        entities = []

        # 1. Gazetteer-based extraction
        entities.extend(self._extract_from_gazetteers(tokens))
        print(f"Entities after gazetteer extraction: {entities}")

        # 2. Context-based extraction
        entities.extend(self._extract_from_context(tokens))
        print(f"Entities after context extraction: {entities}")

        # 3. Merge overlapping entities
        entities = self._merge_entities(entities)
        print(f"Entities after merging: {entities}")
        entities.sort(key=lambda e: e.start)

        return entities

    # def _extract_from_gazetteers(self, tokens: list[str]) -> list[Entity]:
    #     """Extract entities using gazetteer lists (single token only)."""
    #     entities = []
    #     used_positions: set[int] = set()

    #     for i, token in enumerate(tokens):
    #         if i in used_positions:
    #             continue

    #         # Check person names
    #         if token in self.PERSON_NAMES:
    #             entities.append(Entity(
    #                 text=token,
    #                 type="PERSON",
    #                 start=i,
    #                 end=i,
    #                 confidence=0.95
    #             ))
    #             used_positions.add(i)

    #         # Check GPE/locations
    #         elif token in self.GPE_NAMES:
    #             entities.append(Entity(
    #                 text=token,
    #                 type="GPE",
    #                 start=i,
    #                 end=i,
    #                 confidence=0.9
    #             ))
    #             used_positions.add(i)

    #         elif token in self.LOCATIONS:
    #             entities.append(Entity(
    #                 text=token,
    #                 type="LOCATION",
    #                 start=i,
    #                 end=i,
    #                 confidence=0.9
    #             ))
    #             used_positions.add(i)

    #         # Check organizations
    #         elif token in self.ORGANIZATIONS:
    #             entities.append(Entity(
    #                 text=token,
    #                 type="ORGANIZATION",
    #                 start=i,
    #                 end=i,
    #                 confidence=0.9
    #             ))
    #             used_positions.add(i)

    #         # Check numeric words
    #         elif token in self.NUMERIC_WORDS or token.isdigit():
    #             entities.append(Entity(
    #                 text=token,
    #                 type="NUMERIC",
    #                 start=i,
    #                 end=i,
    #                 confidence=0.95
    #             ))
    #             used_positions.add(i)

    #         # Check date indicators
    #         elif token in self.DATE_INDICATORS:
    #             # Look ahead for number
    #             if i + 1 < len(tokens) and (tokens[i + 1].isdigit() or \
    #                                          tokens[i + 1] in self.NUMERIC_WORDS):
    #                 entities.append(Entity(
    #                     text=f"{token} {tokens[i + 1]}",
    #                     type="DATE",
    #                     start=i,
    #                     end=i + 1,
    #                     confidence=0.9
    #                 ))
    #                 used_positions.add(i)
    #                 used_positions.add(i + 1)
    #             else:
    #                 entities.append(Entity(
    #                     text=token,
    #                     type="DATE",
    #                     start=i,
    #                     end=i,
    #                     confidence=0.8
    #                 ))
    #                 used_positions.add(i)

    #     return entities
    def _extract_from_gazetteers(self, tokens: list[str]) -> list[Entity]:
        """Extract entities using gazetteer lists (single token only)."""
        entities = []
        used_positions: set[int] = set()

        for i, token in enumerate(tokens):
            if i in used_positions:
                continue

            # Check person names
            if token in self.PERSON_NAMES:
                entities.append(Entity(
                    text=token,
                    type="PERSON",
                    start=i,
                    end=i,
                    confidence=0.95
                ))
                used_positions.add(i)

            # Check GPE/locations
            elif token in self.GPE_NAMES:
                entities.append(Entity(
                    text=token,
                    type="GPE",
                    start=i,
                    end=i,
                    confidence=0.9
                ))
                used_positions.add(i)

            elif token in self.LOCATIONS:
                entities.append(Entity(
                    text=token,
                    type="LOCATION",
                    start=i,
                    end=i,
                    confidence=0.9
                ))
                used_positions.add(i)

            # Check organizations
            elif token in self.ORGANIZATIONS:
                entities.append(Entity(
                    text=token,
                    type="ORGANIZATION",
                    start=i,
                    end=i,
                    confidence=0.9
                ))
                used_positions.add(i)

            # Check numeric words
            elif token in self.NUMERIC_WORDS or token.isdigit():
                entities.append(Entity(
                    text=token,
                    type="NUMERIC",
                    start=i,
                    end=i,
                    confidence=0.95
                ))
                used_positions.add(i)

            # ✅ ADD THIS: Check date indicators
            elif token in self.DATE_INDICATORS:
                # Look ahead for number or numeric word
                if i + 1 < len(tokens) and (tokens[i + 1].isdigit() or \
                                            tokens[i + 1] in self.NUMERIC_WORDS):
                    entities.append(Entity(
                        text=f"{token} {tokens[i + 1]}",
                        type="DATE",
                        start=i,
                        end=i + 1,
                        confidence=0.9
                    ))
                    used_positions.add(i)
                    used_positions.add(i + 1)
                else:
                    entities.append(Entity(
                        text=token,
                        type="DATE",
                        start=i,
                        end=i,
                        confidence=0.85
                    ))
                    used_positions.add(i)

        return entities

    # def _extract_from_context(self, tokens: list[str]) -> list[Entity]:
    #     """Extract entities using contextual clues."""
    #     entities = []

    #     for i, token in enumerate(tokens):
    #         token_lower = token.lower()

    #         # Rule 1: Honorific + Name (e.g., "Pipa Paulam")
    #         # Only match if next token is NOT already in PERSON_NAMES alone
    #         if token in self.PERSON_HONORIFICS and i + 1 < len(tokens):
    #             next_token = tokens[i + 1]
    #             # Check if next token looks like a name AND not already captured
    #             if (next_token[0].isupper() and
    #                 len(next_token) > 1 and
    #                 next_token not in self.PERSON_NAMES):
    #                 entities.append(Entity(
    #                     text=f"{token} {next_token}",
    #                     type="PERSON",
    #                     start=i,
    #                     end=i + 1,
    #                     confidence=0.95
    #                 ))

    #         # Rule 2: Name before agent marker "in"
    #         # Only if token is capitalized and not an honorific
    #         prev_token = tokens[i - 1] if i > 0 else ""
    #         if (token_lower == "in" and i > 0
    #              and
    #             (prev_token[0].isupper() and
    #                 len(prev_token) > 1 and
    #                 prev_token not in self.PERSON_HONORIFICS) and
    #                 # Check next token is a verb (agent marker)
    #                 i + 1 < len(tokens) and tokens[i + 1] in ["pai", "zoh", "ne", "ci"]
    #         ):
    #                     entities.append(Entity(
    #                         text=prev_token,
    #                         type="PERSON",
    #                         start=i - 1,
    #                         end=i - 1,
    #                         confidence=0.85
    #                     ))

    #         # Rule 3: Location after prepositions
    #         if token_lower in ["in", "pan", "ah"] and i + 1 < len(tokens):
    #             loc_candidate = tokens[i + 1]
    #             if loc_candidate in self.ALL_LOCATIONS:
    #                 entity_type = "GPE" if loc_candidate in self.GPE_NAMES else "LOCATION"
    #                 entities.append(Entity(
    #                     text=loc_candidate,
    #                     type=entity_type,
    #                     start=i + 1,
    #                     end=i + 1,
    #                     confidence=0.9
    #                 ))

    #     return entities
    def _extract_from_context(self, tokens: list[str]) -> list[Entity]:
        """Extract entities using contextual clues."""
        entities = []

        print(f"DEBUG: tokens = {tokens}")  # Temporary debug

        for i, token in enumerate(tokens):
            token_lower = token.lower()

            # Date indicators in context (fallback if gazetteer missed)
            if token_lower in self.DATE_INDICATORS:
                print(f"DEBUG: Found date indicator '{token}' at position {i}")  # Temporary debug
                # Look ahead for number
                if i + 1 < len(tokens) and (tokens[i + 1].isdigit() or \
                                            tokens[i + 1] in self.NUMERIC_WORDS):
                    entities.append(Entity(
                        text=f"{token} {tokens[i + 1]}",
                        type="DATE",
                        start=i,
                        end=i + 1,
                        confidence=0.85
                    ))
                else:
                    entities.append(Entity(
                        text=token,
                        type="DATE",
                        start=i,
                        end=i,
                        confidence=0.8
                    ))

            # Honorific + Name pattern
            if token in self.PERSON_HONORIFICS and i + 1 < len(tokens):
                next_token = tokens[i + 1]
                if (next_token[0].isupper() and
                    len(next_token) > 1 and
                    next_token not in self.PERSON_NAMES):
                    entities.append(Entity(
                        text=f"{token} {next_token}",
                        type="PERSON",
                        start=i,
                        end=i + 1,
                        confidence=0.95
                    ))

            # Name before agent marker
            prev_token = tokens[i - 1] if i > 0 else ""
            if token_lower == "in" and i > 0 and \
                (prev_token[0].isupper() and
                    len(prev_token) > 1 and
                    prev_token not in self.PERSON_HONORIFICS) and \
                    i + 1 < len(tokens) and tokens[i + 1] in ["pai", "zoh", "ne", "ci"]:
                        entities.append(Entity(
                            text=prev_token,
                            type="PERSON",
                            start=i - 1,
                            end=i - 1,
                            confidence=0.85
                        ))

            # Location after prepositions
            if token_lower in ["in", "pan", "ah"] and i + 1 < len(tokens):
                loc_candidate = tokens[i + 1]
                if loc_candidate in self.ALL_LOCATIONS:
                    entity_type = "GPE" if loc_candidate in self.GPE_NAMES else "LOCATION"
                    entities.append(Entity(
                        text=loc_candidate,
                        type=entity_type,
                        start=i + 1,
                        end=i + 1,
                        confidence=0.9
                    ))

        return entities

    def _merge_entities(self, entities: list[Entity]) -> list[Entity]:
        """Merge overlapping or adjacent entities of the SAME TYPE only."""
        if not entities:
            return []

        # Sort by start position
        entities.sort(key=lambda e: (e.start, e.end))

        merged = []
        current = entities[0]

        for next_ent in entities[1:]:
            # Check if overlapping or adjacent
            if next_ent.start <= current.end + 1:
                # Only merge if same type
                if next_ent.type == current.type:
                    current.end = max(current.end, next_ent.end)
                    # Reconstruct text from tokens would be better, but simple join for now
                    if current.end > next_ent.end:
                        current.text = f"{current.text} {next_ent.text}"
                    else:
                        # Keep original text if next entity is fully contained
                        current.text = current.text
                    current.confidence = min(current.confidence, next_ent.confidence)
                else:
                    merged.append(current)
                    current = next_ent
            else:
                merged.append(current)
                current = next_ent

        merged.append(current)
        return merged

    def to_doc(self, doc: ZomiDoc) -> ZomiDoc:
        """Add NER annotations to a ZomiDoc."""
        # Get entities
        entities = self.extract(doc.text)

        # Mark tokens with entity types
        for entity in entities:
            for i in range(entity.start, entity.end + 1):
                if i < len(doc.tokens):
                    doc.tokens[i].ent_type_ = entity.type
                    doc.tokens[i].ent_iob_ = "B" if i == entity.start else "I"

        return doc


class ZomiNERBackend:
    """Adapter for using ZomiNER in the pipeline."""

    def __init__(self) -> None:
        self.ner: ZomiNER = ZomiNER()
        self._name: str = "zomi_ner"
        self._available: bool = True

    def recognize(self, doc: ZomiDoc) -> ZomiDoc:
        """Add NER annotations to document."""
        return self.ner.to_doc(doc)

    def name(self) -> str:
        return self._name

    def is_available(self) -> bool:
        return self._available

    def get_error_message(self) -> Optional[str]:
        return None if self._available else "Zomi NER not available"


def extract_entities_zomi(text: str) -> list[dict[str, str]]:
    """Quick entity extraction for Zomi text."""
    ner = ZomiNER()
    entities = ner.extract(text)
    return [
        {"text": e.text, "type": e.type, "confidence": f"{e.confidence:.2f}"}
        for e in entities
    ]

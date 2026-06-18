"""Rule-based question generator using NLTK.

Generates three question types from source text:
  • MCQ — fill-in-the-blank with noun-based distractors
  • True/False — factual statements, sometimes negated
  • Short Answer — keyword-driven open-ended questions
"""

import random
import re
from typing import Dict, List, Optional

import nltk

# ── Ensure required NLTK data is present ────────────────────────────────────

_NLTK_RESOURCES = [
    ("tokenizers/punkt_tab", "punkt_tab"),
    ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"),
    ("corpora/stopwords", "stopwords"),
]

for resource_path, package_name in _NLTK_RESOURCES:
    try:
        nltk.data.find(resource_path)
    except LookupError:
        nltk.download(package_name, quiet=True)

from nltk.corpus import stopwords  # noqa: E402
from nltk.tag import pos_tag  # noqa: E402
from nltk.tokenize import sent_tokenize, word_tokenize  # noqa: E402


class QuestionGenerator:
    """Singleton question generator driven by NLTK POS tagging."""

    _instance: Optional["QuestionGenerator"] = None

    @classmethod
    def get_instance(cls) -> "QuestionGenerator":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self.stop_words = set(stopwords.words("english"))

    # ── Public API ───────────────────────────────────────────────────────

    def generate(
        self,
        text: str,
        keywords: List[Dict],
        num_questions: int = 5,
        question_types: Optional[List[str]] = None,
        difficulty: str = "medium",
    ) -> List[Dict]:
        """Generate questions from *text* guided by extracted *keywords*.

        Args:
            text: Full source text.
            keywords: List of dicts ``{'keyword': str, 'score': float}``.
            num_questions: Total number of questions to produce.
            question_types: Subset of ``['mcq', 'true_false', 'short_answer']``.
            difficulty: One of ``'easy'``, ``'medium'``, ``'hard'``.

        Returns:
            List of question dicts ready for DB storage / serialization.
        """
        if question_types is None:
            question_types = ["mcq", "true_false", "short_answer"]

        sentences = sent_tokenize(text)
        keyword_texts = [kw["keyword"].lower() for kw in keywords]

        # Prefer sentences that mention at least one keyword
        relevant_sentences: List[str] = []
        other_sentences: List[str] = []
        for sent in sentences:
            sent_lower = sent.lower()
            if any(kw in sent_lower for kw in keyword_texts):
                relevant_sentences.append(sent)
            else:
                other_sentences.append(sent)

        # Fallback: use all sentences if none matched
        if not relevant_sentences:
            relevant_sentences = sentences[:10]

        # Distribute count evenly across requested types
        per_type = max(1, num_questions // len(question_types))
        remainder = num_questions - per_type * len(question_types)

        questions: List[Dict] = []
        _dispatch = {
            "mcq": self._generate_mcqs,
            "true_false": self._generate_true_false,
            "short_answer": self._generate_short_answer,
        }

        for qt in question_types:
            count = per_type + (1 if remainder > 0 else 0)
            remainder -= 1
            handler = _dispatch.get(qt)
            if handler:
                questions.extend(
                    handler(
                        relevant_sentences + other_sentences,
                        keyword_texts,
                        count,
                        difficulty,
                    )
                )

        return questions[:num_questions]

    # ── MCQ generation ───────────────────────────────────────────────────

    def _generate_mcqs(
        self,
        sentences: List[str],
        keywords: List[str],
        count: int,
        difficulty: str,
    ) -> List[Dict]:
        """Generate MCQs by identifying key nouns and creating distractors."""
        questions: List[Dict] = []
        shuffled = list(sentences)
        random.shuffle(shuffled)

        # Collect all nouns across the text for distractor generation
        all_nouns: List[str] = []
        for s in sentences:
            tagged = pos_tag(word_tokenize(s))
            all_nouns.extend(
                w
                for w, tag in tagged
                if tag in ("NN", "NNS", "NNP", "NNPS")
                and w.lower() not in self.stop_words
                and len(w) > 2
            )

        for sent in shuffled:
            if len(questions) >= count:
                break

            tagged = pos_tag(word_tokenize(sent))
            nouns = [
                word
                for word, tag in tagged
                if tag in ("NN", "NNS", "NNP", "NNPS")
                and word.lower() not in self.stop_words
                and len(word) > 2
            ]
            if not nouns:
                continue

            answer = random.choice(nouns)
            question_text = self._create_question_from_sentence(sent, answer)
            if not question_text:
                continue

            # Build distractor list from global nouns, excluding the answer
            distractors = list(
                {n for n in all_nouns if n.lower() != answer.lower()}
            )
            random.shuffle(distractors)
            distractors = distractors[:3]

            while len(distractors) < 3:
                distractors.append(f"Option {len(distractors) + 1}")

            options = distractors[:3] + [answer]
            random.shuffle(options)

            questions.append(
                {
                    "type": "mcq",
                    "question": question_text,
                    "options": options,
                    "answer": answer,
                    "explanation": f'Based on the text: "{sent.strip()}"',
                    "difficulty": difficulty,
                }
            )

        return questions

    # ── True / False generation ──────────────────────────────────────────

    def _generate_true_false(
        self,
        sentences: List[str],
        keywords: List[str],
        count: int,
        difficulty: str,
    ) -> List[Dict]:
        """Generate True/False questions, sometimes negating factual statements."""
        questions: List[Dict] = []
        shuffled = list(sentences)
        random.shuffle(shuffled)

        for sent in shuffled:
            if len(questions) >= count:
                break

            sent = sent.strip()
            if len(sent) < 20 or len(sent) > 300:
                continue

            is_true = random.choice([True, False])

            if is_true:
                question_text = f"True or False: {sent}"
                answer = "True"
            else:
                negated = self._negate_sentence(sent)
                if negated == sent:
                    continue
                question_text = f"True or False: {negated}"
                answer = "False"

            questions.append(
                {
                    "type": "true_false",
                    "question": question_text,
                    "options": ["True", "False"],
                    "answer": answer,
                    "explanation": f'The original statement is: "{sent}"',
                    "difficulty": difficulty,
                }
            )

        return questions

    # ── Short answer generation ──────────────────────────────────────────

    _TEMPLATES = [
        "What is {keyword}?",
        "Explain the concept of {keyword}.",
        "Describe {keyword} in your own words.",
        "What role does {keyword} play?",
        "How is {keyword} significant?",
        "Define {keyword}.",
        "What are the key aspects of {keyword}?",
    ]

    def _generate_short_answer(
        self,
        sentences: List[str],
        keywords: List[str],
        count: int,
        difficulty: str,
    ) -> List[Dict]:
        """Generate short-answer questions from key sentences."""
        questions: List[Dict] = []
        used_keywords: set = set()

        for sent in sentences:
            if len(questions) >= count:
                break

            sent_lower = sent.lower()
            for kw in keywords:
                if kw in sent_lower and kw not in used_keywords:
                    template = random.choice(self._TEMPLATES)
                    question_text = template.format(keyword=kw)
                    used_keywords.add(kw)

                    questions.append(
                        {
                            "type": "short_answer",
                            "question": question_text,
                            "options": None,
                            "answer": sent.strip(),
                            "explanation": "This answer is derived from the source text.",
                            "difficulty": difficulty,
                        }
                    )
                    break

        return questions

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _create_question_from_sentence(sentence: str, answer: str) -> Optional[str]:
        """Convert a declarative sentence into a fill-in-the-blank MCQ."""
        sent = sentence.strip()
        if not sent:
            return None

        pattern = re.compile(re.escape(answer), re.IGNORECASE)
        if pattern.search(sent):
            blanked = pattern.sub("______", sent, count=1)
            return (
                f'Which of the following correctly completes the statement? '
                f'"{blanked}"'
            )
        return None

    @staticmethod
    def _negate_sentence(sentence: str) -> str:
        """Negate a sentence by inserting or removing 'not'.

        Returns the original sentence unchanged if negation is not feasible.
        """
        words = word_tokenize(sentence)
        tagged = pos_tag(words)

        negation_words = {"not", "n't", "never", "no"}
        has_negation = any(w.lower() in negation_words for w in words)

        if has_negation:
            # Remove the negation to flip the meaning
            new_words = [w for w in words if w.lower() not in negation_words]
            return " ".join(new_words)

        # Insert 'not' after the first verb
        for i, (word, tag) in enumerate(tagged):
            if tag.startswith("VB"):
                words.insert(i + 1, "not")
                return " ".join(words)

        return sentence

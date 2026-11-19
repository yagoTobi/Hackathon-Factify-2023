import os
import sys
import unittest

# Add NewsAgent to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "NewsAgent")))

from article_creator import (
    parse_json_from_llm,
    filter_and_balance_proportions,
    batch_classify_slant_prompt,
)


class TestBiasFilter(unittest.TestCase):
    def test_parse_json_from_llm(self):
        # 1. Direct JSON array
        direct_json = '[{"id": 0, "slant_score": -0.2, "category": "left", "extremism_score": 0.1, "reasoning": "mild left"}]'
        parsed = parse_json_from_llm(direct_json)
        self.assertIsNotNone(parsed)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["category"], "left")

        # 2. Markdown fenced JSON array
        fenced_json = """Here is the classification result:
```json
[
  {"id": 0, "slant_score": 0.5, "category": "right", "extremism_score": 0.3, "reasoning": "conservative framing"},
  {"id": 1, "slant_score": 0.0, "category": "center", "extremism_score": 0.05, "reasoning": "neutral facts"}
]
```
Hope this helps!"""
        parsed_fenced = parse_json_from_llm(fenced_json)
        self.assertIsNotNone(parsed_fenced)
        self.assertEqual(len(parsed_fenced), 2)
        self.assertEqual(parsed_fenced[0]["id"], 0)
        self.assertEqual(parsed_fenced[1]["category"], "center")

        # 3. Malformed JSON
        malformed = "Not valid json at all"
        self.assertIsNone(parse_json_from_llm(malformed))

    def test_filter_outliers(self):
        articles = [
            {"title": "Mainstream Left", "category": "left", "slant_score": -0.4, "extremism_score": 0.2},
            {"title": "Moderate Center", "category": "center", "slant_score": 0.0, "extremism_score": 0.1},
            {"title": "Extreme Far-Right Outlier", "category": "right", "slant_score": 0.95, "extremism_score": 0.92},
            {"title": "Conspiracy Far-Left Outlier", "category": "left", "slant_score": -0.92, "extremism_score": 0.89},
            {"title": "Mainstream Right", "category": "right", "slant_score": 0.4, "extremism_score": 0.3},
        ]

        filtered = filter_and_balance_proportions(articles, max_proportion=0.5, extremism_threshold=0.85)
        titles = [a["title"] for a in filtered]

        self.assertIn("Mainstream Left", titles)
        self.assertIn("Moderate Center", titles)
        self.assertIn("Mainstream Right", titles)
        self.assertNotIn("Extreme Far-Right Outlier", titles)
        self.assertNotIn("Conspiracy Far-Left Outlier", titles)

    def test_proportional_capping(self):
        # 10 articles: 7 Left, 1 Center, 2 Right.
        # Max proportion = 0.40 -> max 4 articles from Left.
        # Should keep 4 least extreme from Left, 1 Center, and 2 Right -> total 7.
        articles = [
            {"title": f"Left_{i}", "category": "left", "slant_score": -0.1 * i, "extremism_score": 0.1 * i}
            for i in range(1, 8)
        ]
        articles.append({"title": "Center_1", "category": "center", "slant_score": 0.0, "extremism_score": 0.05})
        articles.append({"title": "Right_1", "category": "right", "slant_score": 0.3, "extremism_score": 0.2})
        articles.append({"title": "Right_2", "category": "right", "slant_score": 0.5, "extremism_score": 0.3})

        self.assertEqual(len(articles), 10)

        balanced = filter_and_balance_proportions(articles, max_proportion=0.40, extremism_threshold=0.85)

        left_count = sum(1 for a in balanced if a["category"] == "left")
        center_count = sum(1 for a in balanced if a["category"] == "center")
        right_count = sum(1 for a in balanced if a["category"] == "right")

        # Capped at ceil(10 * 0.40) = 4
        self.assertEqual(left_count, 4)
        self.assertEqual(center_count, 1)
        self.assertEqual(right_count, 2)

        # The 4 kept left articles should be the ones with lowest extremism
        left_titles = [a["title"] for a in balanced if a["category"] == "left"]
        self.assertListEqual(sorted(left_titles), ["Left_1", "Left_2", "Left_3", "Left_4"])

    def test_empty_and_fallback(self):
        # Empty input
        self.assertEqual(filter_and_balance_proportions([]), [])

        # All extreme articles fallback to the single least extreme
        all_extreme = [
            {"title": "Extreme 1", "category": "right", "slant_score": 0.99, "extremism_score": 0.98},
            {"title": "Extreme 2 (Least)", "category": "left", "slant_score": -0.88, "extremism_score": 0.86},
        ]
        fallback = filter_and_balance_proportions(all_extreme, extremism_threshold=0.85)
        self.assertEqual(len(fallback), 1)
        self.assertEqual(fallback[0]["title"], "Extreme 2 (Least)")


if __name__ == "__main__":
    unittest.main()

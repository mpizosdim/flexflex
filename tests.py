import unittest
from utils import *


class TestUtils(unittest.TestCase):
    def test_calories(self):
        cal = get_calories(88, 183, 29, "male", "very_active", "loose_weight")
        self.assertAlmostEqual(cal, 2599.575)

    def test_macros(self):
        prot, fat, carbs = get_macros(88, 183, 29, "male", "very_active", "maintain_weight")
        self.assertAlmostEqual(prot, 193.6)
        self.assertAlmostEqual(fat, 79.43, 2)
        self.assertAlmostEqual(carbs, 440.046, 2)

    def test_clean(self):
        cleaned_ingre1 = clean_ingredient("1/2 stick (3/4 Cup) Cold Butter")
        cleaned_ingre2 = clean_ingredient("1 pound Breakfast Sausage")
        cleaned_ingre3 = clean_ingredient("1/4 cup Mayonnaise")
        self.assertEqual(cleaned_ingre1, "butter")
        self.assertEqual(cleaned_ingre2, "breakfast sausage")
        self.assertEqual(cleaned_ingre3, "mayonnaise")

if __name__ == '__main__':
    unittest.main()
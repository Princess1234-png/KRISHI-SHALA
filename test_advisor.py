import unittest

from krishishala import advisor


class AdvisorTests(unittest.TestCase):
    def test_english_yellow_leaves(self):
        out = advisor.advise("Why are my leaves turning yellow?")
        self.assertEqual(out["topic"], "yellow_leaves")
        self.assertIn("nitrogen", out["answer"])

    def test_tamil_question_gets_tamil_answer(self):
        out = advisor.advise("இலைகள் மஞ்சள் ஆகிறது", lang="ta")
        self.assertEqual(out["topic"], "yellow_leaves")
        self.assertEqual(out["answer"], advisor.ADVICE["yellow_leaves"]["ta"])

    def test_unknown_language_falls_back_to_english(self):
        out = advisor.advise("insects on my plant", lang="bn")
        self.assertEqual(out["answer"], advisor.ADVICE["pests"]["en"])

    def test_unrecognised_question_refers_to_expert(self):
        self.assertIsNone(advisor.advise("hello")["topic"])

    def test_sensor_alerts_are_attached(self):
        latest = {"crop": "tomato", "moisture": 10, "ph": 6.4, "temp_c": 25, "ec": 2.0}
        self.assertTrue(advisor.advise("wilting", latest_reading=latest)["sensor_alerts"])

    def test_seasons(self):
        self.assertEqual(advisor.what_to_plant(7), ["rice"])
        self.assertEqual(advisor.what_to_plant(12), ["wheat", "spinach"])
        self.assertEqual(advisor.what_to_plant(4), ["tomato"])


if __name__ == "__main__":
    unittest.main()

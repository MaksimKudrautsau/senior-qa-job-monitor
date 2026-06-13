"""
Tests for filters.score_job / is_senior_qa_job.

Run with the stdlib (no pytest needed):  python -m unittest test_filters -v
"""

import unittest

from filters import score_job, is_senior_qa_job


def job(title, location="", description=""):
    return {
        "title": title,
        "location": location,
        "description": description,
        "company": "Example",
        "url": "https://example.com/jobs/1",
        "source": "test",
    }


class TestSeniorQAFilter(unittest.TestCase):
    def assertMatch(self, j):
        s = score_job(j)
        self.assertTrue(s.matched, f"expected MATCH, got {s}")

    def assertNoMatch(self, j):
        s = score_job(j)
        self.assertFalse(s.matched, f"expected NO match, got {s}")

    # --- should match -------------------------------------------------------
    def test_senior_qa_bay(self):
        self.assertMatch(job("Senior QA Engineer", "San Francisco, CA"))

    def test_sr_dotted_qa_bay(self):
        self.assertMatch(job("Sr. QA Automation Engineer", "Sunnyvale, CA"))

    def test_staff_sdet_fremont(self):
        self.assertMatch(job("Staff SDET", "Fremont, CA"))

    def test_senior_qa_remote(self):
        self.assertMatch(job("Senior QA Engineer", "Remote - US"))

    def test_senior_seit_empty_location(self):
        self.assertMatch(job("Staff Software Engineer in Test", ""))

    def test_sdet_bay_no_seniority_word(self):
        self.assertMatch(job("SDET", "San Jose, CA"))

    # --- should NOT match: non-QA titles (regression for the FP report) -----
    def test_python_engineer_not_qa(self):
        self.assertNoMatch(job("Senior Python Engineer", "San Francisco, CA"))

    def test_software_engineer_not_qa(self):
        self.assertNoMatch(job("Senior Software Engineer", "San Francisco, CA"))

    def test_staff_software_engineer_not_qa(self):
        self.assertNoMatch(job("Staff Software Engineer - CAM", "San Jose, CA"))

    def test_qa_analyst_included(self):
        self.assertMatch(job("Senior QA Analyst", "Oakland, CA"))

    def test_quality_analyst_included(self):
        self.assertMatch(job("Senior Quality Analyst", "Sunnyvale, CA"))

    def test_qa_in_description_does_not_qualify(self):
        # Generic eng role whose JD mentions QA must NOT match.
        self.assertNoMatch(
            job("Senior Software Engineer", "San Francisco, CA",
                "You will partner closely with the QA team and write tests.")
        )

    # --- should NOT match: excluded / out-of-area ---------------------------
    def test_qa_manager_excluded(self):
        self.assertNoMatch(job("Senior QA Manager", "San Jose, CA"))

    def test_senior_qa_wrong_city(self):
        self.assertNoMatch(job("Senior QA Engineer", "Austin, TX"))

    def test_plain_qa_wrong_city(self):
        self.assertNoMatch(job("QA Engineer", "Austin, TX"))

    def test_qa_remote_no_seniority_is_near_miss(self):
        # qa(title)=3 + remote=1 = 4 < threshold(5).
        self.assertNoMatch(job("QA Engineer", "Remote - US"))

    # --- regression ---------------------------------------------------------
    def test_wrapper_agrees_with_score(self):
        j = job("Senior QA Engineer", "Palo Alto, CA")
        self.assertEqual(is_senior_qa_job(j), score_job(j).matched)


if __name__ == "__main__":
    unittest.main()
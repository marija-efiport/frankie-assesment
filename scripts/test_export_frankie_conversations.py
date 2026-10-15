import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from uuid import uuid4

import export_frankie_conversations as exporter


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent / "tmp" / "export-tests" / uuid4().hex

    def page(self, messages, page=1, total=None):
        return dict(messages=messages, page=page, per_page=2,
                    total=len(messages) if total is None else total)

    def test_repeated_id_with_distinct_timestamps_is_preserved(self):
        records = [dict(message_id="same", timestamp=str(i)) for i in range(3)]
        pages = {1: self.page(records[:2], 1, 3), 2: self.page(records[2:], 2, 3)}
        actual = exporter.collect(lambda p, q: pages[q['page']], "conversations/u",
                                  {}, "messages", "message_id", self.root)
        self.assertEqual(actual, records)

    def test_exact_overlap_still_fails(self):
        row = dict(message_id="same", timestamp="same-time")
        with self.assertRaisesRegex(ValueError, "repeated record identity"):
            exporter.collect(lambda p, q: self.page([row, row]), "conversations/u",
                             {}, "messages", "message_id", self.root)

    def test_list_count_changes_are_reported(self):
        for expected in (0, 2):
            warnings = []
            self.assertEqual(exporter.verify_message_count(
                [dict(message_id="a")], expected, 1, warnings), 1)
            self.assertEqual(warnings[0]["list_total"], expected)
            self.assertEqual(warnings[0]["detail_records"], 1)

    def test_list_may_also_count_all_occurrences(self):
        self.assertEqual(exporter.verify_message_count(
            [dict(message_id="a"), dict(message_id="a")], 2, 1), 1)

    def test_resume_reuses_completed_users_and_retries_failed_user(self):
        self.check_resume(1)

    def test_resume_finishes_with_warning_when_detail_has_new_messages(self):
        self.check_resume(0)

    def check_resume(self, list_total):
        source = self.root / "source"
        (source / "conversation_pages").mkdir(parents=True)
        (source / "message_pages/user-000001").mkdir(parents=True)
        exporter.save(source / "report.json", dict(users_completed=1, start_time=None,
                                                    end_time=None, anonymize=True))
        exporter.save(source / "conversation_pages/page-00001.json",
                      dict(conversations=[dict(user_id="u1", total_messages=1),
                                          dict(user_id="u2", total_messages=list_total)],
                           total=2, per_page=100, page=1))
        exporter.save(source / "message_pages/user-000001/page-00001.json",
                      self.page([dict(message_id="a", timestamp="t1")]))
        calls = []
        def fetch(path, params):
            calls.append(path)
            self.assertEqual(params["anonymize"], "true")
            return self.page([dict(message_id="b", timestamp="t1"),
                              dict(message_id="b", timestamp="t2")])
        args = SimpleNamespace(resume_from=source, base_url="https://crm.frankie.mindsmiths.io/api/v1",
                               output=self.root / "resumed", session_prompt=False, delay=0,
                               start_time=None, end_time=None, include_personal_data=False,
                               per_page=100, users_only=False)
        with patch.object(exporter, "client", return_value=fetch):
            exporter.export(args)
        self.assertEqual(calls, ["conversations/u2"])
        rows = [json.loads(line) for line in (args.output / "messages.jsonl").read_text().splitlines()]
        self.assertEqual(len(rows), 3)
        self.assertEqual([row["conversation_user_id"] for row in rows], ["u1", "u2", "u2"])
        report = json.loads((args.output / "report.json").read_text())
        self.assertEqual(report["messages"], 3)
        self.assertEqual(report["unique_message_ids_within_conversations"], 2)
        self.assertEqual(report["users_with_repeated_message_ids"], 1)
        if list_total == 0:
            self.assertEqual(report["status"], "export_finished_with_list_count_changes")
            self.assertEqual(report["list_count_changes"][0]["detail_records"], 2)
        else:
            self.assertEqual(report["status"], "export_finished_count_checks_passed")
        self.assertEqual(json.loads((source / "report.json").read_text())["users_completed"], 1)


if __name__ == "__main__":
    unittest.main()

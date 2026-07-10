import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "block_destructive_bash.py"
SPEC = importlib.util.spec_from_file_location("block_destructive_bash", MODULE_PATH)
blocker = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(blocker)


class DestructiveBashBlockerTests(unittest.TestCase):
    def assert_blocked(self, command, rule):
        result = blocker.evaluate_command(command)
        self.assertIsNotNone(result)
        self.assertEqual(result.rule, rule)

    def assert_allowed(self, command):
        self.assertIsNone(blocker.evaluate_command(command))

    def test_blocks_rm_rf_variants(self):
        self.assert_blocked("rm -rf build", "rm -rf")
        self.assert_blocked("sudo rm -fr /tmp/project", "rm -rf")
        self.assert_blocked("rm -r -f -- cache", "rm -rf")
        self.assert_blocked("rm --recursive --force old-output", "rm -rf")
        self.assert_blocked("/bin/rm -rf build", "rm -rf")

    def test_allows_non_forced_rm(self):
        self.assert_allowed("rm file.txt")
        self.assert_allowed("rm -r build")

    def test_blocks_sql_destructive_statements(self):
        self.assert_blocked('psql -c "DROP TABLE users"', "DROP TABLE")
        self.assert_blocked('mysql -e "TRUNCATE sessions"', "TRUNCATE")
        self.assert_blocked('psql -c "DELETE FROM users"', "DELETE FROM without WHERE")

    def test_allows_delete_from_with_where(self):
        self.assert_allowed('psql -c "DELETE FROM users WHERE id = 1"')
        self.assert_allowed('echo "DELETE FROM users WHERE archived = true;"')

    def test_blocks_force_push(self):
        self.assert_blocked("git push --force origin main", "git push --force")
        self.assert_blocked("git push -f origin main", "git push --force")
        self.assert_blocked("git push --force-with-lease", "git push --force")

    def test_allows_normal_commands(self):
        self.assert_allowed("npm test")
        self.assert_allowed("git push origin main")
        self.assert_allowed("python3 manage.py migrate")

    def test_logs_blocked_attempt_as_jsonl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "blocked.log"
            blocker.log_blocked_attempt(
                command="rm -rf build",
                project_path="/tmp/project",
                rule="rm -rf",
                log_path=log_path,
            )
            entry = json.loads(log_path.read_text(encoding="utf-8"))
            self.assertEqual(entry["attempted_command"], "rm -rf build")
            self.assertEqual(entry["project_path"], "/tmp/project")
            self.assertEqual(entry["rule"], "rm -rf")
            self.assertIn("timestamp", entry)


if __name__ == "__main__":
    unittest.main()

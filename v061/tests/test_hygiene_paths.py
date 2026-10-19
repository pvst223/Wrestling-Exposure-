import unittest, os, re
import _path
class T(unittest.TestCase):
    def test_no_absolute_paths_in_new_code(self):
        pat = re.compile(r"""["'](/home/|/root/|/tmp/|/Users/|[A-Za-z]:\\)""")
        bad = []
        for root in ("impl", "tests"):
            for dp, _, fs in os.walk(os.path.join(_path.REPO, "v061", root)):
                for f in fs:
                    if f.endswith(".py") and f != "test_hygiene_paths.py":
                        for i, l in enumerate(open(os.path.join(dp, f), encoding="utf-8"), 1):
                            if pat.search(l): bad.append(f"{f}:{i}")
        self.assertEqual(bad, [])
    def test_no_private_data_in_impl(self):   # impl code must not reference holdout / candidate footage identifiers
        for dp, _, fs in os.walk(os.path.join(_path.REPO, "v061", "impl")):
            for f in fs:
                if f.endswith(".py"): self.assertNotRegex(open(os.path.join(dp, f), encoding="utf-8").read().lower(), r"holdout2_path|holdout_2_dir")
if __name__ == "__main__": unittest.main()

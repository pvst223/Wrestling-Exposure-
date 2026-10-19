# IMPLEMENTATION DIFF vs. Readiness V1 (main @ 1bbe32f)

Generated from git before this file was added. Locked V0.6.1 implementation (v061/impl, v061/tests), spec_v4, frozen records: NO changes (see `git diff --stat` below contains none of them).

## Stat
```
 .../ANATOMICAL_IMPLEMENTATION_MANIFEST.txt         |  33 ++++
 v061/anatomical/EXECUTION_SEQUENCE.md              |  10 +
 v061/anatomical/IMPLEMENTATION_CLARIFICATIONS.md   |  12 ++
 v061/anatomical/OUTPUT_SCHEMA.md                   |   5 +
 v061/anatomical/README_REVIEWER.md                 |   3 +
 v061/anatomical/REUSED_V05_HASHES.json             |  18 ++
 v061/anatomical/anat_manifest.py                   |  20 ++
 v061/anatomical/impl/adapter.py                    |  42 +++++
 v061/anatomical/impl/carry.py                      |  19 ++
 v061/anatomical/impl/merge_guard.py                |  27 +++
 v061/anatomical/impl/metrics.py                    |  87 +++++++++
 v061/anatomical/impl/ownership_stage.py            |  28 +++
 v061/anatomical/impl/pipeline.py                   |  39 ++++
 v061/anatomical/impl/preflight.py                  |  37 ++++
 v061/anatomical/impl/record_class.py               |  23 +++
 v061/anatomical/impl/render_anat.py                |  56 ++++++
 v061/anatomical/impl/run_anat.py                   |  11 ++
 v061/anatomical/impl/seg_posegrid.py               |  24 +++
 v061/anatomical/reused_v05/config/config_v05.json  | 209 +++++++++++++++++++++
 v061/anatomical/reused_v05/src/appearance.py       | 142 ++++++++++++++
 v061/anatomical/reused_v05/src/config.py           |  18 ++
 v061/anatomical/reused_v05/src/cuts_events.py      |  52 +++++
 v061/anatomical/reused_v05/src/integrity_v03.py    |  78 ++++++++
 v061/anatomical/reused_v05/src/integrity_v04.py    |  65 +++++++
 v061/anatomical/reused_v05/src/integrity_v05.py    |  48 +++++
 v061/anatomical/reused_v05/src/ownership_v05.py    | 110 +++++++++++
 v061/anatomical/reused_v05/src/seg_extract.py      |  25 +++
 v061/anatomical/tests/synth.py                     |  23 +++
 v061/anatomical/tests/test_anatomical.py           | 174 +++++++++++++++++
 v061/anatomical_plan/tests/test_contract.py        |   6 +-
 30 files changed, 1441 insertions(+), 3 deletions(-)
```

## Modified existing file: anatomical_plan/tests/test_contract.py (packaging defect fix: use vendored byte-identical V0.5 copies instead of versions/holdout1/)
```diff
diff --git a/v061/anatomical_plan/tests/test_contract.py b/v061/anatomical_plan/tests/test_contract.py
index cfe8773..b2cc151 100644
--- a/v061/anatomical_plan/tests/test_contract.py
+++ b/v061/anatomical_plan/tests/test_contract.py
@@ -36,9 +36,9 @@ class T(unittest.TestCase):
     def _own(self):
         try: import cv2, numpy as np  # noqa
         except Exception: self.skipTest("cv2/numpy unavailable")
-        p = os.path.join(REPO, "versions", "holdout1", "src", "ownership_v05.py"); import importlib.util
+        p = os.path.join(REPO, "v061", "anatomical", "reused_v05", "src", "ownership_v05.py"); import importlib.util
         sp = importlib.util.spec_from_file_location("own05", p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
-        cfg = json.load(open(os.path.join(REPO, "versions", "holdout1", "config", "config_v05.json")))["ownership"]
+        cfg = json.load(open(os.path.join(REPO, "v061", "anatomical", "reused_v05", "config", "config_v05.json")))["ownership"]
         return m, types.SimpleNamespace(**cfg)
     def _scene(self, m, masks, kp_sets):
         import numpy as np
@@ -66,5 +66,5 @@ class T(unittest.TestCase):
     def test_reused_files_unchanged(self):
         import hashlib
         h = lambda p: hashlib.sha256(open(os.path.join(REPO, p), "rb").read()).hexdigest()
-        self.assertTrue(h("versions/holdout1/src/ownership_v05.py").startswith("8cec4f1a")); self.assertTrue(h("versions/holdout1/config/config_v05.json").startswith("7e511eec"))
+        self.assertTrue(h("v061/anatomical/reused_v05/src/ownership_v05.py").startswith("8cec4f1a")); self.assertTrue(h("v061/anatomical/reused_v05/config/config_v05.json").startswith("7e511eec"))
 if __name__ == "__main__": unittest.main()
```

## Reused V0.5 files: vendored copies are byte-identical (REUSED_V05_HASHES.json == REUSE_PROVENANCE.json; checked by tests and preflight). No frozen reused code was altered.

import itertools, json, os, sys, types, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import contract as K
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
class T(unittest.TestCase):
    def test_truth_table_assignment_only_when_all_gates_pass(self):
        for i, nf, o, p in itertools.product(K.ID_STATES, (False, True), K.OWN_STATES, K.POSE):
            r = K.classify(i, nf, o, p)
            ok = i in ("ACCEPT_A", "ACCEPT_B") and not nf and o == "SINGLE_BODY_SUPPORTED" and p == "MEASURED"
            self.assertEqual(r["assigned_label"] is not None, ok, (i, nf, o, p))
            self.assertEqual(r["identity_state_passthrough"], i); self.assertEqual(r["ownership_state_passthrough"], o)
            self.assertEqual(r["identity_unvalidated_flag"], ok)
    def test_abstain_never_becomes_assignment(self):
        r = K.classify("ABSTAIN_AMBIGUOUS", False, "SINGLE_BODY_SUPPORTED", "MEASURED")
        self.assertEqual(r["record_class"], "UNASSIGNED_IDENTITY_AMBIGUOUS"); self.assertIsNone(r["assigned_label"])
    def test_numeric_failure_invalid(self):
        r = K.classify("ACCEPT_A", True, "SINGLE_BODY_SUPPORTED", "MEASURED"); self.assertEqual(r["record_class"], "INVALID_NUMERIC"); self.assertFalse(r["landmarks_emitted"])
    def test_mixed_body_vetoes_accept(self):
        r = K.classify("ACCEPT_B", False, "MIXED_BODY_SUSPECTED", "MEASURED"); self.assertEqual(r["record_class"], "WITHHELD_MIXED_BODY"); self.assertFalse(r["landmarks_emitted"])
    def test_uncertain_ownership_withheld(self):
        for o in ("OWNERSHIP_UNCERTAIN", "OWNERSHIP_NOT_EVALUATED"):
            self.assertFalse(K.classify("ACCEPT_A", False, o, "MEASURED")["landmarks_emitted"])
    def test_nontarget_no_landmarks(self):
        self.assertFalse(K.classify("REJECT_NONTARGET", False, "SINGLE_BODY_SUPPORTED", "MEASURED")["landmarks_emitted"])
    def test_carry_rules(self):
        A = "ASSIGNED_A"
        self.assertIsNone(K.carry([A], False)); self.assertEqual(K.carry([A, "NO_POSE"], False)["age"], 1)
        self.assertEqual(K.carry([A] + ["NO_POSE"] * 3, False)["age"], 3); self.assertIsNone(K.carry([A] + ["NO_POSE"] * 4, False))
        self.assertIsNone(K.carry([A, "NO_POSE"], True))                       # camera cut
        for c in ("UNASSIGNED_IDENTITY_AMBIGUOUS", "WITHHELD_MIXED_BODY", "NONTARGET", "INVALID_NUMERIC"): self.assertIsNone(K.carry([c, "NO_POSE"], False))
        self.assertFalse(K.carry([A, "NO_POSE"], False)["measurement"])
    def test_identity_ownership_independence(self):
        # same ownership state, different identity -> different class; same identity, different ownership -> different class
        self.assertNotEqual(K.classify("ACCEPT_A", False, "SINGLE_BODY_SUPPORTED", "MEASURED")["record_class"], K.classify("ACCEPT_B", False, "SINGLE_BODY_SUPPORTED", "MEASURED")["record_class"])
    # ---- geometry tests of the UNCHANGED V0.5 ownership module on synthetic masks (skipped if cv2 absent)
    def _own(self):
        try: import cv2, numpy as np  # noqa
        except Exception: self.skipTest("cv2/numpy unavailable")
        p = os.path.join(REPO, "versions", "holdout1", "src", "ownership_v05.py"); import importlib.util
        sp = importlib.util.spec_from_file_location("own05", p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        cfg = json.load(open(os.path.join(REPO, "versions", "holdout1", "config", "config_v05.json")))["ownership"]
        return m, types.SimpleNamespace(**cfg)
    def _scene(self, m, masks, kp_sets):
        import numpy as np
        H = W = 200; arr = np.stack(masks); sd = dict(shape=(H, W), conf=np.ones(len(masks)), box=np.zeros((len(masks), 4)), mask=np.packbits(arr, axis=-1))
        return m.FrameSeg(sd, W, H, 0.25)
    def _skel(self, cx, top=20, h=150):
        import numpy as np
        kp = np.zeros((17, 2)); kc = np.ones(17)
        for i in range(17): kp[i] = (cx + (i % 3 - 1) * 6, top + (i / 16.0) * h)
        return kp, kc
    def test_ownership_single_body(self):
        m, C = self._own(); import numpy as np
        mk = np.zeros((200, 200), bool); mk[10:180, 60:90] = True; fs = self._scene(m, [mk], None); kp, kc = self._skel(75)
        M = m.metrics(fs, kp, kc, [], 20.0, 0.5, C); self.assertEqual(m.decide(M, C)[0], "SINGLE_BODY_SUPPORTED")
    def test_ownership_straddling_two_masks_is_mixed(self):
        m, C = self._own(); import numpy as np
        a = np.zeros((200, 200), bool); a[10:90, 60:90] = True; b = np.zeros((200, 200), bool); b[100:180, 60:90] = True
        fs = self._scene(m, [a, b], None); kp, kc = self._skel(75); M = m.metrics(fs, kp, kc, [], 20.0, 0.5, C)
        self.assertIn(m.decide(M, C)[0], ("MIXED_BODY_SUSPECTED", "OWNERSHIP_UNCERTAIN"))
    def test_ownership_two_skeletons_in_one_merged_mask_not_single(self):
        m, C = self._own(); import numpy as np
        mk = np.zeros((200, 200), bool); mk[10:180, 50:120] = True; fs = self._scene(m, [mk], None)
        kp, kc = self._skel(65); okp, okc = self._skel(100); M = m.metrics(fs, kp, kc, [(okp, okc)], 20.0, 0.5, C)
        self.assertNotEqual(m.decide(M, C)[0], "SINGLE_BODY_SUPPORTED")
    def test_reused_files_unchanged(self):
        import hashlib
        h = lambda p: hashlib.sha256(open(os.path.join(REPO, p), "rb").read()).hexdigest()
        self.assertTrue(h("versions/holdout1/src/ownership_v05.py").startswith("8cec4f1a")); self.assertTrue(h("versions/holdout1/config/config_v05.json").startswith("7e511eec"))
if __name__ == "__main__": unittest.main()

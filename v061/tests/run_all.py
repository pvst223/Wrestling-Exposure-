"""Run the V0.6.1 synthetic suite: python v061/tests/run_all.py (needs numpy, scipy; torch/opencv optional -> tests skip)."""
import sys, os, unittest
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
s = unittest.defaultTestLoader.discover(here, pattern="test_*.py"); r = unittest.TextTestRunner(verbosity=1).run(s); sys.exit(0 if r.wasSuccessful() else 1)

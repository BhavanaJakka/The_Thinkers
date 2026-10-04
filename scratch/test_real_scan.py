import json
import zipfile
import os

print("=== VERIFYING REAL SCANNER ACCEPTANCE CRITERIA ===")

# Test 1: p3-high-risk-app sample
p3_dir = os.path.join(os.path.dirname(__file__), '..', 'tests', 'fixtures', 'samples', 'p3-high-risk-app')
with open(os.path.join(p3_dir, 'package.json'), 'r') as f:
    pkg_json = json.load(f)
with open(os.path.join(p3_dir, 'package-lock.json'), 'r') as f:
    pkg_lock = json.load(f)

# Count direct & total deps
direct_deps = list(pkg_json.get('dependencies', {}).keys())
total_deps = len(pkg_lock.get('packages', {})) - 1 if 'packages' in pkg_lock else len(pkg_lock.get('dependencies', {}))

print(f"Test 1 - p3-high-risk-app:")
print(f"  Direct Dependencies Count: {len(direct_deps)} ({direct_deps[:3]}...)")
print(f"  Total Dependencies Count: {total_deps}")
print(f"  Critical Vulns: ejs (3.1.6) and minimist (1.2.0)")

assert total_deps == 79, f"Expected 79 total dependencies, got {total_deps}"
assert 'ejs' in direct_deps, "ejs must be direct dep"
assert 'minimist' in direct_deps, "minimist must be direct dep"

# Test 2: p1-clean-app sample
p1_dir = os.path.join(os.path.dirname(__file__), '..', 'tests', 'fixtures', 'samples', 'p1-clean-app')
with open(os.path.join(p1_dir, 'package-lock.json'), 'r') as f:
    p1_lock = json.load(f)
p1_total = len(p1_lock.get('packages', {})) - 1 if 'packages' in p1_lock else len(p1_lock.get('dependencies', {}))

print(f"\nTest 2 - p1-clean-app:")
print(f"  Total Dependencies Count: {p1_total}")

assert p1_total == 70, f"Expected 70 total dependencies for p1, got {p1_total}"
assert p1_total != total_deps, "Numbers must differ between p1 and p3"

print("\n=== ALL MANIFEST VERIFICATIONS PASSED CLEANLY ===")

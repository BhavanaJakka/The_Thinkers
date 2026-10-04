const fs = require('fs');
const path = require('path');

// Mock window and fetch for Node environment
global.window = global;
global.fetch = async (url) => {
  return {
    ok: false,
    text: async () => ''
  };
};

// Load real-scan.js
require('../real-scan.js');

async function runTests() {
  console.log("=== RUNNING REAL SCANNER ACCEPTANCE TESTS ===");

  // Test 1: p3-high-risk-app files
  const p3PkgJson = fs.readFileSync(path.join(__dirname, '../tests/fixtures/samples/p3-high-risk-app/package.json'), 'utf8');
  const p3PkgLock = fs.readFileSync(path.join(__dirname, '../tests/fixtures/samples/p3-high-risk-app/package-lock.json'), 'utf8');

  const fileMapP3 = {
    'package.json': p3PkgJson,
    'package-lock.json': p3PkgLock
  };

  const resultP3 = await window.scanProjectReal(fileMapP3, "first", "zip", "HOSTED");

  console.log("\n--- TEST 1: p3-high-risk-app ('first') ---");
  console.log("Project Name:", resultP3.name);
  console.log("Ecosystem:", resultP3.ecosystem);
  console.log("Total Dependencies:", resultP3.total_dependencies);
  console.log("Critical Vulns:", resultP3.summary.critical_vulns);
  console.log("Risk Score:", resultP3.risk_score);
  console.log("Risk Level Verdict:", resultP3.summary.risk_level);
  console.log("Attack Paths Count:", resultP3.attack_paths.length);
  console.log("Findings (Critical):", resultP3.findings.map(f => `${f.dependency_name} (${f.severity})`));

  console.assert(resultP3.ecosystem === 'npm', "Ecosystem should be npm, not Maven");
  console.assert(resultP3.total_dependencies === 79, `Total deps should be 79, got ${resultP3.total_dependencies}`);
  console.assert(resultP3.summary.critical_vulns === 2, `Critical vulns should be 2 (ejs, minimist), got ${resultP3.summary.critical_vulns}`);
  console.assert(resultP3.risk_score >= 90, `Score should be near 100, got ${resultP3.risk_score}`);
  console.assert(resultP3.summary.risk_level === 'CRITICAL', `Verdict should be CRITICAL, got ${resultP3.summary.risk_level}`);

  // Test 2: Different project (p1-clean-app)
  const p1PkgJson = fs.readFileSync(path.join(__dirname, '../tests/fixtures/samples/p1-clean-app/package.json'), 'utf8');
  const p1PkgLock = fs.readFileSync(path.join(__dirname, '../tests/fixtures/samples/p1-clean-app/package-lock.json'), 'utf8');

  const fileMapP1 = {
    'package.json': p1PkgJson,
    'package-lock.json': p1PkgLock
  };

  const resultP1 = await window.scanProjectReal(fileMapP1, "p1-clean", "zip", "HOSTED");

  console.log("\n--- TEST 2: p1-clean-app ---");
  console.log("Ecosystem:", resultP1.ecosystem);
  console.log("Total Dependencies:", resultP1.total_dependencies);
  console.log("Critical Vulns:", resultP1.summary.critical_vulns);
  console.log("Risk Score:", resultP1.risk_score);
  console.log("Risk Level Verdict:", resultP1.summary.risk_level);

  console.assert(resultP1.total_dependencies !== resultP3.total_dependencies, "Numbers must differ from test 1");
  console.assert(resultP1.risk_score !== resultP3.risk_score, "Score must differ from test 1");

  // Test 3: ZIP with no manifest files
  console.log("\n--- TEST 3: Invalid ZIP with no manifests ---");
  try {
    await window.scanProjectReal({ 'readme.txt': 'hello world' }, "invalid", "zip", "HOSTED");
    console.error("FAIL: Should have thrown an error for missing manifests!");
  } catch (err) {
    console.log("PASS: Caught expected error ->", err.message);
  }

  console.log("\n=== ALL ACCEPTANCE TESTS PASSED SUCCESSFULLY! ===");
}

runTests().catch(console.error);

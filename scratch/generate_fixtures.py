import os
import json

base_dir = r"c:\Study\Diptrix Solution\tests\fixtures\samples"

def make_sample_dir(name):
    d = os.path.join(base_dir, name)
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(d, "src"), exist_ok=True)
    return d

# ==========================================
# 1. p1-clean-app (70 deps, 0 vulns, 0 suspicious, 0 license flags)
# ==========================================
p1_dir = make_sample_dir("p1-clean-app")

p1_pkg = {
    "name": "p1-clean-app",
    "version": "1.0.0",
    "private": True,
    "dependencies": {f"clean-dep-{i}": "1.0.0" for i in range(1, 11)}
}
with open(os.path.join(p1_dir, "package.json"), "w") as f:
    json.dump(p1_pkg, f, indent=2)

p1_lock_packages = {"": {"name": "p1-clean-app", "version": "1.0.0"}}
for i in range(1, 71):
    dep_name = f"clean-dep-{i}" if i <= 10 else f"transitive-dep-{i}"
    p1_lock_packages[f"node_modules/{dep_name}"] = {
        "version": "1.0.0",
        "resolved": f"https://registry.npmjs.org/{dep_name}/-/{dep_name}-1.0.0.tgz",
        "license": "MIT"
    }

p1_lock = {
    "name": "p1-clean-app",
    "version": "1.0.0",
    "lockfileVersion": 3,
    "requires": True,
    "packages": p1_lock_packages
}
with open(os.path.join(p1_dir, "package-lock.json"), "w") as f:
    json.dump(p1_lock, f, indent=2)

with open(os.path.join(p1_dir, "src", "index.js"), "w") as f:
    f.write("// Clean app code\nconsole.log('App running');\n")

# ==========================================
# 1a. p1-clean-app-plus-one (71 deps for hardcoded test)
# ==========================================
p1_plus_dir = make_sample_dir("p1-clean-app-plus-one")
with open(os.path.join(p1_plus_dir, "package.json"), "w") as f:
    json.dump(p1_pkg, f, indent=2)

p1_plus_packages = dict(p1_lock_packages)
p1_plus_packages["node_modules/extra-dep-71"] = {
    "version": "1.0.0",
    "license": "MIT"
}
p1_plus_lock = dict(p1_lock)
p1_plus_lock["packages"] = p1_plus_packages
with open(os.path.join(p1_plus_dir, "package-lock.json"), "w") as f:
    json.dump(p1_plus_lock, f, indent=2)

with open(os.path.join(p1_plus_dir, "src", "index.js"), "w") as f:
    f.write("// Clean app plus one\n")

# ==========================================
# 2. p2-low-risk-app (70 deps, 2 vulns: moment, lodash; moment used in src, lodash _.template unused)
# ==========================================
p2_dir = make_sample_dir("p2-low-risk-app")

p2_pkg = {
    "name": "p2-low-risk-app",
    "version": "1.0.0",
    "private": True,
    "dependencies": {
        "moment": "2.24.0",
        "lodash": "4.17.15",
        **{f"low-dep-{i}": "1.0.0" for i in range(1, 9)}
    }
}
with open(os.path.join(p2_dir, "package.json"), "w") as f:
    json.dump(p2_pkg, f, indent=2)

p2_lock_packages = {
    "": {"name": "p2-low-risk-app", "version": "1.0.0"},
    "node_modules/moment": {"version": "2.24.0", "license": "MIT"},
    "node_modules/lodash": {"version": "4.17.15", "license": "MIT"}
}
for i in range(1, 69):
    dep_name = f"low-dep-{i}"
    p2_lock_packages[f"node_modules/{dep_name}"] = {"version": "1.0.0", "license": "MIT"}

p2_lock = {
    "name": "p2-low-risk-app",
    "version": "1.0.0",
    "lockfileVersion": 3,
    "packages": p2_lock_packages
}
with open(os.path.join(p2_dir, "package-lock.json"), "w") as f:
    json.dump(p2_lock, f, indent=2)

# src uses moment directly, lodash is imported but _.template is unused
with open(os.path.join(p2_dir, "src", "index.js"), "w") as f:
    f.write("""
const moment = require('moment');
const lodash = require('lodash');

console.log('Today is:', moment().format('YYYY-MM-DD'));
// Lodash is imported here for utility functions, but template and merge functions are unused

""")

# ==========================================
# 3. p3-high-risk-app (79 deps, 15 vulns: 2 critical [ejs, minimist], 10 high, 3 low; 6 transitive; 5 reachable attack paths)
# ==========================================
p3_dir = make_sample_dir("p3-high-risk-app")

# 15 vulnerable packages:
# 2 Critical: ejs (3.1.6), minimist (1.2.0)
# 10 High: lodash (4.17.15), axios (0.21.1), node-fetch (2.6.0), jsonwebtoken (8.5.1), high-vuln-1 (1.0.0), high-vuln-2 (1.0.0), high-vuln-3 (1.0.0), high-vuln-4 (1.0.0), high-vuln-5 (1.0.0), high-vuln-6 (1.0.0) [transitive-only]
# 3 Low: low-vuln-1 (1.0.0), low-vuln-2 (1.0.0), low-vuln-3 (1.0.0)

vuln_pkgs = {
    "ejs": "3.1.6",
    "minimist": "1.2.0",
    "lodash": "4.17.15",
    "axios": "0.21.1",
    "node-fetch": "2.6.0",
    "jsonwebtoken": "8.5.1",
    "high-vuln-1": "1.0.0",
    "high-vuln-2": "1.0.0",
    "high-vuln-3": "1.0.0",
    "high-vuln-4": "1.0.0",
    "high-vuln-5": "1.0.0",
    "high-vuln-6": "1.0.0",
    "low-vuln-1": "1.0.0",
    "low-vuln-2": "1.0.0",
    "low-vuln-3": "1.0.0"
}

# 6 transitive-only vulns: high-vuln-1, high-vuln-2, high-vuln-3, high-vuln-4, high-vuln-5, high-vuln-6
direct_vulns = {"ejs": "3.1.6", "minimist": "1.2.0", "lodash": "4.17.15", "axios": "0.21.1", "node-fetch": "2.6.0", "jsonwebtoken": "8.5.1", "low-vuln-1": "1.0.0", "low-vuln-2": "1.0.0", "low-vuln-3": "1.0.0"}

p3_pkg = {
    "name": "p3-high-risk-app",
    "version": "1.0.0",
    "private": True,
    "dependencies": {
        **direct_vulns,
        **{f"safe-dep-{i}": "1.0.0" for i in range(1, 10)}
    }
}
with open(os.path.join(p3_dir, "package.json"), "w") as f:
    json.dump(p3_pkg, f, indent=2)

p3_lock_packages = {"": {"name": "p3-high-risk-app", "version": "1.0.0"}}
for name, ver in vuln_pkgs.items():
    p3_lock_packages[f"node_modules/{name}"] = {"version": ver, "license": "MIT"}

for i in range(1, 65):
    dep_name = f"safe-dep-{i}"
    p3_lock_packages[f"node_modules/{dep_name}"] = {"version": "1.0.0", "license": "MIT"}

p3_lock = {
    "name": "p3-high-risk-app",
    "version": "1.0.0",
    "lockfileVersion": 3,
    "packages": p3_lock_packages
}
with open(os.path.join(p3_dir, "package-lock.json"), "w") as f:
    json.dump(p3_lock, f, indent=2)

# src has 5 reachable attack paths: lodash _.merge, axios.get, node-fetch, ejs.render, jsonwebtoken.verify
# minimist is NOT called with vulnerable args
with open(os.path.join(p3_dir, "src", "index.js"), "w") as f:
    f.write("""
const _ = require('lodash');
const axios = require('axios');
const fetch = require('node-fetch');
const ejs = require('ejs');
const jwt = require('jsonwebtoken');
const minimist = require('minimist');

// 5 Reachable attack path call sites:
_.merge({}, { a: 1 });
axios.get('https://example.com/api');
fetch('https://example.com/data');
ejs.render('<h1><%= user %></h1>', { user: 'Admin' });
jwt.verify('sample.token.str', 'secret');

// minimist is imported but not called with vulnerable options
""")

# ==========================================
# 4. p4-trap-app (80 deps, 0 vulns, 2 suspicious [expresss, lodassh], 2 licenses [acme-agpl-lib, acme-nolicense-lib])
# Zero false positives: express, lodash.merge, date-fns NOT flagged. safe-setup-tool INFO only.
# ==========================================
p4_dir = make_sample_dir("p4-trap-app")

p4_pkg = {
    "name": "p4-trap-app",
    "version": "1.0.0",
    "private": True,
    "dependencies": {
        "express": "4.18.2",
        "lodash.merge": "4.6.2",
        "date-fns": "2.30.0",
        "expresss": "1.0.0",
        "lodassh": "1.0.0",
        "safe-setup-tool": "file:vendor/safe-setup-tool",
        "acme-agpl-lib": "file:vendor/acme-agpl-lib",
        "acme-nolicense-lib": "file:vendor/acme-nolicense-lib",
        **{f"trap-dep-{i}": "1.0.0" for i in range(1, 10)}
    }
}
with open(os.path.join(p4_dir, "package.json"), "w") as f:
    json.dump(p4_pkg, f, indent=2)

p4_lock_packages = {
    "": {"name": "p4-trap-app", "version": "1.0.0"},
    "node_modules/express": {"version": "4.18.2", "license": "MIT"},
    "node_modules/lodash.merge": {"version": "4.6.2", "license": "MIT"},
    "node_modules/date-fns": {"version": "2.30.0", "license": "MIT"},
    "node_modules/expresss": {"version": "1.0.0", "license": "MIT"},
    "node_modules/lodassh": {"version": "1.0.0", "license": "MIT"},
    "node_modules/safe-setup-tool": {"version": "1.0.0", "resolved": "file:vendor/safe-setup-tool", "license": "MIT"},
    "node_modules/acme-agpl-lib": {"version": "1.0.0", "resolved": "file:vendor/acme-agpl-lib", "license": "AGPL-3.0"},
    "node_modules/acme-nolicense-lib": {"version": "1.0.0", "resolved": "file:vendor/acme-nolicense-lib"}
}
for i in range(1, 73):
    dep_name = f"trap-dep-{i}"
    p4_lock_packages[f"node_modules/{dep_name}"] = {"version": "1.0.0", "license": "MIT"}

p4_lock = {
    "name": "p4-trap-app",
    "version": "1.0.0",
    "lockfileVersion": 3,
    "packages": p4_lock_packages
}
with open(os.path.join(p4_dir, "package-lock.json"), "w") as f:
    json.dump(p4_lock, f, indent=2)

# Vendor directories in p4-trap-app:
vendor_dir = os.path.join(p4_dir, "vendor")
os.makedirs(vendor_dir, exist_ok=True)

# 1. safe-setup-tool: benign install script
sst_dir = os.path.join(vendor_dir, "safe-setup-tool")
os.makedirs(sst_dir, exist_ok=True)
with open(os.path.join(sst_dir, "package.json"), "w") as f:
    json.dump({
        "name": "safe-setup-tool",
        "version": "1.0.0",
        "license": "MIT",
        "scripts": {
            "postinstall": "mkdir -p dist"
        }
    }, f, indent=2)

# 2. acme-agpl-lib: AGPL-3.0 license
agpl_dir = os.path.join(vendor_dir, "acme-agpl-lib")
os.makedirs(agpl_dir, exist_ok=True)
with open(os.path.join(agpl_dir, "package.json"), "w") as f:
    json.dump({
        "name": "acme-agpl-lib",
        "version": "1.0.0",
        "license": "AGPL-3.0"
    }, f, indent=2)

# 3. acme-nolicense-lib: missing license
nolic_dir = os.path.join(vendor_dir, "acme-nolicense-lib")
os.makedirs(nolic_dir, exist_ok=True)
with open(os.path.join(nolic_dir, "package.json"), "w") as f:
    json.dump({
        "name": "acme-nolicense-lib",
        "version": "1.0.0"
    }, f, indent=2)

with open(os.path.join(p4_dir, "src", "index.js"), "w") as f:
    f.write("// Trap app code\n")

print("All fixture samples generated successfully!")

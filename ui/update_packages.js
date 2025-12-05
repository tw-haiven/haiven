// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

function isNodeVersionAtLeast(target) {
  const current = process.versions.node; // e.g., "22.6.0"
  const toNums = (v) => v.split(".").map((n) => parseInt(n, 10));
  const [c1, c2, c3] = toNums(current);
  const [t1, t2, t3] = toNums(target);
  if (c1 !== t1) return c1 > t1;
  if (c2 !== t2) return c2 > t2;
  return c3 >= t3;
}

// Function to update packages in package.json
function updatePackages() {
  const packageJsonPath = path.resolve(process.cwd(), "package.json");

  if (!fs.existsSync(packageJsonPath)) {
    console.error("package.json not found in the current directory.");
    process.exit(1);
  }

  const minNode = "22.18.0";
  if (!isNodeVersionAtLeast(minNode)) {
    console.error(
      `Detected Node ${process.versions.node}. To upgrade all UI dependencies to latest, please use Node >= ${minNode}.\n` +
        "Reason: to standardize on Node v22.18.0 across CI/Docker/local we require this minimum for upgrade scripts.\n" +
        "You can still run the app/tests with your current Node, but full upgrade requires this newer Node.",
    );
    process.exit(2);
  }

  try {
    // Read package.json
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, "utf8"));
    const allDeps = {
      ...packageJson.dependencies,
      ...packageJson.devDependencies,
    };

    // Packages to exclude from --latest (keep within the current major version)
    // These will be upgraded with yarn upgrade (respecting semver) instead
    const excludeFromLatest = ["antd"];

    console.log("Updating dependencies...");
    console.log(
      `Packages pinned to current major version: ${excludeFromLatest.join(", ")}`,
    );

    // Upgrade pinned packages respecting their semver range (e.g., ^5 stays in v5.x)
    console.log(
      "\nUpgrading pinned packages within their current major version...",
    );
    for (const pkg of excludeFromLatest) {
      if (allDeps[pkg]) {
        console.log(`  Upgrading ${pkg} (respecting semver range)...`);
        try {
          execSync(`yarn upgrade ${pkg}`, { stdio: "inherit" });
        } catch (err) {
          console.warn(`  Warning: Could not upgrade ${pkg}, continuing...`);
        }
      }
    }

    // Upgrade all other packages to the latest, excluding pinned ones
    console.log(
      "\nUpgrading remaining dependencies to their latest versions...",
    );
    const packagesToUpgrade = Object.keys(allDeps).filter(
      (pkg) => !excludeFromLatest.includes(pkg),
    );

    // Upgrade in batches to avoid command line length limits
    const batchSize = 20;
    for (let i = 0; i < packagesToUpgrade.length; i += batchSize) {
      const batch = packagesToUpgrade.slice(i, i + batchSize);
      try {
        execSync(`yarn upgrade --latest ${batch.join(" ")}`, {
          stdio: "inherit",
        });
      } catch (err) {
        console.warn(
          "  Warning: Some packages failed to upgrade, continuing...",
        );
      }
    }

    // Install and update yarn.lock
    console.log("\nInstalling updated dependencies and updating yarn.lock...");
    execSync("yarn install", { stdio: "inherit" });

    console.log(
      "\n✓ All dependencies have been updated and yarn.lock is in sync.",
    );
    console.log("\nPackages kept within current major version:");
    for (const pkg of excludeFromLatest) {
      if (allDeps[pkg]) {
        console.log(`  - ${pkg}: ${allDeps[pkg]}`);
      }
    }
  } catch (error) {
    console.error("Error updating dependencies:", error);
    process.exit(1);
  }
}

// Run the update function
updatePackages();

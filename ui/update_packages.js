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
    // Update all dependencies to their latest versions
    console.log("Updating all dependencies to their latest versions...");
    execSync("yarn upgrade --latest", { stdio: "inherit" });

    // Install the latest versions and update yarn.lock
    console.log("Installing updated dependencies and updating yarn.lock...");
    execSync("yarn install", { stdio: "inherit" });

    console.log("All dependencies have been updated and yarn.lock is in sync.");
  } catch (error) {
    console.error("Error updating dependencies:", error);
    process.exit(1);
  }
}

// Run the update function
updatePackages();

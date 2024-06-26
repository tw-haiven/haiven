// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

// Function to update packages in package.json
function updatePackages() {
  const packageJsonPath = path.resolve(process.cwd(), "package.json");
  const packageLockPath = path.resolve(process.cwd(), "yarn.lock");

  if (!fs.existsSync(packageJsonPath)) {
    console.error("package.json not found in the current directory.");
    process.exit(1);
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
  }
}

// Run the update function
updatePackages();

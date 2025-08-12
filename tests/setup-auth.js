// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
const { chromium } = require("@playwright/test");

const environments = {
  demo: {
    url: "https://team-ai-owd2wjctzq-uc.a.run.app/boba/",
    authFile: "playwright/.auth/demo-user.json",
    name: "Demo",
  },
  prod: {
    url: "https://haiven.thoughtworks-labs.net/boba/",
    authFile: "playwright/.auth/prod-user.json",
    name: "Production",
  },
};

(async () => {
  const env = process.argv[2];

  if (!env || !environments[env]) {
    console.log("❌ Please specify environment: demo or prod");
    console.log("Usage: node setup-auth.js <demo|prod>");
    console.log("");
    console.log("Examples:");
    console.log("  node setup-auth.js demo");
    console.log("  node setup-auth.js prod");
    process.exit(1);
  }

  const config = environments[env];

  console.log(`🔐 Setting up ${config.name} environment authentication...`);

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log(`📱 Opening ${config.name.toLowerCase()} environment...`);
  await page.goto(config.url);

  console.log(
    "⏳ Please complete Okta authentication in the opened browser window.",
  );
  console.log(
    "Once you see the Haiven application (not the login page), press Enter...",
  );

  // Wait for user input
  await new Promise((resolve) => {
    process.stdin.resume();
    process.stdin.once("data", resolve);
  });

  console.log("💾 Saving authentication state...");
  await context.storageState({ path: config.authFile });

  console.log(
    `✅ ${config.name} authentication saved! You can now run: npm run test:${env}`,
  );
  await browser.close();
  process.exit(0);
})();

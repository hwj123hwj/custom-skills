#!/usr/bin/env node
'use strict';

const fs = require('fs');

const PLATFORM_PACKAGES = {
  'darwin-arm64': '@jackwener/wx-cli-darwin-arm64',
  'darwin-x64':   '@jackwener/wx-cli-darwin-x64',
  'linux-x64':    '@jackwener/wx-cli-linux-x64',
  'linux-arm64':  '@jackwener/wx-cli-linux-arm64',
  'win32-x64':    '@jackwener/wx-cli-win32-x64',
};

const platformKey = `${process.platform}-${process.arch}`;
const pkg = PLATFORM_PACKAGES[platformKey];

if (!pkg) {
  console.log(`wx-cli: no binary for ${platformKey}, skipping`);
  process.exit(0);
}

const ext = process.platform === 'win32' ? '.exe' : '';

try {
  const binaryPath = require.resolve(`${pkg}/bin/wx${ext}`);
  if (process.platform !== 'win32') {
    fs.chmodSync(binaryPath, 0o755);
  }
} catch {
  console.log(`wx-cli: platform package ${pkg} not installed`);
}

#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT_DIR = path.resolve(__dirname, '..');
const VENV_DIR = path.resolve(ROOT_DIR, '.venv');

const isWindows = process.platform === 'win32';
const VENV_PYTHON = isWindows
  ? path.resolve(VENV_DIR, 'Scripts', 'python.exe')
  : path.resolve(VENV_DIR, 'bin', 'python');
const VENV_PIP = isWindows
  ? path.resolve(VENV_DIR, 'Scripts', 'pip.exe')
  : path.resolve(VENV_DIR, 'bin', 'pip');

function run(cmd, options = {}) {
  console.log(`> ${cmd}`);
  execSync(cmd, { stdio: 'inherit', cwd: ROOT_DIR, ...options });
}

function findSystemPython() {
  const candidates = ['python3', 'python'];
  for (const py of candidates) {
    try {
      const version = execSync(`${py} --version`, { encoding: 'utf8' }).trim();
      return { bin: py, version };
    } catch {
      // Continue searching
    }
  }
  return null;
}

async function setup() {
  console.log('📦 Starting otoge-db environment setup...\n');

  // 1. Check Python
  const pyInfo = findSystemPython();
  if (!pyInfo) {
    console.error('❌ Error: Python 3 was not found in your PATH.');
    console.error('Please install Python 3 (https://www.python.org/) and try again.');
    process.exit(1);
  }
  console.log(`✓ Found system Python: ${pyInfo.version} (${pyInfo.bin})`);

  // 2. Setup virtual environment
  if (!fs.existsSync(VENV_DIR) || !fs.existsSync(VENV_PYTHON)) {
    console.log('🌱 Creating Python virtual environment (.venv)...');
    run(`${pyInfo.bin} -m venv .venv`);
  } else {
    console.log('✓ Virtual environment (.venv) already exists');
  }

  // 3. Install Python requirements
  const requirementsFile = path.resolve(ROOT_DIR, 'requirements.txt');
  if (fs.existsSync(requirementsFile)) {
    console.log('📚 Installing Python requirements from requirements.txt...');
    run(`"${VENV_PYTHON}" -m pip install -r requirements.txt`);
  }

  // 4. Run initial build
  console.log('\n🏗️ Running initial project build...');
  const { buildAll } = require('./build');
  await buildAll();

  console.log('\n========================================');
  console.log('🎉 Setup complete! You are ready to go.');
  console.log('========================================');
  console.log('Commands:');
  console.log('  • yarn dev        - Start local development server with auto-reload');
  console.log('  • yarn build      - Build all Pug, LESS, and JS assets');
  console.log('  • yarn fetch-*    - Fetch songs and data (e.g. yarn fetch-songs --ongeki)');
  console.log('');
}

setup().catch((err) => {
  console.error('\n❌ Setup failed:', err);
  process.exit(1);
});

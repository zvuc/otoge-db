#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const pug = require('pug');
const less = require('less');
const postcss = require('postcss');
const autoprefixer = require('autoprefixer');
const cssnano = require('cssnano');
const esbuild = require('esbuild');

const ROOT_DIR = path.resolve(__dirname, '..');

// Helper to resolve paths relative to root
const resolveRoot = (...segments) => path.resolve(ROOT_DIR, ...segments);

// Ensure directory exists
function ensureDirForFile(filePath) {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

// 1. Pug Compilation
const PUG_TARGETS = [
  { src: 'shared/src/pug/index.pug', dest: 'index.html' },
  { src: 'ongeki/src/pug/index.pug', dest: 'ongeki/index.html' },
  { src: 'ongeki/src/pug/lv/index.pug', dest: 'ongeki/lv/index.html' },
  { src: 'ongeki/src/pug/namuwiki.pug', dest: 'ongeki/namuwiki.html' },
  { src: 'chunithm/src/pug/index.pug', dest: 'chunithm/index.html' },
  { src: 'chunithm/src/pug/lv/index.pug', dest: 'chunithm/lv/index.html' },
  { src: 'maimai/src/pug/index.pug', dest: 'maimai/index.html' },
  { src: 'maimai/src/pug/lv/index.pug', dest: 'maimai/lv/index.html' },
];

async function compilePug(targets = PUG_TARGETS) {
  const start = Date.now();
  console.log('[PUG] Compiling templates...');
  for (const target of targets) {
    const srcPath = resolveRoot(target.src);
    const destPath = resolveRoot(target.dest);
    ensureDirForFile(destPath);
    try {
      const html = pug.renderFile(srcPath, {
        pretty: true,
        basedir: ROOT_DIR,
      });
      fs.writeFileSync(destPath, html, 'utf8');
      console.log(`  ✓ ${target.src} -> ${target.dest}`);
    } catch (err) {
      console.error(`  ✗ Error compiling ${target.src}:`, err.message);
      throw err;
    }
  }
  console.log(`[PUG] Done in ${Date.now() - start}ms`);
}

// 2. LESS + PostCSS (Autoprefixer + CSSnano)
const LESS_TARGETS = [
  { src: 'ongeki/src/less/ongeki.less', dest: 'ongeki/style.css' },
  { src: 'chunithm/src/less/chunithm.less', dest: 'chunithm/style.css' },
  { src: 'maimai/src/less/maimai.less', dest: 'maimai/style.css' },
];

async function compileLess(targets = LESS_TARGETS) {
  const start = Date.now();
  console.log('[LESS] Compiling stylesheets...');
  const postCssProcessor = postcss([autoprefixer, cssnano]);

  for (const target of targets) {
    const srcPath = resolveRoot(target.src);
    const destPath = resolveRoot(target.dest);
    ensureDirForFile(destPath);

    try {
      const lessContent = fs.readFileSync(srcPath, 'utf8');
      const lessResult = await less.render(lessContent, {
        filename: srcPath,
      });

      const postCssResult = await postCssProcessor.process(lessResult.css, {
        from: srcPath,
        to: destPath,
      });

      fs.writeFileSync(destPath, postCssResult.css, 'utf8');
      console.log(`  ✓ ${target.src} -> ${target.dest}`);
    } catch (err) {
      console.error(`  ✗ Error compiling ${target.src}:`, err.message);
      throw err;
    }
  }
  console.log(`[LESS] Done in ${Date.now() - start}ms`);
}

// 3. JavaScript Concatenation & Minification with esbuild
const JS_TARGETS = [
  {
    srcs: [
      'shared/src/js/shared.page-functions.js',
      'shared/src/js/shared.table-config.js',
    ],
    dest: 'shared/shared-functions.js',
  },
  {
    srcs: ['shared/src/js/early-functions.js'],
    dest: 'shared/early-functions.js',
  },
  {
    srcs: ['shared/src/datatables/datatables.custom.js'],
    dest: 'shared/datatables.custom.min.js',
  },
  {
    srcs: ['ongeki/src/js/ongeki.table-config.js'],
    dest: 'ongeki/ongeki-functions.js',
  },
  {
    srcs: ['chunithm/src/js/chunithm.table-config.js'],
    dest: 'chunithm/chunithm-functions.js',
  },
  {
    srcs: ['maimai/src/js/maimai.table-config.js'],
    dest: 'maimai/maimai-functions.js',
  },
];

async function minifyJs(targets = JS_TARGETS) {
  const start = Date.now();
  console.log('[JS] Minifying scripts with esbuild...');
  for (const target of targets) {
    const destPath = resolveRoot(target.dest);
    ensureDirForFile(destPath);

    try {
      const combined = target.srcs
        .map((src) => fs.readFileSync(resolveRoot(src), 'utf8'))
        .join('\n;\n');

      const result = await esbuild.transform(combined, {
        minify: true,
        target: 'es2018',
      });

      fs.writeFileSync(destPath, result.code, 'utf8');
      console.log(`  ✓ ${target.srcs.join(', ')} -> ${target.dest}`);
    } catch (err) {
      console.error(`  ✗ Error minifying ${target.dest}:`, err.message);
      throw err;
    }
  }
  console.log(`[JS] Done in ${Date.now() - start}ms`);
}

// Build All
async function buildAll(options = {}) {
  const totalStart = Date.now();
  console.log('🚀 Starting otoge-db build...\n');

  const tasks = [];
  if (!options.only || options.only === 'pug') tasks.push(compilePug());
  if (!options.only || options.only === 'less') tasks.push(compileLess());
  if (!options.only || options.only === 'js') tasks.push(minifyJs());

  await Promise.all(tasks);
  console.log(`\n✨ Build completed successfully in ${Date.now() - totalStart}ms`);
}

module.exports = {
  compilePug,
  compileLess,
  minifyJs,
  buildAll,
  PUG_TARGETS,
  LESS_TARGETS,
  JS_TARGETS,
};

if (require.main === module) {
  const args = process.argv.slice(2);
  let only = null;
  if (args.includes('--pug')) only = 'pug';
  else if (args.includes('--less')) only = 'less';
  else if (args.includes('--js')) only = 'js';

  buildAll({ only }).catch((err) => {
    console.error('\n❌ Build failed:', err);
    process.exit(1);
  });
}

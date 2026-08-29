#!/usr/bin/env node
const chokidar = require('chokidar');
const browserSync = require('browser-sync').create();
const { compilePug, compileLess, minifyJs, buildAll } = require('./build');

let isBuildingPug = false;
let isBuildingLess = false;
let isBuildingJs = false;

async function startDev() {
  console.log('🚀 Starting initial build...');
  await buildAll();

  console.log('\n🌐 Initializing local development server...');
  browserSync.init({
    server: {
      baseDir: './',
    },
    port: 3000,
    open: false,
    notify: false,
    ui: false,
    ghostMode: false,
  });

  // Watch Pug files
  chokidar
    .watch(['shared/src/pug/**/*', 'ongeki/src/pug/**/*', 'chunithm/src/pug/**/*', 'maimai/src/pug/**/*'], {
      ignoreInitial: true,
    })
    .on('all', async (event, filePath) => {
      if (isBuildingPug) return;
      isBuildingPug = true;
      console.log(`\n[DEV] Pug file changed: ${filePath}`);
      try {
        await compilePug();
        browserSync.reload();
      } catch (e) {
        console.error('[DEV] Pug build failed:', e.message);
      } finally {
        isBuildingPug = false;
      }
    });

  // Watch LESS files
  chokidar
    .watch(['shared/src/less/**/*', 'ongeki/src/less/**/*', 'chunithm/src/less/**/*', 'maimai/src/less/**/*'], {
      ignoreInitial: true,
    })
    .on('all', async (event, filePath) => {
      if (isBuildingLess) return;
      isBuildingLess = true;
      console.log(`\n[DEV] Less file changed: ${filePath}`);
      try {
        await compileLess();
        browserSync.reload('*.css');
      } catch (e) {
        console.error('[DEV] Less build failed:', e.message);
      } finally {
        isBuildingLess = false;
      }
    });

  // Watch JS files
  chokidar
    .watch(
      [
        'shared/src/js/**/*',
        'shared/src/datatables/datatables.custom.js',
        'ongeki/src/js/**/*',
        'chunithm/src/js/**/*',
        'maimai/src/js/**/*',
      ],
      { ignoreInitial: true }
    )
    .on('all', async (event, filePath) => {
      if (isBuildingJs) return;
      isBuildingJs = true;
      console.log(`\n[DEV] JS file changed: ${filePath}`);
      try {
        await minifyJs();
        browserSync.reload();
      } catch (e) {
        console.error('[DEV] JS build failed:', e.message);
      } finally {
        isBuildingJs = false;
      }
    });

  console.log('\n👀 Watching for changes in src directories...\n');
}

startDev().catch((err) => {
  console.error('Failed to start dev server:', err);
  process.exit(1);
});

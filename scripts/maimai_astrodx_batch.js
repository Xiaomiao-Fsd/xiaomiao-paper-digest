#!/usr/bin/env node

const fs = require('fs');
const fsp = require('fs/promises');
const path = require('path');
const os = require('os');
const { Readable } = require('stream');
const { pipeline } = require('stream/promises');
const { createInterface } = require('readline/promises');
const { stdin, stdout } = require('process');

const DXDATA_URL = 'https://dxrating.net/assets/dxdata-853f5308.js';
const ASTRO_BASE_URL = 'https://api.milkbot.cn/server';
const TARGET_VERSIONS = ['FESTiVAL', 'FESTiVAL PLUS', 'BUDDiES', 'BUDDiES PLUS'];
const DEFAULT_MIN_INTERNAL = 14;
const DEFAULT_DELAY_MS = 300;

const workspaceRoot = path.resolve(__dirname, '..');
const defaultStatePath = path.join(workspaceRoot, '.openclaw', 'astrodx-maimai-state.json');
const defaultCaptchaPath = path.join(os.homedir(), 'Documents', 'astrodx_captcha.svg');
const defaultOutDir = path.join(os.homedir(), 'Documents', 'AstroDX_maimai_14plus_festival_buddies');

function printUsage() {
  console.log(`
Usage:
  node scripts/maimai_astrodx_batch.js captcha [--state <file>] [--captcha-out <file>]
  node scripts/maimai_astrodx_batch.js manifest [--out-dir <dir>] [--min <num>]
  node scripts/maimai_astrodx_batch.js download [--code <4chars>] [--state <file>] [--out-dir <dir>] [--no-bga] [--overwrite] [--min <num>]
  node scripts/maimai_astrodx_batch.js interactive [--state <file>] [--captcha-out <file>] [--out-dir <dir>] [--no-bga] [--overwrite] [--min <num>]

What it does:
  - Pulls charts from DXRating
  - Filters maimai FESTiVAL / FESTiVAL PLUS / BUDDiES / BUDDiES PLUS charts with internal level >= 14
  - Uses AstroDX's captcha -> verify -> download-link flow
  - Downloads .adx files into your Documents folder

Examples:
  node scripts/maimai_astrodx_batch.js captcha
  node scripts/maimai_astrodx_batch.js download --code Ab12
  node scripts/maimai_astrodx_batch.js download --code Ab12 --no-bga --out-dir ~/Documents/AstroDX
  node scripts/maimai_astrodx_batch.js interactive --out-dir ~/Documents/AstroDX
`);
}

function parseArgs(argv) {
  const args = {
    command: argv[2],
    state: defaultStatePath,
    captchaOut: defaultCaptchaPath,
    outDir: defaultOutDir,
    min: DEFAULT_MIN_INTERNAL,
    overwrite: false,
    noBga: false,
    code: null,
    delayMs: DEFAULT_DELAY_MS,
  };

  for (let i = 3; i < argv.length; i += 1) {
    const cur = argv[i];
    const next = argv[i + 1];
    switch (cur) {
      case '--state':
        args.state = expandHome(next);
        i += 1;
        break;
      case '--captcha-out':
        args.captchaOut = expandHome(next);
        i += 1;
        break;
      case '--out-dir':
        args.outDir = expandHome(next);
        i += 1;
        break;
      case '--min':
        args.min = Number(next);
        i += 1;
        break;
      case '--code':
        args.code = next;
        i += 1;
        break;
      case '--delay-ms':
        args.delayMs = Number(next);
        i += 1;
        break;
      case '--overwrite':
        args.overwrite = true;
        break;
      case '--no-bga':
        args.noBga = true;
        break;
      case '--help':
      case '-h':
        args.command = 'help';
        break;
      default:
        throw new Error(`Unknown argument: ${cur}`);
    }
  }

  return args;
}

function expandHome(p) {
  if (!p) return p;
  if (p === '~') return os.homedir();
  if (p.startsWith('~/')) return path.join(os.homedir(), p.slice(2));
  return p;
}

function ensureFiniteNumber(value, fallback, label) {
  if (Number.isFinite(value)) return value;
  if (fallback !== undefined) return fallback;
  throw new Error(`${label} must be a number`);
}

async function mkdirp(target) {
  await fsp.mkdir(target, { recursive: true });
}

async function writeJson(filePath, data) {
  await mkdirp(path.dirname(filePath));
  const tmpPath = `${filePath}.tmp`;
  await fsp.writeFile(tmpPath, JSON.stringify(data, null, 2), 'utf8');
  await fsp.rename(tmpPath, filePath);
}

async function readJson(filePath) {
  const raw = await fsp.readFile(filePath, 'utf8');
  return JSON.parse(raw);
}

function sanitizeFilename(name) {
  const cleaned = String(name || 'unknown')
    .replace(/[<>:"/\\|?*\x00-\x1F]/g, '_')
    .replace(/\s+/g, ' ')
    .trim();
  const truncated = cleaned.slice(0, 120).trim();
  return truncated || 'unknown';
}

function cookieFromSetCookie(setCookieValue) {
  if (!setCookieValue) return null;
  return setCookieValue.split(';', 1)[0].trim() || null;
}

function baseHeaders(cookie = null) {
  const headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36',
    Referer: 'https://astrodx.milkbot.cn/',
    Origin: 'https://astrodx.milkbot.cn',
  };
  if (cookie) headers.Cookie = cookie;
  return headers;
}

async function fetchText(url) {
  const res = await fetch(url, { headers: baseHeaders() });
  if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status} ${res.statusText}`);
  return await res.text();
}

function extractDxDataArrayLiteral(source) {
  const marker = 'const l=';
  const markerIndex = source.indexOf(marker);
  if (markerIndex < 0) throw new Error('DXRating data marker `const l=` not found');

  const arrayStart = source.indexOf('[', markerIndex + marker.length);
  if (arrayStart < 0) throw new Error('DXRating data array start not found');

  let depth = 0;
  let inString = false;
  let quote = '';
  let escaped = false;
  let end = -1;

  for (let i = arrayStart; i < source.length; i += 1) {
    const ch = source[i];

    if (inString) {
      if (escaped) escaped = false;
      else if (ch === '\\') escaped = true;
      else if (ch === quote) inString = false;
      continue;
    }

    if (ch === '"' || ch === "'") {
      inString = true;
      quote = ch;
      continue;
    }

    if (ch === '[') depth += 1;
    else if (ch === ']') {
      depth -= 1;
      if (depth === 0) {
        end = i + 1;
        break;
      }
    }
  }

  if (end < 0) throw new Error('DXRating data array end not found');
  return source.slice(arrayStart, end);
}

async function loadTargetCharts(minInternal = DEFAULT_MIN_INTERNAL) {
  const js = await fetchText(DXDATA_URL);
  const arrayLiteral = extractDxDataArrayLiteral(js);
  const songs = Function(`return (${arrayLiteral});`)();
  const versionSet = new Set(TARGET_VERSIONS);

  const downloadable = [];
  const missingInternalId = [];

  for (const song of songs) {
    for (const sheet of song.sheets || []) {
      const version = String(sheet.version || '');
      if (!versionSet.has(version)) continue;

      const internalLevelValue = Number(sheet.internalLevelValue);
      if (!Number.isFinite(internalLevelValue) || internalLevelValue < minInternal) continue;

      const item = {
        internalId: sheet.internalId ?? null,
        title: song.title,
        difficulty: sheet.difficulty,
        type: sheet.type,
        level: sheet.level,
        internalLevelValue,
        version,
      };

      if (item.internalId == null) missingInternalId.push(item);
      else downloadable.push(item);
    }
  }

  downloadable.sort((a, b) =>
    a.version.localeCompare(b.version) ||
    a.internalId - b.internalId ||
    a.title.localeCompare(b.title)
  );
  missingInternalId.sort((a, b) => a.version.localeCompare(b.version) || a.title.localeCompare(b.title));

  const summary = {};
  for (const item of downloadable) summary[item.version] = (summary[item.version] || 0) + 1;

  return { summary, downloadable, missingInternalId };
}

function renderManifestText(data) {
  const lines = [];
  lines.push('maimai FESTiVAL / FESTiVAL PLUS / BUDDiES / BUDDiES PLUS 14+ charts');
  lines.push('');
  lines.push(`Downloadable charts: ${data.downloadable.length}`);
  for (const version of Object.keys(data.summary).sort()) {
    lines.push(`- ${version}: ${data.summary[version]}`);
  }
  lines.push('');

  if (data.missingInternalId.length > 0) {
    lines.push(`Missing internalId (skipped): ${data.missingInternalId.length}`);
    for (const item of data.missingInternalId) {
      lines.push(`- ${item.version} | ${item.title} | ${item.difficulty} | ${item.type} | ${item.level} | ${item.internalLevelValue}`);
    }
    lines.push('');
  }

  lines.push('Downloadable list:');
  for (const item of data.downloadable) {
    lines.push(`${item.internalId}\t${item.version}\t${item.title}\t${item.difficulty}\t${item.type}\t${item.level}\t${item.internalLevelValue}`);
  }
  lines.push('');
  return lines.join('\n');
}

async function writeManifestFiles(outDir, data) {
  await mkdirp(outDir);
  const jsonPath = path.join(outDir, 'manifest.json');
  const txtPath = path.join(outDir, 'manifest.txt');
  await fsp.writeFile(txtPath, renderManifestText(data), 'utf8');
  await writeJson(jsonPath, data);
  return { jsonPath, txtPath };
}

async function fetchCaptcha({ statePath, captchaOut }) {
  const captchaUrl = `${ASTRO_BASE_URL}/api/captcha?t=${Date.now()}`;
  const res = await fetch(captchaUrl, { headers: baseHeaders() });
  if (!res.ok) throw new Error(`Failed to fetch captcha: ${res.status} ${res.statusText}`);

  const setCookie = res.headers.get('set-cookie');
  const cookie = cookieFromSetCookie(setCookie);
  if (!cookie) throw new Error('Captcha response did not include a usable session cookie');

  const buffer = Buffer.from(await res.arrayBuffer());
  await mkdirp(path.dirname(captchaOut));
  await fsp.writeFile(captchaOut, buffer);

  const state = {
    createdAt: new Date().toISOString(),
    cookie,
    captchaOut,
    key: null,
    lastVerifiedAt: null,
  };
  await writeJson(statePath, state);

  return { captchaOut, statePath, cookie };
}

async function loadState(statePath) {
  if (!fs.existsSync(statePath)) {
    throw new Error(`State file not found: ${statePath}. Run the captcha command first.`);
  }
  return await readJson(statePath);
}

async function verifyCaptchaCode({ statePath, code }) {
  if (!/^[a-zA-Z0-9]{4}$/.test(code || '')) {
    throw new Error('Captcha code must be exactly 4 letters/numbers');
  }

  const state = await loadState(statePath);
  if (!state.cookie) throw new Error('Missing captcha session cookie. Run the captcha command again.');

  const res = await fetch(`${ASTRO_BASE_URL}/api/verify_captcha`, {
    method: 'POST',
    headers: {
      ...baseHeaders(state.cookie),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ code }),
  });

  let data;
  try {
    data = await res.json();
  } catch (err) {
    throw new Error(`Captcha verify returned non-JSON response: ${err.message}`);
  }

  if (!res.ok) {
    throw new Error(data?.message || `Captcha verify failed with ${res.status}`);
  }
  if (!data?.success || !data?.key) {
    throw new Error(data?.message || 'Captcha verify did not return a download key');
  }

  state.key = data.key;
  state.lastVerifiedAt = new Date().toISOString();
  await writeJson(statePath, state);
  return data.key;
}

async function getDownloadLink({ statePath, internalId, downloadType }) {
  const state = await loadState(statePath);
  if (!state.key) throw new Error('Missing download key. Run download with --code or verify captcha first.');

  const url = new URL(`${ASTRO_BASE_URL}/api/get_download_link`);
  url.searchParams.set('id', String(internalId));
  url.searchParams.set('key', String(state.key));
  url.searchParams.set('type', downloadType);

  const res = await fetch(url, { headers: baseHeaders(state.cookie || null) });
  let data;
  try {
    data = await res.json();
  } catch (err) {
    throw new Error(`Download link response for ${internalId} was not JSON: ${err.message}`);
  }

  if (!res.ok) {
    throw new Error(data?.message || `Download link request failed for ${internalId} (${res.status})`);
  }
  if (!data?.success || !data?.url) {
    throw new Error(data?.message || `Download link missing for ${internalId}`);
  }
  return data.url;
}

async function downloadToFile(url, filePath) {
  const res = await fetch(url, { headers: baseHeaders() });
  if (!res.ok) {
    throw new Error(`Download failed: ${res.status} ${res.statusText}`);
  }
  if (!res.body) {
    throw new Error('Download response had no body');
  }

  await mkdirp(path.dirname(filePath));
  const readable = Readable.fromWeb(res.body);
  const writable = fs.createWriteStream(filePath);
  await pipeline(readable, writable);
}

async function runManifestCommand(args) {
  const data = await loadTargetCharts(ensureFiniteNumber(args.min, DEFAULT_MIN_INTERNAL, '--min'));
  const files = await writeManifestFiles(args.outDir, data);
  console.log(`Manifest JSON: ${files.jsonPath}`);
  console.log(`Manifest TXT:  ${files.txtPath}`);
  console.log(`Downloadable charts: ${data.downloadable.length}`);
  console.log(`Missing internalId: ${data.missingInternalId.length}`);
}

async function runDownloadCommand(args) {
  const minInternal = ensureFiniteNumber(args.min, DEFAULT_MIN_INTERNAL, '--min');
  const delayMs = ensureFiniteNumber(args.delayMs, DEFAULT_DELAY_MS, '--delay-ms');
  const outDir = args.outDir;
  const downloadType = args.noBga ? 'nobga' : 'bga';

  if (args.code) {
    const key = await verifyCaptchaCode({ statePath: args.state, code: args.code });
    console.log(`Captcha verified. Download key saved to state file. (${String(key).slice(0, 8)}...)`);
  }

  const data = await loadTargetCharts(minInternal);
  const manifestFiles = await writeManifestFiles(outDir, data);
  console.log(`Manifest refreshed: ${manifestFiles.jsonPath}`);

  const failures = [];
  let downloaded = 0;
  let skipped = 0;

  for (let index = 0; index < data.downloadable.length; index += 1) {
    const item = data.downloadable[index];
    const fileName = `${item.internalId}_${sanitizeFilename(item.title)}.adx`;
    const destPath = path.join(outDir, fileName);
    const prefix = `[${index + 1}/${data.downloadable.length}]`;

    if (!args.overwrite && fs.existsSync(destPath) && fs.statSync(destPath).size > 0) {
      skipped += 1;
      console.log(`${prefix} Skip existing: ${fileName}`);
      continue;
    }

    try {
      const downloadUrl = await getDownloadLink({
        statePath: args.state,
        internalId: item.internalId,
        downloadType,
      });
      console.log(`${prefix} Downloading ${fileName}`);
      await downloadToFile(downloadUrl, destPath);
      downloaded += 1;
      console.log(`${prefix} Saved ${destPath}`);
    } catch (err) {
      failures.push({ internalId: item.internalId, title: item.title, error: err.message });
      console.error(`${prefix} Failed ${item.internalId} ${item.title}: ${err.message}`);
      if (/key|验证码|captcha/i.test(err.message)) {
        console.error('Download key likely expired or captcha session became invalid. Stop here and fetch a new captcha.');
        break;
      }
    }

    if (delayMs > 0) {
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }

  const summary = {
    finishedAt: new Date().toISOString(),
    outDir,
    downloadType,
    downloaded,
    skipped,
    failed: failures.length,
    failures,
    missingInternalId: data.missingInternalId,
  };
  const summaryPath = path.join(outDir, 'download-summary.json');
  await writeJson(summaryPath, summary);

  console.log('');
  console.log('Download run finished.');
  console.log(`Downloaded: ${downloaded}`);
  console.log(`Skipped:    ${skipped}`);
  console.log(`Failed:     ${failures.length}`);
  console.log(`Summary:    ${summaryPath}`);
  if (data.missingInternalId.length > 0) {
    console.log(`Skipped (no internalId): ${data.missingInternalId.length}`);
  }

  if (failures.length > 0) {
    process.exitCode = 2;
  }
}

async function runInteractiveCommand(args) {
  const result = await fetchCaptcha({ statePath: args.state, captchaOut: args.captchaOut });
  console.log(`Captcha saved to: ${result.captchaOut}`);
  console.log('Open that file, read the 4-character captcha, then paste it below.');

  const rl = createInterface({ input: stdin, output: stdout });
  try {
    const code = (await rl.question('Captcha code: ')).trim();
    await runDownloadCommand({ ...args, code });
  } finally {
    rl.close();
  }
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv);
  } catch (err) {
    console.error(err.message);
    printUsage();
    process.exit(1);
  }

  if (!args.command || args.command === 'help') {
    printUsage();
    return;
  }

  switch (args.command) {
    case 'captcha': {
      const result = await fetchCaptcha({ statePath: args.state, captchaOut: args.captchaOut });
      console.log(`Captcha saved to: ${result.captchaOut}`);
      console.log(`State saved to:   ${result.statePath}`);
      console.log('Reply with the 4-character captcha code, then run the download command with --code <xxxx>.');
      return;
    }
    case 'manifest': {
      await runManifestCommand(args);
      return;
    }
    case 'download': {
      await runDownloadCommand(args);
      return;
    }
    case 'interactive': {
      await runInteractiveCommand(args);
      return;
    }
    default:
      throw new Error(`Unknown command: ${args.command}`);
  }
}

main().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});

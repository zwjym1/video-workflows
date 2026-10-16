// 素材对齐工具 server: node align/server.mjs [path/to/project.config.json]
// No extra dependencies: esbuild (already used by Remotion) bundles the UI, node:http serves it.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {exec} from 'node:child_process';
import * as esbuild from 'esbuild';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const cfgPath = path.resolve(process.argv[2] ?? path.join(HERE, 'project.config.json'));
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const PUB = path.resolve(ROOT, cfg.publicDir);
const TL = path.resolve(ROOT, cfg.timeline);
const PORT = Number(process.env.PORT ?? cfg.port ?? 3210);
const OUT = path.join(HERE, '.build');
fs.mkdirSync(OUT, {recursive: true});
if (!fs.existsSync(TL)) fs.writeFileSync(TL, JSON.stringify({version: 1, shots: []}, null, 2));

const ctx = await esbuild.context({
  entryPoints: [path.join(HERE, 'app.tsx')], bundle: true, format: 'esm', outfile: path.join(OUT, 'app.js'),
  jsx: 'automatic', loader: {'.json': 'json'}, sourcemap: true, target: 'es2020', logLevel: 'warning',
  alias: {'align-project': path.resolve(ROOT, cfg.entry)},
  define: {'process.env.NODE_ENV': '"development"'},
  plugins: [{name: 'notify', setup(b) { b.onEnd((r) => console.log(r.errors.length ? `✖ 编译出错 ${r.errors.length} 处` : `✔ 界面已编译 ${new Date().toLocaleTimeString()}`)); }}],
});
await ctx.rebuild();
await ctx.watch();

const MIME = {'.js': 'text/javascript', '.css': 'text/css', '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.map': 'application/json',
  '.mp4': 'video/mp4', '.webm': 'video/webm', '.mov': 'video/quicktime', '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml'};
const send = (res, code, body, type = 'text/plain; charset=utf-8') => { res.writeHead(code, {'Content-Type': type, 'Cache-Control': 'no-store'}); res.end(body); };
const serveFile = (req, res, file) => {
  fs.stat(file, (err, st) => {
    if (err || !st.isFile()) return send(res, 404, 'not found');
    const type = MIME[path.extname(file).toLowerCase()] ?? 'application/octet-stream';
    const head = {'Content-Type': type, 'Accept-Ranges': 'bytes', 'Cache-Control': 'no-cache', 'Last-Modified': st.mtime.toUTCString()};
    let a = 0, b = st.size - 1, code = 200;
    const range = req.headers.range;
    if (range) { // video seeking needs byte ranges: "bytes=a-b", "bytes=a-", "bytes=-n"
      const m = /^bytes=(\d*)-(\d*)/.exec(range);
      if (m && (m[1] || m[2])) {
        if (m[1]) { a = +m[1]; if (m[2]) b = Math.min(+m[2], st.size - 1); } else { a = Math.max(0, st.size - +m[2]); }
        if (a > b || a >= st.size) { res.writeHead(416, {'Content-Range': `bytes */${st.size}`}); return res.end(); }
        code = 206; head['Content-Range'] = `bytes ${a}-${b}/${st.size}`;
      }
    }
    head['Content-Length'] = b - a + 1;
    res.writeHead(code, head);
    if (req.method === 'HEAD') return res.end();
    const stream = fs.createReadStream(file, {start: a, end: b});
    stream.on('error', (e) => { console.warn('读取失败', path.basename(file), e.message); res.destroy(); });
    res.on('close', () => stream.destroy()); // browser cancelled (seek) -> free the file handle
    stream.pipe(res);
  });
};
const inside = (base, p) => { const r = path.resolve(base, '.' + p); return r.startsWith(base) ? r : null; };

const server = http.createServer((req, res) => {
  req.on('error', () => {}); res.on('error', () => {});
  const url = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (url === '/' || url === '/index.html') return serveFile(req, res, path.join(HERE, 'index.html'));
  if (url === '/__align/app.js' || url === '/__align/app.js.map' || url === '/__align/app.css') return serveFile(req, res, path.join(OUT, url.slice(9)));
  if (url === '/__align/style.css') return serveFile(req, res, path.join(HERE, 'style.css'));
  if (url === '/api/timeline' && req.method === 'GET') return serveFile(req, res, TL);
  if (url === '/api/timeline' && req.method === 'POST') {
    let body = ''; req.on('data', (c) => (body += c)); req.on('end', () => {
      try { const j = JSON.parse(body); if (!Array.isArray(j.shots)) throw new Error('shots missing');
        const bk = path.join(HERE, 'backups'); fs.mkdirSync(bk, {recursive: true});
        if (fs.existsSync(TL)) fs.copyFileSync(TL, path.join(bk, `${path.basename(TL, '.json')}-${new Date().toISOString().replace(/[:.]/g, '-')}.json`));
        fs.writeFileSync(TL, JSON.stringify(j, null, 2) + '\n'); console.log(`💾 已保存 ${path.relative(ROOT, TL)}（${j.shots.length} 个镜头）`); send(res, 200, '{"ok":true}', 'application/json');
      } catch (e) { send(res, 400, String(e)); } });
    return;
  }
  const f = inside(PUB, url); if (!f) return send(res, 403, 'forbidden');
  serveFile(req, res, f);
});
server.keepAliveTimeout = 65000; server.headersTimeout = 70000; server.requestTimeout = 0;
server.on('clientError', (e, sock) => sock.destroy());
server.listen(PORT, '127.0.0.1', () => {
  const u = `http://localhost:${PORT}/`;
  console.log(`\n  素材对齐工具已启动 → ${u}\n  时间线文件: ${path.relative(ROOT, TL)}\n  按 Ctrl+C 退出\n`);
  if (!process.env.NO_OPEN) exec(process.platform === 'win32' ? `start "" "${u}"` : process.platform === 'darwin' ? `open ${u}` : `xdg-open ${u} >/dev/null 2>&1 || true`);
});

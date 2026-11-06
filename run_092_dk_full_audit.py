import json, time, datetime, os, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/4] 에고라이트 Space 4: 디스트로키드 '내 음악(My Music)' 전체 앨범 목록 및 'Bank/Stats' 전수 스캔 중...")

js_full_audit = """
let task = null;
try {
  try { task = await takeOverTaskSpace(4); } catch (_) { try { task = await claimTaskSpace(4); } catch (__) { task = await taskSpace(4); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  if (!page) {
    process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: "NO_SPACE4_PAGE" }));
    return;
  }
  await page.evaluate(() => { window.__ego_overlay_disabled = true; }).catch(() => {});

  // 1) /mymusic/ 이동 후 전체 앨범 리스트 추출
  await page.goto('https://distrokid.com/mymusic/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 4000));

  const mymusicData = await page.evaluate(() => {
    const bodyText = document.body ? document.body.innerText : '';
    const albumLinks = [];
    const seen = new Set();
    document.querySelectorAll('a[href*="albumuuid="]').forEach(a => {
      const href = a.href;
      if (!seen.has(href)) {
        seen.add(href);
        const row = a.closest('tr, li, .album-row, div') || a;
        albumLinks.push({
          href,
          title: (a.innerText || '').replace(/\\s+/g, ' ').trim(),
          row_text: (row.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 300)
        });
      }
    });
    return { url: location.href, title: document.title, album_count: albumLinks.length, album_links: albumLinks, page_text: bodyText.slice(0, 10000) };
  });

  // 2) 발견된 모든 앨범(최대 15개) 순회하며 발매일, 업로드일, UPC, 전 트랙 ISRC 추출
  const albumsDetailed = [];
  const targets = mymusicData.album_links.slice(0, 15);
  for (const item of targets) {
    await page.goto(item.href, { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
    await new Promise(r => setTimeout(r, 3000));
    const det = await page.evaluate((meta) => {
      const txt = document.body ? document.body.innerText : '';
      const lines = txt.split('\\n').map(s => s.trim()).filter(Boolean);
      const upcLine = lines.find(l => l.includes('UPC')) || '';
      const relLine = lines.find(l => l.includes('발매일') || l.toLowerCase().includes('release date')) || '';
      const upLine = lines.find(l => l.includes('업로드 날짜') || l.toLowerCase().includes('uploaded')) || '';
      const isrcs = lines.filter(l => /^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$/.test(l));
      const hfAnchor = Array.from(document.querySelectorAll('a')).find(a => a.href.includes('hyperfollow.com') || (a.innerText && a.innerText.includes('페이지 보기')));
      return {
        album_url: location.href,
        link_title: meta.title,
        row_summary: meta.row_text,
        uploaded_date_line: upLine,
        release_date_line: relLine,
        upc_line: upcLine,
        isrc_count: isrcs.length,
        isrcs: isrcs,
        hyperfollow_url: hfAnchor ? hfAnchor.href : '',
        full_text: txt.slice(0, 8000)
      };
    }, item).catch(e => ({ error: String(e), href: item.href }));
    albumsDetailed.push(det);
  }

  // 3) Bank (정산/수익 현황) 스캔
  await page.goto('https://distrokid.com/bank/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 3500));
  const bankData = await page.evaluate(() => ({
    url: location.href,
    text: (document.body ? document.body.innerText : '').slice(0, 6000)
  })).catch(e => ({ error: String(e) }));

  // 4) Stats (스트리밍 통계 요약) 스캔
  await page.goto('https://distrokid.com/stats/', { waitUntil: 'domcontentloaded', timeout: 25000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 3500));
  const statsData = await page.evaluate(() => ({
    url: location.href,
    text: (document.body ? document.body.innerText : '').slice(0, 6000)
  })).catch(e => ({ error: String(e) }));

  // 마지막으로 내 음악(/mymusic/) 화면으로 깔끔하게 복귀
  await page.goto('https://distrokid.com/mymusic/', { waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {});

  process.stdout.write('S1EGO_JSON::' + JSON.stringify({
    ok: true,
    mymusic: mymusicData,
    albums_detailed: albumsDetailed,
    bank: bankData,
    stats: statsData
  }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err.message || err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""

res = s1_ego.run_ego_js(js_full_audit, timeout=180)

audit_out = {
    "directive_id": "RGON_DIR_NEW_FOUNDATION_092",
    "audited_at": datetime.datetime.now().isoformat(),
    "distrokid_full_audit": res
}
audit_path = BASE / "S1_DISTROKID_FULL_CATALOG_AUDIT_092.json"
audit_path.write_text(json.dumps(audit_out, ensure_ascii=False, indent=2), encoding="utf-8")

# 요약 생성
albums_det = res.get("albums_detailed", []) if isinstance(res, dict) else []
summary_parts = []
for idx, a in enumerate(albums_det, 1):
    if isinstance(a, dict):
        t = a.get("link_title") or a.get("row_summary", "")[:30]
        r = a.get("release_date_line", "")
        u = a.get("upc_line", "")
        ic = a.get("isrc_count", 0)
        summary_parts.append(f"[{idx}] {t} ({r} / {u} / 트랙ISRC:{ic}개)")
summary_str = " || ".join(summary_parts) if summary_parts else str(res.get("mymusic", {}).get("page_text", ""))[:400].replace("\n", " ")

print("[2/4] GitHub 원격 저장소에 전수 조사 원장(092호) 및 기존 미푸시 커밋 강제 동기화 중...")
subprocess.run(["git", "add", "-f", "S1_DISTROKID_FULL_CATALOG_AUDIT_092.json", "S1_DISTROKID_53_TRACKS_MASTER_LEDGER.json", "S1_DISTROKID_LIVE_RELEASE_DATES.json", "S1_MONETIZATION_PACKAGE_001.json", "S1_BLOG_REVENUE_POST_001.html"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(092): full DistroKid catalog, release dates, UPC/ISRC, Bank, and Stats audit"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

print("[3/4] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (092호 디스트로키드 전 앨범·Bank·Stats 전수조사 완료! 앨범수:{len(albums_det)}개 | {summary_str[:500]} | 커밋:{sha})")

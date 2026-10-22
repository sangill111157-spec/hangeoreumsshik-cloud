#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
upgrade_omni_link_v603.py

실행:
    python -X utf8 upgrade_omni_link_v603.py

대상:
    upgrade_omni_link_v602.py로 업그레이드된 RGON Omni-Link Hub.

변경:
    - 사용자 정의 신경망 역할 등록/삭제
    - 기본 및 사용자 정의 역할별 단독/체크 선택/전체 발사
    - 독대실 컨트롤러 동기화
    - 기존 흡수함/삭제/클립보드/자동 비우기 기능 보존
    - 인증된 localhost:8765 데이터 브리지 재기동 및 200 OK 검증

확장프로그램과 기존 웹 탭은 설치 후 새로고침해야 합니다.
브리지는 데이터를 저장할 뿐 코드를 실행하지 않습니다.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXT = ROOT / "rgon_aside_extension"
PRIVATE = ROOT / ".rgon_omni_private"
OMNI_VERSION = "6.0.3"

BACKGROUND_PATCH = r'''
/* BEGIN OMNI V603 CUSTOM NEURAL */
const OMNI603_BASE = [
  {key: "claude", label: "Claude", mapKey: "Claude", icon: "🧠"},
  {key: "gpt", label: "GPT", mapKey: "GPT", icon: "⚡"},
  {key: "grok", label: "Grok", mapKey: "Grok", icon: "🎯"}
];

function omni603Label(value) {
  const label = typeof value === "string"
    ? value.normalize("NFKC").replace(/\s+/g, " ").trim() : "";
  if (!label || label.length > 80 || /[\u0000-\u001f\u007f]/.test(label))
    throw new Error("신경망 이름은 제어문자 없는 1~80자로 입력하세요.");
  return label;
}
function omni603NormalizeRegistry(value) {
  const records = Array.isArray(value) ? value :
    value && typeof value === "object" ? Object.values(value) : [];
  const result = [];
  const keys = new Set();
  for (const item of records) {
    if (!item || typeof item !== "object") continue;
    if (!/^custom_[a-zA-Z0-9_-]{4,100}$/.test(item.key || "")) continue;
    if (keys.has(item.key)) continue;
    try {
      result.push({
        key: item.key, label: omni603Label(item.label),
        custom: true, icon: "🧩"
      });
      keys.add(item.key);
    } catch {}
  }
  return result.slice(0, 40);
}
async function omni603Catalog() {
  const saved = await chrome.storage.local.get("omni_custom_roles");
  return [...OMNI603_BASE, ...omni603NormalizeRegistry(saved.omni_custom_roles)];
}
function omni603MapKey(key) {
  return OMNI603_BASE.find(item => item.key === key)?.mapKey || key;
}
function omni603Canonical(key) {
  const legacy = OMNI603_BASE.find(item =>
    item.key === key || item.mapKey === key
  );
  return legacy?.key || key;
}
const omni603PreviousMapping = mapping;
mapping = async function() {
  const result = await omni603PreviousMapping();
  const saved = await chrome.storage.local.get([
    "omni_custom_roles", "omni_override"
  ]);
  const custom = omni603NormalizeRegistry(saved.omni_custom_roles);
  const overrides = saved.omni_override || {};
  const tabs = await chrome.tabs.query({});
  const valid = new Set(custom.map(item => item.key));
  for (const item of custom) result[item.key] = [];
  for (const tab of tabs) {
    if (!/^https?:\/\//.test(tab.url || "")) continue;
    const override = overrides[String(tab.id)];
    if (!override) continue;
    const key = typeof override === "string" ? override : override.key;
    const mapKey = omni603MapKey(key);
    if (!valid.has(key) && !["Claude", "GPT", "Grok", "르곤", "시트", "Adobe"].includes(mapKey))
      continue;
    for (const entries of Object.values(result)) {
      const index = entries.findIndex(item => item.id === tab.id);
      if (index >= 0) entries.splice(index, 1);
    }
    if (!result[mapKey]) result[mapKey] = [];
    result[mapKey].push({
      id: tab.id, title: cleanText(tab.title, 180),
      url: cleanText(tab.url, 500), active: !!tab.active
    });
  }
  return result;
};

const omni603Ready = ordered(async () => {
  const stored = await chrome.storage.local.get([
    "omni_custom_roles", "omni_override"
  ]);
  await chrome.storage.local.set({
    omni_custom_roles: omni603NormalizeRegistry(stored.omni_custom_roles),
    omni_override: stored.omni_override &&
      typeof stored.omni_override === "object" ? stored.omni_override : {}
  });
});

async function omni603SetRole(tabId, message) {
  return ordered(async () => {
    const saved = await chrome.storage.local.get([
      "omni_custom_roles", "omni_override", "roleOverrides"
    ]);
    let registry = omni603NormalizeRegistry(saved.omni_custom_roles);
    const overrides = {...(saved.omni_override || {})};
    const legacy = {...(saved.roleOverrides || {})};
    let key = message.role || "";
    let label = "";
    if (key === "__custom__") {
      label = omni603Label(message.label);
      const duplicate = registry.find(item =>
        item.label.toLocaleLowerCase() === label.toLocaleLowerCase()
      );
      if (duplicate) key = duplicate.key;
      else {
        if (registry.length >= 40)
          throw new Error("사용자 정의 신경망은 최대 40개입니다.");
        key = "custom_" + crypto.randomUUID().replace(/-/g, "");
        registry.push({key, label, custom: true, icon: "🧩"});
      }
    } else if (key.startsWith("custom_")) {
      const role = registry.find(item => item.key === key);
      if (!role) throw new Error("삭제되었거나 없는 신경망입니다.");
      label = role.label;
    } else if (key) {
      key = omni603Canonical(key);
      const base = OMNI603_BASE.find(item => item.key === key);
      if (base) label = base.label;
      else if (["르곤", "시트", "Adobe"].includes(key)) label = key;
      else throw new Error("지원하지 않는 역할입니다.");
    }
    if (!key) {
      delete overrides[String(tabId)];
      delete legacy[String(tabId)];
    } else {
      overrides[String(tabId)] = {key, label};
      // v6.0.2의 역할 데이터도 호환되도록 함께 갱신합니다.
      legacy[String(tabId)] = omni603MapKey(key);
    }
    await chrome.storage.local.set({
      omni_custom_roles: registry,
      omni_override: overrides,
      roleOverrides: legacy
    });
    return {ok: true, key, label, message: key ? label + " 역할 지정 완료" : "자동 감지로 복원"};
  });
}

async function omni603RemoveRole(key) {
  return ordered(async () => {
    const saved = await chrome.storage.local.get([
      "omni_custom_roles", "omni_override",
      "roleOverrides", "omni_target_selection"
    ]);
    const registry = omni603NormalizeRegistry(saved.omni_custom_roles);
    if (!registry.some(item => item.key === key))
      throw new Error("삭제할 사용자 정의 신경망이 없습니다.");
    const overrides = {...(saved.omni_override || {})};
    const legacy = {...(saved.roleOverrides || {})};
    const selection = {...(saved.omni_target_selection || {})};
    for (const [tabId, value] of Object.entries(overrides)) {
      if ((typeof value === "string" ? value : value?.key) === key)
        delete overrides[tabId];
    }
    for (const [tabId, value] of Object.entries(legacy)) {
      if (value === key) delete legacy[tabId];
    }
    delete selection[key];
    await chrome.storage.local.set({
      omni_custom_roles: registry.filter(item => item.key !== key),
      omni_override: overrides,
      roleOverrides: legacy,
      omni_target_selection: selection
    });
    return {
      ok: true,
      message: "역할 삭제 완료. 기존 흡수 기록과 실제 탭은 보존했습니다."
    };
  });
}

dispatch = async function(tabId, message) {
  const prompt = cleanText(message.prompt, 30000);
  if (!prompt.trim()) throw new Error("지시문을 입력하세요.");
  const catalog = await omni603Catalog();
  const valid = new Set(catalog.map(item => item.key));
  const requested = message.all === true
    ? catalog.map(item => item.key)
    : [...new Set((Array.isArray(message.roles) ? message.roles : [])
        .map(omni603Canonical))];
  if (!requested.length) throw new Error("발사할 대상을 선택하세요.");
  if (requested.some(key => !valid.has(key)))
    throw new Error("알 수 없거나 삭제된 발사 대상입니다.");

  const map = await mapping();
  const targets = [];
  const missing = [];
  const ambiguous = [];
  for (const key of requested) {
    const entry = catalog.find(item => item.key === key);
    const tabs = map[omni603MapKey(key)] || [];
    if (!tabs.length) { missing.push(entry.label); continue; }
    if (tabs.length !== 1) { ambiguous.push(entry.label); continue; }
    targets.push({...tabs[0], role: key, label: entry.label});
  }
  if (ambiguous.length)
    throw new Error("대상 탭이 여러 개입니다. 역할 지정을 정리하세요: " + ambiguous.join(", "));
  if (message.all !== true && missing.length)
    throw new Error("연결되지 않은 대상: " + missing.join(", "));
  if (!targets.length)
    throw new Error("연결된 발사 대상이 없습니다.");

  // 모든 대상 검증 이후 기존 v6.0.2 자동 초기화 규칙을 적용합니다.
  await omni602Clear("dispatch-v603");
  const results = await Promise.all(targets.map(async target => {
    try {
      const response = await chrome.tabs.sendMessage(target.id, {
        type: "OMNI_FILL", prompt, send: message.send === true
      });
      return {
        role: target.role, label: target.label, tabId: target.id,
        ...(response || {ok: false, error: "응답 없음"})
      };
    } catch (error) {
      return {
        role: target.role, label: target.label,
        tabId: target.id, ok: false, error: error.message
      };
    }
  }));
  await chrome.storage.local.set({
    lastDispatch: {
      time: new Date().toISOString(), results, skippedDisconnected: missing
    }
  });
  return {ok: true, results, skippedDisconnected: missing};
};

omni602AbsorbAll = async function() {
  const reset = await omni602Clear("collect-all-v603");
  const map = await mapping();
  const catalog = await omni603Catalog();
  const tabs = catalog.flatMap(role => map[omni603MapKey(role.key)] || []);
  const unique = [...new Map(tabs.map(tab => [tab.id, tab])).values()];
  const results = await Promise.all(unique.map(async tab => {
    try { return await absorb(tab.id); }
    catch (error) {
      return {ok: false, tabId: tab.id, error: error.message};
    }
  }));
  return {ok: true, cleared: reset.cleared, results};
};

const omni603PreviousRoute = route;
route = async function(message, sender) {
  if (!sender.tab?.id || sender.id !== chrome.runtime.id)
    throw new Error("허용되지 않은 호출");
  await omni603Ready;
  const tabId = sender.tab.id;
  if (message.type === "OMNI_CUSTOM_ROLE_SET")
    return omni603SetRole(tabId, message);
  if (message.type === "OMNI_CUSTOM_ROLE_DELETE")
    return omni603RemoveRole(message.key);
  if (message.type === "OMNI_ROLE")
    return omni603SetRole(tabId, message);
  if (message.type === "OMNI_AUTO_CAPTURE") {
    const stored = await chrome.storage.local.get("autoTabs");
    const map = await mapping();
    const catalog = await omni603Catalog();
    const permitted = catalog.some(role =>
      (map[omni603MapKey(role.key)] || []).some(tab => tab.id === tabId)
    );
    if (!permitted || !(stored.autoTabs || {})[String(tabId)])
      throw new Error("이 신경망 탭에서 자동 흡수를 먼저 승인하세요.");
    return storeRecord(tabId, message.capture, {auto: true});
  }
  const result = await omni603PreviousRoute(message, sender);
  if (message.type === "OMNI_STATE" && result?.ok) {
    const saved = await chrome.storage.local.get([
      "omni_override", "omni_target_selection"
    ]);
    result.roleCatalog = await omni603Catalog();
    result.targetSelection = saved.omni_target_selection || {};
    const override = (saved.omni_override || {})[String(tabId)];
    result.currentRole = typeof override === "string" ? override : override?.key || "";
    result.version = "6.0.3";
  }
  return result;
};
chrome.tabs.onRemoved.addListener(id => {
  ordered(async () => {
    const saved = await chrome.storage.local.get("omni_override");
    const overrides = {...(saved.omni_override || {})};
    delete overrides[String(id)];
    await chrome.storage.local.set({omni_override: overrides});
  }).catch(() => {});
});
/* END OMNI V603 CUSTOM NEURAL */
'''

CONTENT_PATCH = r'''
/* BEGIN OMNI V603 CUSTOM NEURAL UI */
const omni603Defaults = [
  {key: "claude", label: "Claude", mapKey: "Claude", icon: "🧠"},
  {key: "gpt", label: "GPT", mapKey: "GPT", icon: "⚡"},
  {key: "grok", label: "Grok", mapKey: "Grok", icon: "🎯"}
];

function omni603CatalogUI() {
  return currentState?.roleCatalog || omni603Defaults;
}
function omni603Selection(key) {
  const saved = currentState?.targetSelection || {};
  return Object.prototype.hasOwnProperty.call(saved, key)
    ? saved[key] === true : ["claude", "gpt"].includes(key);
}
function omni603Trusted(button, handler) {
  button.addEventListener("click", event => {
    if (event.isTrusted) handler(event);
  });
}
function omni603Button(text, handler) {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = text;
  omni603Trusted(button, handler);
  return button;
}
async function omni603PersistSelection(key, enabled) {
  const stored = await chrome.storage.local.get("omni_target_selection");
  const values = {...(stored.omni_target_selection || {}), [key]: enabled};
  await chrome.storage.local.set({omni_target_selection: values});
  if (currentState) currentState.targetSelection = values;
}
function omni603RenderTargets(container, page = false) {
  container.replaceChildren();
  const controls = document.createElement("div");
  controls.className = "row";
  const all = omni603Button("☑️ 전체 선택", () => omni603ToggleAll(container, true));
  const none = omni603Button("☐ 전체 해제", () => omni603ToggleAll(container, false));
  all.id = page ? "pageSelAllTargets" : "selAllTargets";
  none.id = page ? "pageUnselAllTargets" : "unselAllTargets";
  controls.append(all, none);
  container.append(controls);

  for (const role of omni603CatalogUI()) {
    const row = document.createElement("div");
    row.className = "row";
    row.style.cssText = "display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:7px 0";
    const label = document.createElement("label");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "tgt-chk";
    checkbox.value = role.key;
    checkbox.checked = omni603Selection(role.key);
    checkbox.style.width = "auto";
    checkbox.addEventListener("change", event => {
      if (event.isTrusted)
        omni603PersistSelection(role.key, checkbox.checked).catch(error => status(error.message));
    });
    label.append(checkbox, document.createTextNode(
      " " + (role.icon || "🧩") + " " + role.label
    ));
    const solo = omni603Button(
      (role.icon || "🧩") + " " + role.label + (page ? " 단독" : " 단독 발사"),
      () => omni603Fire([role.key], false, page)
    );
    solo.dataset.solo = role.key;
    row.append(label, solo);
    container.append(row);
  }

  const footer = document.createElement("div");
  footer.className = "row";
  const checked = omni603Button(
    page ? "🚀 체크 선택 발사" : "🚀 체크한 대상만 발사",
    () => omni603Fire(
      [...container.querySelectorAll(".tgt-chk:checked")].map(input => input.value),
      false, page
    )
  );
  const fireAll = omni603Button(
    page ? "🌐 전체 발사" : "🌐 전체 선택 발사",
    () => omni603Fire([], true, page)
  );
  checked.id = page ? "pageFireChecked" : "fireChecked";
  fireAll.id = page ? "pageFireAll" : "fireAll";
  footer.append(checked, fireAll);
  container.append(footer);
  const note = document.createElement("p");
  note.className = "note";
  note.textContent =
    "전체 발사는 연결된 모든 AI·직접 등록 역할에 전송합니다. 미연결 역할은 건너뛰며, 중복 탭은 안전하게 중단합니다.";
  container.append(note);
}
async function omni603ToggleAll(container, enabled) {
  const values = {...(currentState?.targetSelection || {})};
  for (const checkbox of container.querySelectorAll(".tgt-chk")) {
    checkbox.checked = enabled;
    values[checkbox.value] = enabled;
  }
  if (currentState) currentState.targetSelection = values;
  await chrome.storage.local.set({omni_target_selection: values});
}
let omni603Firing = false;
async function omni603Fire(roles, all, page = false) {
  if (omni603Firing) return;
  const root = page ? document.getElementById("rgon-omni-controller-v603") : null;
  const input = page ? root?.querySelector("#prompt") : $("prompt");
  const submit = page
    ? root?.querySelector("#omni-submit")?.checked === true
    : $("send").checked;
  const autoClear = page
    ? root?.querySelector("#autoclear")?.checked !== false
    : $("autoclear")?.checked !== false;
  const notice = page ? root?.querySelector("#rgon-omni-controller-status") : null;
  if (!input?.value.trim()) {
    if (notice) notice.textContent = "지시문을 입력하세요.";
    else status("지시문을 입력하세요.");
    input?.focus(); return;
  }
  if (!all && !roles.length) {
    if (notice) notice.textContent = "발사 대상을 선택하세요.";
    else status("발사 대상을 선택하세요.");
    return;
  }
  if (submit && !confirm("선택한 신경망의 AI 서비스로 지시문을 실제 전송할까요?")) return;
  omni603Firing = true;
  const sentText = input.value;
  try {
    const result = await send({
      type: "OMNI_DISPATCH", roles, all,
      prompt: sentText, send: submit
    });
    const good = omniDispatchSucceeded(result, submit);
    const skipped = result.skippedDisconnected || [];
    const message = good
      ? (submit ? "발사 성공" : "주입 성공") +
        (skipped.length ? " / 미연결 제외: " + skipped.join(", ") : "")
      : "일부 대상 실패 또는 실제 전송 미확인. 입력을 보존했습니다.";
    if (notice) notice.textContent = message;
    else status(message + "\n" + JSON.stringify(result.results, null, 2));
    if (good && autoClear && input.value === sentText) {
      input.value = ""; input.focus();
    }
    await refresh();
  } catch (error) {
    if (notice) notice.textContent = error.message;
    else status(error.message);
  } finally { omni603Firing = false; }
}

function omni603InstallNetworkEditor() {
  if ($("omni603-role-editor")) return;
  const network = $("network");
  if (!network) return;
  let select = $("roleSel") || $("role");
  if (!select) throw new Error("기존 역할 선택창이 없습니다.");
  select.id = "roleSel";

  const originalButton = $("setRole");
  const button = originalButton
    ? originalButton.cloneNode(false)
    : document.createElement("button");
  button.id = "setRole";
  button.type = "button";
  button.textContent = "지정";
  originalButton?.remove();

  const editor = document.createElement("div");
  editor.id = "omni603-role-editor";
  const heading = document.createElement("h3");
  heading.textContent = "✏️ 현재 탭 신경망 역할 직접 지정";
  const custom = document.createElement("input");
  custom.id = "customRoleName";
  custom.placeholder = "새 신경망 이름 입력 (예: Claude Sonnet 5.5, Suno, Perplexity)";
  custom.maxLength = 80;
  custom.hidden = true;
  select.addEventListener("change", () => {
    custom.hidden = select.value !== "__custom__";
    if (!custom.hidden) custom.focus();
  });
  omni603Trusted(button, async () => {
    await action(() => send({
      type: "OMNI_CUSTOM_ROLE_SET",
      role: select.value,
      label: custom.value
    }));
  });
  editor.append(heading, select, custom, button);
  network.append(editor);
}

function omni603RenderNetwork() {
  omni603InstallNetworkEditor();
  const select = $("roleSel");
  const previous = select.value || currentState?.currentRole || "";
  select.replaceChildren();
  const options = [
    {key: "", label: "제목/주소 자동 감지"},
    {key: "르곤", label: "르곤"},
    ...omni603Defaults,
    {key: "시트", label: "시트"},
    {key: "Adobe", label: "Adobe"},
    ...omni603CatalogUI().filter(item => item.custom),
    {key: "__custom__", label: "✏️ 직접 쓰기 (이름 직접 입력)"}
  ];
  for (const item of options) {
    const option = document.createElement("option");
    option.value = item.key;
    option.textContent = item.label;
    select.append(option);
  }
  if ([...select.options].some(option => option.value === previous))
    select.value = previous;
  $("customRoleName").hidden = select.value !== "__custom__";

  const list = $("connections");
  list.replaceChildren();
  const catalog = omni603CatalogUI();
  const shown = [
    {key: "르곤", label: "르곤"},
    ...catalog,
    {key: "시트", label: "시트"},
    {key: "Adobe", label: "Adobe"}
  ];
  for (const item of shown) {
    const mapKey = item.mapKey || item.key;
    const tabs = currentState?.map?.[mapKey] || [];
    const row = document.createElement("div");
    row.className = "light";
    const title = document.createElement("span");
    title.textContent =
      (tabs.length ? "🟢 " : "⚪ ") +
      (item.custom ? "🧩 " : "") + item.label +
      (tabs.length ? " · 연결됨 " : " · 미연결 ");
    row.append(title);
    for (const tab of tabs) {
      const move = omni603Button("이동", () =>
        action(() => send({type: "OMNI_FOCUS", tabId: tab.id}))
      );
      move.title = tab.title || item.label;
      row.append(move);
    }
    if (item.custom) {
      row.append(omni603Button("✕ 역할 삭제", () => {
        if (confirm(item.label + " 역할을 삭제할까요? 실제 탭과 흡수 기록은 보존됩니다."))
          action(() => send({type: "OMNI_CUSTOM_ROLE_DELETE", key: item.key}));
      }));
    }
    list.append(row);
  }
}

function omni603InstallDispatch() {
  const section = $("dispatch");
  if (!section) return;
  // v6.0.2의 입력창·템플릿·지우기·붙여넣기·자동 비우기는 보존합니다.
  for (const id of ["duo", "grok"]) $(id)?.remove();
  let targets = $("omni603-targets");
  if (!targets) {
    targets = document.createElement("div");
    targets.id = "omni603-targets";
    section.append(targets);
  }
  const signature = JSON.stringify([
    omni603CatalogUI(), currentState?.targetSelection || {}
  ]);
  if (targets.dataset.signature !== signature) {
    omni603RenderTargets(targets, false);
    targets.dataset.signature = signature;
  }

  const page = document.getElementById("rgon-omni-controller-v603");
  const pageTargets = page?.querySelector("#omni603-page-targets");
  if (pageTargets && pageTargets.dataset.signature !== signature) {
    omni603RenderTargets(pageTargets, true);
    pageTargets.dataset.signature = signature;
  }
}

const omni603OriginalRefresh = refresh;
refresh = async function() {
  await omni603OriginalRefresh();
  if (!currentState) return;
  omni603RenderNetwork();
  omni603InstallDispatch();
};

const omni603OriginalArena = renderArena;
renderArena = function(records) {
  const catalog = omni603CatalogUI();
  omni603OriginalArena((records || []).map(record => {
    const role = catalog.find(item => item.key === record.role);
    return role?.custom ? {...record, role: role.label} : record;
  }));
};

chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && (
    changes.omni_custom_roles || changes.omni_override ||
    changes.omni_target_selection
  )) refresh().catch(() => {});
});
omni603InstallNetworkEditor();
omni603InstallDispatch();
setTimeout(() => refresh().catch(() => {}), 300);
/* END OMNI V603 CUSTOM NEURAL UI */
'''

HTML_BLOCK = r'''
<!-- OMNI-LINK:BEGIN -->
<div id="rgon-omni-controller-v603" style="position:relative;z-index:1000;padding:12px 16px;background:#132337;color:#eef7ff;border-bottom:1px solid #537389;font:13px/1.5 system-ui,sans-serif">
  <button type="button" data-rgon-omni-open style="padding:10px;border-radius:9px;cursor:pointer">✨ AI 만능 소통창 (르곤⇄클로드⇄GPT⇄그록 직결 허브) 열기</button>
  <span id="rgon-omni-controller-status">확장프로그램 연결 대기</span>
  <details style="margin-top:8px">
    <summary>⚡ 작업 분배 — 단독 / 체크 선택 / 전체</summary>
    <div style="display:flex;gap:7px;flex-wrap:wrap;margin-top:8px">
      <select id="omni-template">
        <option value="">지시문 템플릿 선택</option>
        <option value="요구사항을 분석하고 실행 가능한 전체 코드를 작성하라.">코드 작성</option>
        <option value="제공된 코드의 오류와 보안 문제를 검토하고 수정안을 제시하라.">코드 검수</option>
        <option value="종이컵 광고의 반전형 Hook, Body, CTA와 10초 나레이션을 작성하라.">반전형 광고</option>
      </select>
      <button type="button" data-omni-clear>🗑️ 전체 지우기</button>
      <button type="button" data-omni-paste>📋 새로 붙여넣기</button>
    </div>
    <textarea id="prompt" style="display:block;width:100%;min-height:110px;margin-top:8px;padding:10px;box-sizing:border-box" placeholder="분배할 지시문"></textarea>
    <label style="display:block;margin:8px 0"><input id="autoclear" type="checkbox" checked> 발사 후 입력창 자동 비우기</label>
    <label style="display:block;margin:8px 0"><input id="omni-submit" type="checkbox"> 주입 후 실제 전송도 승인</label>
    <div id="omni603-page-targets">
      <div><button type="button" disabled>☑️ 전체 선택</button> <button type="button" disabled>☐ 전체 해제</button></div>
      <div><label><input type="checkbox" class="tgt-chk" value="claude" checked> 🧠 Claude</label> <button type="button" data-solo="claude" disabled>🧠 Claude 단독</button></div>
      <div><label><input type="checkbox" class="tgt-chk" value="gpt" checked> ⚡ GPT</label> <button type="button" data-solo="gpt" disabled>⚡ GPT 단독</button></div>
      <div><label><input type="checkbox" class="tgt-chk" value="grok"> 🎯 Grok</label> <button type="button" data-solo="grok" disabled>🎯 Grok 단독</button></div>
      <div><button type="button" disabled>🚀 체크 선택 발사</button> <button type="button" disabled>🌐 전체 발사</button></div>
      <p>확장프로그램 연결 후 커스텀 신경망을 포함한 실제 발사 컨트롤러가 활성화됩니다.</p>
    </div>
  </details>
</div>
<script>
(() => {
  const root = document.getElementById("rgon-omni-controller-v603");
  if (!root || root.dataset.bound) return;
  root.dataset.bound = "1";
  const prompt = root.querySelector("#prompt");
  const status = root.querySelector("#rgon-omni-controller-status");
  root.querySelector("[data-omni-clear]").addEventListener("click", () => {
    prompt.value = ""; prompt.focus();
  });
  root.querySelector("[data-omni-paste]").addEventListener("click", async () => {
    prompt.value = ""; prompt.focus();
    try {
      prompt.value = await navigator.clipboard.readText();
      prompt.focus();
    } catch {
      status.textContent = "클립보드 읽기 권한이 필요합니다. Ctrl+V로 붙여넣으세요.";
    }
  });
  root.querySelector("#omni-template").addEventListener("change", event => {
    if (event.target.value) prompt.value = event.target.value;
    prompt.focus();
  });
  root.querySelector("[data-rgon-omni-open]").addEventListener("click", () => {
    window.postMessage({
      source: "RGON_OMNI_CONTROLLER", version: 6, type: "OPEN_HUB"
    }, location.origin);
  });
  window.addEventListener("message", event => {
    if (event.source !== window || event.origin !== location.origin) return;
    if (event.data?.source === "RGON_OMNI_EXTENSION")
      status.textContent = "🟢 Omni-Link 확장프로그램 연결됨";
  });
})();
</script>
<!-- OMNI-LINK:END -->
'''


def say(text):
    print(text, flush=True)


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=str(path.parent), prefix=".omni603_", delete=False
        ) as handle:
            handle.write(data)
            temporary = Path(handle.name)
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def replace_once(source, old, new, label):
    if source.count(old) != 1:
        raise RuntimeError(f"{label}: 지원되는 코드 위치를 유일하게 찾지 못했습니다.")
    return source.replace(old, new, 1)


def patch_background(source):
    source = re.sub(
        r'const OMNI_VERSION = "[^"]+";',
        'const OMNI_VERSION = "6.0.3";',
        source,
    )
    if "/* BEGIN OMNI V603 CUSTOM NEURAL */" in source:
        return source

    required = (
        "/* BEGIN OMNI V602 MEMORY */",
        "async function omni602Clear(",
        "async function storeRecord(",
        "async function route(",
        "const OMNI_TOKEN = ",
    )
    if not all(marker in source for marker in required):
        raise RuntimeError("background.js가 지원되는 v6.0.2 구조가 아닙니다.")

    source = replace_once(
        source,
        "const role = ROLES.find(key =>",
        "const role = Object.keys(map).find(key =>",
        "커스텀 역할 흡수 기록",
    )
    return source.rstrip() + "\n" + BACKGROUND_PATCH + "\n"


def patch_content(source):
    source = re.sub(
        r'const OMNI_VERSION = "[^"]+";',
        'const OMNI_VERSION = "6.0.3";',
        source,
    )
    source = source.replace("RGON Omni-Link v6.0.2", "RGON Omni-Link v6.0.3")
    if "/* BEGIN OMNI V603 CUSTOM NEURAL UI */" in source:
        return source

    required = (
        "/* BEGIN OMNI V602 CONTENT HELPERS */",
        'id="autoclear"',
        "function omniDispatchSucceeded(",
        "function detectModelRole()",
        "function renderArena(records)",
    )
    if not all(marker in source for marker in required):
        raise RuntimeError("content_aside_bar.js가 지원되는 v6.0.2 구조가 아닙니다.")

    end = source.rfind("})();")
    if end < 0:
        raise RuntimeError("콘텐츠 스크립트의 외부 IIFE 경계를 찾지 못했습니다.")
    return source[:end] + CONTENT_PATCH + "\n" + source[end:]


def patch_html(raw):
    text = raw.decode("utf-8-sig")
    counts = (
        len(re.findall(r"STUDIO\s*v5", text, re.I)),
        len(re.findall("firefly", text, re.I)),
    )
    if not all(counts):
        raise RuntimeError("기존 STUDIO v5 및 firefly 블록을 확인하지 못했습니다.")
    patterns = (
        r"<!-- OMNI-LINK:BEGIN -->.*?<!-- OMNI-LINK:END -->",
        r"<!-- BEGIN RGON OMNI CONTROLLER V6 -->.*?<!-- END RGON OMNI CONTROLLER V6 -->",
    )
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.S)
    body = re.search(r"<body\b[^>]*>", text, re.I)
    if not body:
        raise RuntimeError("HTML body 태그가 없습니다.")
    updated = text[:body.end()] + "\n" + HTML_BLOCK + text[body.end():]
    if (
        len(re.findall(r"STUDIO\s*v5", updated, re.I)) < counts[0]
        or len(re.findall("firefly", updated, re.I)) < counts[1]
    ):
        raise RuntimeError("기존 STUDIO/Adobe 블록 보존 검증 실패")
    if updated.count("<!-- OMNI-LINK:BEGIN -->") != 1:
        raise RuntimeError("독대실 컨트롤러 중복 확인 실패")
    return updated.encode("utf-8")


def validate_js(sources):
    node = shutil.which("node")
    if not node:
        raise RuntimeError("JavaScript 검증을 위한 Node.js가 필요합니다.")
    with tempfile.TemporaryDirectory(prefix="omni603_check_") as directory:
        for name, source in sources.items():
            path = Path(directory) / name
            path.write_text(source, encoding="utf-8")
            result = subprocess.run(
                [node, "--check", str(path)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                shell=False,
            )
            if result.returncode:
                raise RuntimeError(f"JS 문법 검증 실패: {name}")
            say(f"[문법 검증] {name}: PASS")


def load_bridge_helpers():
    path = ROOT / "upgrade_omni_link_v601.py"
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("기존 upgrade_omni_link_v601.py가 필요합니다.")
    spec = importlib.util.spec_from_file_location("_rgon603_bridge_helpers", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("브리지 관리 함수 로드 실패")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ("health", "stop_owned_bridge", "launch_bridge"):
        if not callable(getattr(module, name, None)):
            raise RuntimeError(f"기존 브리지 관리 함수 없음: {name}")
    if Path(module.ROOT).resolve() != ROOT:
        raise RuntimeError("브리지 프로젝트 경로 불일치")
    token = (PRIVATE / "bridge_token.txt").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{32,160}", token):
        raise RuntimeError("브리지 토큰 형식 오류")
    module.TOKEN = token
    return module, token


def patch_installer_html(source):
    tree = ast.parse(source)
    assignments = [
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name)
            and target.id in {"HTML_BLOCK", "CONTROLLER_HTML"}
            for target in node.targets
        )
    ]
    lines = source.splitlines(keepends=True)
    for node in sorted(assignments, key=lambda item: item.lineno, reverse=True):
        name = next(
            target.id for target in node.targets
            if isinstance(target, ast.Name)
            and target.id in {"HTML_BLOCK", "CONTROLLER_HTML"}
        )
        lines[node.lineno - 1:node.end_lineno] = [
            name + " = " + repr(HTML_BLOCK) + "\n"
        ]
    updated = "".join(lines)
    ast.parse(updated)
    return updated


def main():
    originals = {}
    applied = []
    launched = None
    stopped_old = False
    helpers = None
    backup = PRIVATE / "upgrade_backups" / datetime.now().strftime(
        "v603_%Y%m%d_%H%M%S_%f"
    )

    try:
        paths = {
            "background": EXT / "background.js",
            "content": EXT / "content_aside_bar.js",
            "manifest": EXT / "manifest.json",
            "bridge": ROOT / "omni_bridge.py",
        }
        for path in paths.values():
            if not path.is_file() or path.is_symlink():
                raise RuntimeError(f"필수 일반 파일 확인 필요: {path.relative_to(ROOT)}")

        helpers, token = load_bridge_helpers()
        background = paths["background"].read_text(encoding="utf-8-sig")
        match = re.search(
            r'const\s+OMNI_TOKEN\s*=\s*("[A-Za-z0-9_-]+");',
            background,
        )
        if not match or json.loads(match.group(1)) != token:
            raise RuntimeError("background.js와 로컬 브리지 토큰이 다릅니다.")

        background = patch_background(background)
        content = patch_content(paths["content"].read_text(encoding="utf-8-sig"))
        bridge = paths["bridge"].read_text(encoding="utf-8-sig")
        if "# BEGIN OMNI V602 MEMORY API" not in bridge:
            raise RuntimeError("v6.0.2 흡수함 동기화 API가 없습니다.")
        bridge = bridge.replace('"version": "6.0.2"', '"version": "6.0.3"')
        ast.parse(bridge, filename="omni_bridge.py")

        manifest = json.loads(paths["manifest"].read_text(encoding="utf-8-sig"))
        manifest["version"] = OMNI_VERSION

        html_script = re.search(
            r"<script>(.*?)</script>", HTML_BLOCK, re.S
        ).group(1)
        validate_js({
            "background.js": background,
            "content_aside_bar.js": content,
            "controller.js": html_script,
        })

        invariants = {
            "입력 전체 지우기": 'id="omni-clear"' in content,
            "클립보드 붙여넣기": "navigator.clipboard.readText()" in content,
            "발사 후 자동 비우기": 'id="autoclear"' in content,
            "흡수함 자동 삭제": 'id = "autoCleanAbs"' in content,
            "흡수함 전체 삭제": 'id = "absClearAll"' in content,
            "개별 카드 삭제": 'dataset.act = "del"' in content,
            "Copy 접두사 정리": "replace(/^Copy\\s*/i" in content,
            "Gemini 오인 방지": "function detectModelRole()" in content,
            "커스텀 신경망": "omni_custom_roles" in background,
            "커스텀 역할 매핑": "omni_override" in background,
            "커스텀 자동 수거": "collect-all-v603" in background,
            "브리지 포트 유지": "http://127.0.0.1:8765" in background,
        }
        failed = [name for name, passed in invariants.items() if not passed]
        if failed:
            raise RuntimeError("기능 보존 확인 실패: " + ", ".join(failed))

        plan = {
            paths["background"]: background.encode("utf-8"),
            paths["content"]: content.encode("utf-8"),
            paths["manifest"]: (
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
            ).encode("utf-8"),
            paths["bridge"]: bridge.encode("utf-8"),
        }
        for relative in (
            "rgon_alpha_chat.html",
            "dashboard/rgon_alpha_chat.html",
            "docs/rgon_alpha_chat.html",
        ):
            path = ROOT / relative
            if not path.is_file() or path.is_symlink():
                raise RuntimeError(f"독대실 HTML 확인 필요: {relative}")
            plan[path] = patch_html(path.read_bytes())

        installer = ROOT / "build_omni_link_communicator.py"
        if installer.is_file():
            plan[installer] = patch_installer_html(
                installer.read_text(encoding="utf-8-sig")
            ).encode("utf-8")

        ignore_path = ROOT / ".gitignore"
        ignore = ignore_path.read_text(encoding="utf-8-sig") if ignore_path.exists() else ""
        for entry in (
            ".rgon_omni_private/",
            "omni_shared_clipboard.json",
            "*.omni.tmp",
            "/rgon_aside_extension/background.js",
        ):
            if entry not in ignore.splitlines():
                ignore = ignore.rstrip() + "\n" + entry + "\n"
        plan[ignore_path] = ignore.encode("utf-8")

        backup.mkdir(parents=True, exist_ok=True)
        for path in plan:
            if path.is_symlink():
                raise RuntimeError("심볼릭 링크 파일은 수정하지 않습니다.")
            parent = path.parent
            while parent != ROOT:
                if parent.is_symlink():
                    raise RuntimeError("심볼릭 링크 폴더 아래에 설치하지 않습니다.")
                parent = parent.parent
            originals[path] = path.read_bytes() if path.exists() else None
            if originals[path] is not None:
                atomic_write(backup / path.relative_to(ROOT), originals[path])

        expected_hash = hashlib.sha256(plan[paths["bridge"]]).hexdigest()
        code, old_health = helpers.health(token)
        reusable = (
            code == 200
            and old_health.get("project") == helpers.PROJECT_ID
            and old_health.get("version") == OMNI_VERSION
            and old_health.get("script_sha256") == expected_hash
            and old_health.get("token_sha256")
                == hashlib.sha256(token.encode()).hexdigest()
        )
        if not reusable:
            helpers.stop_owned_bridge()
            stopped_old = code != 0

        for path, data in plan.items():
            if originals[path] == data:
                continue
            atomic_write(path, data)
            applied.append(path)
            say(f"[적용] {path.relative_to(ROOT)}")

        if reusable:
            say("[브리지] 검증된 v6.0.3 프로세스 재사용")
        else:
            launched = helpers.launch_bridge()

        verified = None
        for _ in range(45):
            code, data = helpers.health(token, timeout=0.7)
            if (
                code == 200
                and data.get("project") == helpers.PROJECT_ID
                and data.get("version") == OMNI_VERSION
                and data.get("script_sha256") == expected_hash
                and data.get("token_sha256")
                    == hashlib.sha256(token.encode()).hexdigest()
            ):
                verified = data
                break
            if launched is not None and launched.poll() is not None:
                raise RuntimeError("브리지 프로세스가 종료되었습니다. 비공개 로그를 확인하세요.")
            time.sleep(0.2)
        if verified is None:
            raise RuntimeError("8765 브리지 인증된 HTTP 200 검증 실패")

        request = urllib.request.Request(
            "http://127.0.0.1:8765/api/memory/sync",
            data=json.dumps({"approved": False, "entries": []}).encode(),
            headers={
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(request, timeout=3):
                pass
            raise RuntimeError("승인 없는 흡수함 수정 요청이 거부되지 않았습니다.")
        except urllib.error.HTTPError as error:
            if error.code != 400:
                raise RuntimeError("흡수함 동기화 API 검증 실패") from error

        receipt = {
            "version": OMNI_VERSION,
            "status": "installed_and_authenticated_bridge_verified",
            "bridge_http_status": 200,
            "bridge_pid": verified["pid"],
            "token_match": True,
            "custom_roles_storage": "omni_custom_roles",
            "overrides_storage": "omni_override",
            "custom_role_limit": 40,
            "dispatch_modes": ["solo", "checked", "all_connected"],
            "disconnected_all_targets": "skip_and_report",
            "duplicate_role_tabs": "reject_without_dispatch",
            "existing_absorber_features_preserved": True,
            "automatic_code_execution": False,
            "chrome_extension_reload_required": True,
            "backup": str(backup.relative_to(ROOT)),
            "invariants": invariants,
        }
        atomic_write(
            PRIVATE / "v603_upgrade_receipt.json",
            (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )

        say("🟢 로컬 브리지 연결됨 (200 OK)")
        say("[신경망] 하단 ✏️ 직접 쓰기 / 커스텀 램프 / 이동 / 역할 삭제 추가")
        say("[분배] Claude·GPT·Grok·커스텀 단독 / 체크 선택 / 전체 연결 대상 발사")
        say("[흡수] 커스텀 신경망도 전체 수거 및 승인된 자동 흡수 대상에 포함")
        say("[보존] 지우기·붙여넣기·자동 비우기·흡수함 삭제·Copy 정리 유지")
        say(f"[백업] {backup}")
        say("[필수] chrome://extensions에서 확장프로그램을 새로고침하세요.")
        say("[필수] AI 탭과 독대실 3개 HTML 페이지도 새로고침하세요.")
        say("[안내] 커스텀 이름은 역할 라벨이며 실제 모델·서비스 기능을 검증하지 않습니다.")
        say("[안내] 사이트별 입력창 구조가 다르면 안전하게 주입/전송을 중단할 수 있습니다.")
        say("[보안] 토큰이 포함된 background.js와 비공개 폴더를 공개 커밋하지 마세요.")
        say("OMNI-LINK v6.0.3 CUSTOM NEURAL & SOLO/CHECK DISPATCH READY!")
        return 0

    except Exception as error:
        if launched is not None and launched.poll() is None:
            launched.terminate()
            try:
                launched.wait(timeout=5)
            except subprocess.TimeoutExpired:
                launched.kill()
                launched.wait(timeout=5)

        failed_restore = []
        for path in reversed(applied):
            try:
                original = originals[path]
                if original is None:
                    path.unlink(missing_ok=True)
                else:
                    atomic_write(path, original)
            except Exception:
                failed_restore.append(str(path.relative_to(ROOT)))

        say(f"[실패] {type(error).__name__}: {error}")
        if failed_restore:
            say("[수동 복구 필요] " + ", ".join(failed_restore))
        elif applied:
            say("[복구] 이번에 변경한 파일을 이전 상태로 되돌렸습니다.")

        if stopped_old and helpers is not None and not failed_restore:
            try:
                restored = helpers.launch_bridge()
                time.sleep(0.5)
                if restored.poll() is None:
                    say("[복구] 이전 브리지 코드로 재기동했습니다.")
                else:
                    say("[안내] 이전 브리지를 수동 재기동하세요.")
            except Exception:
                say("[안내] 이전 브리지를 수동 재기동하세요.")
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
Copy
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import webbrowser

from datetime import datetime
from pathlib import Path


VERSION = "rgon-ad-studio-v4"

TARGETS = (
    "dashboard/rgon_alpha_chat.html",
    "rgon_alpha_chat.html",
    "docs/rgon_alpha_chat.html",
)

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".rgon_ui_backups",
    ".rgon_ad_backups",
}

SCRIPT_RE = re.compile(
    r"<script\b(?P<attrs>[^>]*)>(?P<body>.*?)</script\s*>",
    re.I | re.S,
)


JS_TEMPLATE = r'''
(() => {
  "use strict";

  const VERSION = "__VERSION__";
  const BUILD = "__BUILD__";
  const LOCAL_CONFIG = __LOCAL_CONFIG__;

  if (window.__RGON_AD_STUDIO_VERSION__ === VERSION) return;
  window.__RGON_AD_STUDIO_VERSION__ = VERSION;

  const OPTIONS = {
    inputSelector: "#dokdae-input",
    sendSelector: "",
    ...window.RGON_AD_OPTIONS
  };

  const MODAL_ID = "rgon-ad-v4-overlay";
  const FLOAT_ID = "rgon-ad-v4-floating";
  const STYLE_ID = "rgon-ad-v4-style";

  const STATE = {
    lastInput: null,
    modal: null,
    modalCleanup: null,
    activeRun: null,
    previousFocus: null,
    loweredPanels: [],
    refreshing: false,
    musicWarning: false
  };

  const INPUT_SELECTORS = [
    "#dokdae-input",
    "#chat-input",
    "#chatInput",
    "#message-input",
    "#messageInput",
    "#user-input",
    "#userInput",
    "#prompt",
    'textarea[name="message"]',
    'textarea[name="prompt"]',
    'input[name="message"]',
    'textarea[placeholder*="메시지"]',
    'textarea[placeholder*="질문"]',
    'input[placeholder*="메시지"]',
    'input[placeholder*="질문"]',
    'textarea[placeholder*="입력"]',
    'input[placeholder*="하교"]',
    'input[placeholder*="명령"]',
    'textarea[placeholder*="하교"]',
    '[contenteditable="true"][role="textbox"]'
  ];

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function important(node, properties) {
    for (const [name, value] of Object.entries(properties)) {
      node.style.setProperty(name, String(value), "important");
    }
  }

  function visible(node) {
    return Boolean(
      node &&
      node.isConnected &&
      node.getClientRects().length &&
      getComputedStyle(node).visibility !== "hidden"
    );
  }

  function safeQuery(selector, root = document) {
    if (!selector) return null;
    try {
      return root.querySelector(selector);
    } catch (error) {
      console.warn("[RGON v4] 잘못된 선택자:", selector, error);
      return null;
    }
  }

  function isStudioElement(node) {
    return node instanceof Element && Boolean(
      node.closest(
        "#" + MODAL_ID + ",#" + FLOAT_ID +
        ",.rgon-ad-v4-panel-launcher,.rgon-ad-v4-fallback"
      )
    );
  }

  function getInput(preferred) {
    if (OPTIONS.inputSelector) {
      const explicitNode = safeQuery(OPTIONS.inputSelector);
      if (explicitNode) return explicitNode;
    }

    if (
      preferred instanceof Element &&
      !isStudioElement(preferred) &&
      !preferred.closest("#rgon-clean-aside-modal") &&
      preferred.matches(
        'textarea,input[type="text"],input:not([type]),[contenteditable="true"]'
      )
    ) {
      return preferred;
    }

    for (const selector of INPUT_SELECTORS) {
      const input = safeQuery(selector);
      if (
        visible(input) &&
        !isStudioElement(input) &&
        !input.closest("#rgon-clean-aside-modal")
      ) return input;
    }

    const candidates = Array.from(
      document.querySelectorAll('textarea, input[type="text"]')
    ).filter(node =>
      visible(node) &&
      !isStudioElement(node) &&
      !node.closest("#rgon-clean-aside-modal")
    );

    return candidates.length === 1 ? candidates[0] : null;
  }

  function readInput(input) {
    return input
      ? String(input.isContentEditable ? input.textContent : input.value).trim()
      : "";
  }

  function clearInput(input) {
    if (input.isContentEditable) {
      input.textContent = "";
    } else {
      const prototype = input instanceof HTMLTextAreaElement
        ? HTMLTextAreaElement.prototype
        : HTMLInputElement.prototype;

      const setter = Object.getOwnPropertyDescriptor(
        prototype, "value"
      )?.set;

      if (setter) setter.call(input, "");
      else input.value = "";
    }

    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function isAdRequest(text) {
    return /광고|10\s*초|쇼츠|만들기|주제/i.test(text);
  }

  function cleanTopic(value) {
    return String(value)
      .replace(/^[\s"'“”‘’:：=]+|[\s"'“”‘’]+$/g, "")
      .replace(
        /(?:으로|로)?\s*(?:간단한\s*)?(?:10\s*초\s*)?(?:광고|쇼츠|영상)\s*(?:기획안|기획|제작)?\s*(?:을|를)?\s*(?:만들어\s*줘|만들어줘|만들어|제작해줘|제작해|만들기|부탁해|해주세요|해줘).*$/i,
        ""
      )
      .replace(/[.!?。！？]+$/g, "")
      .trim()
      .slice(0, 60);
  }

  function parseTopic(text) {
    const explicit = text.match(
      /주제(?:\s*(?:는|은|가|를))?\s*[:：=]?\s*(.+)$/i
    );

    if (explicit) {
      const value = cleanTopic(explicit[1]);
      if (value) return value;
    }

    const quoted = text.match(/["“‘']([^"”’']{1,60})["”’']/);
    if (quoted) {
      const value = cleanTopic(quoted[1]);
      if (value) return value;
    }

    const candidate = cleanTopic(
      text
        .replace(/간단한|간단하게|짧은|짧게|멋진|멋지게|하나|좀/g, " ")
        .replace(/10\s*초/g, " ")
        .replace(/광고|쇼츠|영상|기획안|기획|주제/g, " ")
        .replace(
          /만들어\s*줘|만들어줘|만들어|만들기|제작해줘|제작해|해주세요|해줘|부탁해/g,
          " "
        )
        .replace(/\s+/g, " ")
    ).replace(/(?:으로|로|에\s*대한)$/g, "").trim();

    return candidate || null;
  }

  function shortened(text, limit) {
    const chars = Array.from(text);
    return chars.length > limit
      ? chars.slice(0, limit).join("") + "…"
      : text;
  }

  function makePayload(topic) {
    const cup = /종이\s*컵/.test(topic);
    const spokenTopic = shortened(topic, 14).replace(/…$/, "");
    const hashtag = topic.replace(/[^\p{L}\p{N}_]/gu, "") || "광고";

    const payload = {
      id: window.crypto?.randomUUID?.() ||
        "ad-" + Date.now() + "-" + Math.random().toString(36).slice(2),
      topic,
      title: `${topic} 하나로 달라지는 순간 | 10초 세로 광고`,
      pinnedComment:
        `${topic}을 주제로 만든 10초 광고 콘셉트입니다.\n` +
        "가장 인상적인 장면을 댓글로 알려주세요!\n\n" +
        `#${hashtag} #10초광고 #쇼츠 #세로영상 #광고기획`,
      sunoPrompt:
        `Create an original instrumental music cue for a 10-second ` +
        `vertical advertisement about "${topic}". ` +
        "62 BPM, modern clean commercial sound, warm bass, " +
        "light plucked synth, subtle percussion, no vocals, no speech. " +
        "0-3 seconds: immediate sonic hook. " +
        "3-7 seconds: rhythmic lift and product detail. " +
        "7-10 seconds: short memorable resolving sting. " +
        "Do not imitate an existing artist or copyrighted song. " +
        "If the result is longer, edit the cue to 10 seconds.",
      plan: {
        hook: cup
          ? "평범한 종이컵 하나가 화면 중앙에 등장합니다. "
            + "카메라가 다가오며 ‘이 작은 컵, 주인공이 됩니다.’라는 자막."
          : `${topic}을 어두운 배경에서 강조합니다. `
            + "빠른 확대와 함께 ‘잠깐, 이 장면을 보세요.’라는 자막.",
        body: cup
          ? "종이컵의 입구와 종이 질감을 가까이 보여줍니다. "
            + "배경과 조명이 전환되며 일상의 물건을 광고의 주인공으로 바꿉니다."
          : `${topic}의 형태와 디테일을 강조합니다. `
            + "조명과 구도를 전환하며, 확인되지 않은 효능 대신 콘셉트에 집중합니다.",
        cta: cup
          ? "종이컵을 중앙에 배치하고 ‘오늘의 작은 여유를 담다’로 마무리합니다."
          : `${topic}을 중앙에 배치하고 ‘오늘의 장면을 바꿔보세요’로 마무리합니다.`,
        narration: cup
          ? "종이컵 하나로 달라지는 순간. 오늘의 작은 여유, 종이컵으로 완성하세요."
          : `${spokenTopic}, 새롭게 보는 순간. 오늘의 장면을 바꿔보세요.`
      },
      scenes: cup
        ? [
            ["작은 컵, 큰 장면", "이 작은 컵, 주인공이 됩니다."],
            ["일상을 새롭게 담다", "가까이 보면 달라지는 디테일"],
            ["오늘의 여유를 담다", "종이컵으로 완성하는 작은 순간"]
          ]
        : [
            [shortened(topic, 16), "잠깐, 이 장면을 보세요."],
            ["새롭게 보는 디테일", shortened(topic, 22)],
            ["오늘의 장면을 바꾸다", shortened(topic, 22)]
          ],
      createdAt: new Date().toISOString()
    };

    payload.comment = payload.pinnedComment;
    payload.suno = payload.sunoPrompt;
    return payload;
  }

  function installStyles() {
    if (document.getElementById(STYLE_ID)) return;

    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = `
      #${MODAL_ID},#${MODAL_ID} * {
        box-sizing:border-box !important;
        font-family:system-ui,-apple-system,"Malgun Gothic",sans-serif !important;
      }
      #${MODAL_ID} .rav4-shell {
        display:flex !important; flex-direction:column !important;
        width:min(1180px,100%) !important;
        max-height:calc(100dvh - 28px) !important;
        background:#0b1220 !important; color:#e2e8f0 !important;
        border:1px solid #475569 !important; border-radius:20px !important;
        box-shadow:0 25px 100px #000b !important;
        overflow:hidden !important; text-align:left !important;
      }
      #${MODAL_ID} .rav4-header {
        display:flex !important; align-items:center !important;
        justify-content:space-between !important; gap:12px !important;
        padding:16px 20px !important; flex-shrink:0 !important;
        background:#111c30 !important; border-bottom:1px solid #334155 !important;
      }
      #${MODAL_ID} .rav4-title {
        margin:0 !important; font-size:20px !important;
        line-height:1.5 !important; color:#f8fafc !important;
        overflow-wrap:anywhere !important;
      }
      #${MODAL_ID} .rav4-body {
        display:grid !important;
        grid-template-columns:minmax(0,1fr) minmax(290px,360px) !important;
        gap:24px !important; padding:20px !important;
        overflow:auto !important; min-height:0 !important;
      }
      #${MODAL_ID} .rav4-plan { min-width:0 !important; }
      #${MODAL_ID} .rav4-section {
        display:block !important; margin:0 0 18px !important;
        padding:14px !important; background:#111d31 !important;
        border:1px solid #26364d !important; border-radius:12px !important;
      }
      #${MODAL_ID} .rav4-section strong {
        display:block !important; color:#93c5fd !important;
        font-size:15px !important; line-height:1.6 !important;
      }
      #${MODAL_ID} .rav4-section p {
        display:block !important; margin:8px 0 0 !important;
        color:#e2e8f0 !important; font-size:14px !important;
        line-height:1.8 !important; white-space:pre-wrap !important;
        overflow-wrap:anywhere !important;
      }
      #${MODAL_ID} .rav4-player { min-width:0 !important; }
      #${MODAL_ID} .rav4-stage {
        display:block !important; width:min(100%,285px) !important;
        aspect-ratio:9/16 !important; margin:0 auto !important;
        background:#07111f !important; border-radius:14px !important;
        overflow:hidden !important;
      }
      #${MODAL_ID} canvas {
        display:block !important; visibility:visible !important;
        opacity:1 !important; width:100% !important; height:100% !important;
        max-width:none !important; max-height:none !important;
      }
      #${MODAL_ID} .rav4-timer {
        display:block !important; margin:10px 0 !important;
        text-align:center !important; color:#67e8f9 !important;
        font-variant-numeric:tabular-nums !important;
      }
      #${MODAL_ID} .rav4-controls {
        display:flex !important; flex-direction:column !important;
        gap:9px !important;
      }
      #${MODAL_ID} .rav4-button,
      .rgon-ad-v4-panel-launcher,.rav4-copy-button {
        display:inline-flex !important; align-items:center !important;
        justify-content:center !important;
        padding:11px 14px !important; border:1px solid #475569 !important;
        border-radius:10px !important; background:#1e293b !important;
        color:#f8fafc !important; font-size:14px !important;
        line-height:1.5 !important; cursor:pointer !important;
        white-space:normal !important; text-decoration:none !important;
      }
      #${MODAL_ID} .rav4-button:disabled {
        opacity:.5 !important; cursor:wait !important;
      }
      #${MODAL_ID} .rav4-button:focus-visible,
      .rgon-ad-v4-panel-launcher:focus-visible {
        outline:3px solid #60a5fa !important; outline-offset:2px !important;
      }
      #${MODAL_ID} .rav4-status {
        display:block !important; margin-top:12px !important;
        color:#a7f3d0 !important; font-size:13px !important;
        line-height:1.7 !important; white-space:pre-wrap !important;
      }
      #${MODAL_ID} .rav4-note {
        display:block !important; margin-top:12px !important;
        color:#94a3b8 !important; font-size:12px !important;
        line-height:1.7 !important;
      }
      #${MODAL_ID} .rav4-preview {
        width:100% !important; margin-top:14px !important;
        border-radius:12px !important; background:#000 !important;
      }
      #${MODAL_ID} .rav4-preview[hidden] { display:none !important; }
      .rav4-copy-notice {
        margin-top:14px !important; padding:13px 15px !important;
        border:1px solid #22c55e !important; border-radius:10px !important;
        background:#052e16 !important; color:#bbf7d0 !important;
        line-height:1.7 !important; white-space:pre-wrap !important;
      }
      .rav4-copy-notice[hidden] { display:none !important; }
      @media(max-width:760px) {
        #${MODAL_ID} .rav4-body {
          grid-template-columns:minmax(0,1fr) !important;
          padding:14px !important;
        }
        #${MODAL_ID} .rav4-title { font-size:16px !important; }
        #${MODAL_ID} .rav4-header { padding:12px !important; }
        #${MODAL_ID} .rav4-stage { width:min(100%,270px) !important; }
      }
    `;
    document.head.appendChild(style);
  }

  function setFloating(payload) {
    let button = document.getElementById(FLOAT_ID);

    if (!button) {
      button = element("button");
      button.id = FLOAT_ID;
      button.type = "button";

      important(button, {
        position: "fixed",
        right: "18px",
        bottom: "76px",
        top: "auto",
        left: "auto",
        "z-index": "2147483639",
        display: "block",
        visibility: "visible",
        opacity: "1",
        transform: "none",
        padding: "14px 18px",
        border: "1px solid #6ee7b7",
        "border-radius": "14px",
        background: "#065f46",
        color: "#ffffff",
        "box-shadow": "0 8px 30px #0007",
        "font-family": 'system-ui,"Malgun Gothic",sans-serif',
        "font-size": "14px",
        "line-height": "1.5",
        "max-width": "calc(100vw - 36px)",
        cursor: "pointer",
        "pointer-events": "auto"
      });

      button.addEventListener("click", () => {
        if (window.__LAST_AD_PAYLOAD__) {
          openStudio(window.__LAST_AD_PAYLOAD__);
        }
      });

      document.body.appendChild(button);
    }

    const label = `🎬 '${payload.topic}' 10초 광고 스튜디오 열기`;
    if (button.textContent !== label) button.textContent = label;
  }

  function publish(payload) {
    window.__LAST_AD_PAYLOAD__ = payload;
    setFloating(payload);
    refreshPanels();

    window.dispatchEvent(new CustomEvent("rgon:ad-generated", {
      detail: payload
    }));
  }

  function controllerPanels() {
    return Array.from(document.querySelectorAll(
      "#rgon-clean-aside-modal," +
      ".rgon-ad-v4-fallback," +
      '[role="dialog"],dialog[open]'
    )).filter(node =>
      node.id !== MODAL_ID &&
      !node.closest("#" + MODAL_ID)
    );
  }

  function lowerControllerPanels() {
    STATE.loweredPanels = [];

    for (const panel of controllerPanels()) {
      const parentOverlay = panel.closest(
        "#rgon-clean-aside-modal,.rgon-ad-v4-fallback"
      );
      const node = parentOverlay || panel;

      if (STATE.loweredPanels.some(item => item.node === node)) continue;

      STATE.loweredPanels.push({
        node,
        value: node.style.getPropertyValue("z-index"),
        priority: node.style.getPropertyPriority("z-index")
      });

      node.style.setProperty("z-index", "2147483630", "important");
    }
  }

  function restoreControllerPanels() {
    for (const entry of STATE.loweredPanels) {
      if (!entry.node.isConnected) continue;

      if (entry.value) {
        entry.node.style.setProperty(
          "z-index", entry.value, entry.priority
        );
      } else {
        entry.node.style.removeProperty("z-index");
      }
    }

    STATE.loweredPanels = [];
  }

  function closeStudio(restoreFocus = true) {
    STATE.modalCleanup?.();
    STATE.modalCleanup = null;

    STATE.modal?.remove();
    STATE.modal = null;
    restoreControllerPanels();

    if (restoreFocus && STATE.previousFocus?.isConnected) {
      STATE.previousFocus.focus();
    }
  }

  function openStudio(payload) {
    if (!payload) return;

    installStyles();
    closeStudio(false);

    STATE.previousFocus = document.activeElement;
    lowerControllerPanels();

    const overlay = element("div");
    overlay.id = MODAL_ID;
    overlay.dataset.payloadId = payload.id;

    important(overlay, {
      position: "fixed",
      inset: "0",
      "z-index": "2147483640",
      display: "flex",
      "align-items": "center",
      "justify-content": "center",
      padding: "14px",
      margin: "0",
      width: "100%",
      height: "100%",
      "max-width": "none",
      "max-height": "none",
      visibility: "visible",
      opacity: "1",
      transform: "none",
      background: "rgba(2,6,23,.88)",
      "pointer-events": "auto",
      isolation: "isolate",
      overflow: "hidden"
    });

    const shell = element("section", "rav4-shell");
    shell.setAttribute("role", "dialog");
    shell.setAttribute("aria-modal", "true");
    shell.setAttribute("aria-labelledby", "rgon-ad-v4-title");
    shell.tabIndex = -1;

    const header = element("header", "rav4-header");
    const title = element(
      "h2", "rav4-title",
      `🎬 '${payload.topic}' 10초 광고 기획안 + 세로 광고 스튜디오`
    );
    title.id = "rgon-ad-v4-title";

    const close = element("button", "rav4-button", "✖ 닫기");
    close.type = "button";
    close.addEventListener("click", () => closeStudio());

    header.append(title, close);

    const body = element("div", "rav4-body");
    const plan = element("div", "rav4-plan");

    const sections = [
      ["🎯 [0~3초 시선강탈 훅(Hook)]", payload.plan.hook],
      ["🔥 [3~7초 핵심 반전 & 디테일(Body)]", payload.plan.body],
      ["🚀 [7~10초 강렬한 클로징(CTA)]", payload.plan.cta],
      ["🎙️ [10초 음성 나레이션 대본]", payload.plan.narration]
    ];

    for (const [label, text] of sections) {
      const section = element("section", "rav4-section");
      section.append(
        element("strong", "", label),
        element("p", "", text)
      );
      plan.appendChild(section);
    }

    const planPanelButton = element(
      "button", "rav4-button", "🚀 한마디 올인원"
    );
    planPanelButton.type = "button";
    planPanelButton.addEventListener("click", () => {
      closeStudio(false);
      openCommanderPanel();
    });
    plan.appendChild(planPanelButton);

    const player = element("div", "rav4-player");
    body.append(plan, player);
    shell.append(header, body);
    overlay.appendChild(shell);

    document.body.appendChild(overlay);
    STATE.modal = overlay;

    let disposePlayer = () => {};

    try {
      disposePlayer = buildPlayer(player, payload);
    } catch (error) {
      console.error("[RGON v4] 플레이어 초기화 실패:", error);
      player.appendChild(element(
        "div", "rav4-status",
        `⚠️ 플레이어 초기화 실패: ${error.message}`
      ));
    }

    function onKey(event) {
      if (event.key === "Escape") {
        event.preventDefault();
        event.stopImmediatePropagation();
        closeStudio();
        return;
      }

      if (event.key === "Tab") {
        const controls = Array.from(shell.querySelectorAll(
          "button:not([disabled]),a[href],video[controls]"
        )).filter(visible);

        const first = controls[0];
        const last = controls[controls.length - 1];

        if (!first) {
          event.preventDefault();
          shell.focus();
        } else if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    }

    window.addEventListener("keydown", onKey, true);

    overlay.addEventListener("click", event => {
      if (event.target === overlay) closeStudio();
    });

    STATE.modalCleanup = () => {
      window.removeEventListener("keydown", onKey, true);
      disposePlayer();
    };

    close.focus();
  }

  function roundedRect(ctx, x, y, width, height, radius) {
    const r = Math.min(radius, width / 2, height / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + width, y, x + width, y + height, r);
    ctx.arcTo(x + width, y + height, x, y + height, r);
    ctx.arcTo(x, y + height, x, y, r);
    ctx.arcTo(x, y, x + width, y, r);
    ctx.closePath();
  }

  function wrapText(ctx, text, x, y, width, lineHeight, maxLines = 3) {
    const lines = [];
    let line = "";

    for (const char of Array.from(text)) {
      if (ctx.measureText(line + char).width > width && line) {
        lines.push(line);
        line = char;
      } else {
        line += char;
      }
    }

    if (line) lines.push(line);

    const shown = lines.slice(0, maxLines);
    if (lines.length > maxLines && shown.length) {
      shown[shown.length - 1] =
        shown[shown.length - 1].slice(0, -1) + "…";
    }

    shown.forEach((textLine, index) => {
      ctx.fillText(textLine, x, y + index * lineHeight);
    });
  }

  function drawCup(ctx, seconds, scene) {
    ctx.save();
    ctx.translate(270, 452 + Math.sin(seconds * 2.3) * 8);
    ctx.rotate(Math.sin(seconds * 1.5) * 0.025);

    const scale = scene === 1 ? 1.09 : 1;
    ctx.scale(scale, scale);

    const paper = ctx.createLinearGradient(-100, 0, 100, 0);
    paper.addColorStop(0, "#cbd5e1");
    paper.addColorStop(0.45, "#ffffff");
    paper.addColorStop(1, "#94a3b8");

    ctx.shadowColor = "rgba(0,0,0,0.53)";
    ctx.shadowBlur = 24;
    ctx.shadowOffsetY = 14;
    ctx.fillStyle = paper;

    ctx.beginPath();
    ctx.moveTo(-102, -116);
    ctx.lineTo(102, -116);
    ctx.lineTo(68, 136);
    ctx.quadraticCurveTo(0, 156, -68, 136);
    ctx.closePath();
    ctx.fill();

    ctx.shadowBlur = 0;
    ctx.shadowOffsetY = 0;

    ctx.fillStyle = "#f8fafc";
    ctx.beginPath();
    ctx.ellipse(0, -116, 104, 26, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#64748b";
    ctx.beginPath();
    ctx.ellipse(0, -116, 88, 15, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#e2e8f0";
    ctx.beginPath();
    ctx.ellipse(0, -119, 86, 10, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = "#cbd5e1";
    ctx.lineWidth = 2;
    for (let i = -2; i <= 2; i++) {
      ctx.beginPath();
      ctx.moveTo(i * 31, -78);
      ctx.lineTo(i * 22, 114);
      ctx.stroke();
    }

    ctx.fillStyle = "#0f766e";
    roundedRect(ctx, -57, -18, 114, 64, 12);
    ctx.fill();

    ctx.fillStyle = "#ecfeff";
    ctx.font = 'bold 22px "Malgun Gothic",sans-serif';
    ctx.textAlign = "center";
    ctx.fillText("PAPER", 0, 23);
    ctx.restore();
  }

  function drawGeneric(ctx, payload, seconds, scene) {
    ctx.save();
    ctx.translate(270, 450 + Math.sin(seconds * 2) * 9);
    ctx.rotate(Math.sin(seconds * 1.4) * 0.03);

    const scale = scene === 1 ? 1.06 : 1;
    ctx.scale(scale, scale);

    const gradient = ctx.createLinearGradient(-130, -150, 130, 150);
    gradient.addColorStop(0, "#38bdf8");
    gradient.addColorStop(1, "#7c3aed");

    ctx.fillStyle = gradient;
    ctx.shadowColor = "rgba(56,189,248,0.4)";
    ctx.shadowBlur = 32;
    roundedRect(ctx, -132, -150, 264, 300, 30);
    ctx.fill();

    ctx.shadowBlur = 0;
    ctx.strokeStyle = "rgba(255,255,255,0.4)";
    ctx.lineWidth = 2;
    roundedRect(ctx, -112, -130, 224, 260, 22);
    ctx.stroke();

    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "center";
    ctx.font = 'bold 36px "Malgun Gothic",sans-serif';
    wrapText(ctx, shortened(payload.topic, 18), 0, -10, 204, 48, 3);
    ctx.restore();
  }

  function renderFrame(canvas, payload, seconds) {
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("Canvas 2D 컨텍스트를 만들 수 없습니다.");

    const t = Math.max(0, Math.min(10, seconds));
    const scene = t < 3 ? 0 : t < 7 ? 1 : 2;
    const local = t - [0, 3, 7][scene];

    const colors = [
      ["#07182b", "#123f59"],
      ["#10223c", "#124e4d"],
      ["#24143e", "#125258"]
    ][scene];

    const gradient = ctx.createLinearGradient(0, 0, 540, 960);
    gradient.addColorStop(0, colors[0]);
    gradient.addColorStop(1, colors[1]);

    ctx.globalAlpha = 1;
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 540, 960);

    for (let i = 0; i < 14; i++) {
      ctx.fillStyle = `rgba(255,255,255,${0.035 + i % 3 * 0.02})`;
      ctx.beginPath();
      ctx.arc(
        (i * 97 + t * 19) % 600 - 30,
        (i * 137 + t * 31) % 1020 - 30,
        8 + i % 4 * 5,
        0,
        Math.PI * 2
      );
      ctx.fill();
    }

    ctx.textAlign = "left";
    ctx.fillStyle = "#a5f3fc";
    ctx.font = 'bold 21px "Malgun Gothic",sans-serif';
    ctx.fillText("RGON ALPHA · 10s AD", 34, 54);

    ctx.textAlign = "right";
    ctx.fillStyle = "#e2e8f0";
    ctx.font = '20px "Malgun Gothic",sans-serif';
    ctx.fillText(`${t.toFixed(1)} / 10.0s`, 506, 54);

    ctx.textAlign = "center";
    ctx.globalAlpha = Math.min(1, local * 4 + 0.2);
    ctx.fillStyle = "#ffffff";
    ctx.font = 'bold 43px "Malgun Gothic",sans-serif';
    wrapText(ctx, payload.scenes[scene][0], 270, 145, 470, 58, 2);
    ctx.globalAlpha = 1;

    if (/종이\s*컵/.test(payload.topic)) drawCup(ctx, t, scene);
    else drawGeneric(ctx, payload, t, scene);

    ctx.fillStyle = "rgba(2,6,23,0.73)";
    roundedRect(ctx, 27, 699, 486, 150, 18);
    ctx.fill();

    ctx.fillStyle = "#f8fafc";
    ctx.font = 'bold 29px "Malgun Gothic",sans-serif';
    wrapText(ctx, payload.scenes[scene][1], 270, 754, 440, 42, 3);

    ctx.fillStyle = "#67e8f9";
    ctx.font = 'bold 20px "Malgun Gothic",sans-serif';
    ctx.fillText(
      ["0–3초 · HOOK", "3–7초 · BODY", "7–10초 · CTA"][scene],
      270, 894
    );

    ctx.fillStyle = "rgba(255,255,255,0.2)";
    ctx.fillRect(28, 924, 484, 7);
    ctx.fillStyle = "#34d399";
    ctx.fillRect(28, 924, 484 * t / 10, 7);

    ctx.fillStyle = "#cbd5e1";
    ctx.font = '14px "Malgun Gothic",sans-serif';
    ctx.fillText("프론트엔드 콘셉트 렌더링", 270, 951);
  }

  function speak(text) {
    if (!("speechSynthesis" in window)) return false;

    const voices = speechSynthesis.getVoices().filter(voice =>
      /^ko(?:-|_)/i.test(voice.lang)
    );

    const voice = voices.find(item =>
      /인준|InJoon|남성|\bmale\b/i.test(item.name)
    ) || voices[0];

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "ko-KR";
    if (voice) utterance.voice = voice;
    utterance.rate = 1.16;
    utterance.pitch = 1.03;
    utterance.volume = 1;

    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
    return true;
  }

  async function makeMusic() {
    const AudioContextClass =
      window.AudioContext || window.webkitAudioContext;

    if (!AudioContextClass) return null;

    const context = new AudioContextClass();
    const nodes = [];
    let destination;

    try {
      await context.resume();
      destination = context.createMediaStreamDestination();

      const master = context.createGain();
      master.gain.value = 0.11;
      master.connect(context.destination);
      master.connect(destination);
      nodes.push(master);

      return {
        destination,

        start() {
          const start = context.currentTime + 0.03;
          const beat = 60 / 62;
          const melody = [523.25, 659.25, 783.99, 659.25, 587.33];

          function note(frequency, offset, duration, volume, type) {
            const oscillator = context.createOscillator();
            const gain = context.createGain();
            const when = start + offset;

            oscillator.type = type;
            oscillator.frequency.value = frequency;

            gain.gain.setValueAtTime(0.0001, when);
            gain.gain.exponentialRampToValueAtTime(volume, when + 0.025);
            gain.gain.exponentialRampToValueAtTime(
              0.0001, when + duration
            );

            oscillator.connect(gain);
            gain.connect(master);
            oscillator.start(when);
            oscillator.stop(when + duration + 0.03);

            nodes.push(oscillator, gain);
          }

          for (let i = 0; i * beat < 9.4; i++) {
            const offset = i * beat;
            note(
              melody[i % melody.length], offset,
              Math.min(0.55, 9.8 - offset), 0.45, "triangle"
            );
            note(i % 2 ? 130.81 : 98, offset, 0.4, 0.28, "sine");
          }

          for (const frequency of [523.25, 659.25, 783.99]) {
            note(frequency, 9.15, 0.6, 0.23, "sine");
          }
        },

        async close() {
          for (const node of nodes) {
            try { node.stop?.(); } catch (_) {}
            try { node.disconnect(); } catch (_) {}
          }
          destination.stream.getTracks().forEach(track => track.stop());
          if (context.state !== "closed") {
            await context.close().catch(() => {});
          }
        }
      };

    } catch (error) {
      await context.close().catch(() => {});
      console.warn("[RGON v4] BGM 초기화 실패:", error);
      return null;
    }
  }

  function webmType() {
    if (!window.MediaRecorder) return "";

    return [
      "video/webm;codecs=vp9,opus",
      "video/webm;codecs=vp8,opus",
      "video/webm;codecs=vp8",
      "video/webm"
    ].find(type => MediaRecorder.isTypeSupported(type)) || "";
  }

  function filename(topic) {
    const safe = topic
      .replace(/[<>:"/\\|?*\u0000-\u001f]/g, "_")
      .replace(/[. ]+$/g, "")
      .slice(0, 55);

    return `ad_${safe || "topic"}_10s.webm`;
  }

  function buildPlayer(host, payload) {
    const stage = element("div", "rav4-stage");
    const canvas = document.createElement("canvas");
    canvas.width = 540;
    canvas.height = 960;
    canvas.setAttribute("aria-label", `${payload.topic} 세로 광고 Canvas`);
    stage.appendChild(canvas);

    const timer = element("div", "rav4-timer", "0.0초 / 10.0초");
    const controls = element("div", "rav4-controls");

    const play = element(
      "button", "rav4-button", "▶ 10초 광고 영상 재생 + 나레이션 듣기"
    );
    const download = element(
      "button", "rav4-button", "💾 10초 광고 영상(.webm) 다운로드"
    );
    const stop = element("button", "rav4-button", "■ 중지");
    const panel = element("button", "rav4-button", "🚀 한마디 올인원");

    for (const button of [play, download, stop, panel]) button.type = "button";
    stop.disabled = true;
    controls.append(play, download, stop, panel);

    const status = element(
      "div", "rav4-status", "준비 완료 · 현재 탭에서 재생 또는 녹화하세요."
    );
    status.setAttribute("role", "status");

    const note = element(
      "div", "rav4-note",
      "WebM에는 실제 Canvas 영상과 내장 합성 BGM이 저장됩니다. " +
      "브라우저 나레이션은 청취용이며 파일에 녹음되지 않습니다. " +
      "발화는 10초에서 종료하며 음색은 설치된 한국어 음성에 따라 다릅니다."
    );

    const video = document.createElement("video");
    video.className = "rav4-preview";
    video.controls = true;
    video.playsInline = true;
    video.hidden = true;

    host.append(stage, timer, controls, status, note, video);
    renderFrame(canvas, payload, 0);

    let playbackUrl = null;
    let ownRun = null;
    let disposed = false;

    async function run(recording) {
      if (disposed) return;
      if (STATE.activeRun) {
        status.textContent = "다른 재생 또는 녹화를 먼저 중지하세요.";
        return;
      }
      if (document.hidden) {
        status.textContent = "현재 탭을 활성화한 뒤 다시 실행하세요.";
        return;
      }

      const mimeType = recording ? webmType() : "";

      if (recording && (!canvas.captureStream || !mimeType)) {
        status.textContent =
          "Canvas WebM 녹화를 지원하지 않습니다. 최신 Chrome/Edge를 사용하세요.";
        return;
      }

      let music = null;
      let canvasStream = null;
      let combinedStream = null;
      let recorder = null;
      let stopPromise = null;
      let animation = 0;
      let timeout = 0;
      let chunks = [];
      let done = false;
      let started = 0;

      const token = {};
      ownRun = token;
      STATE.activeRun = token;

      play.disabled = true;
      download.disabled = true;
      stop.disabled = false;
      status.textContent = recording ? "녹화 준비 중…" : "재생 준비 중…";

      async function finish(success, message) {
        if (done) return;
        done = true;

        cancelAnimationFrame(animation);
        clearTimeout(timeout);
        document.removeEventListener("visibilitychange", onVisibility);
        window.removeEventListener("pagehide", onPageHide);

        if ("speechSynthesis" in window) speechSynthesis.cancel();

        try {
          if (recorder && recorder.state !== "inactive") recorder.stop();

          if (stopPromise) {
            await Promise.race([
              stopPromise,
              new Promise((_, reject) => {
                setTimeout(() => reject(
                  new Error("녹화 종료 응답 시간이 초과되었습니다.")
                ), 3000);
              })
            ]);
          }

          if (success && !disposed) {
            renderFrame(canvas, payload, 10);
            timer.textContent = "10.0초 / 10.0초";
          }

          if (recording && success && !disposed) {
            const blob = new Blob(chunks, { type: mimeType });
            if (!blob.size) throw new Error("녹화 결과가 비어 있습니다.");

            if (playbackUrl) URL.revokeObjectURL(playbackUrl);
            playbackUrl = URL.createObjectURL(blob);

            video.src = playbackUrl;
            video.hidden = false;

            const link = document.createElement("a");
            link.href = playbackUrl;
            link.download = filename(payload.topic);
            document.body.appendChild(link);
            link.click();
            link.remove();

            status.textContent =
              `✅ ${filename(payload.topic)} 다운로드 요청 완료\n` +
              "아래 플레이어에서 실제 녹화 결과를 확인하세요. " +
              "자동 저장이 제한되면 플레이어 메뉴에서 저장할 수 있습니다.";
          } else if (!disposed) {
            status.textContent =
              message || (success ? "✅ 10초 재생 완료" : "중지했습니다.");
          }

        } catch (error) {
          if (!disposed) status.textContent = `⚠️ ${error.message}`;

        } finally {
          canvasStream?.getTracks().forEach(track => track.stop());
          combinedStream?.getTracks().forEach(track => track.stop());
          await music?.close();

          chunks = [];

          if (!disposed) {
            play.disabled = false;
            download.disabled = false;
            stop.disabled = true;
          }

          if (STATE.activeRun === token) STATE.activeRun = null;
          if (ownRun === token) ownRun = null;
        }
      }

      function onVisibility() {
        if (document.hidden) {
          finish(false, "탭이 비활성화되어 중지했습니다. 현재 탭에서 다시 실행하세요.");
        }
      }

      function onPageHide() {
        finish(false, "페이지 이동으로 중지했습니다.");
      }

      token.cancel = () => finish(false, "사용자가 중지했습니다.");

      try {
        music = await makeMusic();

        if (done || disposed) {
          await music?.close();
          return;
        }

        if (document.hidden) {
          await finish(false, "현재 탭을 활성화한 뒤 다시 실행하세요.");
          return;
        }

        renderFrame(canvas, payload, 0);

        if (recording) {
          canvasStream = canvas.captureStream(30);
          combinedStream = new MediaStream([
            ...canvasStream.getVideoTracks(),
            ...(music ? music.destination.stream.getAudioTracks() : [])
          ]);

          recorder = new MediaRecorder(combinedStream, {
            mimeType,
            videoBitsPerSecond: 2800000,
            audioBitsPerSecond: 128000
          });

          recorder.addEventListener("dataavailable", event => {
            if (event.data?.size) chunks.push(event.data);
          });

          recorder.addEventListener("error", event => {
            finish(
              false,
              `녹화 오류: ${event.error?.message || "알 수 없는 오류"}`
            );
          });

          const stopped = new Promise(resolve => {
            recorder.addEventListener("stop", resolve, { once: true });
          });

          recorder.start(250);
          stopPromise = stopped;
        }

        music?.start();
        const speaking = speak(payload.plan.narration);
        started = performance.now();

        status.textContent =
          (recording ? "🔴 실제 WebM 녹화 중" : "▶ 광고 재생 중") +
          (speaking ? " · 한국어 나레이션" : " · TTS 미지원") +
          (music ? " · 합성 BGM" : " · BGM 사용 불가");

        document.addEventListener("visibilitychange", onVisibility);
        window.addEventListener("pagehide", onPageHide, { once: true });

        function tick(now) {
          if (done) return;

          if (!host.isConnected) {
            finish(false, "스튜디오가 닫혀 중지했습니다.");
            return;
          }

          const seconds = Math.min(10, (now - started) / 1000);

          try {
            renderFrame(canvas, payload, seconds);
            timer.textContent = `${seconds.toFixed(1)}초 / 10.0초`;
          } catch (error) {
            finish(false, `Canvas 오류: ${error.message}`);
            return;
          }

          animation = requestAnimationFrame(tick);
        }

        animation = requestAnimationFrame(tick);

        timeout = setTimeout(() => {
          if (performance.now() - started > 11200) {
            finish(false, "브라우저 지연으로 녹화를 취소했습니다. 다시 실행하세요.");
          } else {
            finish(true);
          }
        }, 10000);

      } catch (error) {
        await finish(false, `⚠️ 실행 실패: ${error.message}`);
      }
    }

    play.addEventListener("click", () => run(false));
    download.addEventListener("click", () => run(true));
    stop.addEventListener("click", () => ownRun?.cancel?.());

    panel.addEventListener("click", () => {
      closeStudio(false);
      openCommanderPanel();
    });

    return () => {
      disposed = true;
      ownRun?.cancel?.();
      video.pause();
      video.removeAttribute("src");
      video.load();

      if (playbackUrl) {
        URL.revokeObjectURL(playbackUrl);
        playbackUrl = null;
      }
    };
  }

  async function copyText(text) {
    try {
      if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(text);
      return;
    } catch (_) {
      const input = document.createElement("textarea");
      input.value = text;
      input.readOnly = true;
      input.style.cssText =
        "position:fixed;left:-9999px;top:0;opacity:0";
      document.body.appendChild(input);
      input.select();

      let copied = false;
      try {
        copied = document.execCommand("copy");
      } finally {
        input.remove();
      }

      if (!copied) throw new Error("클립보드 권한을 확인해 주세요.");
    }
  }

  function copyRow(panel) {
    let row = panel.querySelector(
      ".rgon-copies,.rgon-ad-panel-copies,.rav4-panel-copies"
    );
    if (row) return row;

    const buttons = Array.from(panel.querySelectorAll("button"));
    const a = buttons.find(button => /제목.*복사/.test(button.textContent));
    const b = buttons.find(button => /고정댓글.*복사/.test(button.textContent));
    const c = buttons.find(button => /Suno.*복사|BGM.*복사/i.test(button.textContent));

    if (
      a && b && c &&
      a.parentElement === b.parentElement &&
      a.parentElement === c.parentElement &&
      a.parentElement.children.length === 3
    ) return a.parentElement;

    return null;
  }

  function wireCopies(panel, row, payload) {
    if (row.dataset.rgonV4Payload === payload.id) return;

    row.dataset.rgonV4Payload = payload.id;
    row.replaceChildren();

    let notice = panel.querySelector(".rgon-notice,.rav4-copy-notice");

    if (!notice) {
      notice = element("div", "rav4-copy-notice");
      notice.hidden = true;
      notice.setAttribute("role", "status");

      const content = panel.querySelector(
        ".rgon-panel,.rav4-fallback-content"
      ) || panel;

      content.appendChild(notice);
    }

    const specs = [
      [
        `📋 '${payload.topic}' 10초 광고 제목 복사`,
        "title", "업로드 화면의 제목 입력란에 붙여넣으세요."
      ],
      [
        `💬 '${payload.topic}' 고정댓글 복사`,
        "pinnedComment", "댓글 입력란에 붙여넣고 게시 후 고정하세요."
      ],
      [
        `🎵 '${payload.topic}' Suno BGM 복사`,
        "sunoPrompt", "Suno의 음악 설명 입력란에 붙여넣으세요."
      ]
    ];

    for (const [label, key, guide] of specs) {
      const button = element(
        "button", "rgon-action rav4-copy-button", label
      );
      button.type = "button";

      button.addEventListener("click", async () => {
        const latest = window.__LAST_AD_PAYLOAD__ || payload;
        button.disabled = true;

        try {
          await copyText(latest[key]);
          notice.textContent =
            `✅ '${latest.topic}' 복사 완료\n${guide}\n` +
            "붙여넣기: Ctrl+V / Mac: ⌘V";
        } catch (error) {
          notice.textContent = `⚠️ ${error.message}`;
        } finally {
          button.disabled = false;
          notice.hidden = false;
        }
      });

      row.appendChild(button);
    }
  }

  function refreshPanels() {
    const payload = window.__LAST_AD_PAYLOAD__;
    if (!payload || STATE.refreshing) return;

    STATE.refreshing = true;

    try {
      for (const panel of controllerPanels()) {
        const row = copyRow(panel);

        if (!row && !panel.matches(
          "#rgon-clean-aside-modal,.rgon-ad-v4-fallback"
        )) continue;

        if (row) wireCopies(panel, row, payload);

        let launcher = panel.querySelector(".rgon-ad-v4-panel-launcher");

        if (!launcher) {
          launcher = element("button", "rgon-ad-v4-panel-launcher");
          launcher.type = "button";

          launcher.addEventListener("click", event => {
            event.preventDefault();
            event.stopPropagation();

            if (window.__LAST_AD_PAYLOAD__) {
              openStudio(window.__LAST_AD_PAYLOAD__);
            }
          });

          if (row?.parentNode) {
            row.parentNode.insertBefore(launcher, row.nextSibling);
          } else {
            const content = panel.querySelector(
              ".rgon-panel,.rav4-fallback-content"
            ) || panel;
            content.appendChild(launcher);
          }
        }

        const label =
          `🎬 방금 만든 '${payload.topic}' 10초 광고 영상 스튜디오 열기`;

        if (launcher.textContent !== label) launcher.textContent = label;
      }

    } finally {
      STATE.refreshing = false;
    }
  }

  function safeLink(value) {
    if (typeof value !== "string" || !value.trim()) return null;

    try {
      const url = new URL(value, location.href);
      return /^https?:$/.test(url.protocol) ? url.href : null;
    } catch (_) {
      return null;
    }
  }

  function fallbackCommanderPanel() {
    document.querySelector(".rgon-ad-v4-fallback")?.remove();

    const overlay = element("div", "rgon-ad-v4-fallback");
    important(overlay, {
      position: "fixed",
      inset: "0",
      "z-index": "2147483635",
      display: "flex",
      "align-items": "center",
      "justify-content": "center",
      padding: "20px",
      background: "#000b"
    });

    const content = element("section", "rav4-fallback-content");
    content.setAttribute("role", "dialog");
    content.setAttribute("aria-modal", "true");
    content.setAttribute("aria-label", "실전 지휘 패널");

    important(content, {
      width: "min(950px,100%)",
      "max-height": "90vh",
      overflow: "auto",
      padding: "22px",
      background: "#101827",
      color: "#f8fafc",
      border: "1px solid #475569",
      "border-radius": "16px"
    });

    const close = element("button", "rav4-copy-button", "✖ 닫기");
    close.type = "button";
    close.addEventListener("click", () => overlay.remove());

    const links = element("nav");
    const copies = element("div", "rav4-panel-copies");

    important(links, {
      display: "flex", "flex-wrap": "wrap", gap: "10px", margin: "16px 0"
    });
    important(copies, {
      display: "flex", "flex-wrap": "wrap", gap: "10px", margin: "16px 0"
    });

    const specs = [
      ["①1청사 퀀트", LOCAL_CONFIG.quant_url],
      ["②3청사 미디어", LOCAL_CONFIG.media_url],
      ["③Suno 작곡창", LOCAL_CONFIG.suno_url || "https://suno.com/create"],
      [
        "④유튜브 업로드",
        LOCAL_CONFIG.youtube_url || "https://www.youtube.com/upload"
      ],
      [
        "⑤틱톡 업로드",
        LOCAL_CONFIG.tiktok_url ||
        "https://www.tiktok.com/tiktokstudio/upload"
      ]
    ];

    for (const [label, value] of specs) {
      const url = safeLink(value);
      const link = element(
        url ? "a" : "span",
        "rav4-copy-button",
        url ? label : label + " · URL 미설정"
      );

      if (url) {
        link.href = url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
      }
      links.appendChild(link);
    }

    content.append(
      element("h2", "", "🚀 노트북 어사이드 실전 지휘 패널"),
      close, links, copies
    );
    overlay.appendChild(content);
    document.body.appendChild(overlay);

    overlay.addEventListener("click", event => {
      if (event.target === overlay) overlay.remove();
    });

    refreshPanels();
    close.focus();
  }

  function wrapExistingModal() {
    const original = window.showRealAsideControllerModal;
    if (typeof original !== "function" || original.__rgonV4Wrapped) return;

    const wrapped = function(...args) {
      const result = original.apply(this, args);
      refreshPanels();
      queueMicrotask(refreshPanels);
      requestAnimationFrame(refreshPanels);
      return result;
    };

    wrapped.__rgonV4Wrapped = true;

    try {
      window.showRealAsideControllerModal = wrapped;
    } catch (error) {
      console.warn("[RGON v4] 지휘 패널 래핑 불가:", error);
    }
  }

  function openCommanderPanel() {
    wrapExistingModal();

    if (typeof window.showRealAsideControllerModal === "function") {
      try {
        window.showRealAsideControllerModal();
        refreshPanels();
      } catch (error) {
        console.error("[RGON v4] 기존 지휘 패널 오류:", error);
        fallbackCommanderPanel();
      }
    } else {
      fallbackCommanderPanel();
    }
  }

  function handleRequest(input, event) {
    const text = readInput(input);
    if (!text || !isAdRequest(text)) return false;

    if (event) {
      event.preventDefault();
      event.stopImmediatePropagation();
    }

    const topic = parseTopic(text);

    if (!topic) {
      alert('광고 주제를 입력하세요.\n예: 간단한 10초 광고 만들기 주제는 종이컵');
      input.focus();
      return true;
    }

    try {
      const payload = makePayload(topic);
      publish(payload);
      openStudio(payload);
      speak(payload.plan.narration);

      clearInput(input);

    } catch (error) {
      console.error("[RGON v4] 광고 생성 실패:", error);
      alert(
        "광고 화면 생성 중 오류가 발생했습니다.\n" +
        error.message +
        "\n브라우저 개발자도구 Console을 확인하세요."
      );
    }

    return true;
  }

  function wrapDokdaeSender() {
    if (typeof window.sendDokdaeMessage === "function" && !window.sendDokdaeMessage.__rgonV4Wrapped) {
      const origSend = window.sendDokdaeMessage;
      const wrappedSend = function(...args) {
        const input = getInput(STATE.lastInput);
        if (input && handleRequest(input, null)) {
          return;
        }
        return origSend.apply(this, args);
      };
      wrappedSend.__rgonV4Wrapped = true;
      window.sendDokdaeMessage = wrappedSend;
    }
  }

  function installInterceptors() {
    wrapDokdaeSender();

    window.addEventListener("focusin", event => {
      const input = getInput(event.target);
      if (input === event.target) STATE.lastInput = input;
    }, true);

    window.addEventListener("submit", event => {
      const form = event.target;
      if (!(form instanceof HTMLFormElement) || isStudioElement(form)) return;

      const preferred =
        STATE.lastInput && form.contains(STATE.lastInput)
          ? STATE.lastInput
          : form.querySelector("textarea,input[type=text],[contenteditable=true]");

      const input = getInput(preferred);
      if (input && form.contains(input)) handleRequest(input, event);
    }, true);

    window.addEventListener("keydown", event => {
      if (
        event.key !== "Enter" ||
        event.shiftKey ||
        event.isComposing ||
        event.keyCode === 229 ||
        event.defaultPrevented ||
        isStudioElement(event.target)
      ) return;

      const input = getInput(event.target);
      if (input === event.target) handleRequest(input, event);
    }, true);

    window.addEventListener("click", event => {
      if (!(event.target instanceof Element) || isStudioElement(event.target)) {
        return;
      }

      let button = event.target.closest(
        "button,input[type=submit],[role=button]"
      );

      if (OPTIONS.sendSelector) {
        try {
          button = event.target.closest(OPTIONS.sendSelector) || button;
        } catch (_) {}
      }

      if (!button) return;

      const description = [
        button.textContent || button.value || "",
        button.getAttribute("aria-label") || "",
        button.getAttribute("title") || "",
        button.id || "",
        typeof button.className === "string" ? button.className : "",
        button.getAttribute("onclick") || ""
      ].join(" ");

      let isSend = false;

      if (OPTIONS.sendSelector) {
        try {
          isSend = button.matches(OPTIONS.sendSelector);
        } catch (_) {}
      }

      isSend ||= (
        button.matches('input[type="submit"]') ||
        (
          button instanceof HTMLButtonElement &&
          button.type === "submit" &&
          Boolean(button.form)
        ) ||
        /전송|보내기|하교|\bsend\b|send[-_]?btn|send[-_]?button|sendDokdaeMessage/i.test(description)
      );

      if (!isSend) return;

      const form = button.closest("form");
      let input = getInput(STATE.lastInput || document.activeElement);

      if (form && (!input || !form.contains(input))) {
        input = getInput(
          form.querySelector("textarea,input[type=text],[contenteditable=true]")
        );
      }

      if (input) handleRequest(input, event);
    }, true);
  }

  function moveTunnelBadge() {
    for (const node of document.querySelectorAll(
      "body span,body div,body a,body button"
    )) {
      const text = node.textContent.replace(/\s+/g, "");
      if (!/^\[?5G터널추적ON\]?$/.test(text)) continue;

      if (Array.from(node.children).some(child =>
        /^\[?5G터널추적ON\]?$/.test(
          child.textContent.replace(/\s+/g, "")
        )
      )) continue;

      important(node, {
        position: "fixed",
        top: "auto",
        left: "auto",
        right: "18px",
        bottom: "18px",
        margin: "0",
        transform: "none",
        "z-index": "1000"
      });
    }
  }

  async function clearPwaState() {
    try {
      if ("serviceWorker" in navigator) {
        const registrations =
          await navigator.serviceWorker.getRegistrations();

        const results = await Promise.allSettled(
          registrations.map(registration => registration.unregister())
        );

        results.forEach(result => {
          if (result.status === "rejected") {
            console.warn("[RGON v4] 워커 해제 실패:", result.reason);
          }
        });
      }

      if ("caches" in window) {
        const names = await caches.keys();

        const results = await Promise.allSettled(
          names.map(name => caches.delete(name))
        );

        results.forEach(result => {
          if (result.status === "rejected") {
            console.warn("[RGON v4] 캐시 삭제 실패:", result.reason);
          }
        });
      }
    } catch (error) {
      console.warn("[RGON v4] PWA 초기화 확인 필요:", error);
    }
  }

  function start() {
    installStyles();
    installInterceptors();
    wrapExistingModal();
    moveTunnelBadge();
    refreshPanels();

    if ("speechSynthesis" in window) speechSynthesis.getVoices();

    clearPwaState();
    window.addEventListener("load", clearPwaState, { once: true });

    setTimeout(clearPwaState, 1000);
    setTimeout(clearPwaState, 3000);

    let scheduled = false;

    const observer = new MutationObserver(() => {
      if (scheduled) return;
      scheduled = true;

      requestAnimationFrame(() => {
        scheduled = false;
        wrapDokdaeSender();
        wrapExistingModal();
        refreshPanels();
        moveTunnelBadge();

        if (window.__LAST_AD_PAYLOAD__) {
          setFloating(window.__LAST_AD_PAYLOAD__);
        }
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    window.RGON_AD_STUDIO = {
      version: VERSION,
      build: BUILD,

      generate(topic) {
        topic = cleanTopic(topic || "");
        if (!topic) throw new Error("광고 주제가 필요합니다.");

        const payload = makePayload(topic);
        publish(payload);
        openStudio(payload);
        return payload;
      },

      open() {
        if (!window.__LAST_AD_PAYLOAD__) {
          throw new Error("먼저 광고 주제를 생성하세요.");
        }
        openStudio(window.__LAST_AD_PAYLOAD__);
      },

      close: closeStudio,
      openPanel: openCommanderPanel,

      stop() {
        STATE.activeRun?.cancel?.();
      }
    };

    console.info(
      "[RGON v4] body 직속 고정 모달 엔진 설치 완료",
      VERSION,
      BUILD
    );
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})();
'''


SW_TEMPLATE = r'''
/* __VERSION__ / __BUILD__: online-only cache reset worker */
const RGON_VERSION = "__VERSION__";
const RGON_BUILD = "__BUILD__";

self.addEventListener("install", event => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const names = await caches.keys();

    await Promise.allSettled(
      names.map(name => caches.delete(name))
    );

    await self.clients.claim();

    const windows = await self.clients.matchAll({
      type: "window",
      includeUncontrolled: true
    });

    await self.registration.unregister();

    await Promise.allSettled(windows.map(async client => {
      const url = new URL(client.url);

      if (url.origin !== self.location.origin) return;
      if (!url.pathname.endsWith("/rgon_alpha_chat.html")) return;
      if (url.searchParams.get("__rgon_ad_build") === RGON_BUILD) return;

      url.searchParams.set("__rgon_ad", RGON_VERSION);
      url.searchParams.set("__rgon_ad_build", RGON_BUILD);
      await client.navigate(url.href);
    }));
  })());
});
'''


def read_utf8(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        raise RuntimeError(
            f"UTF-8이 아닌 파일입니다: {path}\n"
            "원본 인코딩을 확인한 후 실행하세요."
        ) from error


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".rgon_ad_tmp")

    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as file:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary, path)

    finally:
        temporary.unlink(missing_ok=True)


def js_json(value: dict) -> str:
    return (
        json.dumps(value, ensure_ascii=False)
        .replace("<", r"\u003c")
        .replace(">", r"\u003e")
        .replace("&", r"\u0026")
        .replace("\u2028", r"\u2028")
        .replace("\u2029", r"\u2029")
    )


def load_config(root: Path) -> dict:
    path = root / ".rgon_ui_config.json"

    if not path.exists():
        return {}

    config = json.loads(read_utf8(path))
    if not isinstance(config, dict):
        raise RuntimeError(".rgon_ui_config.json은 JSON 객체여야 합니다.")

    keys = (
        "quant_url",
        "media_url",
        "suno_url",
        "youtube_url",
        "tiktok_url",
    )

    return {
        key: config[key]
        for key in keys
        if isinstance(config.get(key), str)
    }


def check_javascript(code: str, label: str) -> None:
    node = shutil.which("node")

    if not node:
        print(f"[문법 검사 생략] Node.js 없음: {label}")
        return

    temporary = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".js",
            encoding="utf-8",
            delete=False,
        ) as file:
            file.write(code)
            temporary = Path(file.name)

        result = subprocess.run(
            [node, "--check", str(temporary)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            check=False,
        )

        if result.returncode:
            raise RuntimeError(
                f"{label} 문법 검사 실패:\n"
                f"{result.stderr or result.stdout}"
            )

        print(f"[문법 검사 OK] {label}")

    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def patch_html(source: str, javascript: str, build: str) -> tuple[str, int]:
    removed = 0

    marker_pattern = (
        r"<!--\s*RGON_AD_STUDIO(?:_V4)?_BEGIN\s*-->.*?"
        r"<!--\s*RGON_AD_STUDIO(?:_V4)?_END\s*-->"
    )

    source, count = re.subn(
        marker_pattern,
        "",
        source,
        flags=re.I | re.S,
    )
    removed += count

    def remove_old_engine(match: re.Match) -> str:
        nonlocal removed

        attrs = match.group("attrs")
        body = match.group("body")

        is_engine_id = re.search(
            r"""\bid\s*=\s*["']rgon-ad-(?:studio|v4)-script["']""",
            attrs,
            re.I,
        )

        is_inline_engine = (
            not re.search(r"\bsrc\s*=", attrs, re.I)
            and "__RGON_AD_STUDIO_VERSION__" in body
            and "RGON_AD_STUDIO" in body
        )

        if is_engine_id or is_inline_engine:
            removed += 1
            return ""

        return match.group(0)

    source = SCRIPT_RE.sub(remove_old_engine, source)

    if "</script" in javascript.lower():
        raise RuntimeError("삽입 JavaScript에 닫는 script 태그가 있습니다.")

    block = (
        "\n<!-- RGON_AD_STUDIO_BEGIN -->\n"
        f'<script id="rgon-ad-studio-script" '
        f'data-version="{VERSION}" data-build="{build}">\n'
        f"{javascript}\n"
        "</script>\n"
        "<!-- RGON_AD_STUDIO_END -->\n"
    )

    if re.search(r"</body\s*>", source, re.I):
        patched = re.sub(
            r"</body\s*>",
            lambda _: block + "\n</body>",
            source,
            count=1,
            flags=re.I,
        )
    else:
        patched = source + block

    if patched.count('id="rgon-ad-studio-script"') != 1:
        raise RuntimeError("광고 엔진 스크립트 단일성 검증 실패")

    if patched.count("window.__RGON_AD_STUDIO_VERSION__ = VERSION") != 1:
        raise RuntimeError("구 광고 엔진 잔존 또는 중복 검증 실패")

    if "getMessageHost(" in javascript:
        raise RuntimeError("v4에 기존 채팅 컨테이너 의존 코드가 남아 있습니다.")

    return patched, removed


def find_workers(root: Path) -> list[Path]:
    workers = {root / "sw.js"}

    for current, directories, files in os.walk(root):
        directories[:] = [
            name for name in directories
            if name not in SKIP_DIRS
        ]

        if "sw.js" in files:
            workers.add(Path(current) / "sw.js")

    return sorted(workers)


def commit_with_backup(root: Path, changes: dict[Path, str]) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup = root / ".rgon_ad_backups" / stamp
    backup.mkdir(parents=True)

    manifest = []
    written = []

    for path in changes:
        relative = path.relative_to(root)
        existed = path.exists()

        manifest.append({
            "path": str(relative),
            "existed": existed,
        })

        if existed:
            destination = backup / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)

    (backup / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    try:
        for path, content in changes.items():
            written.append(path)
            atomic_write(path, content)

    except Exception:
        rollback_errors = []

        for path in reversed(written):
            original = backup / path.relative_to(root)

            try:
                if original.exists():
                    shutil.copy2(original, path)
                else:
                    path.unlink(missing_ok=True)
            except Exception as error:
                rollback_errors.append(f"{path}: {error}")

        if rollback_errors:
            print(
                "[롤백 확인 필요]\n" + "\n".join(rollback_errors),
                file=sys.stderr,
            )
        raise

    return backup


def verify_http(base_url: str, build: str) -> bool:
    routes = (
        "/rgon_alpha_chat.html",
        "/dashboard/rgon_alpha_chat.html",
        "/docs/rgon_alpha_chat.html",
        "/sw.js",
    )

    main_ok = False
    print("\n[실제 HTTP 응답 확인]")

    for route in routes:
        url = (
            base_url.rstrip("/")
            + route
            + f"?__rgon_verify={time.time_ns()}"
        )

        request = urllib.request.Request(
            url,
            headers={
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=6) as response:
                body = response.read().decode("utf-8", errors="replace")

            if VERSION in body and build in body:
                print(f"  OK   {route}")
                if route == "/rgon_alpha_chat.html":
                    main_ok = True
            else:
                print(f"  확인 필요: {route} — v4/build 표시 없음")

        except Exception as error:
            print(f"  확인 불가: {route} — {error}")

    return main_ok


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RGON 광고 스튜디오 v4: body 직속 고정 모달 패치"
    )
    parser.add_argument(
        "--root",
        default=".",
        help="프로젝트 최상위 폴더",
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8501",
        help="로컬 서버 기본 URL",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="완료 후 브라우저를 열지 않음",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    build = datetime.now().strftime("%Y%m%d%H%M%S%f")

    targets = [
        root / relative
        for relative in TARGETS
        if (root / relative).is_file()
    ]

    if not targets:
        raise RuntimeError(
            f"대상 HTML을 찾지 못했습니다: {root}\n"
            '--root "실제 프로젝트 최상위 폴더"를 지정하세요.'
        )

    print("=" * 72)
    print("RGON ALPHA · 광고 스튜디오 v4 고정 모달 업그레이드")
    print("=" * 72)
    print(f"[프로젝트] {root}")
    print(f"[VERSION] {VERSION}")
    print(f"[BUILD] {build}")
    print("[방식] 기존 채팅 DOM 미사용 / document.body 직속 고정 모달")
    print("[주의] PWA 오프라인 캐시를 해제합니다.")

    javascript = (
        JS_TEMPLATE
        .replace("__VERSION__", VERSION)
        .replace("__BUILD__", build)
        .replace("__LOCAL_CONFIG__", js_json(load_config(root)))
    )

    worker = (
        SW_TEMPLATE
        .replace("__VERSION__", VERSION)
        .replace("__BUILD__", build)
    )

    check_javascript(javascript, "광고 엔진 v4")
    check_javascript(worker, "캐시 초기화 워커")

    changes: dict[Path, str] = {}

    for path in targets:
        patched, removed = patch_html(
            read_utf8(path),
            javascript,
            build,
        )
        changes[path] = patched

        print(
            f"[HTML 준비] {path.relative_to(root)}"
            f" | 이전 광고 엔진 제거 {removed}건"
        )

    for path in find_workers(root):
        changes[path] = worker
        print(f"[워커 준비] {path.relative_to(root)}")

    backup = commit_with_backup(root, changes)

    print(f"\n[파일 패치 완료] {len(changes)}개")
    print(f"[원본 백업] {backup}")

    main_ok = verify_http(args.url, build)

    page = (
        args.url.rstrip("/")
        + "/rgon_alpha_chat.html"
        + f"?__rgon_ad={VERSION}&__rgon_ad_build={build}"
    )

    print(f"\n[열기 URL]\n{page}")

    if not args.no_open:
        webbrowser.open(page)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n사용자가 취소했습니다.")
        sys.exit(130)
    except Exception as error:
        print(f"\n[실패] {error}", file=sys.stderr)
        sys.exit(1)

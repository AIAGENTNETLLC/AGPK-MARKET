/* Workbench i18n: follow system (navigator / server LANG), override via ?lang= or UI switch. */
(function (global) {
  const STR = {
    en: {
      title: "Forgejo Workbench · AgentOS",
      brand: "Forgejo Workbench",
      badge: "ui · depends core",
      loading: "Loading…",
      checking_core: "Checking core…",
      create_repo: "Create repository",
      name: "Name",
      name_ph: "my-repo",
      description: "Description",
      desc_ph: "optional",
      private: "Private",
      btn_create: "Create via core API",
      btn_refresh: "Refresh list",
      btn_full: "Open full Forgejo (in-app)",
      tab_repos: "Repositories",
      tab_embed: "Full web (embedded)",
      col_name: "Name",
      col_private: "Private",
      col_updated: "Updated",
      detail: "Detail",
      yes: "yes",
      no: "no",
      core_up: "core up",
      core_down: "core down",
      core_reachable: "core reachable",
      core_unreachable: "core unreachable",
      token: "token",
      token_present: "present",
      token_missing: "missing",
      status_failed: "status failed",
      empty_repos: "No repositories yet — create one on the left.",
      name_required: "Name is required",
      created: "Created",
      footnote:
        "Agent automation stays on <strong>core</strong> commands (<code>forgejo.repo.*</code>). This workbench is the human desktop face — not a second Forgejo process, not xdg-open system browser as primary path.",
    },
    zh: {
      title: "Forgejo 工作台 · AgentOS",
      brand: "Forgejo 工作台",
      badge: "界面包 · 依赖 core",
      loading: "加载中…",
      checking_core: "正在检查 core…",
      create_repo: "创建仓库",
      name: "名称",
      name_ph: "我的仓库",
      description: "说明",
      desc_ph: "可选",
      private: "私有",
      btn_create: "通过 core API 创建",
      btn_refresh: "刷新列表",
      btn_full: "应用内打开完整 Forgejo",
      tab_repos: "仓库列表",
      tab_embed: "完整网页（内嵌）",
      col_name: "名称",
      col_private: "私有",
      col_updated: "更新时间",
      detail: "详情",
      yes: "是",
      no: "否",
      core_up: "core 在线",
      core_down: "core 离线",
      core_reachable: "core 可达",
      core_unreachable: "core 不可达",
      token: "令牌",
      token_present: "已配置",
      token_missing: "缺失",
      status_failed: "状态检查失败",
      empty_repos: "暂无仓库 — 请在左侧创建。",
      name_required: "请填写名称",
      created: "已创建",
      footnote:
        "Agent 自动化仍走 <strong>core</strong> 命令面（<code>forgejo.repo.*</code>）。本工作台是给人用的桌面入口——不是第二套 Forgejo 进程，也不是把 xdg-open 系统浏览器当主路径。",
    },
  };

  function normalizeLang(raw) {
    if (!raw) return null;
    const s = String(raw).toLowerCase().replace(/_/g, "-");
    if (s === "zh" || s.startsWith("zh-") || s.includes("chinese")) return "zh";
    if (s === "en" || s.startsWith("en-")) return "en";
    if (s.startsWith("c.") || s === "c" || s === "posix") return "en";
    return null;
  }

  function detectLang(serverHint) {
    const q = new URLSearchParams(location.search).get("lang");
    if (normalizeLang(q)) return normalizeLang(q);
    try {
      const stored = localStorage.getItem("forgejo_wb_lang");
      if (normalizeLang(stored)) return normalizeLang(stored);
    } catch (_) {}
    if (normalizeLang(serverHint)) return normalizeLang(serverHint);
    const nav = (navigator.languages && navigator.languages[0]) || navigator.language || "";
    return normalizeLang(nav) || "en";
  }

  let lang = "en";

  function t(key) {
    return (STR[lang] && STR[lang][key]) || STR.en[key] || key;
  }

  function apply() {
    document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const k = el.getAttribute("data-i18n");
      if (k) el.textContent = t(k);
    });
    document.querySelectorAll("[data-i18n-html]").forEach((el) => {
      const k = el.getAttribute("data-i18n-html");
      if (k) el.innerHTML = t(k);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const k = el.getAttribute("data-i18n-placeholder");
      if (k) el.setAttribute("placeholder", t(k));
    });
    const title = document.querySelector("title[data-i18n], title");
    if (title) title.textContent = t("title");
    const zhBtn = document.getElementById("lang-zh");
    const enBtn = document.getElementById("lang-en");
    if (zhBtn) zhBtn.classList.toggle("active", lang === "zh");
    if (enBtn) enBtn.classList.toggle("active", lang === "en");
    try {
      localStorage.setItem("forgejo_wb_lang", lang);
    } catch (_) {}
  }

  function setLang(next) {
    lang = normalizeLang(next) || "en";
    apply();
    if (typeof global.onForgejoLangChange === "function") {
      global.onForgejoLangChange(lang);
    }
  }

  function init(serverHint) {
    lang = detectLang(serverHint);
    apply();
    const zhBtn = document.getElementById("lang-zh");
    const enBtn = document.getElementById("lang-en");
    if (zhBtn) zhBtn.addEventListener("click", () => setLang("zh"));
    if (enBtn) enBtn.addEventListener("click", () => setLang("en"));
  }

  global.ForgejoI18n = { t, setLang, init, getLang: () => lang, STR };
})(window);

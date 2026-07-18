/* Forgejo AgentOS workbench — local proxy; UI strings via i18n (system / 中文 / EN). */
async function api(path, opts = {}) {
  const r = await fetch(path, {
    headers: { Accept: "application/json", ...(opts.body ? { "Content-Type": "application/json" } : {}) },
    ...opts,
  });
  const text = await r.text();
  let body;
  try {
    body = JSON.parse(text);
  } catch {
    body = { raw: text };
  }
  if (!r.ok) throw new Error(body.error || body.message || text || r.status);
  return body;
}

function $(id) {
  return document.getElementById(id);
}
function t(k) {
  return window.ForgejoI18n ? ForgejoI18n.t(k) : k;
}

function showMsg(text, ok) {
  const el = $("msg");
  el.className = ok ? "ok" : "err";
  el.textContent = text || "";
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

async function loadStatus() {
  try {
    const s = await api("/api/local/status");
    if (window.ForgejoI18n && !localStorage.getItem("forgejo_wb_lang") && !new URLSearchParams(location.search).get("lang")) {
      // honor host LANG/LC_* from workbench server when user has not chosen
      if (s.system_locale) {
        const loc = String(s.system_locale).toLowerCase();
        if (loc.startsWith("zh")) ForgejoI18n.setLang("zh");
        else if (loc && !loc.startsWith("c") && loc !== "posix") {
          /* keep navigator-based lang from init() */
        }
      }
    }
    $("hdr-meta").textContent = `${s.core_url || "?"} · ${s.core_reachable ? t("core_up") : t("core_down")}`;
    const st = $("core-status");
    st.className = "status" + (s.core_reachable ? "" : " bad");
    st.innerHTML = s.core_reachable
      ? `<strong>${esc(t("core_reachable"))}</strong><br/>${esc(s.core_url)}<br/>${esc(t("token"))}: ${s.has_token ? t("token_present") : t("token_missing")}`
      : `<strong>${esc(t("core_unreachable"))}</strong><br/>${esc(s.core_url || "")}<br/>${esc(s.detail || "")}`;
    $("forge-frame").src = s.core_url || "about:blank";
    return s;
  } catch (e) {
    $("core-status").className = "status bad";
    $("core-status").innerHTML = `<strong>${esc(t("status_failed"))}</strong><br/>${esc(String(e.message || e))}`;
  }
}

async function refreshRepos() {
  const body = $("repo-body");
  body.innerHTML = `<tr><td colspan="4">${esc(t("loading"))}</td></tr>`;
  try {
    const data = await api("/api/proxy/user/repos?limit=50");
    const repos = Array.isArray(data) ? data : data.repos || data.data || [];
    if (!repos.length) {
      body.innerHTML = `<tr><td colspan="4">${esc(t("empty_repos"))}</td></tr>`;
      return;
    }
    body.innerHTML = repos
      .map((r) => {
        const name = r.full_name || r.name;
        const priv = r.private ? t("yes") : t("no");
        const updated = (r.updated_at || "").replace("T", " ").slice(0, 19);
        return `<tr>
        <td>${esc(name)}</td>
        <td>${esc(priv)}</td>
        <td>${esc(updated)}</td>
        <td><a href="#" data-owner="${esc(r.owner?.login || r.owner?.username || "")}" data-repo="${esc(r.name)}">${esc(t("detail"))}</a></td>
      </tr>`;
      })
      .join("");
    body.querySelectorAll("a[data-repo]").forEach((a) => {
      a.addEventListener("click", async (ev) => {
        ev.preventDefault();
        const owner = a.getAttribute("data-owner");
        const repo = a.getAttribute("data-repo");
        try {
          const d = await api(`/api/proxy/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}`);
          $("repo-detail").innerHTML = `<h3 style="margin:0 0 8px;font-size:14px">${esc(d.full_name || repo)}</h3>
            <div class="status">id=${d.id} private=${d.private} default_branch=${esc(d.default_branch || "")}<br/>
            clone=${esc(d.clone_url || "")}<br/>html=${esc(d.html_url || "")}</div>`;
        } catch (e) {
          $("repo-detail").innerHTML = `<div class="err">${esc(String(e.message || e))}</div>`;
        }
      });
    });
  } catch (e) {
    body.innerHTML = `<tr><td colspan="4" class="err">${esc(String(e.message || e))}</td></tr>`;
  }
}

async function createRepo() {
  const name = $("repo-name").value.trim();
  if (!name) {
    showMsg(t("name_required"), false);
    return;
  }
  $("btn-create").disabled = true;
  try {
    const body = {
      name,
      description: $("repo-desc").value.trim(),
      private: $("repo-private").checked,
      auto_init: true,
      default_branch: "main",
    };
    const r = await api("/api/proxy/user/repos", { method: "POST", body: JSON.stringify(body) });
    showMsg(`${t("created")} ${r.full_name || name}`, true);
    $("repo-name").value = "";
    await refreshRepos();
  } catch (e) {
    showMsg(String(e.message || e), false);
  } finally {
    $("btn-create").disabled = false;
  }
}

function showTab(which) {
  $("panel-repos").style.display = which === "repos" ? "block" : "none";
  $("panel-embed").style.display = which === "embed" ? "block" : "none";
}

$("btn-refresh").addEventListener("click", () => refreshRepos());
$("btn-create").addEventListener("click", () => createRepo());
$("btn-full").addEventListener("click", () => showTab("embed"));
$("tab-repos").addEventListener("click", () => showTab("repos"));
$("tab-embed").addEventListener("click", () => showTab("embed"));

window.onForgejoLangChange = function () {
  loadStatus().then(() => refreshRepos());
};

// init i18n immediately (navigator), refine after status with system_locale
if (window.ForgejoI18n) ForgejoI18n.init();
loadStatus().then(() => refreshRepos());

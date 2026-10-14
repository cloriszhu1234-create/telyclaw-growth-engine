"use strict";
let state, analysis, currentDraft;
let liveStatus;
let modeVersion = 0;
let dirty = false;
const $ = (id) => document.getElementById(id);
const escapeHTML = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const e = escapeHTML;
const dateLabel = (value) =>
  new Date(value).toLocaleString("en-GB", {
    timeZone: "Asia/Shanghai",
    dateStyle: "medium",
    timeStyle: "short",
  }) + " CST";
let toastTimer;
function toast(message, error = false) {
  $("toast").textContent = message;
  $("toast").className = error ? "error" : "";
  $("toast").style.display = "block";
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => ($("toast").style.display = "none"), 6000);
}
async function api(path, method = "GET", body) {
  const response = await fetch("/api/" + path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json();
  if (!response.ok)
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : data.detail?.message ||
          (Array.isArray(data.detail)
            ? data.detail
                .map((item) => item.loc.slice(1).join(".") + ": " + item.msg)
                .join("; ")
            : JSON.stringify(data.detail || data)),
    );
  return data;
}
function tab(name) {
  document
    .querySelectorAll(".view")
    .forEach((v) => v.classList.toggle("hidden", v.id !== name));
  document
    .querySelectorAll(".nav")
    .forEach((v) => v.classList.toggle("active", v.dataset.tab === name));
  $("page-name").textContent = {
    opportunities: "Opportunities",
    review: "Content studio",
    sources: "Sources & settings",
  }[name];
}
document
  .querySelectorAll(".nav")
  .forEach((button) => (button.onclick = () => tab(button.dataset.tab)));
async function refresh() {
  state = await api("state");
  $("draft-count").textContent = state.drafts.length;
  $("account-list").innerHTML =
    state.accounts
      .map(
        (a) =>
          `<div class="account-row"><input type="checkbox" aria-label="Monitor ${e(a.handle)}" data-handle="${e(a.handle)}" ${a.enabled ? "checked" : ""}><span>@${e(a.handle)}</span><button data-remove="${e(a.handle)}">Remove</button></div>`,
      )
      .join("") || "<p>No accounts. Add an account to begin.</p>";
  $("account-list")
    .querySelectorAll("input")
    .forEach(
      (input) =>
        (input.onchange = async () => {
          try {
            await api("accounts", "POST", {
              handle: input.dataset.handle,
              enabled: input.checked,
            });
            toast("Source selection saved. Run a new analysis to apply.");
          } catch (err) {
            input.checked = !input.checked;
            toast(err.message, true);
          }
        }),
    );
  $("account-list")
    .querySelectorAll("button")
    .forEach(
      (button) =>
        (button.onclick = async () => {
          try {
            await api("accounts/" + button.dataset.remove, "DELETE");
            await refresh();
            toast(
              "Account removed. Existing evidence snapshots are preserved.",
            );
          } catch (err) {
            toast(err.message, true);
          }
        }),
    );
  $("positioning").value = state.brief.positioning;
  $("audience").value = state.brief.audience;
  $("keywords").value = state.brief.keywords.join(", ");
  $("import-count").textContent =
    state.imported_posts +
    " imported posts stored. Choose Imported posts on the radar to analyze them.";
  await refreshManual();
  renderDrafts();
  updateClock();
}
function updateClock() {
  const mode = $("mode").value;
  $("mode-label").textContent = {
    demo: "DEMO WORKSPACE",
    live: "LIVE X · CACHED DATA",
    imported: "JSON IMPORTS",
    manual: "MANUAL IMPORTS",
  }[mode];
  $("live-panel").classList.toggle("hidden", mode !== "live");
  $("sample-warning").classList.toggle("hidden", mode !== "manual");
  if (mode === "manual")
    $("sample-warning").textContent =
      analysis?.mode === "manual"
        ? analysis.sample_warning || analysis.source_warning
        : "Manually selected posts form a limited, unverified sample. Analyze to check coverage for the selected time window.";
  $("posts-scope").textContent =
    mode === "live"
      ? "Cached posts for selected username"
      : "Filtered to enabled accounts";
  $("clock").textContent =
    mode === "demo"
      ? "Scenario clock: " + dateLabel(state.demo_clock)
      : "Current time · " +
        (mode === "live" ? "cached X posts" : "imported posts");
  $("provenance").textContent = {
    demo: "Fictional accounts, synthetic posts and engagement. No live X connection.",
    imported:
      "User-imported posts. Accuracy is not independently verified. No live X connection.",
    manual:
      "Manually entered X posts. Text, timestamps and metrics are unverified. No scraping or API requests.",
    live: "Official X API cache only. No automatic fetch, no synthetic fallback, no platform-wide trend claim.",
  }[mode];
}
async function inspectLive() {
  const handle = $("live-username").value;
  try {
    const result = await api("x/status?username=" + encodeURIComponent(handle));
    if (handle !== $("live-username").value) return;
    liveStatus = result;
    renderLive();
  } catch (err) {
    $("live-status").textContent = err.message;
    $("live-status").className = "error";
  }
}
function renderLive() {
  if (!liveStatus) return;
  const value = liveStatus;
  $("live-status").textContent = value.message;
  $("live-status").className = ["ready", "cached", "success", "empty"].includes(
    value.code,
  )
    ? ""
    : "error";
  $("live-facts").innerHTML =
    `<span>Account: @${e(value.username)}</span><span>Last successful fetch: ${value.last_fetch ? e(dateLabel(value.last_fetch)) : "Never"}</span><span>Last response: ${value.last_retrieved} posts</span><span>Cached: ${value.cached_posts} unique posts (${value.cache_fresh ? "fresh" : "stale or empty"})</span><span>Request budget: ${value.requests_used} / ${value.request_cap} used</span>${value.next_fetch_at ? `<span>Next network fetch after: ${e(dateLabel(value.next_fetch_at))}</span>` : ""}`;
}
$("mode").onchange = () => {
  modeVersion++;
  updateClock();
  clearAnalysis();
  if ($("mode").value === "live") inspectLive();
};
$("live-username").onchange = () => {
  modeVersion++;
  clearAnalysis();
  inspectLive();
};
$("fetch-x").onclick = async () => {
  const handle = $("live-username").value;
  $("fetch-x").disabled = true;
  $("live-username").disabled = true;
  $("live-status").textContent =
    "Fetching manually from X… No automatic retry will run.";
  $("live-status").className = "";
  try {
    liveStatus = await api("x/fetch", "POST", {
      username: handle,
      limit: Number($("live-limit").value),
    });
    renderLive();
    clearAnalysis();
    toast(liveStatus.message + " Click Analyze signals to use the cache.");
  } catch (err) {
    await inspectLive();
    $("live-status").textContent =
      err.message +
      " Any existing X cache is preserved; no demo data was substituted.";
    $("live-status").className = "error";
  } finally {
    $("fetch-x").disabled = false;
    $("live-username").disabled = false;
  }
};
$("window").onchange = () => {
  modeVersion++;
  clearAnalysis();
};
function clearAnalysis() {
  analysis = null;
  updateClock();
  $("topic-list").innerHTML =
    '<div class="empty">Selection changed. Analyze signals to refresh results.</div>';
  $("detail").innerHTML =
    '<div class="empty">Select a trend after analyzing.</div>';
  ["posts", "accounts", "trends"].forEach((id) => ($(id).textContent = "—"));
  $("run-status").textContent = "New analysis required";
}
$("analyze").onclick = async () => {
  $("analyze").disabled = true;
  $("analyze").textContent = "Analyzing…";
  const version = modeVersion;
  try {
    const result = await api("analyze", "POST", {
      hours: Number($("window").value),
      mode: $("mode").value,
      username:
        $("mode").value === "live" ? $("live-username").value : "elonmusk",
    });
    if (version !== modeVersion) return;
    analysis = result;
    updateClock();
    $("posts").textContent = analysis.post_count;
    $("accounts").textContent = analysis.account_count;
    $("trends").textContent = analysis.topics.length;
    $("run-status").textContent =
      "Run completed · " + dateLabel(analysis.analyzed_at);
    $("topic-list").innerHTML =
      analysis.topics
        .map(
          (t) =>
            `<button class="topic" data-topic="${e(t.id)}"><div class="topic-top"><span>${t.top ? "↗ TOP " + t.rank : "SIGNAL " + t.rank}${!t.recommended ? " · LOW RELEVANCE" : ""}</span><span class="score">${t.score}<small> / 100</small></span></div><h3>${e(t.title)}</h3><p>${e(t.summary)}</p><div class="topic-meta"><span>◎ ${t.authors.length} accounts</span><span>▤ ${t.evidence.length} unique posts</span><span>${t.momentum === null ? "No baseline" : (t.momentum > 0 ? "+" : "") + t.momentum + "% momentum"}</span></div></button>`,
        )
        .join("") ||
      '<div class="empty">No eligible posts in this window. For Live X, fetch manually when access is enabled, then analyze the cache. Otherwise enable accounts, choose a wider window, or import recent data.</div>';
    $("topic-list")
      .querySelectorAll("button")
      .forEach(
        (button) => (button.onclick = () => selectTopic(button.dataset.topic)),
      );
    if (analysis.mode === "live") {
      liveStatus = analysis.live_status;
      renderLive();
    }
    if (analysis.topics.length) selectTopic(analysis.topics[0].id);
    else
      $("detail").innerHTML =
        '<div class="empty">No topics yet. Adjust your sources or time window.</div>';
  } catch (err) {
    toast(err.message, true);
  } finally {
    $("analyze").disabled = false;
    $("analyze").textContent = "✳ Analyze signals";
  }
};
function sourceLink(p) {
  // Build links from validated IDs/handles, never an arbitrary imported href.
  return ["live_x", "manual_x"].includes(p.provenance) &&
    /^\d+$/.test(p.x_id || "") &&
    /^[a-z0-9_]{1,15}$/i.test(p.handle)
    ? `https://x.com/${p.handle}/status/${p.x_id}`
    : null;
}
function evidenceHTML(p) {
  const link = sourceLink(p);
  const flags =
    p.provenance === "live_x"
      ? [
          p.post_type,
          p.is_reply && p.post_type !== "reply" ? "also reply" : null,
          p.is_quote && p.post_type !== "quote" ? "also quote" : null,
        ]
          .filter(Boolean)
          .join(" / ")
      : p.provenance === "manual_x"
        ? "Manual · unverified"
        : p.provenance;
  return `<div class="evidence"><strong>@${e(p.handle)}${p.provenance === "live_x" ? " timeline" : ""}</strong> <span class="tag">${e(flags)}</span><p>${e(p.text)}</p><small>${e(dateLabel(p.created_at))} · ${p.likes ?? "N/A"} likes · ${p.reposts ?? "N/A"} reposts · ${p.replies ?? "N/A"} replies · ${e(p.provenance)}</small>${link ? `<div class="source-links"><a href="${e(link)}" target="_blank" rel="noopener noreferrer">Original X post ↗</a></div>` : ""}</div>`;
}
function selectTopic(id) {
  const t = analysis.topics.find((t) => t.id === id);
  document
    .querySelectorAll(".topic")
    .forEach((b) => b.classList.toggle("selected", b.dataset.topic === id));
  $("detail").innerHTML =
    `<div class="detail-label">OPPORTUNITY BRIEF · ${analysis.mode === "demo" ? "SYNTHETIC EVIDENCE" : analysis.mode === "live" ? "LIVE X CACHE" : analysis.mode === "manual" ? "MANUAL · UNVERIFIED" : "JSON IMPORTS"}</div><h2>${e(t.title)}</h2><div class="summary">${e(t.summary)}<br><small class="subtle">${e(t.summary_method)}</small></div><h4>Why this is worth a look</h4><p>${e(t.reason)}</p>${analysis.source_warning ? `<p class="source-warning">${e(analysis.source_warning)}</p>` : ""}<h4>Opportunity score <span class="tag">${t.score} / 100</span></h4>${Object.entries(
      t.factors,
    )
      .map(
        ([k, v]) =>
          `<div class="factor"><span>${e(k)} · ${Math.round(t.weights[k] * 100)}%</span><div class="bar"><i style="width:${v ?? 0}%"></i></div><b>${v ?? "N/A"}</b></div>`,
      )
      .join(
        "",
      )}<p class="subtle">Weighted heuristic, not a prediction. Relevance uses your brand keywords. Source engagement = likes + 2×reposts + 2×replies.</p><details><summary>Inspect ${t.evidence.length} source posts & methodology</summary><p>TF-IDF similarity clustering, exact-text deduplication and representative-source summaries. Previous equal window: ${t.prior_count} matching posts. Similarity may merge or split topics incorrectly.</p>${t.evidence.map(evidenceHTML).join("")}</details><button class="primary" id="generate">Create angles & draft →</button><p class="subtle">Local editorial templates by default; optional OpenAI configuration. Human approval required.</p>`;
  $("generate").onclick = async () => {
    $("generate").disabled = true;
    $("generate").textContent = "Preparing draft…";
    try {
      currentDraft = await api("drafts", "POST", {
        analysis_id: analysis.id,
        topic_id: id,
      });
      await refresh();
      renderEditor();
      tab("review");
      toast("Three angles and a draft are ready for your review.");
    } catch (err) {
      toast(err.message, true);
    } finally {
      if ($("generate")) {
        $("generate").disabled = false;
        $("generate").textContent = "Create angles & draft →";
      }
    }
  };
}
function renderDrafts() {
  $("draft-list").innerHTML =
    state.drafts
      .map(
        (d) =>
          `<button class="draft-card" data-draft="${e(d.id)}"><span class="status ${d.status}">${e(d.status)}</span><strong>${e(d.topic_title)}</strong><small class="subtle">${d.mode === "demo" ? "Synthetic signal" : d.mode === "live" ? "Live X signal" : d.mode === "manual" ? "Manual X signal" : "Imported signal"} · ${e(dateLabel(d.created_at))}</small></button>`,
      )
      .join("") ||
    '<div class="empty">No drafts yet. Start with the trend radar.</div>';
  $("draft-list")
    .querySelectorAll("button")
    .forEach(
      (b) =>
        (b.onclick = () => {
          if (dirty && !confirm("Discard unsaved draft edits?")) return;
          currentDraft = state.drafts.find((d) => d.id === b.dataset.draft);
          renderEditor();
        }),
    );
}
function renderEditor() {
  if (!currentDraft) return;
  dirty = false;
  const d = currentDraft;
  $("editor").innerHTML =
    `<span class="status ${d.status}" id="draft-status">${e(d.status)}</span><h2>${e(d.topic_title)}</h2><p>${e(d.provider)} · ${e(d.mode)} source data</p>${d.source_warning ? `<p>${e(d.source_warning)}</p>` : ""}${(
      d.sources || []
    )
      .filter(
        (p) =>
          ["live_x", "manual_x"].includes(p.provenance) &&
          /^https:\/\/x\.com\/[a-z0-9_]+\/status\/\d+$/i.test(p.url || ""),
      )
      .map(
        (p) =>
          `<p class="source-links"><a href="${e(p.url)}" target="_blank" rel="noopener noreferrer">Source: @${e(p.handle)} (${e(p.post_type)}) ↗</a></p>`,
      )
      .join(
        "",
      )}<h4>Three ways into the conversation</h4>${d.angles.map((a) => `<div class="angle"><strong>${e(a.type)}</strong><p>${e(a.idea)}</p></div>`).join("")}<label for="draft-text">Your X post</label><textarea id="draft-text" rows="6" maxlength="280">${e(d.text)}</textarea><div class="editor-tools"><span id="save-state">Saved · ${d.approved_at ? "Approved " + e(dateLabel(d.approved_at)) : "Review claims and positioning before approval"}</span><span id="char-count">${d.text.length} / 280</span></div><p>Draft suggestions are labeled by provider and are not verified TelyClaw product claims. Check the source, add your expertise, and confirm the angle fits your audience. MVP export supports ASCII text without URLs.</p><div class="actions"><button class="secondary" id="save-draft">Save changes</button><button class="primary" id="approve-draft">Approve post</button><a class="secondary ${d.status !== "approved" ? "hidden" : ""}" id="export-draft" href="/api/drafts/${e(d.id)}/export">Export approved text ↗</a></div><p class="subtle">Export downloads text for manual publishing. Nothing is posted to X by this application. Editing approved text requires approval again.</p>`;
  $("draft-text").oninput = () => {
    dirty = true;
    $("char-count").textContent = $("draft-text").value.length + " / 280";
    $("save-state").textContent = "Unsaved changes · Approval required";
    $("export-draft").classList.add("hidden");
    $("draft-status").textContent = "Edited";
  };
  $("save-draft").onclick = () => saveDraft(false);
  $("approve-draft").onclick = () => saveDraft(true);
}
async function saveDraft(approve) {
  $("save-draft").disabled = true;
  $("approve-draft").disabled = true;
  try {
    currentDraft = await api("drafts/" + currentDraft.id, "PUT", {
      text: $("draft-text").value,
    });
    if (approve)
      currentDraft = await api(
        "drafts/" + currentDraft.id + "/approve",
        "POST",
      );
    await refresh();
    renderEditor();
    toast(
      approve
        ? "Approved. Export is ready for manual publishing."
        : "Saved. Any changed text needs fresh approval.",
    );
  } catch (err) {
    toast(err.message, true);
  } finally {
    if ($("save-draft")) {
      $("save-draft").disabled = false;
      $("approve-draft").disabled = false;
    }
  }
}
async function refreshManual() {
  const data = await api("manual/posts");
  $("manual-count").textContent =
    `${data.total} saved posts. Showing the latest ${data.posts.length}. Select Manual Imports on the radar to analyze enabled accounts.`;
  $("manual-list").innerHTML =
    data.posts.map(evidenceHTML).join("") ||
    "<p>No manual posts yet. Add posts from different accounts to compare topics.</p>";
}
$("manual-form").onsubmit = async (event) => {
  event.preventDefault();
  $("save-manual").disabled = true;
  $("manual-result").textContent = "Saving locally…";
  $("manual-result").className = "";
  try {
    const metric = (id) => ($(id).value === "" ? null : Number($(id).value));
    const result = await api("manual/posts", "POST", {
      url: $("manual-url").value,
      handle: $("manual-handle").value,
      text: $("manual-text").value,
      created_at: new Date($("manual-time").value + "+08:00").toISOString(),
      likes: metric("manual-likes"),
      reposts: metric("manual-reposts"),
      replies: metric("manual-replies"),
    });
    [
      "manual-url",
      "manual-text",
      "manual-time",
      "manual-likes",
      "manual-reposts",
      "manual-replies",
    ].forEach((id) => ($(id).value = ""));
    modeVersion++;
    clearAnalysis();
    await refresh();
    $("manual-result").textContent = result.message;
    toast(result.message);
  } catch (err) {
    $("manual-result").textContent = err.message;
    $("manual-result").className = "error";
  } finally {
    $("save-manual").disabled = false;
  }
};
$("add-account").onsubmit = async (event) => {
  event.preventDefault();
  try {
    await api("accounts", "POST", { handle: $("handle").value, enabled: true });
    $("handle").value = "";
    await refresh();
    toast("Account added. Import posts for new handles to analyze them.");
  } catch (err) {
    toast(err.message, true);
  }
};
$("brief-form").onsubmit = async (event) => {
  event.preventDefault();
  try {
    await api("brief", "PUT", {
      positioning: $("positioning").value,
      audience: $("audience").value,
      keywords: $("keywords")
        .value.split(",")
        .map((s) => s.trim())
        .filter(Boolean),
    });
    await refresh();
    toast("Brand brief saved. Run a new analysis to apply.");
  } catch (err) {
    toast(err.message, true);
  }
};
$("import").onclick = async () => {
  const file = $("import-file").files[0];
  if (!file) return toast("Choose a JSON file first.", true);
  if (file.size > 6_000_000) return toast("File must be under 6 MB.", true);
  $("import").disabled = true;
  try {
    const result = await api("import", "POST", JSON.parse(await file.text()));
    await refresh();
    toast(
      result.imported + " posts imported. Select Imported posts on the radar.",
    );
  } catch (err) {
    toast(err.message, true);
  } finally {
    $("import").disabled = false;
  }
};
window.addEventListener("beforeunload", (event) => {
  if (dirty) {
    event.preventDefault();
    event.returnValue = "";
  }
});
refresh()
  .then(() => $("analyze").click())
  .catch((err) => toast("Could not load workspace: " + err.message, true));

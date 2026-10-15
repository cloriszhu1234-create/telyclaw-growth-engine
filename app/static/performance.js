"use strict";
let performanceData;
const metricNames = {
  impressions: "Views / impressions",
  likes: "Likes",
  reposts: "Reposts",
  replies: "Replies",
  bookmarks: "Bookmarks",
  link_clicks: "Link clicks",
  profile_visits: "Profile visits",
  attributed_followers: "Post-attributed followers",
};
const measured = (value) =>
  value === null || value === undefined
    ? "Not measured"
    : Number(value).toLocaleString();
function cstInput(value = new Date()) {
  return new Date(value)
    .toLocaleString("sv-SE", {
      timeZone: "Asia/Shanghai",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hourCycle: "h23",
    })
    .replace(" ", "T");
}
async function loadPerformance(selectId) {
  performanceData = await api("performance");
  const data = performanceData,
    a = data.aggregate;
  $("performance-formula").textContent = data.formula;
  $("performance-warning").textContent = data.warning;
  $("performance-totals").innerHTML =
    `<article><span>Published records</span><strong>${a.posts}</strong><small>${a.measured_posts} with measured metrics</small></article><article><span>Total measured engagement</span><strong>${measured(a.total_engagement)}</strong><small>${a.engagement_complete ? "All four counts available" : "Partial / unmeasured counts; not qualified by default"}</small></article><article><span>Engagement rate</span><strong>${a.engagement_rate === null ? "Not measured" : a.engagement_rate + "%"}</strong><small>${a.rate_posts} posts with paired positive impressions</small></article><article><span>Measured impressions</span><strong>${measured(a.totals.impressions)}</strong><small>${a.metric_coverage.impressions} / ${a.posts} posts measured</small></article>`;
  if ($("performance-outcomes"))
    $("performance-outcomes").innerHTML = Object.entries(metricNames)
      .map(
        ([key, label]) =>
          `<p>${e(label)}: <strong>${measured(a.totals[key])}</strong> · ${a.metric_coverage[key]} / ${a.posts} posts measured</p>`,
      )
      .join("");
  $("performance-topics").innerHTML = data.topics.length
    ? `<div class="topic-performance">${data.topics.map((t) => `<article class="panel"><h3>${e(t.title)}</h3><p>${t.posts} published posts · ${t.measured_posts} with metrics</p><p>Engagement: ${measured(t.total_engagement)} ${t.engagement_complete ? "" : "(partial / incomplete)"}<br>Rate: ${t.engagement_rate === null ? "Not measured" : t.engagement_rate + "%"} (${t.rate_posts} paired posts)</p></article>`).join("")}</div><p class="subtle">Compare topics using consistent measurement windows and audience quality. These observational totals do not prove that a topic caused growth.</p>`
    : "<p>No topic outcomes yet. Publication and measurement records will appear here.</p>";
  $("publication-list").innerHTML = data.posts
    .map(
      (p) =>
        `<button class="draft-card" data-publication="${e(p.id)}"><span class="status published">Published · manual</span><small>Source mode: ${e(p.mode)}</small><strong>${e(p.topic_title)}</strong><small>${e(dateLabel(p.published_at))}</small><p>${measured(p.calculated.total_engagement)} engagement · ${p.metrics.measured_at ? "Updated " + e(dateLabel(p.metrics.measured_at)) : "Not measured"}</p></button>`,
    )
    .join("");
  $("publication-list")
    .querySelectorAll("button")
    .forEach(
      (b) =>
        (b.onclick = () =>
          measurementEditor(
            data.posts.find((p) => p.id === b.dataset.publication),
          )),
    );
  if (data.posts.length)
    measurementEditor(
      data.posts.find((p) => p.id === selectId) || data.posts[0],
    );
}
function measurementEditor(post) {
  const m = post.metrics;
  const field = (key) =>
    `<div><label for="metric-${key}">${e(metricNames[key])}</label><input id="metric-${key}" type="number" min="0" max="100000000000" step="1" placeholder="Not measured" value="${m[key] ?? ""}"></div>`;
  $("measurement-editor").innerHTML =
    `<h2>${e(post.topic_title)}</h2><p><a href="${e(post.url)}" target="_blank" rel="noopener noreferrer">Published X post ↗</a> · ${e(dateLabel(post.published_at))}</p><p>${e(post.provenance)} · Source mode: ${e(post.mode)}</p><details><summary>Approved published text</summary><p>${e(post.text)}</p></details><h3>Record cumulative metrics</h3><p>Enter actual observed totals, not increments. Blank means Not measured. A new snapshot replaces the previous snapshot for totals; history is kept.</p><form id="metrics-form"><label for="measured-time">Measurement time (Asia/Shanghai, UTC+08:00)</label><input id="measured-time" type="datetime-local" step="1" required value="${cstInput()}"><div class="manual-metrics">${["impressions", "likes", "reposts", "replies", "bookmarks"].map(field).join("")}</div><details ${(m.link_clicks !== undefined && m.link_clicks !== null) || (m.profile_visits !== undefined && m.profile_visits !== null) || (m.attributed_followers !== undefined && m.attributed_followers !== null) ? "open" : ""}><summary>Optional outcomes and attribution</summary><div class="manual-metrics">${["link_clicks", "profile_visits", "attributed_followers"].map(field).join("")}</div><p>Account-level follower growth is not attributable to this post. Leave post-attributed followers blank unless you have reliable post-level evidence, including for a zero value.</p><label for="attribution-evidence">Attribution evidence (required for post-attributed followers)</label><textarea id="attribution-evidence" maxlength="2000">${e(m.attribution_evidence || "")}</textarea></details><button class="primary" id="save-metrics">Save measurement</button><p id="metric-result" role="status"></p></form><h4>Latest outcome</h4><p>Engagement: ${measured(post.calculated.total_engagement)} ${post.calculated.engagement_complete ? "" : "(partial / unmeasured)"} · Rate: ${post.calculated.engagement_rate === null ? "Not measured" : post.calculated.engagement_rate + "%"}</p><details><summary>Measurement history (${post.snapshots.length} snapshots)</summary>${
      post.snapshots
        .map(
          (s) =>
            `<div class="evidence"><strong>${e(dateLabel(s.measured_at))}</strong><p>${Object.keys(
              metricNames,
            )
              .map((k) => e(metricNames[k]) + ": " + measured(s[k]))
              .join(" · ")}</p></div>`,
        )
        .join("") || "<p>No measurements yet.</p>"
    }</details>`;
  $("metrics-form").onsubmit = async (event) => {
    event.preventDefault();
    $("save-metrics").disabled = true;
    try {
      const payload = {
        measured_at: new Date(
          $("measured-time").value + "+08:00",
        ).toISOString(),
        attribution_evidence: $("attribution-evidence").value || null,
      };
      Object.keys(metricNames).forEach(
        (k) =>
          (payload[k] =
            $("metric-" + k).value === ""
              ? null
              : Number($("metric-" + k).value)),
      );
      await api("publications/" + post.id + "/measurements", "POST", payload);
      await loadPerformance(post.id);
      toast(
        "Real metric snapshot saved. Aggregates use only the latest snapshot per post.",
      );
    } catch (err) {
      $("metric-result").textContent = err.message;
      $("save-metrics").disabled = false;
    }
  };
}

let personId = "P-001";
let roles = [];

const $ = (id) => document.getElementById(id);

async function api(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function boot() {
  try {
    const health = await api("/api/health");
    $("health").textContent = health.ok
      ? "● CognoDB connected"
      : "● Database unavailable";
    $("health").style.color = health.ok ? "#0d8a63" : "#b26a00";
  } catch (e) {
    $("health").textContent = "● Database unavailable";
  }

  roles = await api("/api/roles");
  $("roleSelect").innerHTML = roles
    .map((r) => `<option value="${r.id}">${r.title}</option>`)
    .join("");

  await loadPerson();
  await selectRole(roles[0]?.id);
}

async function loadPerson() {
  const p = await api(`/api/profile/${personId}`);
  $("personName").textContent = p.name;
  $("personHeadline").textContent = p.headline;
  $("stats").innerHTML = `
    <div class="stat"><b>${p.skills.length}</b><span>skills in profile</span></div>
    <div class="stat"><b>${p.targets.length}</b><span>target role</span></div>
    <div class="stat"><b>${roles.length}</b><span>roles in graph</span></div>`;

  renderRecommendations(
    await api(`/api/profile/${personId}/recommendations`)
  );
  renderGraph(await api(`/api/profile/${personId}/graph`));
}

function renderRecommendations(items) {
  const el = $("recommendations");
  el.className = "role-list";
  el.innerHTML = items
    .map(
      (r, i) => `
      <div class="role ${i === 0 ? "active" : ""}" data-role="${r.id}">
        <div class="role-top">
          <div>
            <div class="role-title">${r.title}</div>
            <div class="role-meta">${r.level} · ${r.overlap}/${r.total_required} required skills</div>
          </div>
          <span class="score">${r.match_percent}% fit</span>
        </div>
      </div>`
    )
    .join("");

  el.querySelectorAll(".role").forEach(
    (x) => (x.onclick = () => selectRole(x.dataset.role))
  );
}

async function selectRole(roleId) {
  if (!roleId) return;
  $("roleSelect").value = roleId;
  const role = roles.find((r) => r.id === roleId);
  $("gapTitle").textContent = role ? role.title : "Skill gap";
  $("gaps").className = "gap-list loading";
  $("gaps").textContent = "Tracing skill gaps…";
  $("learning").className = "learning-list loading";
  $("learning").textContent = "Following the graph…";

  try {
    const [gaps, learning] = await Promise.all([
      api(`/api/profile/${personId}/gaps/${roleId}`),
      api(`/api/profile/${personId}/learning-path/${roleId}`),
    ]);

    $("gaps").className = "gap-list";
    $("gaps").innerHTML = gaps.length
      ? gaps
          .map(
            (g) => `
          <div class="gap">
            <div><div class="gap-name">${g.skill}</div><div class="category">${g.category}</div></div>
            <span class="score">learn</span>
          </div>`
          )
          .join("")
      : `<div class="empty">No gaps — this profile already covers the role's required skills.</div>`;

    $("learning").className = "learning-list";
    $("learning").innerHTML = learning.length
      ? learning
          .map((x) => {
            const r = (x.resources || [])[0];
            return `<div class="resource">
              <div><div class="gap-name">${x.skill}</div><div class="category">${x.category}</div></div>
              ${r?.url ? `<a href="${r.url}" target="_blank" rel="noreferrer">${r.title} ↗</a>` : ""}
            </div>`;
          })
          .join("")
      : `<div class="empty">Nothing new to learn for this role.</div>`;

    document
      .querySelectorAll(".role")
      .forEach((x) => x.classList.toggle("active", x.dataset.role === roleId));
  } catch (e) {
    $("gaps").textContent = "Could not load skill gaps.";
    $("learning").textContent = "Could not load learning path.";
  }
}

function renderGraph(g) {
  const el = $("graph");
  el.innerHTML = "";

  const nodes = [
    { id: "person", label: g.person, type: "person", x: 12, y: 50 },
    ...(g.owned_skills || []).slice(0, 5).map((n, i) => ({
      ...n, x: 31, y: 15 + i * 18,
    })),
    ...(g.roles || []).slice(0, 4).map((n, i) => ({
      ...n, x: 58, y: 22 + i * 19,
    })),
    ...(g.adjacent_skills || []).slice(0, 5).map((n, i) => ({
      ...n, x: 82, y: 15 + i * 18,
    })),
  ];

  const person = nodes[0];
  nodes.slice(1).forEach((n) => {
    const line = document.createElement("div");
    line.className = "edge";
    const dx = n.x - person.x;
    const dy = n.y - person.y;
    const len = Math.sqrt(dx * dx + dy * dy);
    line.style.left = person.x + "%";
    line.style.top = person.y + "%";
    line.style.width = len + "%";
    line.style.transform = `rotate(${Math.atan2(dy, dx)}rad)`;
    el.appendChild(line);
  });

  nodes.forEach((n) => {
    const d = document.createElement("div");
    d.className = `node ${n.type}`;
    d.textContent = n.label;
    d.style.left = n.x + "%";
    d.style.top = n.y + "%";
    el.appendChild(d);
  });
}

$("personSelect").onchange = async (e) => {
  personId = e.target.value;
  await loadPerson();
  await selectRole($("roleSelect").value);
};

$("roleSelect").onchange = (e) => selectRole(e.target.value);

boot().catch((e) => {
  console.error(e);
  $("health").textContent = "● Start the API and configure CognoDB";
});

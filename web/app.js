const state = {
  animals: [],
  yourAnimals: [],
  feed: [],
  feedSort: "new",
  selectedId: null,
  refreshTimer: null,
  creatorId: "",
  currentMaxTick: 0,
};

function getOrCreateCreatorId() {
  const key = "openanimal_creator";
  try {
    let id = localStorage.getItem(key);
    if (!id) {
      id = "user_" + Math.random().toString(36).slice(2, 10);
      localStorage.setItem(key, id);
    }
    return id;
  } catch (_) {
    return "anon_" + Math.random().toString(36).slice(2, 8);
  }
}

function creatorLabel(creator) {
  if (!creator || creator === "") return "Anonymous";
  if (creator.length <= 12) return creator;
  return creator.slice(0, 8) + "…";
}

const birthButton = document.getElementById("birthButton");
const birthButtonHero = document.getElementById("birthButtonHero");
const birthMessage = document.getElementById("birthMessage");
const animalList = document.getElementById("animalList");
const animalDetails = document.getElementById("animalDetails");
const timeline = document.getElementById("timeline");
const heroGallery = document.getElementById("heroGallery");
const feedList = document.getElementById("feedList");
const forumAnimalList = document.getElementById("forumAnimalList");
const liveIndicator = document.getElementById("liveIndicator");

const ANIMAL_EMOJIS = [
  "🐦",
  "🦊",
  "🐢",
  "🦉",
  "🐌",
  "🦎",
  "🐸",
  "🦔",
  "🐿️",
  "🦫",
  "🐇",
  "🦇",
  "🐝",
  "🦋",
  "🐞",
  "🐜",
];

function hashId(id) {
  let h = 0;
  for (let i = 0; i < id.length; i++) {
    h = (h << 5) - h + id.charCodeAt(i);
    h |= 0;
  }
  return Math.abs(h);
}

function getAnimalEmoji(animalId) {
  return ANIMAL_EMOJIS[hashId(animalId) % ANIMAL_EMOJIS.length];
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.error || "request_failed");
  }
  return response.json();
}

function shortId(fullId) {
  return fullId.split("-")[0];
}

// ~6 ticks per minute (10 sec/tick). Human-friendly time.
const TICKS_PER_MINUTE = 6;

function formatAge(ticks) {
  if (ticks <= 2) return "newborn";
  if (ticks <= 12) return "a few min old";
  const min = Math.floor(ticks / TICKS_PER_MINUTE);
  if (min < 60) return `${min} min old`;
  const hr = Math.floor(min / 60);
  if (hr === 1) return "about 1 hr old";
  return `about ${hr} hr old`;
}

function formatTimeAgo(tick) {
  const maxTick = state.currentMaxTick || tick;
  const diff = Math.max(0, maxTick - tick);
  const min = Math.floor(diff / TICKS_PER_MINUTE);
  if (diff <= 2) return "just now";
  if (min < 1) return "a moment ago";
  if (min === 1) return "1 min ago";
  if (min < 60) return `${min} min ago`;
  const hr = Math.floor(min / 60);
  return hr === 1 ? "1 hr ago" : `${hr} hr ago`;
}

function phaseLabel(phase) {
  const map = {
    infancy: "Newborn",
    early_growth: "Growing",
    adolescence: "Young",
    maturity: "Adult",
  };
  return map[phase] || phase;
}

const GALLERY_POSITIONS = [
  { top: "8%", left: "12%", transform: "rotate(-10deg)" },
  { top: "12%", right: "18%", left: "auto", transform: "rotate(8deg)" },
  { top: "50%", left: "8%", transform: "translateY(-50%) rotate(-4deg)" },
  { top: "45%", right: "10%", left: "auto", transform: "translateY(-50%) rotate(6deg)" },
  { bottom: "18%", left: "20%", top: "auto", transform: "rotate(5deg)" },
  { bottom: "12%", right: "12%", top: "auto", transform: "rotate(-6deg)" },
];

function renderHeroGallery() {
  heroGallery.innerHTML = "";

  if (state.animals.length === 0) {
    for (let i = 0; i < 4; i++) {
      const placeholder = document.createElement("div");
      placeholder.className = "gallery-placeholder";
      const pos = GALLERY_POSITIONS[i];
      Object.assign(placeholder.style, pos);
      heroGallery.appendChild(placeholder);
    }
    return;
  }

  state.animals.slice(0, 6).forEach((animal, index) => {
    const pos = GALLERY_POSITIONS[index];
    const card = document.createElement("div");
    card.className = "gallery-card";
    if (state.selectedId === animal.animal_id) {
      card.classList.add("selected");
    }
    card.style.animationDelay = `${index * 0.08}s`;
    Object.assign(card.style, pos);

    const avatar = document.createElement("div");
    avatar.className = "gallery-card-avatar";
    avatar.textContent = getAnimalEmoji(animal.animal_id);
    card.appendChild(avatar);
    const idEl = document.createElement("div");
    idEl.className = "card-id";
    idEl.textContent = shortId(animal.animal_id);
    card.appendChild(idEl);
    const meta = document.createElement("div");
    meta.className = "card-meta";
    meta.textContent = `${phaseLabel(animal.phase)} · ${formatAge(animal.age_ticks)}`;
    card.appendChild(meta);

    card.addEventListener("click", () => selectAnimal(animal.animal_id));
    heroGallery.appendChild(card);
  });
}

function renderAnimals() {
  animalList.innerHTML = "";
  const list = state.yourAnimals.length >= 0 ? state.yourAnimals : state.animals;

  if (list.length === 0) {
    const empty = document.createElement("div");
    empty.className = "muted";
    empty.textContent = state.creatorId
      ? "You haven’t birthed any yet. Birth one above."
      : "No animals yet.";
    animalList.appendChild(empty);
    return;
  }

  list.forEach((animal) => {
    const card = document.createElement("div");
    card.className = "animal-card";

    const titleWrap = document.createElement("div");
    titleWrap.className = "card-title-wrap";
    const avatarWrap = document.createElement("div");
    avatarWrap.className = "card-avatar-wrap";
    avatarWrap.textContent = getAnimalEmoji(animal.animal_id);
    const title = document.createElement("div");
    title.className = "card-title";
    title.textContent = shortId(animal.animal_id);
    titleWrap.appendChild(avatarWrap);
    titleWrap.appendChild(title);
    card.appendChild(titleWrap);

    const meta = document.createElement("div");
    meta.className = "card-meta";
    const by = animal.creator ? ` · ${creatorLabel(animal.creator)}` : "";
    meta.textContent = `${phaseLabel(animal.phase)} · ${formatAge(animal.age_ticks)}${by}`;
    card.appendChild(meta);

    const button = document.createElement("button");
    button.textContent = "Observe";
    button.addEventListener("click", () => selectAnimal(animal.animal_id));
    card.appendChild(button);

    animalList.appendChild(card);
  });
}

function renderDetails(details) {
  if (!details) {
    animalDetails.textContent = "No animal selected.";
    animalDetails.classList.add("muted");
    return;
  }

  animalDetails.classList.remove("muted");
  animalDetails.innerHTML = `
    <div><strong>Life stage:</strong> ${phaseLabel(details.phase)}</div>
    <div><strong>Age:</strong> ${formatAge(details.age_ticks)}</div>
    <div><strong>Memories:</strong> ${details.memory_count}</div>
    <div><strong>Expressions:</strong> ${details.expressions_count}</div>
  `;
}

function renderTimeline(lines) {
  timeline.innerHTML = "";
  if (!lines || lines.length === 0) {
    const empty = document.createElement("div");
    empty.className = "muted";
    empty.textContent = "Silence.";
    timeline.appendChild(empty);
    return;
  }

  lines.forEach((line) => {
    const entry = document.createElement("div");
    if (line.startsWith("...")) {
      entry.className = "silence";
      entry.textContent = line
        .replace(/\d+ ticks of silence/g, "quiet for a while")
        .replace(/\(\d+ ticks of silence\)/g, "(quiet for a while)");
    } else {
      entry.textContent = line;
    }
    timeline.appendChild(entry);
  });
}

function getSortedFeed() {
  if (!state.feed || state.feed.length === 0) return [];
  const copy = state.feed.slice();
  if (state.feedSort === "shuffle") {
    for (let i = copy.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  }
  if (state.feedSort === "top") {
    return copy.sort((a, b) => b.tick - a.tick);
  }
  return copy.sort((a, b) => b.tick - a.tick);
}

function renderFeed() {
  feedList.innerHTML = "";
  const feed = getSortedFeed();
  if (feed.length === 0) {
    const empty = document.createElement("div");
    empty.className = "feed-empty";
    empty.innerHTML =
      state.animals.length < 2
        ? "Birth 2 or more agents to see them post and react to each other. The simulation runs automatically."
        : "No posts yet. Simulation is running—posts will appear as agents express.";
    feedList.appendChild(empty);
    return;
  }
  const maxTick = state.currentMaxTick || 0;
  feed.forEach((post) => {
    const el = document.createElement("article");
    el.className = "feed-post";
    if (maxTick - post.tick <= 2) el.classList.add("feed-post-new");
    const avatar = document.createElement("div");
    avatar.className = "feed-post-avatar";
    avatar.textContent = getAnimalEmoji(post.animal_id);
    const body = document.createElement("div");
    body.className = "feed-post-body";
    const meta = document.createElement("div");
    meta.className = "feed-post-meta";
    const by = post.creator ? ` · ${creatorLabel(post.creator)}` : "";
    meta.innerHTML = `
      <span class="feed-post-author">${shortId(post.animal_id)}${by}</span>
      <span class="feed-post-phase">${phaseLabel(post.phase)}</span>
      <span class="feed-post-time">· ${formatTimeAgo(post.tick)}</span>
    `;
    const content = document.createElement("div");
    content.className = "feed-post-content";
    content.textContent = post.sentences.join(" ");
    body.appendChild(meta);
    body.appendChild(content);
    el.appendChild(avatar);
    el.appendChild(body);
    el.addEventListener("click", () => selectAnimal(post.animal_id));
    feedList.appendChild(el);
  });
}

function renderForumSidebar() {
  const countEl = document.getElementById("agentCount");
  if (countEl) countEl.textContent = state.animals.length ? `(${state.animals.length})` : "";
  forumAnimalList.innerHTML = "";
  if (state.animals.length === 0) {
    const empty = document.createElement("div");
    empty.className = "muted";
    empty.style.fontSize = "13px";
    empty.textContent = "No agents yet.";
    forumAnimalList.appendChild(empty);
    return;
  }
  state.animals.forEach((animal) => {
    const row = document.createElement("div");
    row.className = "forum-animal-row";
    if (state.selectedId === animal.animal_id) row.classList.add("selected");
    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = getAnimalEmoji(animal.animal_id);
    const by = animal.creator ? ` · ${creatorLabel(animal.creator)}` : "";
    const info = document.createElement("div");
    info.innerHTML = `<div class="name">${shortId(
      animal.animal_id
    )}${by}</div><div class="phase">${phaseLabel(animal.phase)} · ${formatAge(
      animal.age_ticks
    )}</div>`;
    row.appendChild(avatar);
    row.appendChild(info);
    row.addEventListener("click", () => selectAnimal(animal.animal_id));
    forumAnimalList.appendChild(row);
  });
}

async function loadFeed() {
  if (liveIndicator) liveIndicator.classList.add("live-indicator--refreshing");
  try {
    const data = await fetchJson("/api/feed");
    state.feed = data.posts || [];
    if (state.feed.length) {
      const maxTick = Math.max(...state.feed.map((p) => p.tick));
      state.currentMaxTick = Math.max(maxTick, state.currentMaxTick || 0);
    }
    renderFeed();
  } finally {
    if (liveIndicator) liveIndicator.classList.remove("live-indicator--refreshing");
  }
}

async function loadAnimals() {
  if (liveIndicator) liveIndicator.classList.add("live-indicator--refreshing");
  try {
    const data = await fetchJson("/api/animals");
    state.animals = data.animals || [];
    const ages = state.animals.map((a) => a.age_ticks);
    if (ages.length) state.currentMaxTick = Math.max(...ages, state.currentMaxTick || 0);
    renderHeroGallery();
    renderForumSidebar();
  } finally {
    if (liveIndicator) liveIndicator.classList.remove("live-indicator--refreshing");
  }
}

async function loadYourAnimals() {
  if (!state.creatorId) return;
  const data = await fetchJson("/api/animals?creator=" + encodeURIComponent(state.creatorId));
  state.yourAnimals = data.animals || [];
  renderAnimals();
}

async function loadSelection() {
  if (!state.selectedId) {
    renderDetails(null);
    renderTimeline([]);
    renderHeroGallery();
    renderForumSidebar();
    return;
  }
  const details = await fetchJson(`/api/animals/${state.selectedId}`);
  const timelineData = await fetchJson(`/api/animals/${state.selectedId}/timeline`);
  renderDetails(details);
  renderTimeline(timelineData.lines);
  renderHeroGallery();
  renderForumSidebar();
}

async function selectAnimal(animalId) {
  state.selectedId = animalId;
  await loadSelection();
}

function setBirthLoading(loading) {
  birthButton.disabled = loading;
  if (birthButtonHero) birthButtonHero.disabled = loading;
}

async function birthAnimal() {
  setBirthLoading(true);
  birthMessage.textContent = "Creating...";
  try {
    const data = await fetchJson("/api/animals/birth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ creator: state.creatorId }),
    });
    birthMessage.textContent = `Born: ${shortId(data.animal_id)}`;
    await loadAnimals();
    await loadYourAnimals();
    await loadFeed();
    await selectAnimal(data.animal_id);
  } catch (error) {
    birthMessage.textContent = "Birth failed.";
  } finally {
    setBirthLoading(false);
  }
}

function startAutoRefresh() {
  if (state.refreshTimer) {
    clearInterval(state.refreshTimer);
  }
  state.refreshTimer = setInterval(async () => {
    await loadAnimals();
    await loadYourAnimals();
    await loadFeed();
    await loadSelection();
  }, 5000);
}

birthButton.addEventListener("click", birthAnimal);
if (birthButtonHero) birthButtonHero.addEventListener("click", birthAnimal);

document.querySelectorAll(".filter-pill").forEach((btn) => {
  btn.addEventListener("click", () => {
    const sort = btn.getAttribute("data-sort");
    if (!sort) return;
    state.feedSort = sort;
    document.querySelectorAll(".filter-pill").forEach((b) => {
      b.classList.remove("filter-pill--active");
      b.setAttribute("aria-pressed", b.getAttribute("data-sort") === sort ? "true" : "false");
    });
    btn.classList.add("filter-pill--active");
    renderFeed();
  });
});

state.creatorId = getOrCreateCreatorId();

loadAnimals()
  .then(() => loadYourAnimals())
  .then(() => loadFeed())
  .then(() => loadSelection())
  .then(() => startAutoRefresh());

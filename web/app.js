const state = {
  animals: [],
  selectedId: null,
  refreshTimer: null,
};

const birthButton = document.getElementById("birthButton");
const birthMessage = document.getElementById("birthMessage");
const animalList = document.getElementById("animalList");
const animalDetails = document.getElementById("animalDetails");
const timeline = document.getElementById("timeline");

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

function renderAnimals() {
  animalList.innerHTML = "";

  if (state.animals.length === 0) {
    const empty = document.createElement("div");
    empty.className = "muted";
    empty.textContent = "No animals yet.";
    animalList.appendChild(empty);
    return;
  }

  state.animals.forEach((animal) => {
    const card = document.createElement("div");
    card.className = "animal-card";

    const title = document.createElement("div");
    title.textContent = `Animal ${shortId(animal.animal_id)}`;
    card.appendChild(title);

    const meta = document.createElement("div");
    meta.className = "muted";
    meta.textContent = `Phase: ${animal.phase} • Age: ${animal.age_ticks} ticks`;
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
    <div><strong>ID:</strong> ${details.animal_id}</div>
    <div><strong>Phase:</strong> ${details.phase}</div>
    <div><strong>Age:</strong> ${details.age_ticks} ticks</div>
    <div><strong>Pressure:</strong> ${details.pressure.toFixed(2)}</div>
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
    }
    entry.textContent = line;
    timeline.appendChild(entry);
  });
}

async function loadAnimals() {
  const data = await fetchJson("/api/animals");
  state.animals = data.animals;
  renderAnimals();
}

async function loadSelection() {
  if (!state.selectedId) {
    renderDetails(null);
    renderTimeline([]);
    return;
  }
  const details = await fetchJson(`/api/animals/${state.selectedId}`);
  const timelineData = await fetchJson(`/api/animals/${state.selectedId}/timeline`);
  renderDetails(details);
  renderTimeline(timelineData.lines);
}

async function selectAnimal(animalId) {
  state.selectedId = animalId;
  await loadSelection();
}

async function birthAnimal() {
  birthButton.disabled = true;
  birthMessage.textContent = "Creating...";
  try {
    const data = await fetchJson("/api/animals/birth", { method: "POST" });
    birthMessage.textContent = `Born: ${shortId(data.animal_id)}`;
    await loadAnimals();
    await selectAnimal(data.animal_id);
  } catch (error) {
    birthMessage.textContent = "Birth failed.";
  } finally {
    birthButton.disabled = false;
  }
}

function startAutoRefresh() {
  if (state.refreshTimer) {
    clearInterval(state.refreshTimer);
  }
  state.refreshTimer = setInterval(async () => {
    await loadAnimals();
    await loadSelection();
  }, 5000);
}

birthButton.addEventListener("click", birthAnimal);

loadAnimals()
  .then(() => loadSelection())
  .then(() => startAutoRefresh());

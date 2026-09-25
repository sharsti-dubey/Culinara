/* ═══════════════════════════════════════════════════════
   CULINARA — app.js
   Recipe loading, filtering, drawer, voice assistant
   ═══════════════════════════════════════════════════════ */

// ── Category gradient map ────────────────────────────────
const CAT_GRADIENTS = {
  Italian:  "linear-gradient(135deg,#fff0e8,#ffd4b8)",
  Indian:   "linear-gradient(135deg,#fff8e0,#ffe0a0)",
  French:   "linear-gradient(135deg,#e8f0ff,#c8d8f8)",
  Thai:     "linear-gradient(135deg,#e8fff0,#b8f0c8)",
  Japanese: "linear-gradient(135deg,#ffe8f0,#f8c8d8)",
  Mexican:  "linear-gradient(135deg,#fff0d8,#ffd898)",
  American: "linear-gradient(135deg,#f0f8ff,#c8e4ff)",
  Dessert:  "linear-gradient(135deg,#fff0f8,#f8c8e8)",
  default:  "linear-gradient(135deg,#f3ede3,#e8d5c0)",
};

// ── State ────────────────────────────────────────────────
let allRecipes  = [];
let activeCategory   = "all";
let activeDifficulty = "all";
let searchQuery = "";
let currentRecipe = null;
let isSpeaking = false;

// ── DOM refs ──────────────────────────────────────────────
const grid           = document.getElementById("recipeGrid");
const countEl        = document.querySelector(".stat-num");
const searchInput    = document.getElementById("searchInput");
const categoryItems  = document.querySelectorAll(".cat-item");
const diffItems      = document.querySelectorAll(".diff-item");
const activeFilters  = document.getElementById("activeFilters");
const drawerOverlay  = document.getElementById("drawerOverlay");
const recipeDrawer   = document.getElementById("recipeDrawer");
const drawerClose    = document.getElementById("drawerClose");
const drawerContent  = document.getElementById("drawerContent");
const voiceBtn       = document.getElementById("voiceBtn");
const voiceTranscript= document.getElementById("voiceTranscript");
const voiceResponse  = document.getElementById("voiceResponse");
const waveform       = document.getElementById("waveform");

// ════════════════════════════════════════════════════════
// 1. DATA LOADING
// ════════════════════════════════════════════════════════

async function fetchRecipes(params = {}) {
  const url = new URL("/api/recipes/search", window.location.origin);
  Object.entries(params).forEach(([k, v]) => v && url.searchParams.set(k, v));
  const res = await fetch(url);
  const data = await res.json();
  return data.recipes || [];
}

async function init() {
  try {
    allRecipes = await fetchRecipes();
    renderGrid(allRecipes);
    countEl.textContent = allRecipes.length;
  } catch (e) {
    grid.innerHTML = `<div class="empty-state">
      <div class="empty-emoji">⚠️</div>
      <h3>Couldn't connect to server</h3>
      <p>Make sure the Flask app is running on port 5000.</p>
    </div>`;
  }
}

// ════════════════════════════════════════════════════════
// 2. RENDER GRID
// ════════════════════════════════════════════════════════

function renderGrid(recipes) {
  if (!recipes.length) {
    grid.innerHTML = `<div class="empty-state">
      <div class="empty-emoji">🔍</div>
      <h3>No recipes found</h3>
      <p>Try a different search term or clear your filters.</p>
    </div>`;
    return;
  }

  grid.innerHTML = recipes.map((r, i) => recipeCard(r, i)).join("");

  // Bind click events
  grid.querySelectorAll(".recipe-card").forEach(card => {
    card.addEventListener("click", () => openDrawer(parseInt(card.dataset.id)));
  });
}

function recipeCard(r, i) {
  const bg = CAT_GRADIENTS[r.category] || CAT_GRADIENTS.default;
  const badgeCls = {Easy: "badge-easy", Medium: "badge-medium", Hard: "badge-hard"}[r.difficulty] || "";
  const total = r.prep_time + r.cook_time;
  const tags = (r.tags || []).slice(0, 3).map(t => `<span class="tag">#${t}</span>`).join("");

  return `
  <div class="recipe-card" data-id="${r.id}" style="animation-delay:${i * 0.04}s">
    <div class="card-hero" style="--card-bg:${bg}">
      <span>${r.emoji || "🍽️"}</span>
      <span class="card-badge ${badgeCls}">${r.difficulty}</span>
    </div>
    <div class="card-body">
      <div class="card-cuisine">${r.cuisine}</div>
      <div class="card-name">${r.name}</div>
      <div class="card-desc">${r.description}</div>
      <div class="card-meta">
        <span class="meta-item"><span class="meta-icon">⏱️</span>${total} min</span>
        <span class="meta-item"><span class="meta-icon">👥</span>${r.servings} servings</span>
      </div>
      ${tags ? `<div class="card-tags">${tags}</div>` : ""}
    </div>
  </div>`;
}

// ════════════════════════════════════════════════════════
// 3. FILTER & SEARCH
// ════════════════════════════════════════════════════════

async function applyFilters() {
  const params = {};
  if (searchQuery)           params.q          = searchQuery;
  if (activeCategory !== "all") params.category = activeCategory;
  if (activeDifficulty !== "all") params.difficulty = activeDifficulty;

  const results = await fetchRecipes(params);
  renderGrid(results);
  countEl.textContent = results.length;
  renderChips();
}

function renderChips() {
  const chips = [];
  if (activeCategory !== "all") {
    chips.push(`<span class="chip" data-clear="category">
      ${activeCategory} <span class="chip-x">×</span></span>`);
  }
  if (activeDifficulty !== "all") {
    chips.push(`<span class="chip" data-clear="difficulty">
      ${activeDifficulty} <span class="chip-x">×</span></span>`);
  }
  if (searchQuery) {
    chips.push(`<span class="chip" data-clear="search">
      "${searchQuery}" <span class="chip-x">×</span></span>`);
  }
  activeFilters.innerHTML = chips.join("");
  activeFilters.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const type = chip.dataset.clear;
      if (type === "category")   { activeCategory = "all";   categoryItems.forEach(i => i.classList.remove("active")); document.querySelector('[data-cat="all"]').classList.add("active"); }
      if (type === "difficulty") { activeDifficulty = "all"; diffItems.forEach(i => i.classList.remove("active")); }
      if (type === "search")     { searchQuery = ""; searchInput.value = ""; }
      applyFilters();
    });
  });
}

// Search
let searchDebounce;
searchInput.addEventListener("input", e => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    searchQuery = e.target.value.trim();
    applyFilters();
  }, 400);
});
document.getElementById("searchBtn").addEventListener("click", () => {
  searchQuery = searchInput.value.trim();
  applyFilters();
});
searchInput.addEventListener("keydown", e => {
  if (e.key === "Enter") { searchQuery = e.target.value.trim(); applyFilters(); }
});

// Category filter
categoryItems.forEach(item => {
  item.addEventListener("click", () => {
    categoryItems.forEach(i => i.classList.remove("active"));
    item.classList.add("active");
    activeCategory = item.dataset.cat;
    applyFilters();
  });
});

// Difficulty filter
diffItems.forEach(item => {
  item.addEventListener("click", () => {
    const wasActive = item.classList.contains("active");
    diffItems.forEach(i => i.classList.remove("active"));
    if (!wasActive) {
      item.classList.add("active");
      activeDifficulty = item.dataset.diff;
    } else {
      activeDifficulty = "all";
    }
    applyFilters();
  });
});

// ════════════════════════════════════════════════════════
// 4. RECIPE DRAWER
// ════════════════════════════════════════════════════════

async function openDrawer(id) {
  const res = await fetch(`/api/recipes/${id}`);
  const data = await res.json();
  if (!data.success) return;
  currentRecipe = data.recipe;
  renderDrawer(currentRecipe);
  recipeDrawer.classList.add("open");
  drawerOverlay.classList.add("open");
  document.body.style.overflow = "hidden";
}

function closeDrawer() {
  recipeDrawer.classList.remove("open");
  drawerOverlay.classList.remove("open");
  document.body.style.overflow = "";
  stopSpeaking();
}

drawerClose.addEventListener("click", closeDrawer);
drawerOverlay.addEventListener("click", closeDrawer);

function renderDrawer(r) {
  const bg = CAT_GRADIENTS[r.category] || CAT_GRADIENTS.default;
  const total = r.prep_time + r.cook_time;

  const ingredients = (r.ingredients || []).map(ing => `
    <div class="ingredient-item">
      <span class="ingredient-amount">${ing.amount}</span>
      <span class="ingredient-name">${ing.name}</span>
    </div>`).join("");

  const instructions = (r.instructions || []).map((ins, i) => `
    <div class="instruction-item">
      <div class="step-num">${ins.step_no || i + 1}</div>
      <div class="step-text">${ins.step}</div>
    </div>`).join("");

  drawerContent.innerHTML = `
    <div class="drawer-hero" style="background:${bg}">${r.emoji || "🍽️"}</div>
    <div class="drawer-info">
      <div class="drawer-cuisine">${r.cuisine} Cuisine · ${r.category}</div>
      <h2 class="drawer-name">${r.name}</h2>
      <p class="drawer-desc">${r.description}</p>

      <div class="drawer-stats">
        <div class="stat-box">
          <div class="stat-box-num">${r.prep_time}m</div>
          <div class="stat-box-lbl">Prep</div>
        </div>
        <div class="stat-box">
          <div class="stat-box-num">${r.cook_time}m</div>
          <div class="stat-box-lbl">Cook</div>
        </div>
        <div class="stat-box">
          <div class="stat-box-num">${total}m</div>
          <div class="stat-box-lbl">Total</div>
        </div>
        <div class="stat-box">
          <div class="stat-box-num">${r.servings}</div>
          <div class="stat-box-lbl">Serves</div>
        </div>
      </div>

      <!-- Voice read button -->
      <button class="voice-read-btn" id="readRecipeBtn">
        🔊 Read Recipe Aloud
      </button>

      <!-- Tabs -->
      <div class="drawer-tabs">
        <button class="drawer-tab active" data-tab="ingredients">🧂 Ingredients</button>
        <button class="drawer-tab" data-tab="instructions">📋 Method</button>
        <button class="drawer-tab" data-tab="tips">💡 Tips</button>
      </div>

      <div class="drawer-tab-content active" id="tab-ingredients">
        <div class="ingredient-list">${ingredients}</div>
      </div>
      <div class="drawer-tab-content" id="tab-instructions">
        <div class="instruction-list">${instructions}</div>
      </div>
      <div class="drawer-tab-content" id="tab-tips">
        <div class="tips-box">
          <h4>⭐ Chef's Tips</h4>
          <p>${r.tips || "Cook with love and patience!"}</p>
        </div>
      </div>
    </div>`;

  // Tab switching
  drawerContent.querySelectorAll(".drawer-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      drawerContent.querySelectorAll(".drawer-tab").forEach(t => t.classList.remove("active"));
      drawerContent.querySelectorAll(".drawer-tab-content").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      document.getElementById(`tab-${tab.dataset.tab}`).classList.add("active");
    });
  });

  // Voice read button in drawer
  document.getElementById("readRecipeBtn").addEventListener("click", () => {
    readRecipeAloud(r);
  });

  // Scroll to top
  recipeDrawer.scrollTop = 0;
}

// ════════════════════════════════════════════════════════
// 5. VOICE ASSISTANT (Web Speech API)
// ════════════════════════════════════════════════════════

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  recognition.continuous = false;

  recognition.onstart = () => {
    isListening = true;
    voiceBtn.classList.add("listening");
    voiceBtn.querySelector(".voice-btn-label").textContent = "Listening…";
    waveform.classList.add("active");
    voiceTranscript.textContent = "";
    voiceResponse.textContent = "";
  };

  recognition.onend = () => {
    isListening = false;
    voiceBtn.classList.remove("listening");
    voiceBtn.querySelector(".voice-btn-label").textContent = "Tap to Speak";
    waveform.classList.remove("active");
  };

  recognition.onerror = (e) => {
    isListening = false;
    voiceBtn.classList.remove("listening");
    voiceBtn.querySelector(".voice-btn-label").textContent = "Tap to Speak";
    waveform.classList.remove("active");
    const msgs = {
      "not-allowed": "Microphone access denied. Please allow in browser settings.",
      "no-speech":   "No speech detected. Try again.",
      "network":     "Network error. Check your connection.",
    };
    showToast(msgs[e.error] || `Voice error: ${e.error}`, "info");
  };

  recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript;
    voiceTranscript.textContent = `"${transcript}"`;
    await handleVoiceCommand(transcript);
  };

} else {
  voiceBtn.title = "Voice not supported in this browser";
}

voiceBtn.addEventListener("click", () => {
  if (!SpeechRecognition) {
    showToast("Voice recognition not supported. Try Chrome or Edge.", "info");
    return;
  }
  if (isListening) {
    recognition.stop();
  } else {
    stopSpeaking();
    recognition.start();
  }
});

// ─── Handle voice command via backend ────────────────────
async function handleVoiceCommand(transcript) {
  voiceResponse.textContent = "Processing…";
  try {
    const res = await fetch("/api/voice", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transcript }),
    });
    const data = await res.json();

    voiceResponse.textContent = data.voice_response || "Here's what I found!";

    // Speak the response
    speakText(data.voice_response);

    // Show result
    if (data.intent === "recipe_detail" && data.recipe) {
      openDrawer(data.recipe.id);
      showToast(`📖 Opening: ${data.recipe.name}`, "success");
    } else if (data.recipes && data.recipes.length) {
      renderGrid(data.recipes);
      countEl.textContent = data.recipes.length;
      showToast(`🔍 Found ${data.recipes.length} recipes`, "success");
    }

  } catch (e) {
    voiceResponse.textContent = "Sorry, I couldn't process that.";
  }
}

// ════════════════════════════════════════════════════════
// 6. SPEECH SYNTHESIS (text-to-speech)
// ════════════════════════════════════════════════════════

function speakText(text) {
  if (!window.speechSynthesis || !text) return;
  stopSpeaking();
  const utt = new SpeechSynthesisUtterance(text);
  utt.lang  = "en-US";
  utt.rate  = 0.92;
  utt.pitch = 1.0;
  utt.volume = 1.0;

  // Prefer a pleasant voice
  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(v =>
    v.name.includes("Samantha") || v.name.includes("Karen") ||
    v.name.includes("Google US English") || v.lang === "en-US"
  );
  if (preferred) utt.voice = preferred;

  isSpeaking = true;
  utt.onend = () => { isSpeaking = false; };
  window.speechSynthesis.speak(utt);
}

function stopSpeaking() {
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
    isSpeaking = false;
  }
}

// ─── Read full recipe aloud (from drawer) ────────────────
function readRecipeAloud(r) {
  if (!r) return;
  const total = r.prep_time + r.cook_time;
  const ingText = (r.ingredients || [])
    .map(i => `${i.amount} ${i.name}`).join(", ");
  const stepsText = (r.instructions || [])
    .map((s, i) => `Step ${s.step_no || i + 1}: ${s.step}`).join(". ");

  const script = `
    ${r.name}. A ${r.difficulty.toLowerCase()} ${r.cuisine} recipe.
    Serves ${r.servings} people. Total time: ${total} minutes.
    You will need: ${ingText}.
    Now for the method. ${stepsText}.
    Chef's tip: ${r.tips || "Enjoy!"}
  `;

  speakText(script);
  showToast("🔊 Reading recipe aloud…", "info");

  const btn = document.getElementById("readRecipeBtn");
  if (btn) {
    btn.textContent = "⏹ Stop Reading";
    btn.onclick = () => {
      stopSpeaking();
      btn.textContent = "🔊 Read Recipe Aloud";
      btn.onclick = () => readRecipeAloud(r);
    };
  }
}

// ════════════════════════════════════════════════════════
// 7. TOAST NOTIFICATIONS
// ════════════════════════════════════════════════════════

function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity .3s";
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

// ════════════════════════════════════════════════════════
// 8. KEYBOARD SHORTCUTS
// ════════════════════════════════════════════════════════

document.addEventListener("keydown", e => {
  if (e.key === "Escape") closeDrawer();
  if ((e.key === "/" || e.key === "f") && !["INPUT","TEXTAREA"].includes(document.activeElement.tagName)) {
    e.preventDefault();
    searchInput.focus();
  }
  if (e.key === "v" && !["INPUT","TEXTAREA"].includes(document.activeElement.tagName)) {
    voiceBtn.click();
  }
});

// ════════════════════════════════════════════════════════
// 9. BOOT
// ════════════════════════════════════════════════════════
document.addEventListener("DOMContentLoaded", init);

// Preload voices
window.speechSynthesis && window.addEventListener("load", () => {
  window.speechSynthesis.getVoices();
});
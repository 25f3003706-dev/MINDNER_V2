(function() {
  "use strict";

  const STORAGE_KEY = "mindner_level_progress_v3";
  const TOTAL_LEVELS = 5;
  const GAME_CATALOG = [
    { key: "daily_life", name: "Daily Life", path: "daily-life.html", difficulty: 1 },
    { key: "memory_match", name: "Memory Match", path: "memory-match.html", difficulty: 1 },
    { key: "life_memory", name: "Life Memory", path: "life-memory.html", difficulty: 2 },
    { key: "object_recognition", name: "Object Recognition", path: "obj-reg.html", difficulty: 2 },
    { key: "image_recognition", name: "Image Recognition", path: "imag-reg.html", difficulty: 3 },
    { key: "shape_recognition", name: "Shape Recognition", path: "shape_reg.html", difficulty: 3 }
  ];

  function emptyProgress() {
    return { currentLevel: 1, completedLevels: [], failedLevels: [], assignments: {}, recentDifficulties: [] };
  }

  function load() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
      const progress = saved && typeof saved === "object" ? saved : emptyProgress();
      progress.completedLevels = Array.isArray(progress.completedLevels) ? progress.completedLevels : [];
      progress.failedLevels = Array.isArray(progress.failedLevels) ? progress.failedLevels : [];
      progress.assignments = progress.assignments && typeof progress.assignments === "object" ? progress.assignments : {};
      progress.recentDifficulties = Array.isArray(progress.recentDifficulties) ? progress.recentDifficulties : [];
      return progress;
    } catch (error) {
      return emptyProgress();
    }
  }

  function save(progress) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  }

  function currentLevel() {
    // Check URL parameter first (for game navigation)
    const requestedLevel = Number(new URLSearchParams(window.location.search).get("level"));
    if (requestedLevel >= 1 && requestedLevel <= TOTAL_LEVELS) return requestedLevel;
    
    // Fall back to localStorage
    const stored = load();
    return Math.min(Math.max(Number(stored.currentLevel) || 1, 1), TOTAL_LEVELS);
  }

  function homeUrl(level = currentLevel()) {
    const target = new URL("../home.html", window.location.href);
    target.searchParams.set("level", String(level));
    target.searchParams.set("completed", "true");
    return target.toString();
  }

  window.MINDNER_GAME_PROGRESS = {
    catalog: GAME_CATALOG,
    load,
    currentLevel,
    homeUrl,
    goHome(level = currentLevel()) {
      window.location.href = homeUrl(level);
    },
    getAssignment(level) {
      return load().assignments[String(level)] || null;
    },
    ensureAssignment(level) {
      const progress = load();
      const key = String(level);
      if (progress.assignments[key]) return progress.assignments[key];

      const previousDifficulty = progress.recentDifficulties[progress.recentDifficulties.length - 1];
      const minimumDifficulty = Math.min(3, Math.max(1, Number(level)));
      const candidates = GAME_CATALOG.filter(game => game.difficulty >= minimumDifficulty && game.difficulty !== previousDifficulty);
      const pool = candidates.length ? candidates : GAME_CATALOG.filter(game => game.difficulty >= minimumDifficulty);
      const game = pool[Math.floor(Math.random() * pool.length)];
      const assignment = { gameKey: game.key, gameName: game.name, path: game.path, difficulty: game.difficulty, status: "pending" };
      progress.assignments[key] = assignment;
      progress.recentDifficulties = progress.recentDifficulties.concat(game.difficulty).slice(-3);
      save(progress);
      return assignment;
    },
    reset() {
      save(emptyProgress());
    },
    markFailed(level) {
      const progress = load();
      if (!progress.failedLevels.includes(level)) progress.failedLevels.push(level);
      if (progress.assignments[String(level)]) progress.assignments[String(level)].status = "failed";
      save(progress);
    },
    markCompleted(level) {
      const progress = load();
      if (!progress.completedLevels.includes(level)) progress.completedLevels.push(level);
      progress.failedLevels = progress.failedLevels.filter(item => item !== level);
      if (progress.assignments[String(level)]) progress.assignments[String(level)].status = "completed";
      if (progress.currentLevel === level && level < TOTAL_LEVELS) progress.currentLevel = level + 1;
      save(progress);
    }
  };
})();

// English Sounds Practice — web version
// Tap a phonetic symbol to hear the sound in isolation;
// tap the example word to hear the word.

const SECTIONS = [
  {
    title: "Consonants",
    items: [
      ["p", "pen"],
      ["b", "bag"],
      ["t", "tie"],
      ["d", "dog"],
      ["k", "key"],
      ["g", "girl"],
      ["m", "man"],
      ["n", "nose"],
      ["ŋ", "singer"],
      ["f", "fall"],
      ["v", "van"],
      ["θ", "thin"],
      ["ð", "this"],
      ["s", "see"],
      ["z", "zoo"],
      ["ʃ", "shoe"],
      ["ʒ", "genre"],
      ["tʃ", "chain"],
      ["dʒ", "jazz"],
      ["l", "leg"],
      ["r", "red"],
      ["h", "house"],
      ["x", "Hanukkah"],
      ["j", "yes"],
      ["w", "wet"],
    ],
  },
  {
    title: "Vowels",
    items: [
      ["iː", "eat"],
      ["i", "anyway"],
      ["ɪ", "if"],
      ["e", "egg"],
      ["æ", "add"],
      ["ə", "about"],
      ["ɜː", "earth"],
      ["ʌ", "up"],
      ["uː", "ooze"],
      ["u", "actual"],
      ["ʊ", "oops"],
      ["ɔː", "order"],
      ["ɒ", "on"],
      ["ɑː", "arm"],
    ],
  },
  {
    title: "Diphthongs",
    items: [
      ["eɪ", "eight"],
      ["əʊ", "open"],
      ["aɪ", "ice"],
      ["aʊ", "out"],
      ["ɔɪ", "oil"],
      ["ɪə", "ear"],
      ["eə", "airport"],
      ["ʊə", "tourist"],
    ],
  },
];

const player = document.getElementById("player");
let activeBtn = null;

function clearActive() {
  if (activeBtn) {
    activeBtn.classList.remove("playing");
    activeBtn = null;
  }
}

function play(symbol, kind, btn) {
  // kind: "isolation" or "words"
  const src = "audio/" + encodeURIComponent(symbol + "_" + kind) + ".mp3";

  // Stop anything currently playing (mirrors stop_all_effects)
  player.pause();
  player.currentTime = 0;
  clearActive();

  player.src = src;
  activeBtn = btn;
  btn.classList.add("playing");

  player.play().catch((err) => {
    // Autoplay/permission or missing file — just clear the highlight
    clearActive();
    console.warn("Could not play", src, err);
  });
}

player.addEventListener("ended", clearActive);
player.addEventListener("error", clearActive);

function buildCard(symbol, word) {
  const card = document.createElement("div");
  card.className = "card";

  const symBtn = document.createElement("button");
  symBtn.type = "button";
  symBtn.className = "card-btn symbol";
  symBtn.textContent = symbol;
  symBtn.setAttribute("aria-label", "Play sound " + symbol);
  symBtn.addEventListener("click", () => play(symbol, "isolation", symBtn));

  const wordBtn = document.createElement("button");
  wordBtn.type = "button";
  wordBtn.className = "card-btn word";
  wordBtn.textContent = word;
  wordBtn.setAttribute("aria-label", "Play word " + word);
  wordBtn.addEventListener("click", () => play(symbol, "words", wordBtn));

  card.appendChild(symBtn);
  card.appendChild(wordBtn);
  return card;
}

function render() {
  const content = document.getElementById("content");
  const frag = document.createDocumentFragment();

  for (const section of SECTIONS) {
    const h = document.createElement("h2");
    h.className = "section-title";
    h.textContent = section.title;
    frag.appendChild(h);

    const grid = document.createElement("div");
    grid.className = "grid";
    for (const [symbol, word] of section.items) {
      grid.appendChild(buildCard(symbol, word));
    }
    frag.appendChild(grid);
  }

  content.appendChild(frag);
}

render();

// Register service worker for offline use (optional, ignored if unsupported)
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("sw.js").catch(() => {});
  });
}

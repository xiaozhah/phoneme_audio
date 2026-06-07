# English Sounds Practice — Web App

A simple web app for practising the sounds of British English. It shows buttons
for consonants, vowels, and diphthongs, each paired with an example word. Tap a
phonetic symbol to hear its pronunciation, or tap the word to hear the word.

It runs in any modern browser on a phone, tablet, or computer — just open the
page. It is also an installable PWA (Progressive Web App), so you can "Add to
Home Screen" and use it offline.

> This started life as a [Pythonista](https://omz-software.com/pythonista/) iOS
> script (`phoneme_audio.py`, kept for reference) and was rebuilt as a static
> web app so it works everywhere from a single URL.

The audio files are sourced from the
[Oxford Dictionary](https://oalecd10.cp.com.cn/#/desktop/dict).

## Features

- **Open and use** — works in any browser on mobile or desktop, no install needed.
- **Audio playback** — tap a phonetic symbol to hear the sound in isolation; tap
  the example word to hear the word.
- **Organised sections** — consonants, vowels, and diphthongs.
- **Responsive layout** — the grid adapts from phone to desktop.
- **Dark mode** — follows your system appearance.
- **Installable & offline (PWA)** — add to home screen; audio is cached after
  first play so it works without a connection.

## Run it locally

Because the app fetches audio files, open it through a local web server (not by
double-clicking the HTML file):

```bash
# from the project folder
python3 -m http.server 8000
# then open http://localhost:8000 in your browser
```

## Deploy

It is a fully static site — the entire project folder (`index.html`,
`styles.css`, `app.js`, the PWA files, and the `audio/` folder) can be dropped
onto any static host:

- **Vercel / Netlify** — import the repo (or drag-and-drop the folder); no build
  command, output directory is the project root.
- **GitHub Pages** — enable Pages on the repository, serving from the root.
- Any other static hosting that serves files over HTTPS.

No build step and no server-side code are required.

## Project structure

```
index.html              App shell (header, layout, audio element)
styles.css              Styling, responsive grid, dark mode
app.js                  Phoneme data + UI rendering + audio playback
manifest.webmanifest    PWA metadata (installable)
icon.svg                App icon
sw.js                   Service worker (offline support)
audio/                  *_isolation.mp3 (the sound) and *_words.mp3 (the word)
phoneme_audio.py        Original Pythonista script (reference only)
```

## How playback maps to files

Each sound has two audio files, named by its IPA symbol:

- `audio/<symbol>_isolation.mp3` — the sound on its own (played by the symbol button)
- `audio/<symbol>_words.mp3` — the example word (played by the word button)

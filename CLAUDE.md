# Finger This

Scale trainer for guitar, banjo and ukulele, with a tuner, metronome, practice log and recorder.
It ships as one web app in two forms:
- **Windows (and any browser):** an installable PWA.
- **Android:** a native APK that wraps the same page in a WebView.

Read `memory.md` for the owner's requirements and the decisions behind them before changing behavior.

## Layout

| Path | What it is |
|---|---|
| `src/app.html` | The whole app: markup, CSS and JS in one file. Written as page *content*, with no doctype, html, head or body tags; the build adds those. |
| `src/INSTALL.txt` | User install guide, copied into the zip. |
| `build.py` | Builds `dist/finger-this/` (PWA: index.html, manifest, sw.js, icons), `dist/preview.html` (artifact copy) and `dist/FingerThis-app.zip`. |
| `build_apk.py` | Builds `dist/FingerThis.apk` from `dist/finger-this/index.html` (run `build.py` first). |
| `android/` | `AndroidManifest.xml`, `res/values/strings.xml` and `src/app/fingerthis/MainActivity.java` (the WebView wrapper). |
| `signing/finger-this.jks` | APK signing key. Alias `fingerthis`; the store/key password comes from `FINGERTHIS_KS_PASS` or `signing/password.txt` (gitignored). |
| `tests/verify_positions.py` | Checks all 3,960 instrument × tuning × scale × key combinations. |

## Build

```bash
python3 build.py                 # PWA folder, preview.html, zip
python3 build_apk.py             # signed APK
python3 tests/verify_positions.py   # must print "bad 0" and "ERRS 0"
```

**APK toolchain.** Google and Maven hosts are blocked in the sandbox, so Gradle and the Android SDK are unavailable. Install the tools from Ubuntu instead:

```bash
apt-get install -y aapt apksigner zipalign android-sdk-platform-23 dalvik-exchange
```

The pipeline is javac → dalvik-exchange (dx) → aapt package → zipalign → apksigner.

**APK rules**
- Java source must be Java 8 and use **no lambdas**, because dx doesn't desugar them; use anonymous classes.
- The code compiles against `android-23/android.jar`, so it can only call API ≤ 23 methods. Reach newer things through raw strings, as the MediaStore Downloads insert in `Bridge.saveFile` does.
- minSdk is 24 and targetSdk is 34.
- **Bump `android:versionCode`** (and versionName) in `AndroidManifest.xml` for every APK release.
- **Always sign with `signing/finger-this.jks`.** A different key won't install over the owner's existing app. If this workspace is new, ask the owner to attach the `.jks` they were given; if it's missing, a new key gets generated and they would have to uninstall first.
- The WebView loads the page with `loadDataWithBaseURL("https://finger-this.app/")`. That gives a secure origin, which getUserMedia and localStorage need. Don't change the base URL: localStorage is keyed to it.

**Preview artifact.** Publish `dist/preview.html` to update the existing preview at https://claude.ai/artifact/2EUzLh6A3fWEebkd37vSJ7 (title "Finger This"). Recording and the tuner need the microphone, so they don't work in the preview.

## app.html map (in source order)

1. **Music data**
   - `KEYS` is ordered by popularity: G C D A E F B♭ E♭ B A♭ F♯ D♭.
   - `SCALE_GROUPS` holds scales grouped exactly as the owner listed them, each with a formula string such as `1 2 ♭3 4 5 ♭6 7`. **The formula is the single source of truth:** semitones, note spelling (letter = degree number), degree labels and chord tones all derive from it.
   - `INSTR` holds frets, `fretOpts` and tunings. Strings are listed as MIDI numbers from low string to string 1. The banjo's short 5th string is a separate `fifth` value.
2. **State `S`**, persisted to localStorage `fretwise.v1`. The log is `fretwise.log.v1`, IndexedDB is `fretwise`, and the test hook is `window.__fretwise`. These internal names predate the rename. **Don't rename them**, or users lose their settings, log and recordings.
3. **`buildModel()`**
   - Note spelling and chord tones (third, fifth, seventh chosen by degree number, then by semitone).
   - The interlocking position engine (see below).
   - The 3-notes-per-string alternative.
   - The practice route `seq`.
4. **`drawBoard()`**, an SVG fretboard. `showPosition` and `showStep` highlight positions and notes.
5. **Audio**
   - A lookahead scheduler: `setInterval` every 25 ms schedules up to 120 ms ahead, and a rAF draw queue keeps visuals in sync with sound.
   - `click()` is the metronome sound and `pluck()` the note sound.
   - Drone (`DR`).
6. **Tuner.** YIN-style pitch detection and a spring-damped needle. It turns green within ±5 cents, red otherwise; the A4 reference is adjustable.
7. **Recording** (`R`). MediaRecorder; takes are stored in IndexedDB.
8. **Practice log.** Best clean tempo per instrument + scale + Play mode + key, plus practice time and day streak.
9. **Tunings tab.** `TUNINGS` is the owner's CSV as given (129 rows of [name, tuning, description, songs]). `TMERGED` merges rows with identical notes at runtime (104 tunings). Song edits are saved to localStorage `fretwise.tunings.v2`, keyed by the tuning notes; older v1 edits (keyed by row number) migrate on first load, so keep the `TUNINGS` row order.
10. **About.** The `ABOUT` text is the owner's own wording; keep it, converting notation to ♭ ♯.
11. **Android hooks**
    - `window.__appPause()` stops audio, tuner and recording.
    - `window.__appBack()` closes About or the options menu first and returns `'handled'`.
    - `window.FingerThisAndroid.saveFile(name, mime, b64)` is the native bridge for saving recordings.

## Interlocking positions (owner's core requirement)

Rules:
- There are 7 positions.
- **On every string, the highest note of position k is the lowest note of position k+1.**
- Within a position, strings abut: string i+1 starts on the scale note right after string i's top note, so each position plays stepwise with no repeats.

Algorithm:
1. **Position 1.** Enumerate options at start fret f0 with 1–4 notes per string, kept within the hand-span limit and no lower than f0−1.
2. **Later positions are forced.** After P1 the only free choice is how far the top string advances, because `T[k] = prev(T_prev[k+1])` for every other string.
3. **Search.** A DFS finds the most positions, then the lowest cost. Cost = fret span + 1.5 for each one-note string.
4. **Fallbacks.** Span limits are tried in order 4, 5, 6. Start frets go root on the lowest string first, then lower scale notes. "Start nearest the nut" changes the candidate list.
5. **Re-entrant strings** (a string higher than the one below it, e.g. a ukulele's high g) are excluded from positions.

Fit:
- For 7-note scales, 7 interlocked positions climb about two octaves. **The guitar therefore defaults to 24 frets**, which lets every key and scale fit in standard and half-step-down tuning.
- `fitNote()` tells the user when fewer than 7 fit (common in Drop D, DADGAD and banjo Double C).

Route:
- "Whole neck" plays P1↑ P2↓ P3↑ … P7↑, then back down to P1.
- Repeated notes at joins are dropped.
- Other options: "Position N" (that position up and back down) and "Loop Pn ↔ Pn+1".

After any change to positions, run `tests/verify_positions.py`, then look at screenshots at 740×350 (phone landscape) and 900×420.

## Design

- **Dark only, on purpose:** an ebony and rosewood fretboard with brass accents.
- **Tokens** are on `:root`: `--ebony --panel --raised --line --bone --muted --brass --ok --bad`.
- **Fonts:** Saira Condensed for display and Figtree for body, with offline fallbacks including `sans-serif-condensed` for Android.
- **Android is landscape only.** Keep layouts working at 740×350 with no horizontal scroll.
- **Musical text** always uses the real ♭ and ♯ characters, never b or #.
- **Copy** is plain, user-side wording, and every control says what it does.

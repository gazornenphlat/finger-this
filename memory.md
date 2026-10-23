# Memory: Finger This

The owner's requirements, the decisions made and why, and what's still open. Newest changes are at the bottom of the timeline.

## Owner
- Learning scales on **guitar, banjo and ukulele**. Wants apps for **Windows and Android**, and **Android in landscape**.
- Communicates with short, direct specs, sometimes as an attached text file. Prefers that features simply get built.

## Requirements (cumulative)

**Tabs:** Scales, Tuner, Metronome, plus Progress and an **About** button.

**Scales screen**
- Choose the key, scale, instrument and metronome settings.
- Tempo controls: − / + buttons (hold to repeat), a typed BPM box, and Start / Stop.
- Each position shows the **finger number on every note** of the fretboard.
- Notes play **one per metronome beat**, lowest to highest in a position.
- **Route:** up P1, down P2, up P3 … through **position 7**, then back down. It must move fluidly up and down the neck.
- **Positions interlock:** on each string, the highest note of P1 is the lowest note of P2, and so on.
- **Keys:** every key, most-used first.
- **Scales:** every scale from the owner's list, **grouped in the owner's categories** (Major family and modes, Minor families, Pentatonic & Blues, Symmetric, Exotic/Ethnic, Bebop, Japanese).
- **Notation:** use real ♭ and ♯ symbols.

**Tuner**
- A floating needle dial with flat on the left, in tune in the middle and sharp on the right.
- Shows the nearest note.
- The screen turns **red when out of tune and green when in tune**.

**Metronome:** − / + buttons, a typed BPM box, and Start / Stop.

**About:** the owner's scale descriptions, printed on the About screen.

**Name:** **"Finger This"** (renamed from "Fretwise" on 2026-10-08).

**Android:** delivered as an **APK**.

## Timeline
- **2026-10-07 — v1.** Scales, tuner and metronome as a PWA, with an install guide. Claude's extras: tunings, note tones, count-in, speed-up trainer, label modes, left-handed fretboard, tap tempo, subdivisions, A4 reference and keyboard shortcuts.
- **2026-10-07 — v2.** The owner asked for all six suggested features:
  - root drone (root alone or root + 5th)
  - looping the change between two positions
  - 3-notes-per-string guitar layout
  - triad and 7th-chord arpeggio modes, with chord tones circled
  - record and play back (stored on the device)
  - practice log with fastest clean tempo per key, practice time and streak
- **2026-10-08 — v3.** 7 interlocking positions, the full categorized scale list, the About screen, and the formula shown beside the Scale menu.
- **2026-10-08 — v4.** Renamed to Finger This. Built `FingerThis.apk` (versionCode 1, versionName 1.0) and gave the owner the signing key `finger-this.jks`.
- **2026-10-22.** Created this file and CLAUDE.md.

## Decisions and why
- **24-fret guitar by default.** For 7-note scales, 7 interlocking positions span about two octaves, which can't fit on 22 frets. 24 frets fits every key and scale in standard tuning. The owner can set their real fret count under ⚙ More; the app then says how many positions fit.
- **Positions span 5–6 frets with stretches.** The interlock forces about 3 notes per string. Fingering marks the stretches with 1 or 4.
- **Position 1 sits at or above the root.** This gives the familiar shapes: G major at frets 2–5, the A minor pentatonic box at 5–8.
- **High-g ukulele string and banjo 5th string are left out of the patterns.** Otherwise the standard ukulele fit only 3 positions. Low-G tuning uses all four strings.
- **Choices on ambiguous scales** (each noted in About):
  - Diminished is listed twice, Whole-Half and Half-Whole.
  - Kumoi uses 1 ♭2 4 5 ♭6, because the owner's first formula has the same notes as Minor Pentatonic.
  - Bebop Locrian uses the added major 7th.
  - "Hirojoshi" is spelled Hirajoshi.
- **Practice log** records the tempo of the last *complete* lap, and only after the owner confirms the lap was clean.
- **APK is a WebView wrapper built with Ubuntu's tools,** because Google and Maven downloads are blocked in the sandbox.
- **Internal storage names keep "fretwise"** so saved data survives the rename.

## Known limitations
- The APK hasn't been run on a real phone or emulator; it was only built, signature-verified and its page tested in Chromium.
- Google Play Protect warns on install because the app isn't from the Play Store.
- Drop D, DADGAD and banjo Double C often fit only 4–6 positions.
- Without internet, the custom fonts fall back to system fonts.
- In the claude.ai preview, the microphone is unavailable, so the tuner and recording don't work there, and "Save as file" does nothing.
- **Source of truth is now GitHub:** https://github.com/gazornenphlat/finger-this (public). Clone it to continue in a new session; the signing key `finger-this.jks` is *not* in the repo and must be attached separately so updates install over the existing app.

## Ideas not yet built
- Exporting the practice log.
- A Microsoft Store (MSIX) package via PWABuilder.
- Publishing to Google Play (would need an AAB and a Play developer account).

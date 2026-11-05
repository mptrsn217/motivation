# Motivation

A one-page site behind a QR code. Scanning it opens a flow: a question with
buttons, pick the right one and a video plays, then the next question, and so on.
Any wrong button ends it: the "gave up" message shows, the screen goes black and
stays dead until the page is opened again. Progress is remembered on the phone,
so closing the page and scanning again continues where they left off (unless they
gave up, which sends them back to the start).

## Files

| File | What it is |
|---|---|
| `index.html` | The page. Colours and font are at the top of the file under `/* Theme */`. |
| `flow.json` | **Your content**: the questions, the answers, and the order of videos. |
| `videos/` | Your video files. Use `.mp4` for best phone support. |
| `build.py` | Checks `flow.json` and the video files, and makes the QR code. |
| `qr.png`, `qr.svg` | The QR code (after `build.py --url ...`). Use the SVG for print. |

## Editing the flow

Open `flow.json` in any text editor. Steps run top to bottom.

```json
{
  "type": "question",
  "text": "When do you start?",
  "options": [
    { "label": "Monday", "correct": false },
    { "label": "Now", "correct": true }
  ],
  "wrongText": "Nope. Try again."
}
```

```json
{ "type": "video", "src": "videos/3.mp4" }
```

- Put as many steps as you like, in any order. A question can follow a video,
  two videos can follow each other, and so on.
- A question can have a single option (one button that just leads on).
- A shot sequence: every press of the button is a miss; after `misses` presses the
  screen cuts to black and the video plays. `giveUp` is the wrong button.

```json
{ "type": "shots", "text": "Game on the line.", "button": "Take the shot",
  "missText": "Missed.", "misses": 10, "giveUp": "Give up" }
```

- `gaveUp` at the top sets the message shown on a wrong button. `"restart": false`
  would let them continue from the same step after reopening instead of starting over.
- A video `src` can also be a full `https://...` link to a video hosted elsewhere.
- `start` and `end` set the first and last screen. `start.continueButton` is the
  label shown when someone comes back mid-way (default "Continue").

After editing, check it:

```bash
python build.py
```

It reports missing files, questions with no correct answer, and anything else wrong.

## Hosting

Live at **https://mptrsn217.github.io/motivation/** from the GitHub repository
`mptrsn217/motivation` (GitHub Pages, main branch, root folder).

To update: edit `flow.json` or add videos, then

```bash
python build.py
git add -A && git commit -m "update"
git push
```

The live site updates about a minute after the push. If the address ever changes,
remake the QR code with `python build.py --url <new address>`.

## Testing on this computer

```bash
python -m http.server 8765
```

Then open http://localhost:8765/ in a browser. Opening `index.html` directly from
the folder does not work, because browsers block it from reading `flow.json`.

## Notes

- Anyone with the link or the QR code can open it. There is no password.
- The page has `noindex` set so search engines will not list it.
- The QR code uses high error correction, so it still scans if the poster gets scuffed.

# Motivation

A one-page site behind a QR code. Scanning it opens a flow: a question with two
buttons, pick the right one and a video plays, then the next question, and so on.
Wrong answers shake and let you try again. Progress is remembered on the phone,
so closing the page and scanning again continues where they left off.

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
- `wrongText` on a question is optional. Without it the top-level `wrongText` is used.
- A video `src` can also be a full `https://...` link to a video hosted elsewhere.
- `start` and `end` set the first and last screen. `start.continueButton` is the
  label shown when someone comes back mid-way (default "Continue").

After editing, check it:

```bash
python build.py
```

It reports missing files, questions with no correct answer, and anything else wrong.

## Hosting (Netlify, free)

1. Make a free account at app.netlify.com.
2. Choose **Deploy manually** and drag this whole folder onto the page.
3. Netlify gives you an address like `something.netlify.app`. Rename it under
   Site settings if you want a nicer one.
4. Make the QR code for that address:

```bash
python build.py --url https://your-site.netlify.app/
```

5. Put `qr.svg` (or `qr.png`) on the poster, at least 2.5 cm (1 inch) wide. Scan it to check.

To update later: edit `flow.json` or add videos, run `python build.py`, drag the folder onto Netlify again.

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

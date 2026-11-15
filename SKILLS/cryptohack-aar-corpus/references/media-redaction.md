# Media PII redaction and verification

For screenshots/images inside a publication tree that must carry zero third-party identity.
The text gates (regex) do not cover binaries; the independent OCR/vision pass IS the gate.

## Pipeline
1. Inventory every candidate image; classify: identity-clean (ship as-is), redactable,
   or exclude (identity inseparable from the point — e.g. a terminal screenshot whose
   prompt content is the PII).
2. For review and for vision verification, first shrink: `im.thumbnail((1100,1100))` and
   save JPEG quality ~80. Full-size screenshots time out vision passes; the thumbnail both
   verifies and shows what a reader sees.
3. Pixelate identity regions on the ORIGINAL (thumbnail only for review):

```python
from PIL import Image
def pix(im, box, blocks=9):        # box = fractions (l,t,r,b) of the image
    W, H = im.size
    l, t, r, b = int(box[0]*W), int(box[1]*H), int(box[2]*W), int(box[3]*H)
    c = im.crop((l, t, r, b)); w, h = c.size
    im.paste(c.resize((max(1, w//blocks), max(1, h//blocks)), Image.NEAREST)
               .resize((w, h), Image.NEAREST), (l, t))
    return im
```

Pillow may need `python -m pip install pillow`; if the venv's `pip.exe` is absent, always
invoke via `python -m pip`.

4. Verify with an independent vision call under a strict prompt: "Quote ANY username,
display name, handle, @mention, or even a 3-4 character fragment still readable; if none,
state NONE." Fragments count as leaks (a visible first-4-chars of a name is still an
identifier); "Fir"-style label fragments are fine only when the fragment belongs to static
UI text, not to a name.
5. Iterate: fix boxes on the original, re-shrink, re-verify until NONE. Only then copy into
   the repo's `assets/`.
6. After two failed box guesses, stop estimating: ask the vision model for the identity
   token's bounding box AS PERCENTAGES ("left,top,right,bottom 0-100 for the exact text
   'X'"), then apply that box on the original with a ~30% margin on every side. Model-
   returned coordinates land where layout guessing misses (name line vs body line in
   short-height chat crops).

## Leak classes the first pass reliably misses
- Inline @mentions / handles inside message BODY text — avatar+name-row boxes do not reach them.
- First data row of a table: start the column box at the header line, not below it.
- Leader-style 'First Blood: <name>' lines outside the table — cover the whole strip.
- Case variants surviving a case-sensitive pseudonym replace in text files: after any
  handle->pseudonym sweep, re-scan case-INsensitively.

## Documentation
Record in the gates file, per shipped image: clean / redacted-then-OCR-verified / excluded,
with the reason. Image redaction is lossy by design — say so rather than implying the
image is original.

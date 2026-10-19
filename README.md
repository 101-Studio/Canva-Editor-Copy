# Sushi.Edit — final build

## Steps (once)
1. Put index.html.txt + patch_sushi.py + setup.sh (or setup.bat)
   in the same folder.
2. Run one of these:
     Mac/Linux :  ./setup.sh
     Windows   :  setup.bat
     Any OS    :  python patch_sushi.py index.html.txt   (then rename
                  index.fixed.html → index.html)
3. Double-click index.html in your browser. Done.

## What's fixed
General (20 patches):
  • Video preview close button works
  • Undo history capped at 60 steps
  • Shortcuts no longer fire while on other screens
  • Video export can't hang forever
  • Download blob URLs are freed
  • Canvas resize no longer breaks the current page
  • Backup / synced image sources are HTML-escaped
  • Photos over ~1600 px are downscaled before saving

Ghost mannequin (8 patches):
  • Median background sampling (robust when garment touches edges)
  • ↶ Undo brush  +  Reset edits  buttons
  • Inner-neck position derived from top of mask (auto-placed)
  • Cylinder shading inside the neck
  • Softer inner-neck fade
  • Edge-softness is clamped so huge photos don't blow out
  • Send-to-Design creates a real project with the cutout on top

If any line reports SKIP, it means you edited that part of the original —
the script still applies every other patch. Nothing is destroyed.

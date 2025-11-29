Place your Mapbox style files here.

Steps:
1. Copy the attached `style.json` into this folder as `style.json`.
2. Copy the entire `sprite_images/` folder (from your attached map package) into this folder so it becomes `wwwroot/map-style/sprite_images/`.

Notes:
- The style should reference sprites using a relative URL that will resolve to:
    /map-style/sprite_images/<sprite-base>
  Mapbox expects requests to `<base>.json` and `<base>.png` (for example `/map-style/sprite_images/sprite.json` and `/map-style/sprite_images/sprite.png`).
- After copying files, restart the app and open `/Home/Index` or `/Home/Dashboard` to see the custom style.

If you want I can copy the files for you — paste the `style.json` contents and list of files in `sprite_images/` here or move them into the repository workspace and I will finish the copy automatically.
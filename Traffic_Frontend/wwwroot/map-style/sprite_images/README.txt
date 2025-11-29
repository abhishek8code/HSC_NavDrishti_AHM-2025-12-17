Place your sprite image files here if you want to serve them locally.

Notes:
- The style's `sprite` property currently references a Mapbox-hosted sprite:
  "sprite": "mapbox://sprites/abhi8code/cmihl5ebg003p01r184ixfrqb/b8fjw435hx85pp7j172f016pl"

- If you want to serve sprites locally, provide these files in this folder and update
  `style.json`'s `sprite` field to a relative path, for example:
    "sprite": "/map-style/sprite_images/sprite"
  The browser will then request:
    /map-style/sprite_images/sprite.json
    /map-style/sprite_images/sprite.png

- If you want me to convert the `sprite` entry in the style to point to local sprites, attach the sprite files (or list filenames) and I'll update `style.json` accordingly.
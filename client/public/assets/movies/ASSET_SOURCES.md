# Movie artwork sources

CineMatch contains a unique, locally generated abstract artwork SVG for each MovieLens catalog item. These are original decorative illustrations labeled with each film title and genre; they are not film stills or official movie posters. This keeps artwork visible throughout the catalog without hotlinking to movie image APIs.

Two historical public domain posters are also included as exact film matches:

| MovieLens ID | Movie | File | Source and rights |
|---:|---|---|---|
| 6987 | The Cabinet of Dr. Caligari (1920) | `posters/6987.jpg` | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Das_Kabinett_des_Doktor_Caligari_1920_Poster.jpg). Commons marks this poster public domain and identifies its artists. |
| 2010 | Metropolis (1927) | `posters/2010.jpg` | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Boris_Bilinski_-_Filmplakat_f%C3%BCr_Metropolis_restored.jpg). Commons marks this poster public domain and identifies Boris Bilinski. |

Files are served from the app's own `public` directory. Run `node server/scripts/generate-catalog-art.js` from the `server` folder to regenerate the catalog art and mappings.

Expeditious
======

Expeditious is a collection of tools for working with songs.

- **Monsen**: Takes in a music file, and a start point and duration, and creates a new file with the given duration, with
  fade up and fade down.
- **Amundsen**: Converts the result of Monsens work into mp3 and ogg (whatever is needed for full browser support for HTML audio tag),
  and transfers the result to a remote server.
- **Nansen**: Queries a page for a JSON array of songs with the attribute "filename", and merges them all together before pushing
  to a remote server.

All together these explorers are what keeps our music running on monday evenings.

Dependencies
------------

All:
- Sox

Amundsen:
- Mutagen
- Lame

Expeditious
======

Expeditious is a collection of tools for working with songs.

- **Monsen**: Takes in a music file, and a start point and duration, and creates a new file with
the given duration, with fade up and fade down.
- **Nansen**: Queries a page for a JSON array of songs with the attribute "filename", and merges
them all together before pushing to a remote server. This is planned to be incorporated into
slingsby so that it's handled automatically.

Together these explorers keeps our music running on Monday evenings.

Installation and usage
----------------------

    $ pip install -e .
    $ monsen mysong.flac --start 25 --duration 45

The above will generate `mysong_trimmed.flac`, starting at 25 s into mysong, fading up, going
for 45 seconds and then fade down.

Type `monsen -h` for help.

Dependencies
------------

[SoX](http://sox.sourceforge.net/).
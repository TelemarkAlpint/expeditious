Expeditious
===========

Expeditious is a collection of tools for working with songs. The're basically just wrapping sox
to provide consistent results for all of our songs and an easier interface for our needs.

- **Monsen**: Takes in a music file, and a start point and duration, and creates a new file with
the given duration, with fade up and fade down.
- **Nansen**: Queries a page for a JSON array of songs with the attribute "filename", and merges
them all together before pushing to a remote server. This is planned to be incorporated into
slingsby so that it's handled automatically.

Together these explorers keeps our music running on Monday evenings.

This repo is cloned to `/home/groups/telemark/expeditious` and `update_top_song.py` is called to
update the song as seen from slingsby. Note that there's a post-merge git hook in that repo that
chmod's all files to g+w. Remember to re-create that hook if you re-create the repo!

The hook looks like this:

```
#!/bin/bash

chmod -R g+w *
```


Installation and usage
----------------------

    $ pip install -e .
    $ monsen mysong.flac --start 25

The above will generate `mysong_trimmed.flac`, starting at 25 s into mysong, fading up, going
for 45 seconds and then fade down.

Eventually, assuming you have VirtualBox and Vagrant installed, you can just fire up a VM which has
sox and the tools installed, by simply issuing:

	$ vagrant up

You can ssh into the machine with either `vagrant ssh` or ssh to `localhost` at port 2222. User/pw
vagrant/Vagrant.

The local directory `files` is shared with the VM, at `/home/vagrant/files`. So just cd in there,
and use `monsen` to the dirty work. Upload the raw files and the resulting yaml and trimmed
versions to the Dropbox, upload the trimmed version on the website for conversion. Done.

Type `monsen -h` for help.


Dependencies
------------

[SoX](http://sox.sourceforge.net/).


Recording audio?
----------------

If you're fetching a new song from somewhere, and you record with silence at the start and
beginning, you can utilize the small `trim-silence` script in this repo. From inside vagrant:

    $ trim-silence <inputfile>

This will trim away silence at both the start and the end, and encode the result as FLAC.

Make sure you record in 44,1kHz, otherwise stuff will fail when you try to combine the songs later!

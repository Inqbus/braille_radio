# braille_radio

A neat commandline internet radio for braille users or small character displays (e.g. Raspberry Pi).

### Function

Braille_radio plays internet radio stations. The station information is gathered from
the open radio data project [https://www.radio-browser.info](https://www.radio-browser.info).

### Slow indexing for lighting fast searching:

The station information is processed by [Whoosh](https://whoosh.readthedocs.io/en/latest/intro.html) into a quick search index.
Therefore the initial start of braille_radio will need a minute or two to create the index, so please be patient. 
The subsequent starts will be quite fast. Then you can fluidly search (offline) as you type.

### Optimized GUI:

The GUI is quite minimal. The main action takes place in the top line of the screen. This is for the comfort of the braille users. 
Additional lines are displayed for further help/information, only.

### Sound output:

The sound output is via VLC only. So you will need VLC to use this software.

### Work in progress

This is a work in progress. Please open an issue if you have a question, found a bug or like to introduce some new ideas. 

### Installation:

    $ pip install braille_radio
    

### Usage:

    $ braille_radio
  
    







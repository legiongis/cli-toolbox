### doc creation

served live here: http://cli-toolbox.readthedocs.io/en/latest/home.html

markdown cheatsheet: https://github.com/adam-p/markdown-here/wiki/Markdown-Here-Cheatsheet

+ To edit an existing file (you can test stuff out the home.md file) just click on it and click the edit icon in the top right corner of the file contents. Github is great because you can preview your changes while editing a file.
+ To add a new file, enter the docs directory, click the new file button, and name the file whatever you want (no spaces) and end the name with .md.
+ To add a new file to the table of contents, open up and edit the index.rst file. You can see where "installation" and "home" are listed, just put the name of the new file (without the .md ending) in the list wherever you want it.
+ To add images in the docs, enter the docs folder and upload the image there. Rename all images so there are no spaces. You can see an example of an image in home.md. _The image path must be the full url of the uploaded image once it has been saved to github. Probably easiest to copy/paste from the dubuque_library.jpg example and just change the file name._
+ Whenever you are ready to commit a change, you will have the opportunity to add a little note summarizing your changes. This is pretty important, but for the docs it won't need to be too detailed. For now, just choose the "Commit directly to the master branch. " option.
+ Every time you make a commit, readthedocs will be triggered and the documentation will be rebuilt. Looks like it's taking about a minute to complete right now.

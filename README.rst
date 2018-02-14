Color By Score --- PyMOL Plugin
===============================
The Coloy By Score plugin makes it easy to visualize how structures are scored 
by Rosetta, i.e. which residues have good or bad scores, and which terms are 
responsible.  It can also show the difference in score between two structures.  
Being able to easily visualize the scores Rosetta is assigning your models is 
important, because it's a good way to gain confidence that rosetta is doing 
what you want it to (i.e. there aren't residues on the far side of the protein 
dramatically influencing the score because they weren't properly relaxed, or 
something like that).

Installation
------------
1. Download and compile rosetta.

2. Create an environment variable called ``ROSETTA`` that contains the path to 
   the Rosetta installation you want Color By Score to use.  For example, if 
   you checked out Rosetta in ``~/rosetta`` like so::

      git clone git@github.com:RosettaCommons/main.git ~/rosetta

   Then you would add the following line (or something like it) to your 
   ``~/.bashrc`` file::

      export ROSETTA=~/rosetta

   If you skip this step, you'll be prompted for the path to Rosetta every time 
   you run Color By Score.

3. In PyMOL, go to Plugin > Plugin Manager > Install New Plugin.  In the 
   "Install from PyMolWiki or any URL" section, enter the following path into 
   the URL field, then click Fetch::

      https://raw.githubusercontent.com/kalekundert/color_by_score/master/color_by_score.py

Displaying scores
-----------------
1. Load your model into PyMOL.

2. Click Plugins > Color By Score or enter ``score`` in the PyMOL command line.  
   Wait a few seconds while the rosetta scores are calculated, then the whole 
   scene will be recolored according to those scores.

   If you only want to show scores for a particular selection, you can specify 
   that selection as the first argument to the command line interface.  For 
   example, if you only want to score chain A::

      score chain A

3. If you want to change which term is being shown, click on the "Term" menu on 
   the right side of the screen.

4. If you want to change the color scheme being used, click on the "Colors" 
   menu on the right side of the screen.  Better scores will be represented by 
   the left-most colors.  For example, the default colors are 
   ``blue_white_red``, meaning that residues with good scores will be colored 
   blue, intermediate scores white, and bad scores red.

   .. note::
      The scale is relative to the scores present in the structure, so there 
      will always be at least one residue at either end of the spectrum.  So a 
      bright red residue doesn't necessarily mean a bad score in an absolute 
      sense, it just means that residue has the worst score in that structure.

5. Click "Done" to exit the wizard.
   
Displaying score differences
----------------------------
1. Load two structures you want to compare into PyMOL.

2. Launch Color By Score like so::

      score <model selection>, <reference selection>

3. You can use the "Show" menu to switch between showing the difference in 
   score between the model and the reference ("delta-score") and showing just 
   the score for the model ("score").

Troubleshooting
---------------
Color By Score works by running the Rosetta score app and parsing the output.  
If something goes wrong, it may be useful to look at the input and output files 
for those runs.  You can find the path to these files by looking for the 
following lines at the end of the command-line output produced by the plugin::

   All files used to score 'all' will be kept until the wizard is closed:
   /tmp/color_by_score_XXXXXX

One thing I anticipate causing problems is ligands, since at present there's no 
way to provide ligand params file to the plugin.  If you have this problem, you 
can work around it by providing a selection that excludes the ligand.  For 
example, if the ligand is chain X, run the plugin like so::

   score not chain X

If you have any other problems, feel free to make an issue or submit a pull 
request via GitHub.

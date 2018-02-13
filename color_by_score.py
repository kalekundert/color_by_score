#!/usr/bin/env python3

import os, sys
from pymol import cmd
from pymol.wizard import Wizard
from pprint import pprint

class ColorByScore (Wizard):

    def __init__(self, obj='', ref_obj=''):
        self.obj = None
        self.ref_obj = ref_obj
        self.original_colors = {}
        self.rosetta_path = os.environ.get('ROSETTA')
        self.rosetta_args = []
        self.active_prompt = ''
        self.is_rosetta_running = False
        self.active_term = 'total'
        self.indices = {}
        self.scores = {}
        self.terms = {}

        self.set_object(obj)

    def get_panel(self):
        """
        Return a list of lists describing the entries that should appear in the 
        right-hand panel of the GUI (below all the selections) when the wizard 
        is running.
        """

        # Each entry is described by a list with 3 elements.  The first element 
        # is a number that specifies the type of entry: 1 for text, 2 for a 
        # button, 3 for a menu.  The second element is the text that will be 
        # seen by the user.  The third element is an argument that means 
        # different things for each type of entry.  For buttons, it's a piece 
        # of code (given as a string) that should be executed when the button 
        # is pressed.  For menus, it's a "tag" that can be passed to get_menu()
        # to get a description of the menu in question.

        # If the user hasn't provided object to score and the path to rosetta, 
        # then get_prompt() should be leading them through the process of doing 
        # that.  Until then, just display the name of the wizard and the option 
        # to quit.

        if not self.obj or not self.rosetta_path or self.is_rosetta_running:
            return [
                [1, "Color by Score", ''],
                [2, "Cancel", 'cmd.get_wizard().cleanup()'],
            ]

        # Make the buttons and menus that control the basic actions and 
        # settings that don't depend on the specific system being studied.

        buttons = [
            [1, "Color by Score", ''],
            [3, "Term: {}".format(self.active_term), 'term'],
            [2, "Done", 'cmd.get_wizard().cleanup()'],
        ]

        return buttons

    def get_menu(self, tag):
        """
        Return a dictionary describing the entries in the menu associated with 
        the given tag.  These tags come from get_panel(), so each menu is 
        associated with one buttons on the right-hand side of the GUI.
        """
        menus = {
            'term': [[2, 'Score Term', '']],
            'colorscheme': [[2, 'Colorscheme', '']],
        }

        # Define the term menu.
        for term in sorted(self.terms, key=self.terms.__getitem__):
            menus['term'] += [[
                1, term, 'cmd.get_wizard().set_active_term("{}")'.format(term)]]

        # Return the right menu.
        return menus[tag]

    def get_prompt(self):
        """
        Return text to be displayed in the top left corner of the view area.
        If the user has not yet provided wildtype and mutant objects, prompt 
        for that.  Otherwise, tell the user about the <Ctrl-Space> hotkey.
        """
        # The \999 code changes the text color to white.
        if not self.obj:
            return ["Select the object to score: \\999{}".format(self.active_prompt)]
        if not self.rosetta_path:
            return ["Provide the path to rosetta: \\999{}".format(self.active_prompt)]
        elif self.is_rosetta_running:
            return ["Running rosetta... Press <Esc> for details..."]
        else:
            return

    def do_key(self, key, x, y, mod):
        """
        Take responsibility for handling key presses.
        """
        # If the user hasn't specified an object to score, prompt for one.  
        # Letters (key >= 32), Backspace (key in 8, 127), and Enter (key in 10, 
        # 13) are handled specially.  Everything else is passed on to pymol.

        if self.obj and self.rosetta_path:
            return 0

        if key in (8, 127):
            self.active_prompt = self.active_prompt[:-1]
        elif key >= 32:
            self.active_prompt += chr(key)
        elif key in (10, 13):
            if not self.obj: self.set_object(self.active_prompt)
            if not self.rosetta_path: self.set_rosetta_path(self.active_prompt)
            self.active_prompt = ''
        else:
            return 0

        cmd.refresh_wizard()
        return 1

    def get_event_mask(self):
        return Wizard.event_mask_key

    def set_object(self, obj):
        self.obj = obj
        self._save_colors()
        self._update_score()

    def set_rosetta_path(self, path):
        self.rosetta_path = path
        self._update_score()

    def set_rosetta_args(self, *args):
        self.rosetta_args = args
        self._update_score()

    def set_active_term(self, term):
        self.active_term = term
        self._update_colors()

    def cleanup(self):
        if self.obj:
            self._restore_colors()
        cmd.set_wizard()

    def _save_colors(self):
        if self.obj:
            cmd.iterate(
                    self.obj,
                    'self.original_colors[chain, resi, name] = color',
                    space=locals(),
            )

    def _update_score(self):
        from tempfile import mkdtemp
        from subprocess import Popen, PIPE
        from shutil import rmtree

        if not self.obj and self.rosetta_path:
            return

        # Create a temporary directory.
        tempdir = mkdtemp(prefix='color_by_score_')
        pdb_path = os.path.join(tempdir, 'pymol_obj.pdb')
        score_path = os.path.join(tempdir, 'default.sc')

        # Create a PDB from the indicated object.
        cmd.save(pdb_path, self.obj)

        self.indices = {}
        cmd.iterate(
                self.obj,
                'residues.add(resi); self.indices[chain, resi, name] = len(residues)',
                space=dict(self=self, residues=set(), len=len),
        )

        # Score the PDB with rosetta.
        score_app = os.path.join(self.rosetta_path, 'source', 'bin', 'score')
        score_cmd = [
                score_app,
                '-in:file:s', pdb_path,
                '-rescore:verbose',
        ] +     self.rosetta_args

        self.is_rosetta_running = True
        cmd.refresh_wizard()
        p = Popen(score_cmd, stdout=PIPE, stderr=PIPE, cwd=tempdir)
        stdout, stderr = p.communicate()
        self.is_rosetta_running = False

        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')

        print(stdout)
        print(stderr)

        rmtree(tempdir)

        # Scrape the score terms from rosetta's output log.
        self.scores = {}
        self.terms = {'total': 0}

        for line in stdout.split('\n'):
            if line.startswith('protocols.simple_moves.ScoreMover: E   '):
                fields = line.split()
                self.terms.update({x: i for i, x in enumerate(fields[2:], 1)})

            if line.startswith('protocols.simple_moves.ScoreMover: E(i)'):
                fields = line.split()
                resi = int(fields[2])
                terms = [float(x) for x in fields[3:]]
                self.scores[resi] = [sum(terms)] + terms
        
        # Re-color the protein.
        self._update_colors()

    def _update_colors(self):
        active_scores = {
                resi: self.scores[resi][self.terms[self.active_term]]
                for resi in self.scores
        }
        colorscheme = range(3322, 3405)

        def color_from_score(x, #
                lo=min(active_scores.values()),
                hi=max(active_scores.values()),
                c=colorscheme):
            return int(len(c) * (hi - x) / (hi - lo)) + c[0]

        colors = {
                resi: color_from_score(active_scores[resi])
                for resi in self.scores
        }

        cmd.alter(
                self.obj,
                'color = colors[self.indices[chain, resi, name]]',
                space=locals(),
        )
        cmd.recolor()
        
    def _restore_colors(self):
        if self.obj:
            cmd.alter(
                    self.obj,
                    'color = self.original_colors[chain, resi, name]',
                    space=locals(),
            )
            cmd.recolor()



def color_by_score(obj=None, ref_obj=None):
    """
    Provide a convenient way to launch the wizard from the command-line.
    """
    wizard = ColorByScore(obj, ref_obj)
    cmd.set_wizard(wizard)


## Add "score" as pymol command
cmd.extend('score', color_by_score)
cmd.auto_arg[0]['score'] = cmd.auto_arg[0]['zoom']
cmd.auto_arg[1]['score'] = cmd.auto_arg[0]['zoom']

## Trick to get "wizard score" working
sys.modules['pymol.wizard.score'] = sys.modules[__name__]

## Add item to plugin menu
try:
    from pymol.plugins import addmenuitem
    def __init_plugin__(self): #
        addmenuitem('Color by Score', lambda s=self: color_by_score())
except:
    def __init__(self): #
        self.menuBar.addmenuitem(
                'Plugin', 'command', 'Color by Score',
                label='Color by Score', command=lambda s=self: color_by_score())

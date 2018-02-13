#!/usr/bin/env python3

import os, sys
import pytest

TESTS = os.path.dirname(__file__)
sys.path.append(os.path.join(TESTS, '..'))
import color_by_score

def test_parse_scores():
    with open(os.path.join(TESTS, 'stdout')) as file:
        lines = file.read()

    terms, scores = color_by_score.parse_scores(lines)

    assert terms == {
            'total':                 0,
            'fa_atr':                1,
            'fa_rep':                2,
            'fa_sol':                3,
            'fa_intra_rep':          4,
            'fa_intra_sol_xover4':   5,
            'lk_ball_wtd':           6,
            'fa_elec':               7,
            'pro_close':             8,
            'hbond_sr_bb':           9,
            'hbond_lr_bb':          10,
            'hbond_bb_sc':          11,
            'hbond_sc':             12,
            'dslf_fa13':            13,
            'omega':                14,
            'fa_dun':               15,
            'p_aa_pp':              16,
            'yhh_planarity':        17,
            'ref':                  18,
            'rama_prepro':          19,
    }

    values = [
           -3.18,
            0.46,
            3.57,
            1.73,
            0.09,
           -0.25,
           -2.40,
            0.00,
            0.00,
            0.00,
            0.00,
            0.00,
            0.00,
           -0.07,
            2.48,
            0.00,
            0.00,
            1.66,
            0.00,
    ]
    assert scores[1][1:] == pytest.approx(values)


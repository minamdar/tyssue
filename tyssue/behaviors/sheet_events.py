"""
Event management module
=======================


"""

import logging
import pandas as pd
from ..topology.sheet_topology import (remove_face,
                                       type1_transition,
                                       cell_division)
logger = logging.getLogger(__name__)


class SheetEvents():

    def __init__(self, sheet, model, geom):
        self.sheet = sheet
        self.model = model
        self.geom = geom

    def idx_lookup(self, face_id):
        return self.sheet.face_df[
            self.sheet.face_df.id == face_id].index[0]

    @property
    def events(self):
        events = {
            'shrink': self.shrink,
            'grow': self.grow,
            'contract': self.contract,
            'type1_at_shorter': self.type1_at_shorter,
            'type3': self.type3,
            'divide': self.divide,
            'ab_pull': self.ab_pull,
            }
        return events

    def shrink(self, face, *args):

        factor = args[0]
        new_vol = self.sheet.specs['face']['prefered_vol'] * factor
        self.sheet.face_df.loc[self.idx_lookup(face),
                               'prefered_vol'] = new_vol

    def grow(self, face, *args):
        self.shrink(face, *args)

    def contract(self, face, *args):

        factor = args[0]
        new_contractility = self.sheet.specs['face']['contractility'] * factor
        self.sheet.face_df.loc[self.idx_lookup(face),
                               'contractility'] += new_contractility

    def type1_at_shorter(self, face, *args):

        edges = self.sheet.edge_df[self.sheet.edge_df['face'] ==
                                   self.idx_lookup(face)]
        shorter = edges.length.argmin()
        type1_transition(self.sheet, shorter)

        self.geom.update_all(self.sheet)

    def type3(self, face, *args):

        remove_face(self.sheet, face)
        self.geom.update_all(self.sheet)

    def ab_pull(self, face, *args):

        verts = self.sheet.edge_df[self.sheet.edge_df['face'] ==
                                   self.idx_lookup(face)]['srce'].unique()
        factor = args[0]
        new_tension = self.sheet.specs['edge']['line_tension'] * factor
        self.sheet.vert_df.loc[verts, 'radial_tension'] += new_tension

    def divide(self, face, *args):
        cell_division(self.sheet, self.idx_lookup(face), self.geom, *args)

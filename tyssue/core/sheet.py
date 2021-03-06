'''
An epithelial sheet, i.e a 2D mesh in a 2D or 3D space,
akin to a HalfEdge data structure in CGAL.

For purely 2D the geometric properties are defined in
 `tyssue.geometry.planar_geometry`
A dynamical model derived from Fahradifar et al. 2007 is provided in
`tyssue.dynamics.planar_vertex_model`


For 2D in 3D, the geometric properties are defined in
 `tyssue.geometry.sheet_geometry`
A dynamical model derived from Fahradifar et al. 2007 is provided in
`tyssue.dynamics.sheet_vertex_model`


'''


import numpy as np
import pandas as pd

from .objects import Epithelium, get_opposite
from ..config.geometry import flat_sheet


class Sheet(Epithelium):
    '''
    An epithelial sheet, i.e a 2D mesh in a 2D or 3D space,
    akin to a HalfEdge data structure in CGAL.

    The geometric properties are defined in `tyssue.geometry.sheet_geometry`
    A dynamical model derived from Fahradifar et al. 2007 is provided in
    `tyssue.dynamics.sheet_vertex_model`


    '''

    def __init__(self, identifier, datasets,
                 specs=None, coords=None):
        '''
        Creates an epithelium sheet, such as the apical junction network.

        Parameters
        ----------
        identifier: `str`, the tissue name
        face_df: `pandas.DataFrame` indexed by the faces indexes
            this df holds the vertices associated with

        '''
        if specs is None:
            specs = flat_sheet()
        super().__init__(identifier, datasets,
                         specs, coords)

    def get_neighbors(self, face):
        """Returns the faces adjacent to `face`
        """
        if 'opposite' not in self.edge_df.columns:
            self.edge_df['opposite'] = get_opposite(self.edge_df)

        face_edges = self.edge_df[self.edge_df['face'] == face]
        op_edges = face_edges['opposite'].dropna().astype(np.int)
        return self.edge_df.loc[op_edges, 'face'].values

    def get_neighborhood(self, face, order):
        """Returns `face` neighborhood up to a degree of `order`

        For example, if `order` is 2, it wil return the adjacent, faces
        and theses faces neighbors.

        Returns
        -------
        neighbors : pd.DataFrame with two colums, the index
            of the neighboring face, and it's neighboring order

        """
        # Start with the face so that it's not gathered later
        neighbors = pd.DataFrame.from_dict({'face': [face],
                                            'order': [0]})
        for k in range(order+1):
            for neigh in neighbors[neighbors['order'] == k-1]['face']:
                new_neighs = self.get_neighbors(neigh)
                new_neighs = set(new_neighs).difference(neighbors['face'])

                orders = np.ones(len(new_neighs), dtype=np.int) * k
                new_neighs = pd.DataFrame.from_dict({'face': list(new_neighs),
                                                     'order': orders},
                                                    dtype=np.int)
                neighbors = pd.concat([neighbors, new_neighs])

        return neighbors.reset_index(drop=True).loc[1:]

    @classmethod
    def planar_sheet_2d(cls, identifier,
                        nx, ny, distx, disty):
        from scipy.spatial import Voronoi
        from ..config.geometry import planar_spec
        from ..generation import hexa_grid2d, from_2d_voronoi
        grid = hexa_grid2d(nx, ny, distx, disty)
        datasets = from_2d_voronoi(Voronoi(grid))
        return cls(identifier, datasets,
                   specs=planar_spec(),
                   coords=['x', 'y'])

    @classmethod
    def planar_sheet_3d(cls, identifier,
                        nx, ny, distx, disty):
        from scipy.spatial import Voronoi
        from ..config.geometry import flat_sheet
        from ..generation import hexa_grid2d, from_2d_voronoi
        grid = hexa_grid2d(nx, ny,
                           distx, disty)
        datasets = from_2d_voronoi(Voronoi(grid))
        datasets['vert']['z'] = 0
        datasets['face']['z'] = 0

        return cls(identifier, datasets,
                   specs=flat_sheet(),
                   coords=['x', 'y', 'z'])

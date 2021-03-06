import pytest
from tyssue.core.generation import three_faces_sheet
from tyssue.core.sheet import Sheet

from tyssue.geometry.sheet_geometry import SheetGeometry as geom
from tyssue.topology.base_topology import (close_face, add_vert,
                                           condition_4i,
                                           condition_4ii)

from tyssue.core.generation import three_faces_sheet
from tyssue.stores import load_datasets
from tyssue.topology.sheet_topology import (cell_division,
                                            type1_transition,
                                            split_vert)
from tyssue.config.geometry import sheet_spec



def test_condition4i():
    sheet = Sheet('test', *three_faces_sheet())
    assert len(condition_4i(sheet)) == 0

    sheet.edge_df = sheet.edge_df.append(sheet.edge_df.iloc[-1], ignore_index=True)
    sheet.edge_df.index.name = 'edge'
    sheet.reset_index()
    sheet.reset_topo()
    assert len(condition_4i(sheet)) == 1


def test_condition4ii():
    sheet = Sheet('test', *three_faces_sheet())
    assert len(condition_4ii(sheet)) == 0
    add_vert(sheet, 0)
    sheet.reset_index()
    sheet.reset_topo()
    assert len(condition_4ii(sheet)) == 1

def test_division():

    h5store = 'small_hexagonal.hf5'
    datasets = load_datasets(h5store,
                             data_names=['face',
                                         'vert',
                                         'edge'])
    specs = sheet_spec()
    sheet = Sheet('emin', datasets, specs)
    geom.update_all(sheet)

    Nf, Ne, Nv = sheet.Nf, sheet.Ne, sheet.Nv

    cell_division(sheet, 17, geom)

    assert sheet.Nf - Nf == 1
    assert sheet.Nv - Nv == 2
    assert sheet.Ne - Ne == 6


def test_t1_transition():

    h5store = 'small_hexagonal.hf5'
    datasets = load_datasets(
        h5store,
        data_names=['face', 'vert', 'edge'])
    specs = sheet_spec()
    sheet = Sheet('emin', datasets, specs)
    geom.update_all(sheet)
    face = sheet.edge_df.loc[84, 'face']
    type1_transition(sheet, 84)
    assert sheet.edge_df.loc[84, 'face'] != face


def test_split_vert():

    datasets, specs = three_faces_sheet()
    sheet = Sheet('3cells_2D', datasets, specs)
    geom.update_all(sheet)

    split_vert(sheet, 0, epsilon=1e-1)
    geom.update_all(sheet)
    assert sheet.Nv == 15
    assert sheet.Ne == 18

    datasets, specs = three_faces_sheet()
    sheet = Sheet('3cells_2D', datasets, specs)
    geom.update_all(sheet)

    split_vert(sheet, 1, epsilon=1e-1)
    geom.update_all(sheet)
    assert sheet.Nv == 14
    assert sheet.Ne == 18



def test_close_face():
    sheet = Sheet('test', *three_faces_sheet())
    e0 = sheet.edge_df.index[0]
    face = sheet.edge_df.loc[e0, 'face']
    Ne = sheet.Ne
    sheet.edge_df = sheet.edge_df.loc[sheet.edge_df.index[1:]].copy()
    close_face(sheet, face)
    assert sheet.Ne == Ne

    close_face(sheet, face)
    assert sheet.Ne == Ne

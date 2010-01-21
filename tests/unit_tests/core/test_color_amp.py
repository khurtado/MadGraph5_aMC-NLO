################################################################################
#
# Copyright (c) 2009 The MadGraph Development team and Contributors
#
# This file is a part of the MadGraph 5 project, an application which 
# automatically generates Feynman diagrams and matrix elements for arbitrary
# high-energy processes in the Standard Model and beyond.
#
# It is subject to the MadGraph license which should accompany this 
# distribution.
#
# For more information, please visit: http://madgraph.phys.ucl.ac.be
#
################################################################################

"""Unit test library for the routines of the core library related to writing
color information for diagrams."""

import copy
import fractions
import unittest

import madgraph.core.base_objects as base_objects
import madgraph.core.diagram_generation as diagram_generation

import madgraph.core.color_amp as color_amp
import madgraph.core.color_algebra as color

class ColorAmpTest(unittest.TestCase):
    """Test class for the color_amp module"""

    mypartlist = base_objects.ParticleList()
    myinterlist = base_objects.InteractionList()
    mymodel = base_objects.Model()

    def setUp(self):
        # A gluon
        self.mypartlist.append(base_objects.Particle({'name':'g',
                      'antiname':'g',
                      'spin':3,
                      'color':8,
                      'mass':'zero',
                      'width':'zero',
                      'texname':'g',
                      'antitexname':'g',
                      'line':'curly',
                      'charge':0.,
                      'pdg_code':21,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':True}))

        # A quark U and its antiparticle
        self.mypartlist.append(base_objects.Particle({'name':'u',
                      'antiname':'u~',
                      'spin':2,
                      'color':3,
                      'mass':'zero',
                      'width':'zero',
                      'texname':'u',
                      'antitexname':'\bar u',
                      'line':'straight',
                      'charge':2. / 3.,
                      'pdg_code':2,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':False}))
        antiu = copy.copy(self.mypartlist[1])
        antiu.set('is_part', False)

        # A quark D and its antiparticle
        self.mypartlist.append(base_objects.Particle({'name':'d',
                      'antiname':'d~',
                      'spin':2,
                      'color':3,
                      'mass':'zero',
                      'width':'zero',
                      'texname':'u',
                      'antitexname':'\bar u',
                      'line':'straight',
                      'charge':-1. / 3.,
                      'pdg_code':1,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':False}))
        antid = copy.copy(self.mypartlist[2])
        antid.set('is_part', False)

        # A photon
        self.mypartlist.append(base_objects.Particle({'name':'a',
                      'antiname':'a',
                      'spin':3,
                      'color':1,
                      'mass':'zero',
                      'width':'zero',
                      'texname':'\gamma',
                      'antitexname':'\gamma',
                      'line':'wavy',
                      'charge':0.,
                      'pdg_code':22,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':True}))

        # A Higgs
        self.mypartlist.append(base_objects.Particle({'name':'h',
                      'antiname':'h',
                      'spin':1,
                      'color':1,
                      'mass':'mh',
                      'width':'wh',
                      'texname':'h',
                      'antitexname':'h',
                      'line':'dashed',
                      'charge':0.,
                      'pdg_code':25,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':True}))

        # 3 gluon vertiex
        self.myinterlist.append(base_objects.Interaction({
                      'id': 1,
                      'particles': base_objects.ParticleList(\
                                            [self.mypartlist[0]] * 3),
                      'color': [color.ColorString([color.f(0, 1, 2)])],
                      'lorentz':['L1'],
                      'couplings':{(0, 0):'G'},
                      'orders':{'QCD':1}}))

        # 4 gluon vertex
        self.myinterlist.append(base_objects.Interaction({
                      'id': 2,
                      'particles': base_objects.ParticleList(\
                                            [self.mypartlist[0]] * 4),
                      'color': [color.ColorString([color.f(-1, 0, 2),
                                                   color.f(-1, 1, 3)]),
                                color.ColorString([color.f(-1, 0, 3),
                                                   color.f(-1, 1, 2)]),
                                color.ColorString([color.f(-1, 0, 1),
                                                   color.f(-1, 2, 3)])],
                      'lorentz':['L(p1,p2,p3)', 'L(p2,p3,p1)', 'L3'],
                      'couplings':{(0, 0):'G^2',
                                   (1, 1):'G^2',
                                   (2, 2):'G^2'},
                      'orders':{'QCD':2}}))

        # Gluon couplings to up and down quarks
        self.myinterlist.append(base_objects.Interaction({
                      'id': 3,
                      'particles': base_objects.ParticleList(\
                                            [self.mypartlist[1], \
                                             antiu, \
                                             self.mypartlist[0]]),
                      'color': [color.ColorString([color.T(2, 0, 1)])],
                      'lorentz':['L1'],
                      'couplings':{(0, 0):'GQQ'},
                      'orders':{'QCD':1}}))

        self.myinterlist.append(base_objects.Interaction({
                      'id': 4,
                      'particles': base_objects.ParticleList(\
                                            [self.mypartlist[2], \
                                             antid, \
                                             self.mypartlist[0]]),
                      'color': [color.ColorString([color.T(2, 0, 1)])],
                      'lorentz':['L1'],
                      'couplings':{(0, 0):'GQQ'},
                      'orders':{'QCD':1}}))

        # Photon coupling to up
        self.myinterlist.append(base_objects.Interaction({
                      'id': 5,
                      'particles': base_objects.ParticleList(\
                                            [self.mypartlist[1], \
                                             antiu, \
                                             self.mypartlist[3]]),
                      'color': [color.ColorString([color.T(0, 1)])],
                      'lorentz':['L1'],
                      'couplings':{(0, 0):'GQED'},
                      'orders':{'QED':1}}))

        self.mymodel.set('particles', self.mypartlist)
        self.mymodel.set('interactions', self.myinterlist)

    def test_colorize_uu_gg(self):
        """Test the colorize function for uu~ > gg"""

        myleglist = base_objects.LegList()

        myleglist.append(base_objects.Leg({'id':-2,
                                         'state':'initial'}))
        myleglist.append(base_objects.Leg({'id':2,
                                         'state':'initial'}))

        myleglist.extend([base_objects.Leg({'id':21,
                                            'state':'final'})] * 2)

        myprocess = base_objects.Process({'legs':myleglist,
                                        'model':self.mymodel})

        myamplitude = diagram_generation.Amplitude()

        myamplitude.set('process', myprocess)

        myamplitude.generate_diagrams()

        my_col_basis = color_amp.ColorBasis()

        # S channel
        col_dict = my_col_basis.colorize(myamplitude['diagrams'][0],
                                     self.mymodel)

        goal_dict = {(0, 0):color.ColorString([color.T(-1000, 1, 2),
                                               color.f(-1000, 4, 3)])}

        self.assertEqual(col_dict, goal_dict)

        # T channel
        col_dict = my_col_basis.colorize(myamplitude['diagrams'][1],
                                     self.mymodel)

        goal_dict = {(0, 0):color.ColorString([color.T(3, 1, -1000),
                                               color.T(4, -1000, 2)])}

        self.assertEqual(col_dict, goal_dict)

        # U channel
        col_dict = my_col_basis.colorize(myamplitude['diagrams'][2],
                                     self.mymodel)

        goal_dict = {(0, 0):color.ColorString([color.T(4, 1, -1000),
                                               color.T(3, -1000, 2)])}

        self.assertEqual(col_dict, goal_dict)

    def test_colorize_uux_ggg(self):
        """Test the colorize function for uu~ > ggg"""

        myleglist = base_objects.LegList()

        myleglist.append(base_objects.Leg({'id':-2,
                                         'state':'initial'}))
        myleglist.append(base_objects.Leg({'id':2,
                                         'state':'initial'}))

        myleglist.extend([base_objects.Leg({'id':21,
                                            'state':'final'})] * 3)

        myprocess = base_objects.Process({'legs':myleglist,
                                        'model':self.mymodel})

        myamplitude = diagram_generation.Amplitude()

        myamplitude.set('process', myprocess)

        myamplitude.generate_diagrams()

        my_col_basis = color_amp.ColorBasis()

        # First diagram with two 3-gluon vertices
        col_dict = my_col_basis.colorize(myamplitude['diagrams'][0],
                                     self.mymodel)

        goal_dict = {(0, 0, 0):color.ColorString([color.T(-1000, 1, 2),
                                               color.f(-1001, 4, 3),
                                               color.f(5, -1001, -1000)])}

        self.assertEqual(col_dict, goal_dict)

        # Diagram with one 4-gluon vertex
        col_dict = my_col_basis.colorize(myamplitude['diagrams'][3],
                                     self.mymodel)

        goal_dict = {(0, 0):color.ColorString([color.T(-1000, 1, 2),
                                               color.f(-1002, -1000, 4),
                                               color.f(-1002, 5, 3)]),
                     (0, 1):color.ColorString([color.T(-1000, 1, 2),
                                               color.f(-1003, -1000, 3),
                                               color.f(-1003, 5, 4)]),
                     (0, 2):color.ColorString([color.T(-1000, 1, 2),
                                               color.f(-1004, -1000, 5),
                                               color.f(-1004, 4, 3)])}

        self.assertEqual(col_dict, goal_dict)

    def test_color_basis_uux_aggg(self):
        """Test the color basis building for uu~ > aggg (3! elements)"""

        myleglist = base_objects.LegList()

        myleglist.append(base_objects.Leg({'id':2,
                                         'state':'initial'}))
        myleglist.append(base_objects.Leg({'id':-2,
                                         'state':'initial'}))

        myleglist.append(base_objects.Leg({'id':22,
                                         'state':'final'}))
        myleglist.extend([base_objects.Leg({'id':21,
                                            'state':'final'})] * 3)

        myprocess = base_objects.Process({'legs':myleglist,
                                        'model':self.mymodel})

        myamplitude = diagram_generation.Amplitude()

        myamplitude.set('process', myprocess)

        myamplitude.generate_diagrams()

        new_col_basis = color_amp.ColorBasis(myamplitude, self.mymodel)

        self.assertEqual(len(new_col_basis), 6)

class ColorSquareTest(unittest.TestCase):
    """Test class for the color_amp module"""

    mypartlist = base_objects.ParticleList()
    myinterlist = base_objects.InteractionList()
    mymodel = base_objects.Model()

    def setUp(self):
        # A gluon
        self.mypartlist.append(base_objects.Particle({'name':'g',
                      'antiname':'g',
                      'spin':3,
                      'color':8,
                      'mass':'zero',
                      'width':'zero',
                      'texname':'g',
                      'antitexname':'g',
                      'line':'curly',
                      'charge':0.,
                      'pdg_code':21,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':True}))

        # A quark U and its antiparticle
        self.mypartlist.append(base_objects.Particle({'name':'u',
                      'antiname':'u~',
                      'spin':2,
                      'color':3,
                      'mass':'zero',
                      'width':'zero',
                      'texname':'u',
                      'antitexname':'\bar u',
                      'line':'straight',
                      'charge':2. / 3.,
                      'pdg_code':2,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':False}))
        antiu = copy.copy(self.mypartlist[1])
        antiu.set('is_part', False)

        # A quark D and its antiparticle
        self.mypartlist.append(base_objects.Particle({'name':'d',
                      'antiname':'d~',
                      'spin':2,
                      'color':3,
                      'mass':'zero',
                      'width':'zero',
                      'texname':'u',
                      'antitexname':'\bar u',
                      'line':'straight',
                      'charge':-1. / 3.,
                      'pdg_code':1,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':False}))
        antid = copy.copy(self.mypartlist[2])
        antid.set('is_part', False)

        # 3 gluon vertiex
        self.myinterlist.append(base_objects.Interaction({
                      'id': 1,
                      'particles': base_objects.ParticleList(\
                                            [self.mypartlist[0]] * 3),
                      'color': [color.ColorString([color.f(0, 1, 2)])],
                      'lorentz':['L1'],
                      'couplings':{(0, 0):'G'},
                      'orders':{'QCD':1}}))

        # 4 gluon vertex
        self.myinterlist.append(base_objects.Interaction({
                      'id': 2,
                      'particles': base_objects.ParticleList(\
                                            [self.mypartlist[0]] * 4),
                      'color': [color.ColorString([color.f(-1, 0, 2),
                                                   color.f(-1, 1, 3)]),
                                color.ColorString([color.f(-1, 0, 3),
                                                   color.f(-1, 1, 2)]),
                                color.ColorString([color.f(-1, 0, 1),
                                                   color.f(-1, 2, 3)])],
                      'lorentz':['L(p1,p2,p3)', 'L(p2,p3,p1)', 'L3'],
                      'couplings':{(0, 0):'G^2',
                                   (1, 1):'G^2',
                                   (2, 2):'G^2'},
                      'orders':{'QCD':2}}))

        # Gluon couplings to up and down quarks
        self.myinterlist.append(base_objects.Interaction({
                      'id': 3,
                      'particles': base_objects.ParticleList(\
                                            [self.mypartlist[1], \
                                             antiu, \
                                             self.mypartlist[0]]),
                      'color': [color.ColorString([color.T(2, 0, 1)])],
                      'lorentz':['L1'],
                      'couplings':{(0, 0):'GQQ'},
                      'orders':{'QCD':1}}))

        self.myinterlist.append(base_objects.Interaction({
                      'id': 4,
                      'particles': base_objects.ParticleList(\
                                            [self.mypartlist[2], \
                                             antid, \
                                             self.mypartlist[0]]),
                      'color': [color.ColorString([color.T(2, 0, 1)])],
                      'lorentz':['L1'],
                      'couplings':{(0, 0):'GQQ'},
                      'orders':{'QCD':1}}))


        self.mymodel.set('particles', self.mypartlist)
        self.mymodel.set('interactions', self.myinterlist)

    def test_color_matrix_multi_gluons(self):
        """Test the color matrix building for gg > n*g with n up to 3"""

        goal = [fractions.Fraction(7, 3),
                fractions.Fraction(19, 6),
                fractions.Fraction(455, 108),
                fractions.Fraction(3641, 648)]

        goal_line1 = [(fractions.Fraction(7, 3), fractions.Fraction(-2, 3)),
                      (fractions.Fraction(19, 6), fractions.Fraction(-1, 3),
                       fractions.Fraction(-1, 3), fractions.Fraction(-1, 3),
                       fractions.Fraction(2, 3), fractions.Fraction(-1, 3)),
                    (fractions.Fraction(455, 108), fractions.Fraction(-29, 54),
                       fractions.Fraction(17, 27), fractions.Fraction(7, 54),
                       fractions.Fraction(-1, 27), fractions.Fraction(17, 27),
                       fractions.Fraction(5, 108), fractions.Fraction(7, 54),
                       fractions.Fraction(7, 54), fractions.Fraction(-1, 27),
                       fractions.Fraction(7, 54), fractions.Fraction(5, 108),
                       fractions.Fraction(-10, 27), fractions.Fraction(-29, 54),
                       fractions.Fraction(-29, 54), fractions.Fraction(-29, 54),
                       fractions.Fraction(-29, 54), fractions.Fraction(7, 54),
                       fractions.Fraction(17, 27), fractions.Fraction(-1, 27),
                       fractions.Fraction(-1, 27), fractions.Fraction(17, 27),
                       fractions.Fraction(-1, 27), fractions.Fraction(17, 27))]

        for n in range(3):
            myleglist = base_objects.LegList()

            myleglist.append(base_objects.Leg({'id':21,
                                             'state':'initial'}))
            myleglist.append(base_objects.Leg({'id':21,
                                             'state':'initial'}))

            myleglist.extend([base_objects.Leg({'id':21,
                                                'state':'final'})] * (n + 1))

            myprocess = base_objects.Process({'legs':myleglist,
                                            'model':self.mymodel})

            myamplitude = diagram_generation.Amplitude()

            myamplitude.set('process', myprocess)

            myamplitude.generate_diagrams()

            col_basis = color_amp.ColorBasis(myamplitude, self.mymodel)

            col_matrix = color_amp.ColorMatrix(col_basis, Nc=3)

            # Check diagonal
            for i in range(len(col_basis.items())):
                self.assertEqual(col_matrix.col_matrix_fixed_Nc[(i, i)],
                                 (goal[n], 0))

            # Check first line
            for i in range(len(col_basis.items())):
                self.assertEqual(col_matrix.col_matrix_fixed_Nc[(0, i)],
                                 (goal_line1[n][i], 0))

    def test_color_matrix_multi_quarks(self):
        """Test the color matrix building for qq~ > n*(qq~) with n up to 2"""

        goal = [fractions.Fraction(2, 1),
                fractions.Fraction(72, 54)]



        goal_line1 = [(fractions.Fraction(2, 1), fractions.Fraction(-2, 3)),
                      (fractions.Fraction(4, 3), fractions.Fraction(-5, 27),
                       fractions.Fraction(7, 6), fractions.Fraction(-1, 3),
                       fractions.Fraction(1, 9), fractions.Fraction(-7, 18),
                       fractions.Fraction(-5, 27), fractions.Fraction(-7, 18),
                       fractions.Fraction(1, 18), fractions.Fraction(31, 27),
                       fractions.Fraction(-5, 27), fractions.Fraction(-7, 18),
                       fractions.Fraction(-1, 3), fractions.Fraction(31, 27),
                       fractions.Fraction(-1, 3), fractions.Fraction(-4, 9),
                       fractions.Fraction(1, 9), fractions.Fraction(7, 6),
                       fractions.Fraction(-1, 6), fractions.Fraction(-5, 27),
                       fractions.Fraction(-1, 54), fractions.Fraction(1, 9),
                       fractions.Fraction(1, 18), fractions.Fraction(1, 18),
                       fractions.Fraction(4, 27), fractions.Fraction(-1, 54),
                       fractions.Fraction(5, 9), fractions.Fraction(1, 9),
                       fractions.Fraction(-4, 9), fractions.Fraction(-1, 54),
                       fractions.Fraction(71, 54), fractions.Fraction(1, 18),
                       fractions.Fraction(-7, 18), fractions.Fraction(-1, 3),
                       fractions.Fraction(-1, 54), fractions.Fraction(5, 9))
                      ]

        for n in range(2):
            myleglist = base_objects.LegList()

            myleglist.append(base_objects.Leg({'id':2,
                                             'state':'initial'}))
            myleglist.append(base_objects.Leg({'id':-2,
                                             'state':'initial'}))

            myleglist.extend([base_objects.Leg({'id':2,
                                                'state':'final'}),
                             base_objects.Leg({'id':-2,
                                                'state':'final'})] * (n + 1))

            myprocess = base_objects.Process({'legs':myleglist,
                                            'model':self.mymodel})

            myamplitude = diagram_generation.Amplitude()

            myamplitude.set('process', myprocess)

            myamplitude.generate_diagrams()

            col_basis = color_amp.ColorBasis(myamplitude, self.mymodel)

            col_matrix = color_amp.ColorMatrix(col_basis, Nc=3)

            # Check diagonal
            for i in range(len(col_basis.items())):
                self.assertEqual(col_matrix.col_matrix_fixed_Nc[(i, i)],
                                 (goal[n], 0))

            # Check first line
            for i in range(len(col_basis.items())):
                self.assertEqual(col_matrix.col_matrix_fixed_Nc[(0, i)],
                                 (goal_line1[n][i], 0))

    def test_color_matrix_Nc_restrictions(self):
        """Test the Nc power restriction during color basis building """

        goal = [fractions.Fraction(3, 8),
                fractions.Fraction(-9, 4),
                fractions.Fraction(45, 16)]

        for n in range(3):
            myleglist = base_objects.LegList()

            myleglist.append(base_objects.Leg({'id':21,
                                             'state':'initial'}))
            myleglist.append(base_objects.Leg({'id':21,
                                             'state':'initial'}))

            myleglist.extend([base_objects.Leg({'id':21,
                                                'state':'final'})] * 2)

            myprocess = base_objects.Process({'legs':myleglist,
                                            'model':self.mymodel})

            myamplitude = diagram_generation.Amplitude()

            myamplitude.set('process', myprocess)

            myamplitude.generate_diagrams()

            col_basis = color_amp.ColorBasis(myamplitude, self.mymodel)

            col_matrix = color_amp.ColorMatrix(col_basis, Nc=3,
                                                  Nc_power_min=n,
                                                  Nc_power_max=2 * n)

            for i in range(len(col_basis.items())):
                self.assertEqual(col_matrix.col_matrix_fixed_Nc[(i, i)],
                                 (goal[n], 0))


    def test_color_matrix_fixed_indices(self):
        """Test index fixing for immutable color string"""

        immutable1 = (('f', (1, -1, -3)), ('T', (-1, -3, 4)))
        immutable2 = (('d', (1, -2, -1)), ('T', (-1, -2, 4)))

        self.assertEqual(color_amp.ColorMatrix.fix_summed_indices(immutable1,
                                                               immutable2),
                         (('d', (1, -2, -5)), ('T', (-5, -2, 4))))

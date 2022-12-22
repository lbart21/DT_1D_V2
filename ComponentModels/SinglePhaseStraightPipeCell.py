import math as m
import importlib
import sys
from Algorithms.DesignToolAlgorithmV2.FluidModel.FlowState import FlowState
from gdtk.gas import GasModel, GasState

class SinglePhaseStraightPipeCell():
    def __init__(self, cell_ID, fluidPair, label) -> None:
        self.GEO = {}
        self.flowState = {}
        self.cell_ID = cell_ID
        self.fluidPair = fluidPair
        self.WestInterface = None
        self.EastInterface = None
        self.label = label
        self.phase = "Single"
        self.InteriorCellFlag = True

        self.conservedProperties = {
            "mass"      : 0.0,
            "xMom"      : 0.0,
            "energy"    : 0.0
        }

        eilmer_fluid_name = fluidPair["fluid"]
        gm = GasModel(eilmer_fluid_name)
        gs = GasState(gm)
        self.fs = FlowState(model = gm, state = gs) #fs = flow state, not fluid state                                                                # object with constants already defined in it (gamma, Cp, etc), 
                                                                                            # then update is inherent from flowState object, so don't have to reimport every time.
                                                                                            # Same occurs in left and right states of interface.
        
    def fillGeometry(self, Geometry):
        self.GEO = Geometry
        
    def fillProps(self, prop1, prop2, propsGiven, vel_x):
        if propsGiven == "pT":
            self.fs.fluid_state.p = prop1
            self.fs.fluid_state.T = prop2
            self.fs.vel_x = vel_x
            self.fs.fluid_state.update_thermo_from_pT() 
        if propsGiven == "rhoP":
            self.fs.fluid_state.p = prop1
            self.fs.fluid_state.rho = prop2
            self.fs.vel_x = vel_x
            self.fs.fluid_state.update_thermo_from_rhop()
        self.fs.fluid_state.update_sound_speed()
        self.initialiseConservedProperties()

    def updatePrimativeProperties(self):
        new_density = self.conservedProperties["mass"] 
        new_vel_x = self.conservedProperties["xMom"] / self.conservedProperties["mass"] 
        new_u = self.conservedProperties["energy"] / self.conservedProperties["mass"] - 0.5 * new_vel_x ** 2.0
        self.fs.vel_x = new_vel_x
        self.fs.fluid_state.rho = new_density
        self.fs.fluid_state.u = new_u
        self.fs.fluid_state.update_thermo_from_rhou()
        self.fs.fluid_state.update_sound_speed()
        
    def initialiseConservedProperties(self):
        self.conservedProperties["mass"] = self.fs.fluid_state.rho
        self.conservedProperties["xMom"] = self.fs.fluid_state.rho * self.fs.vel_x
        self.conservedProperties["energy"] = self.fs.fluid_state.rho * (self.fs.fluid_state.u + 0.5 * self.fs.vel_x ** 2)

    def maxAllowableDt(self, cfl):
        return cfl * self.GEO["dx"] / (abs(self.fs.vel_x) + self.fs.fluid_state.a)
    
    def update_properties(self):
        self.updatePrimativeProperties()

    def completeCellMethods(self, cellArray, dt_inv):
        pass
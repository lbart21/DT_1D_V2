from Algorithms.DesignToolAlgorithmV2.ComponentModels.SinglePhaseInterface import SinglePhaseInterface
from Algorithms.DesignToolAlgorithmV2.ComponentModels.SinglePhaseConicalNozzleCell import SinglePhaseConicalNozzleCell
from Algorithms.DesignToolAlgorithmV2.ComponentModels.meshObject import meshObject
import numpy as np

class SinglePhaseConicalNozzle():
    def __init__(self, Geometry, prop1, prop2, propsGiven, vel_x, Eilmer_fluid_file, \
                        reconstructionScheme, limiter, reconstructionProperties, updateFrom, componentLabel, fluxScheme) -> None:
        """
        Geometry = [D1, D2, L, nCells]
        """
        nCells = Geometry[3]
        self.meshObject = meshObject(nCells = nCells)

        self.fluidPairs = {}
        self.fluidPairs["fluid"] = Eilmer_fluid_file  #Dictionary of strings of .lua file names to generate Eilmer GasModels and hence GasStates
                                                            
        self.meshObject.componentLabels = [componentLabel]

        ### Define cells
        self.initialiseCells(Geometry = Geometry, prop1 = prop1, \
                                prop2 = prop2, propsGiven = propsGiven, \
                                vel_x = vel_x, componentLabel = componentLabel)
            
        ### Define interfaces
        self.initialiseInterfaces(Geometry = Geometry, reconstructionScheme = reconstructionScheme, \
                                    limiter = limiter, reconstructionProperties = reconstructionProperties, \
                                    updateFrom = updateFrom, fluxScheme = fluxScheme)

        ### Form connections
        self.connectCellsToInterfaces()

    def initialiseCells(self, Geometry, prop1, prop2, propsGiven, vel_x, componentLabel):
        [D1, D2, L, nCells] = Geometry
        self.nCells = nCells
        
        for cell in range(nCells):
            cellObject = SinglePhaseConicalNozzleCell(cell_ID = cell, fluidPair = self.fluidPairs, label = componentLabel)
            dx = L / nCells
            D_L = self.D_at_x(D1 = D1, D2 = D2, x = cell * dx, L = L)
            D_c = self.D_at_x(D1 = D1, D2 = D2, x = (0.5 + cell) * dx, L = L)
            D_R = self.D_at_x(D1 = D1, D2 = D2, x = (1.0 + cell) * dx, L = L)
            
            GEO = {
                "dx"    :   dx,
                "dV"    :   np.pi * (D_L ** 2.0 + D_L * D_R + D_R ** 2.0) * dx / 12.0,
                "A_c"   :   0.25 * np.pi * D_c ** 2.0,
                "A_s"   :   0.5 * np.pi * (D_L + D_R) * dx * (1.0 + (0.5 * (D_R - D_L) / dx) ** 2.0) ** 0.5,
                "pos_x" :   (0.5 + cell) * dx
            }
            cellObject.fillGeometry(Geometry = GEO)
            cellObject.fillProps(prop1 = prop1, prop2 = prop2, \
                                        propsGiven = propsGiven, vel_x = vel_x)
            self.meshObject.cellArray[cell] = cellObject
        
    def D_at_x(self, D1, D2, x, L):
        return D1 + (D2 - D1) * x / L

    def initialiseInterfaces(self, Geometry, reconstructionScheme, limiter, reconstructionProperties, updateFrom, fluxScheme):
        self.meshObject.interfaceArray = [None] * (self.nCells + 1)
        [D1, D2, L, nCells] = Geometry
        for interface in range(self.nCells + 1):
            interfaceObject = SinglePhaseInterface(interface_ID = interface, nL = interface, nR = self.nCells - interface, \
                                                    fluidPair = self.fluidPairs, fluxScheme = fluxScheme, \
                                                    reconstructionScheme = reconstructionScheme, limiter = limiter, \
                                                    reconstructionProperties = reconstructionProperties, updateFrom = updateFrom)
            D = self.D_at_x(D1 = D1, D2 = D2, x = interface * L / nCells, L = L)
            GEO = {"A"  : 0.25 * np.pi * D ** 2}
            interfaceObject.fillGeometry(Geometry = GEO)
            self.meshObject.interfaceArray[interface] = interfaceObject
        
        self.meshObject.boundaryInterfaceIDs = [0, self.nCells]
        
    def connectCellsToInterfaces(self):
        self.meshObject.mapCellIDToWestInterfaceIdx = [None] * self.nCells
        self.meshObject.mapCellIDToEastInterfaceIdx = [None] * self.nCells
        self.meshObject.mapInterfaceIDToWestCellIdx = [None] * (self.nCells + 1)
        self.meshObject.mapInterfaceIDToEastCellIdx = [None] * (self.nCells + 1)

        for array_idx in range(len(self.meshObject.cellArray)):
            self.meshObject.mapCellIDToWestInterfaceIdx[array_idx] = array_idx
            self.meshObject.mapCellIDToEastInterfaceIdx[array_idx] = array_idx + 1
            self.meshObject.mapInterfaceIDToWestCellIdx[array_idx + 1] = array_idx
            self.meshObject.mapInterfaceIDToEastCellIdx[array_idx] = array_idx
        
    def addBoundaryConditions(self, BC):
        self.meshObject.boundaryConditions.append(BC)
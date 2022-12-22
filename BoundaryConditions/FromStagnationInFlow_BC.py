from copy import deepcopy

def FromStagnationInFlow_BC(mesh, BC):
    """
    [p_stag, T_stag] = BC[1][2]
    Take p_stag and T_stag to create a stagnation state. Use velocity on inside of 
    boundary and stagnation enthalpy to find static enthalpy. Update properties from 
    stagnation entropy and static enthalpy. All cells have the interior cell's velocity.
    Velocity is set to 0 if flow is out of boundary.
    Then update the flow properties to complete the state.
    """
    vel_x_boundary = mesh.cellArray[0].fs.vel_x
    [p_stag, T_stag] = BC[1][2]
    bulk_speed = max(0.0, vel_x_boundary) # 0.0 if vel_x_boundary negative, vel_x_boundary if positive, 
                                          # this assumes flow in is always on
                                          # the west boundary 
                                          # TODO adjust this to allow BC on east boundary
    flowState = deepcopy(mesh.cellArray[0].fs)
    flowState.fluid_state.p = p_stag
    flowState.fluid_state.T = T_stag
    flowState.vel_x = bulk_speed
    flowState.fluid_state.update_thermo_from_pT()
    stagnation_enthalpy = flowState.fluid_state.enthalpy
    static_enthalpy = stagnation_enthalpy - 0.5 * bulk_speed ** 2.0

    flowState.fluid_state.update_thermo_from_hs(h = static_enthalpy, s = flowState.fluid_state.entropy)

    for cell in range(len(mesh.cellArray)):
        mesh.cellArray[cell].fs.vel_x = flowState.vel_x
        mesh.cellArray[cell].fs.fluid_state.copy_values(flowState.fluid_state)
        #print(flowState.fluid_state.p)
        #print(mesh.cellArray[cell].flowState.fluid_state.p)
    #print("printing in FromStagnationInFlow_BC module")
    #for cell in range(len(mesh.cellArray)):
        #print(mesh.cellArray[cell].fs.fluid_state.p)
    return mesh
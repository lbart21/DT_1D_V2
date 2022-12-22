def SupersonicInFlow_BC(mesh, BC):
    """
    Simply put specified flow state which is in index [1][2] of BC list in order
    [vel_x, p, T] = BC[1][2]
    Then update the flow properties to complete the state.
    All cells have the same properties
    """
    for cell in range(len(mesh.cellArray)):
        [vel_x, p, T] = BC[1][2]
        mesh.cellArray[cell].fs.vel_x = vel_x
        mesh.cellArray[cell].fs.fluid_state.p = p
        mesh.cellArray[cell].fs.fluid_state.T = T
        mesh.cellArray[cell].fs.fluid_state.update_thermo_from_pT()
        mesh.cellArray[cell].fs.fluid_state.update_sound_speed()

    return mesh
"""
Utility functions for the mdi-ani-tutorial driver.
"""

import argparse
import mdi

import numpy as np
import torch, torchani

from typing import Union

device = torch.device("cpu")
model = torchani.models.ANI2x(periodic_table_index=True).to(device)


def create_parser():
    """Create the parser for the mdi-ani-tutorial driver"""

    parser = argparse.ArgumentParser(description="mdi-ani-tutorial Driver")

    parser.add_argument(
        "-mdi",
        help="flags for mdi.",
        default=None,
        type=str,
    )

    # add any additional arguments here

    return parser


def connect_to_engines(nengines):
    """Connect to the engines.
    
    Parameters
    ----------
    nengines : int
        The number of engines to connect to.
    
    Returns
    -------
    dict
        A dictionary of engines. The keys corresponds to the engine names.
    """

    engines = {}
    for iengine in range(nengines):
        comm = mdi.MDI_Accept_Communicator()

        # Check the name of the engine
        mdi.MDI_Send_Command("<NAME", comm)
        engine_name = mdi.MDI_Recv(mdi.MDI_NAME_LENGTH, mdi.MDI_CHAR, comm)

        engines[engine_name] = comm

    return engines

def mass_to_atomic_number(masses):
    conversion_dict =  {
    1.008: 1,     # Hydrogen
    12.011: 6,    # Carbon
    14.007: 7,    # Nitrogen
    15.999: 8,    # Oxygen
    18.998: 9,    # Fluorine
    35.453: 17,   # Chlorine
    32.065: 16    # Sulfur
}

    atomic_numbers = [ [ conversion_dict[mass] for mass in masses ] ]

    return atomic_numbers

def calculate_ANI_force(masses: Union[np.ndarray, list[float]], coordinates: np.ndarray, cell: np.ndarray):
    """
    Calculate the ANI2x force for system of atoms.

    Parameters
    ----------
    masses :
        An array or list containing the masses of the atoms.
    coordinates :
        An array containing the 3D coordinates of the atoms.
    cell : 
        A 3x3 array representing the periodic boundary conditions of the simulation cell.

    Returns
    -------
    np.ndarray
        A flattened array of forces acting on each atom, reshaped to be 1-dimensional.
    """

    coords_reshape = coordinates.reshape(1, -1, 3)

    elements = mass_to_atomic_number(masses)

    torch_coords = torch.tensor(coords_reshape, requires_grad=True, device=device).float()
    elements_torch = torch.tensor(elements, device=device)
    pbc = torch.tensor([True, True, True], device=device)
    cell = torch.tensor(cell.reshape(3, 3), device=device).float()

    # Calculate the energy and forces   
    energy = model((elements_torch, torch_coords), cell=cell, pbc=pbc).energies
    derivative = torch.autograd.grad(energy, torch_coords)[0]
    forces = -derivative.squeeze()

    forces_np = forces.cpu().detach().numpy()

    # reshape to be 1-dimensional like MDI wants
    forces_np = forces_np.reshape(-1)

    return forces_np

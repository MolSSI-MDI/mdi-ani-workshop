"""
Calculate energies using Psi4 and ANI2x for water clusters.
"""

import glob
import os 
import time

import psi4
import torch
import torchani

import numpy as np
import matplotlib.pyplot as plt

import tabulate


device = torch.device("cpu")
model = torchani.models.ANI2x(periodic_table_index=True).to(device)

def elements_to_atomic_numbers(elements):
    """
    Convert element symbols to atomic numbers using a predefined dictionary.

    Parameters
    ----------
    elements : list of str
        A list of element symbols.

    Returns
    -------
    list of int
        A list of atomic numbers corresponding to the element symbols.
    """

    conversion_dict =  {
    "H": 1,     # Hydrogen
    "C": 6,    # Carbon
    "N": 7,    # Nitrogen
    "O": 8,    # Oxygen
    "F": 9,    # Fluorine
    "Cl": 17,   # Chlorine
    "S": 16    # Sulfur
    }

    return [ conversion_dict[element] for element in elements ]

def calculate_ANI_energy(xyz_file):
    """
    Calculate the ANI2x energy for system of atoms.

    Parameters
    ----------
    elements:
        An array or list containing the elements of the atoms in the system.
    coordinates:
        An array containing the 3D coordinates of the atoms.
    
    Returns
    -------
    tuple(float, float)
        The energy of the system and the time taken to calculate the energy.
    """

    coordinates = np.loadtxt(xyz_file, skiprows=2, usecols=(1, 2, 3))
    elements = np.loadtxt(xyz_file, skiprows=2, usecols=0, dtype=str)

    coords_reshape = coordinates.reshape(1, -1, 3)
    atomic_numbers = elements_to_atomic_numbers(elements)

    torch_coords = torch.tensor(coords_reshape, requires_grad=True, device=device).float()
    atomic_numbers_torch = torch.tensor([atomic_numbers], device=device)
   
    # Calculate the energy
    start = time.time() 
    energy = model((atomic_numbers_torch, torch_coords)).energies
    end = time.time()   
    
    # Return the energy
    return energy.item(), end - start   

def calculate_Psi4_energy(xyz_file, name=None):
    """
    Calculate the energy of a system using Psi4 and the wb97x/6-31g* level of theory.

    Parameters
    ----------
    xyz_file:
        The path to the xyz file.
    name:   
        The name of the output file. If not provided, the name of the xyz file will be used.

    Returns
    -------
    tuple(float, float)
        The energy of the system as calculated by Psi4 using the wb97x/6-31g* level of theory.    
    """

    with open(xyz_file, 'r') as file:
        xyz_data = file.read()
    
    if not name:
        name = os.path.basename(xyz_file).split(".")[0]

    # set the geometry for Psi4
    psi4.geometry(xyz_data)
    
    # set output file for Psi4
    psi4.set_output_file(F'{name}.dat', False)
    
    # calculate the energy
    start = time.time()
    psi4_energy = psi4.energy("wb97x/6-31g*")
    end = time.time()   

    return psi4_energy, end - start


if __name__ == "__main__":

    xyz_files = glob.glob("xyz/scaling/*.xyz")

    energies = []
    times = []
    differences = []   

    for xyz in xyz_files:
        ani_energy, ani_time = calculate_ANI_energy(xyz)
        psi4_energy, psi4_time = calculate_Psi4_energy(xyz)

        n_water = int(os.path.basename(xyz).split(".")[0].split("_")[1])

        energies.append((n_water, ani_energy, psi4_energy))
        times.append((n_water, ani_time, psi4_time))
        differences.append((n_water, ani_energy - psi4_energy))

    # Sort the results
    energies = sorted(energies)
    times = sorted(times)
    differences = sorted(differences)

    # Print energies
    energy_headers = ["Number of Water Molecules", "ANI Energy (Ha)", "Psi4 Energy (Ha)"]
    print(tabulate.tabulate(energies, headers=energy_headers, tablefmt="grid"))

    # Print energy differences
    energy_diff_headers = ["Number of Water Molecules", "Energy Difference (Ha)"]
    print(tabulate.tabulate(differences, headers=energy_diff_headers, tablefmt="grid"))

    # Print times
    time_headers = ["Number of Water Molecules", "ANI Time (s)", "Psi4 Time (s)"]
    print(tabulate.tabulate(times, headers=time_headers, tablefmt="grid"))

    # Write the energies to a file
    with open("benchmark_energies.txt", "w") as f:
        f.write("Number of water molecules, ANI Energy (Ha), Psi4 Energy (Ha)\n")
        for energy in energies:
            f.write(f"{energy[0]}, {energy[1]}, {energy[2]}\n")
    
    # Write the timing information to a file
    with open("benchmark_times.txt", "w") as f:
        f.write("Number of water molecules, ANI Time (s), Psi4 Time (s)\n")
        for time in times:
            f.write(f"{time[0]}, {time[1]}, {time[2]}\n")

    # Create a plot of the energy differences
    plt.figure()
    plt.plot([x[0] for x in differences], [x[1] for x in differences], 'o-', label='Energy Difference (ANI - Psi4)')
    plt.xlabel("Number of Water Molecules")
    plt.ylabel("Energy Difference (Ha)")
    plt.legend()

    plt.savefig("energy_differences.png")

    # Create a plot of the timings
    plt.figure()
    plt.plot([x[0] for x in times], [x[1] for x in times], 'o-', label='ANI Time')
    plt.plot([x[0] for x in times], [x[2] for x in times], 's-', label='Psi4 Time')
    plt.xlabel("Number of Water Molecules")
    plt.ylabel("Time (s)")
    plt.legend()

    plt.savefig("timing.png") 

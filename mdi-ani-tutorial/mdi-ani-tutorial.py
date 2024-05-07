import sys
import warnings

# Import the MDI Library
import mdi

# Import MPI Library
try:
    from mpi4py import MPI

    use_mpi4py = True
    mpi_comm_world = MPI.COMM_WORLD
except ImportError:
    use_mpi4py = False
    mpi_comm_world = None

# Import parser
from util import create_parser, connect_to_engines, mass_to_atomic_number, calculate_ANI_force

if __name__ == "__main__":

    # Read in the command-line options
    args = create_parser().parse_args()

    mdi_options = args.mdi

    if mdi_options is None:
        mdi_options = (
            "-role DRIVER -name driver -method TCP -port 8021 -hostname localhost"
        )
        warnings.warn(f"Warning: -mdi not provided. Using default value: {mdi_options}")

    # Initialize the MDI Library
    mdi.MDI_Init(mdi_options)

    # Get the correct MPI intra-communicator for this code
    mpi_comm_world = mdi.MDI_MPI_get_world_comm()

    engines = connect_to_engines(1)

    ###########################
    # Perform the simulation
    ###########################

    # Send the "EXIT" command to each of the engines
    for comm in engines.values():
        mdi.MDI_Send_Command("EXIT", comm)

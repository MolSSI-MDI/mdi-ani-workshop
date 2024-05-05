"""
Utility functions for the mdi-ani-tutorial driver.
"""

import argparse
import mdi


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

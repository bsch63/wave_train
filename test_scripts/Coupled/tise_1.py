from wave_train.hamilton.coupled import Coupled
from wave_train.dynamics.tise import TISE
from wave_train.io.logging import TeeLogger
from os.path import basename, splitext

def coupled_tise(batch_mode):
    # Detect name of this script file (without extension)
    base_name = basename(__file__)
    my_file = splitext(base_name)[0]

    # logging instance: will be initialized with 
    # class for logging to both console and logfile
    logger = None
    if not batch_mode:
        logger = TeeLogger(log_file=my_file + ".log")

    # Set up the coupled excitonic-phononic Hamiltonian for a chain
    hamilton = Coupled(
        n_site=5,                        # number of sites
        periodic=True,                   # periodic boundary conditions
        homogen=True,                    # homogeneous chain/ring
        alpha=1e-1,                      # excitonic site energy
        beta=-1e-2,                      # coupling strength (NN)
        eta=0,                           # constant energy offset
        mass=1,                          # particle mass
        nu=1e-3,                         # position restraints
        omg=1e-3 * 2**(1/2),             # nearest neighbours
        chi=0e-4,                        # exciton-phonon tuning: localized
        rho=0e-4,                        # exciton-phonon tuning: non-symmetric
        sig=2e-4,                        # exciton-phonon tuning: symmetrized
        tau=0e-4,                        # exciton-phonon coupling: pair distance
    )

    # Set up TT representation of the Hamiltonian
    hamilton.get_TT(
        n_basis=[2, 4],                  # size of excitonic basis set
        qtt=False                        # using quantized TT format
    )

    # Set up  TISE solver
    dynamics = TISE(
        hamilton=hamilton,               # choice of Hamiltonian, see above
        n_levels=4,                      # number of energy levels to be calculated
        solver='als',                    # choice of eigensolver for the full system
        eigen='eigs',                    # choice of eigensolver for the micro systems
        ranks=20,                        # rank of initial guess for ALS
        repeats=20,                      # number of sweeps in eigensolver scheme
        conv_eps=1e-8,                   # threshold for detecting convergence of the eigenvalue
        e_est=0.070,                     # estimation: eigenvalues closest to this number
        e_min=0.070,                     # lower end of energy plot axis (if exact energies not available!)
        e_max=0.100,                     # upper end of energy plot axis (if exact energies not available!)
        save_file=my_file+'.pic',        # if not None, generated data will be saved to this file
        load_file=None,                  # if not None, reference data will be loaded from this file
        compare=None                     # type of comparison with reference data
    )

    # Batch mode
    if batch_mode:
        dynamics.solve()                 # Solve TISE *without* visualization

    # Interactive mode: Setup animated visualization
    else:
        from wave_train.graphics.factory import VisualTISE
        graphics = VisualTISE(
            dynamics=dynamics,           # choice of dynamics (EoM), see above
            plot_type='Positions2',      # select your favorite plot type
            plot_expect=True,            # toggle plotting of expectation values
            figure_pos=(100, 50),        # specifying position (x,y) of upper left of figure [in pixels]
            figure_size=(1050, 450),     # specifying size (w,h) of figure [in pixels]
            image_file=my_file+'.png',   # if not None, image (last frame) will be written to this file
            movie_file=my_file+'.mp4',   # if not None, animation will be written to this file
            snapshots=False,             # save each snapshot
            frame_rate=1,                # Frames per second in mp4 animation file
            plot_style={'scaling': 0.025}  # Scaling the classical coordinates
        ).create()
        graphics.solve()                # Solve TISE *with* visualization


if __name__ == '__main__':
    coupled_tise(batch_mode=False)

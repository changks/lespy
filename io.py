import numpy as _np

def empty_array(simulation, n_con=False):
    """ Creates an empty array with the shape dictated by simulation """
    sim=simulation
    if n_con:
        blank=_np.full((sim.domain.ld, sim.ny, sim.nz_tot, sim.n_con), _np.nan, dtype=_np.float64)
    else:
        blank=_np.full((sim.domain.ld, sim.ny, sim.nz_tot), _np.nan, dtype=_np.float64)
    return blank


def write_to_les(array, fname, simulation=None, **kwargs):
    """
    Writes array into a file fname in a format that LES can easily understand
    """
    sim=simulation
    array[sim.nx:] = 0.
    array.T.tofile(fname, **kwargs)
    return


def read_aver(fname, simulation, squeeze=True, return_times=False, **kwargs):
    """Reads aver_* files from LES"""
    sim=simulation
    aver=_np.loadtxt(fname, **kwargs)
    if 'pcon' in fname.lower():
        aver=aver.reshape(-1, sim.n_con, aver.shape[-1], order='C').transpose(0,2,1)
    ndtimes = aver[:,0]
    aver = aver[:,1:]
    if squeeze:
        aver = _np.squeeze(aver)

    if return_times:
        return ndtimes, aver
    else:
        return aver



def readBinary(fname, simulation=None, domain=None, n_con=None, as_DA=True, pcon_index='size'):
    """
    Reads a binary file according to the simulation or domain object passed

    Parameters
    ----------
    fname: string
        path of the binary file you want to open
    simulation: lespy.Simulation
        simulation that contains important information to assemble the file. Mostly
        it's used to get number of points, if temperature is in the file or not and n_con.
    domain: lespy.Domain
        depending on what you're doing, just a domain file suffices
    read_pcon: bool
        if the file is vel_sc, try to read pcon after it finishes reading u,v,w,T.
        It just gives a warning if it fails
    n_con: int
        number of pcon sizes to read. Overwrites n_con from simulation
    only_pcon: bool
        if file is vel_sc, skip u,v,w,T and read just pcon. Makes reading pcon a lot faster.
    """
    from os import path
    from . import Simulation
    import numpy as np

    if isinstance(simulation, str):
        from ..simClass import Simulation as Sim
        simulation = Sim(simulation)

    #---------
    # Trying to be general
    if simulation!=None:
        sim = simulation
        domain = sim.domain
    else:
        if domain==None:
            sim = Simulation(path.dirname(path.abspath(fname)))
            domain = sim.domain
        else:
            sim = Simulation(domain=domain, n_con=n_con)
    #---------

    #---------
    # Useful for later. Might as well do it just once here
    u_nd = domain.nx*domain.ny*domain.nz_tot
    u_nd2 = domain.ld*domain.ny
    #---------

    #---------
    bfile = open(fname, 'rb')
    #---------

    if path.basename(fname).startswith('uv0_jt'):
        u0, v0 = np.fromfile(bfile, dtype=np.float64).reshape(2,-1, order='C')
        u0 = u0.reshape((domain.nx, domain.ny), order='F')
        v0 = v0.reshape((domain.nx, domain.ny), order='F')
        if as_DA:
            u0=sim.DataArray(u0*sim.u_scale, dims=['x', 'y'])
            v0=sim.DataArray(v0*sim.u_scale, dims=['x', 'y'])
        return u0, v0

    #--------------
    # For fortran unformatted direct files you have to skip first 4 bytes
    if fname.endswith('.bin'): bfile.read(4)
    #--------------
    
    #---------
    # Straightforward
    if path.basename(fname).startswith('pcon'):
        if n_con==None:
            n_con = sim.n_con
        p_nd = u_nd*n_con
        pcon = np.fromfile(bfile, dtype=np.float64, count=p_nd).reshape((domain.nx, domain.ny, domain.nz_tot, n_con), order='F')
        pcon *= sim.pcon_scale
        if as_DA:
            pcon=sim.DataArray(pcon, dims=['x', 'y', 'z', pcon_index])
        return pcon
    #---------
    
    #---------
    # Straightforward
    elif path.basename(fname).startswith('theta_jt'):
        T = np.fromfile(bfile, dtype=np.float64, count=u_nd).reshape((domain.nx, domain.ny, domain.nz_tot), order='F')
        T = 2.*sim.t_init - T*sim.t_scale
        if as_DA:
            T=sim.DataArray(T, dims=['x', 'y', 'z'])
        return T
    #---------

    #---------
    # Straightforward
    elif path.basename(fname).startswith('uvw_jt'):
        u = np.fromfile(bfile, dtype=np.float64, count=u_nd).reshape((domain.nx, domain.ny, domain.nz_tot), order='F')
        v = np.fromfile(bfile, dtype=np.float64, count=u_nd).reshape((domain.nx, domain.ny, domain.nz_tot), order='F')
        w = np.fromfile(bfile, dtype=np.float64, count=u_nd).reshape((domain.nx, domain.ny, domain.nz_tot), order='F')
        u = u*sim.u_scale
        v = v*sim.u_scale
        w =-w*sim.u_scale
        if as_DA:
            u=sim.DataArray(u, dims=['x', 'y', 'z_u'])
            v=sim.DataArray(v, dims=['x', 'y', 'z_u'])
            w=sim.DataArray(w, dims=['x', 'y', 'z_w'])
        return u,v,w
    #---------

    #---------
    # Spectra
    elif path.basename(fname).startswith('spec_uvwT'):
        ndz=4*(domain.nx//2)*(domain.nz_tot-1)
        u,v,w,T = np.fromfile(bfile, dtype=np.float32, count=ndz).reshape((4,domain.nx//2, domain.nz_tot-1), order='F')
        print('Not normalized')
        return u,v,w,T
    #---------

    return




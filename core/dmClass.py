
class Domain(object):
    """Class for domain parameters"""
    def __init__(self, nx=None, ny=None, nz=None, nz_tot=None,
                    dx=None, dy=None, dz=None, lx=None, ly=None, lz=None, origin=(0,0,0)):
        """Initialize the class. dx, dy, and dz can be calculated"""
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.nz_tot = nz_tot
        self.ld = 2*((self.nx//2)+1)
        self.origin_node = origin

        self.lx = lx
        self.ly = ly
        self.lz = lz

        self.dx = dx
        self.dy = dy
        self.dz = dz

        self.points = self.nx*self.ny*self.nz
        self.get_resolution()
        self.get_delta()
        self.makeAxes()

    def get_resolution(self):
        """gets the x, y, z resolution if it isn't given"""
        if self.dx==None:
            try:
                self.dx = self.lx/self.nx
            except:
                pass
        if self.dy==None:
            try:
                self.dy = self.ly/self.ny
            except:
                pass
        if self.dz==None:
            try:
                self.dz = self.lz/self.nz
            except:
                pass
        return
    
    def get_delta(self):
        """Gets the characteristic volume box delta"""
        self.delta = (self.dx*self.dy*self.dz)**(1./3.)
        return
    

    def makeAxes(self):
        """Creates the x, y and z axes based on dx and nx"""
        import numpy as np

        x = np.arange(0, self.nx)*self.dx - self.origin_node[0]*self.dx
        y = np.arange(0, self.ny)*self.dy - self.origin_node[1]*self.dy
        z = np.arange(0, self.nz_tot)*self.dz - self.origin_node[2]*self.dz
        self.x = x
        self.y = y
        self.z = z

        return


    def __str__(self):
        buff = """<lespy.domain object>
nx, ny, nz: {self.nx} x {self.ny} x {self.nz} = {self.points} points
dx, dy, dz: {self.dx:.2f} x {self.dy:.2f} x {self.dz:.2f}
lx, ly, lz: {self.lx} x {self.ly} x {self.lz}""".format(**locals())
        return buff

    def __repr__(self):
        buff = """<lespy.domain with {}x{}x{} points>""".format(self.nx, self.ny, self.nz)
        return buff



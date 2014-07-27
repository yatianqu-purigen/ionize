import warnings
from math import sqrt, copysign
from ..viscosity import viscosity


class Ion(object):

    """Describe an ion dissolved in aqueous solution.

    This class draws significantly on Bagha Electrophoresis 2010
    "Ionic strength effects on electrophoretic focusing and separations"
    The ion is defined by a name, and a set of charge states (z).
    Each charge state must have an associated acidity constant (pKa).
    Each charge state must have an associated fully ionized mobility
    (absolute_mobility).

    This is a direct port of the Matlab code written by Lewis Marshall.
    """
    # Weakly private variables
    # These are constants and should not change.
    # Eventually, _T may be  removed from the constants list.
    _F = 96485.34         # Faraday's const.[C/mol]
    _Lpm3 = 1000.0        # Conversion from liters to m^3

    # The following are constants in eqtn 6 of Bahga 2010.
    _Adh = 0.5102         # L^1/2 / mol^1/2, approximate for RT
    _aD = 1.5             # mol^-1/2 mol^-3/2, approximation
    R = 8.314             # J/mol-K
    # The reference properties of the ion are stored in private variables.
    _pKa_ref = []
    _absolute_mobility_ref = []  # m^2/V/s.
    dH = None
    dCp = None

    def __init__(self, name, z, pKa_ref, absolute_mobility_ref,
                 T=25.0, T_ref=25.0):
        """Initialize an ion object."""
        self.name = name
        self.T = T
        self._T_ref = T_ref

        try:
            self.z = [zp for zp in z]
        except:
            self.z = [z]

        try:
            self._pKa_ref = [p for p in pKa_ref]
        except:
            self._pKa_ref = [pKa_ref]

        try:
            self._absolute_mobility_ref = [m for m in absolute_mobility_ref]
        except:
            self._absolute_mobility_ref = [absolute_mobility_ref]

        if T == T_ref:
            self.pKa = self._pKa_ref
            self.absolute_mobility = self._absolute_mobility_ref
        else:
            _Adh = self.get_Adh()
            self.pKa = self.correct_pKa()

            self.absolute_mobility =\
                [viscosity(self._T_ref)/viscosity(self.T)*m
                 for m in self._absolute_mobility_ref]

        self.actual_mobility = None                 # Fill by solution

        # Check that z is a vector of integers
        assert all([isinstance(zp, int) for zp in self.z]), "z contains non-integer"

        # Check that the pKa is a vector of numbers of the same length as z.
        assert len(self.pKa) == len(self.z), "pKa is not the same length as z"

        assert len(self.absolute_mobility) == len(self.z), '''absolute_mobility is not
                                                    the same length as z'''

        # Force the sign of the fully ionized mobilities to match the sign of
        # the charge. This command provides a warning.
        if not all([copysign(z, m) == z for z, m in zip(self.z,
                    self.absolute_mobility)]):
            self.absolute_mobility = [copysign(m, z) for z, m in zip(self.z,
                                      self.absolute_mobility)]
            warnings.warn('Mobility signs and charge signs don\'t match. Forcing.')

        # After storing the ion properties, ensure that the properties are
        # sorted in order of charge. All other ion methods assume that the
        # states will be sorted by charge.
        self = self.z_sort()

    def z_sort(obj):
        """Sort the charge states from lowest to highest."""
        # Zip the lists together and sort them by z.
        obj.z, obj.pKa, obj.absolute_mobility = zip(*sorted(zip(obj.z, obj.pKa,
                                                    obj.absolute_mobility)))
        obj.z = list(obj.z)
        obj.pKa = list(obj.pKa)
        obj.absolute_mobility = list(obj.absolute_mobility)

        full = set(range(min(obj.z), max(obj.z)+1, 1)) - {0}
        assert set(obj.z) ^ full == set(), "Charge states missing."

        return obj

    def Ka(obj):
        """Return the Kas based on the pKas.

        These values are not corrected for ionic strength.
        """
        Ka = [10.**-p for p in obj.pKa]
        return Ka

    def z0(obj):
        """Return the list of charge states with 0 inserted."""
        z0 = [0]+obj.z
        z0 = sorted(z0)
        return z0

    from ..dielectric import dielectric

    def get_Adh(obj, T=None):
        if not T:
            T = obj.T
        T_ref = 25
        Adh_ref = 0.5102
        d = obj.dielectric(T)
        d_ref = obj.dielectric(T)
        Adh = Adh_ref * ((T_ref+273.15)*d_ref/(T+273.15)/d)**(-1.5)
        return Adh

    def __str__(obj):
        """Return a string representing the ion."""
        return ("Ion object -- " + obj.name + ": " +
                str(dict(zip(obj.z, zip(obj.pKa, obj.absolute_mobility)))))

    def __repr__(obj):
        """Return a representation of the ion."""
        return obj.__str__()

    from ionization_fraction import ionization_fraction
    from activity_coefficient import activity_coefficient
    from effective_mobility import effective_mobility
    from Ka_eff import Ka_eff
    from L import L
    from molar_conductivity import molar_conductivity
    from robinson_stokes_mobility import robinson_stokes_mobility
    from correct_pKa import correct_pKa, vant_hoff, clark_glew

if __name__ == '__main__':
    hcl = Ion('hydrochloric acid', -1, -2.0, -7.91e-8)
    try:
        pass
        poor_ion = Ion('poor', [1.5], [-2], [3])
    except:
        print "Poor ion rejected."
        pass
    print hcl
    print "Name:", hcl.name
    print "Z:", hcl.z
    print "pKa:", hcl.pKa
    print "Absolute mobility:", hcl.absolute_mobility
    print "Robinson-Stokes mobility at 0.1 M:",\
        hcl.robinson_stokes_mobility(.1)
    print "Ka:", hcl.Ka()
    print "z0:", hcl.z0()
    print "L:", hcl.L()
    print "Ionization fraction at pH 7:", hcl.ionization_fraction(7)
    print "Activity coefficient at 0.3 M:", hcl.activity_coefficient(.03)
    print hcl.__dict__
    help(Ion)

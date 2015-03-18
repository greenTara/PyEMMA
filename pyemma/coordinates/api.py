r"""User-API for the pyemma.coordinates package

"""

__docformat__ = "restructuredtext en"


from pyemma.util.annotators import deprecated

from discretizer import Discretizer
# io
from io.feature_reader import FeatureReader
from io.data_in_memory import DataInMemory
# transforms
from transform.pca import PCA
from transform.tica import TICA
# clustering
from clustering.kmeans import KmeansClustering
from clustering.uniform_time import UniformTimeClustering
from clustering.regspace import RegularSpaceClustering
from clustering.assign import AssignCenters


__author__ = "Frank Noe, Martin Scherer"
__copyright__ = "Copyright 2015, Computational Molecular Biology Group, FU-Berlin"
__credits__ = ["Benjamin Trendelkamp-Schroer", "Martin Scherer", "Frank Noe"]
__license__ = "FreeBSD"
__version__ = "2.0.0"
__maintainer__ = "Martin Scherer"
__email__ = "m.scherer AT fu-berlin DOT de"

__all__ = ['discretizer',
           'feature_reader',
           'memory_reader',
           'tica',
           'pca',
           'cluster_regspace',
           'cluster_kmeans',
           'cluster_uniform_time',
           'cluster_assign_centers',
           'kmeans',
           'regspace',
           'assign_centers',
           'uniform_time',
           ]


def discretizer(reader,
                transform=None,
                cluster=KmeansClustering(n_clusters=100)):
    """
    Constructs a discretizer object, which processes all data


    Parameters
    ----------

    reader : instance of :class:`pyemma.coordinates.io.reader.ChunkedReader`
        the reader instance provides access to the data. If you are working with
        MD data, you most likely want to use a FeatureReader.

    transform : instance of Transformer
        an optional transform like PCA/TICA etc.

    cluster : instance of clustering Transformer (optional)
        a cluster algorithm to assign transformed data to discrete states. By
        default we use Kmeans clustering with k=100


    Examples
    --------

    Construct a discretizer pipeline processing all coordinates of trajectory 
    "traj01.xtc" with a PCA transformation and cluster the principle components
    with uniform time clustering:

    >>> reader = feature_reader(['traj01.xtc'], 'topology.pdb')
    >>> transform = pca(dim=2)
    >>> cluster = uniform_time(n_clusters=100)
    >>> disc = discretizer(reader, transform, cluster)

    Finally you want to run the pipeline
    >>> disc.run()


    Access the the discrete trajectories and saving them to files:

    >>> disc.dtrajs
    [array([0, 0, 1, 1, 2, ... ])]

    This will store the discrete trajectory to "traj01.dtraj":

    >>> disc.save_dtrajs()

    """
    return Discretizer(reader, transform, cluster)

#==============================================================================
#
# READERS
#
#==============================================================================


def feature_reader(trajfiles, topfile):
    r"""Constructs a molecular feature reader.

    Parameters
    ----------

    trajfiles : list of str
        list of filenames to read sequentially
    topfile : str
        path to a topology file (eg. pdb)

    Returns
    -------

    """
    return FeatureReader(trajfiles, topfile)


def memory_reader(data):
    r"""Constructs a reader from an in-memory ndarray.

    Parameters
    ----------
    data : (N,d) ndarray
        array with N frames of d dimensions

    Returns
    -------
    obj : :class:`DataInMemory`

    """
    return DataInMemory(data)


#=========================================================================
#
# TRANSFORMATION ALGORITHMS
#
#=========================================================================


def pca(data=None, dim=2):
    r"""Constructs a PCA object.

    Parameters
    ----------

    data : ndarray (N, d)
        with the data, if available. When given, the PCA is
        immediately parametrized.

    dim : int
        the number of dimensions to project onto

    Returns
    -------
    obj : a PCA transformation object
    """
    res = PCA(dim)
    if data is not None:
        inp = DataInMemory(data)
        res.data_producer = inp
        res.parametrize()
    return res


def tica(data=None, lag=10, dim=2):
    r"""Time-lagged independent component analysis (TICA).

    Parameters
    ----------
    data : ndarray(N, d), optional
        array with the data, if available. When given, the TICA transformation
        is immediately computed and can be used to transform data.
    lag : int, optional, default = 10
        the lag time, in multiples of the input time step
    dim : int, optional, default = 2
        the number of dimensions to project onto

    Returns
    -------
    tica : a :class:`pyemma.coordinates.transform.TICA` transformation object

    Notes
    -----
    When data is given, the transform is immediately computed.
    Otherwise, an empty TICA object is returned.

    Given a sequence of multivariate data :math:`X_t`, computes the mean-free
    covariance and time-lagged covariance matrix:

    .. math::

        C_0 &=      (X_t - \mu)^T (X_t - \mu) \\
        C_{\tau} &= (X_t - \mu)^T (X_t + \tau - \mu)

    and solves the eigenvalue problem

    .. math:: C_{\tau} r_i = C_0 \lambda_i r_i

    where :math:`r_i` are the independent components and :math:`\lambda_i` are
    their respective normalized time-autocorrelations. The eigenvalues are
    related to the relaxation timescale by

    .. math:: t_i = -\tau / \ln |\lambda_i|

    When used as a dimension reduction method, the input data is projected
    onto the dominant independent components.

    References
    ----------
    .. [1] Perez-Hernandez G, F Paul, T Giorgino, G De Fabritiis and F Noe. 2013.
    Identification of slow molecular order parameters for Markov model construction
    J. Chem. Phys. 139, 015102. doi: 10.1063/1.4811489

    """
    res = TICA(lag, dim)
    if data is not None:
        inp = DataInMemory(data)
        res.data_producer = inp
        res.parametrize()
    return res


#=========================================================================
#
# CLUSTERING ALGORITHMS
#
#=========================================================================

@deprecated
def kmeans(data=None, k=100, max_iter=1000):
    return cluster_kmeans(data, k, max_iter)


def cluster_kmeans(data=None, k=100, max_iter=1000):
    r"""Constructs a k-means clustering object.

    Parameters
    ----------
    data: ndarray
        input data, if available in memory
    k: int
        the number of cluster centers

    Returns
    -------
    kmeans : A KmeansClustering object

    Examples
    --------

    >>> traj_data = [np.random.random((100, 3)), np.random.random((100,3))
    >>> clustering = kmeans(traj_data, n_clusters=20)
    >>> clustering.dtrajs
    [array([0, 0, 1, ... ])]

    """
    res = KmeansClustering(n_clusters=k, max_iter=max_iter)
    if data is not None:
        inp = DataInMemory(data)
        res.data_producer = inp
        res.parametrize()
    return res


@deprecated
def uniform_time(data=None, k=100):
    return cluster_uniform_time(data, k)


def cluster_uniform_time(data=None, k=100):
    r"""Constructs a uniform time clustering object.

    Parameters
    ----------
    data : ndarray(N, d)
        input data, if available in memory
    k : int
        the number of cluster centers

    Returns
    -------
        A UniformTimeClustering object

    """
    res = UniformTimeClustering(k)
    if data is not None:
        inp = DataInMemory(data)
        res.data_producer = inp
        res.parametrize()
    return res


@deprecated
def regspace(data=None, dmin=-1, max_centers=1000):
    return cluster_regspace(data, dmin, max_centers)


def cluster_regspace(data=None, dmin=-1, max_centers=1000):
    r"""Constructs a regular space clustering object.

    Parameters
    ----------
    data : ndarray(N, d)
        input data, if available in memory
    dmin : float
        the minimal distance between cluster centers
    max_centers : int (optional), default=1000
        If max_centers is reached, the algorithm will stop to find more centers,
        but this may not approximate the state space well. It is maybe better
        to increase dmin then.

    Returns
    -------
    obj : A RegularSpaceClustering object

    """
    if dmin == -1:
        raise ValueError("provide a minimum distance for clustering")
    res = RegularSpaceClustering(dmin)
    if data is not None:
        inp = DataInMemory(data)
        res.data_producer = inp
        res.parametrize()
    return res


@deprecated
def assign_centers(data=None, centers=None):
    return cluster_assign_centers(data, centers)


def cluster_assign_centers(data=None, centers=None):
    r"""Assigns given (precalculated) cluster centers.

    If you already have cluster centers from somewhere, you use this
    to assign your data to the centers.

    Parameters
    ----------
    clustercenters : path to file (csv) or ndarray
        cluster centers to use in assignment of data

    Returns
    -------
    obj : AssignCenters

    Examples
    --------

    Load data to assign to clusters from 'my_data.csv' by using the cluster
    centers from file 'my_centers.csv'

    >>> data = np.loadtxt('my_data.csv')
    >>> cluster_centers = np.loadtxt('my_centers.csv')
    >>> disc = assign_centers(data, cluster_centers)
    >>> disc.dtrajs
    [array([0, 0, 1, ... ])]

    """
    if centers is None:
        raise ValueError('You have to provide centers in form of a filename'
                         ' or NumPy array')
    res = AssignCenters(centers)
    if data is not None:
        inp = DataInMemory(data)
        res.data_producer = inp
        res.parametrize()
    return res
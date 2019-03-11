
"""CSDModel."""

from __future__ import print_function, division
from .independent_variable import IndependentVariable
from .dependent_variable import DependentVariable
import numpy as np
import json
from scipy.fftpack import fft, fftshift

from copy import deepcopy
from .__version__ import __version__ as version
from ._utils_download_file import download_file_from_url

from urllib.parse import urlparse
from os import path

# from test_files import test_file

script_path = path.dirname(path.abspath(__file__))
# print(script_path)


test_file = {
    "test01": path.normpath(script_path+'/../tests/test01.csdf'),
    "test02": path.normpath(script_path+'/../tests/test02.csdf')
    }


def _import_json(filename):
    res = urlparse(filename)
    if res[0] not in ['file', '']:
        filename = download_file_from_url(filename)
    with open(filename, "rb") as f:
        content = f.read()
        return (json.loads(str(content, encoding="UTF-8")))


def load(filename=None):
    r"""
    Open a `.csdf or `.csdfx` file and return a :ref:`csdm_api` object.

    The file must be a JSON serialization of the CSD Model. ::

        >>> import csdfpy as cp
        >>> data1 = cp.load('local_address/file.csdf')  # doctest: +SKIP
        >>> data2 = cp.load('url_address/file.csdf')  # doctest: +SKIP

    In the above example, ``data1`` is an instance of CSDModel class.

    :params: filename: A local or remote address to the `.csdf or
                        `.csdfx` file.
    :returns: CSDModel object.
    """
    if filename is None:
        raise Exception("'open' method requires a data file address.")

    try:
        dictionary = _import_json(filename)
    except Exception as e:
        raise Exception(e)

    # Create the CSDModel and populate the attribures
    _version = dictionary['CSDM']['version']

    csdm = CSDModel(filename, _version)

    for dim in dictionary['CSDM']['independent_variables']:
        csdm.add_independent_variable(dim)

    for dat in dictionary['CSDM']['dependent_variables']:
        csdm.add_dependent_variable(dat)    # filename)

    # if np.all(_type):
    npts = [item.number_of_points for item in csdm.independent_variables]
    csdm._reshape(npts[::-1])
    # [item.reshape(npts[::-1]) for item in csdm.dependent_variables]


# Create the augmentation layer model #

    return csdm


def new():
    r"""
    Return an empty CSDModel object. ::

        >>> import csdfpy as cp
        >>> emptydata = cp.new()
        >>> print(emptydata.data_structure)
        {
          "CSDM": {
            "dependent_variables": [],
            "independent_variables": [],
            "version": "1.0.0"
          }
        }

    :returns: A CSDModel object
    """
    return CSDModel()


class CSDModel:
    r"""
    The CSDModel class is a python for the CSD model file exchange formats.

    The module is based on the core scientific dataset (CSD) model which is
    designed as a building block in the development of a more sophisticated
    portable scientific dataset file standard.
    The CSDModel supports :math:`p`-component independent variable, :math:`y`,
    which is discretely sampled at :math:`N` points in a :math:`d`-dimensional
    independent variable space :math:`(x_0, x_1, ... x_k, ... x_{d-1})`.
    The CSDModel class also support multiple dependent variables that are
    simultaneously sampled over the :math:`d`-dimensional independent variable
    space.

    In the `csdfpy` module, every independent variable, :math:`x_k`, is an
    instance of the :ref:`iv_api` class and every dependent variable,
    :math:`y`, is an instance of the :ref:`dv_api` class.
    The CSDModel class aggregates and manages the tuples of both these
    instance types.

    :returns: A ``CSDModel`` instance.
    """

    __version__ = version
    _old_compatible_versions = ('0.0.9')
    _old_incompatible_versions = ()

    __slots__ = [
            '_independent_variables',
            '_dependent_variables',
            '_version',
            '_filename',
        ]

    def __init__(self, filename='', version=None):
        """Python module from reading and writing CSDM files."""
        if version is None:
            version = self.__version__
        elif version in self._old_incompatible_versions:
            raise Exception(
                (
                    "Files created with the version {0} of the CSDModel "
                    "are no longer supported."
                ).format(version)
            )

        self._independent_variables = ()
        self._dependent_variables = ()
        self._version = version
        self._filename = filename

    # @classmethod
    # def __delattr__(cls, name):
    #     """Delete attribute."""
    #     if name in cls.__slots__:
    #         raise AttributeError(
    #             "Attribute '{0}' cannot be deleted.".format(name)
    #         )

    # @classmethod
    # def __setattr__(cls, name, value):
    #     """Set attribute."""
    #     if name in cls.__slots__:
    #         raise AttributeError(
    #             "Attribute '{0}' cannot be modified.".format(name)
    #         )
    #     else:
    #         raise AttributeError(
    #             "The '{0}' object has no attribute '{1}'.".format(
    #                 cls.__name__, name)
    #         )

# ---- Attribute ----#
# controlled variables
    @property
    def independent_variables(self):
        """Returns a tuple of the :ref:`iv_api` instances."""
        return self._independent_variables

# uncontrolled variables
    @property
    def dependent_variables(self):
        """Returns a tuple of the :ref:`dv_api` instances."""
        return self._dependent_variables

# CSD model version on file
    @property
    def version(self):
        """Returns the version number of the :ref:`csdm_api` on file."""
        return self._version

# CSD model version on file
    @property
    def filename(self):
        """
        Returns the local file address of the current file.

        The file extensions includes the `.csdf` and the `.csdfe`.
        """
        return self._filename

    @property
    def data_structure(self):
        r"""
        Returns the :ref:`csdm_api` instance as a JSON serialized object.

        The attribute cannot be modified.

        :raises AttributeError: When modified.
        """
        dictionary = self._get_python_dictionary(
            self.filename, print_function=True
        )

        return (json.dumps(dictionary, ensure_ascii=False,
                           sort_keys=False, indent=2))

# private method

    def _reshape(self, shape):
        r"""
        Reshapes the components array.

        The array is reshaped to
        :math:`(p \times N_{d-1} \times ... N_1 \times N_0)` where :math:`p`
        is the number of components and :math:`N_k` is the number of points
        sampled along the :math:`k^\mathrm{th}` independent variable.
        """
        for item in self.dependent_variables:
            item1 = item.subtype
            _shape = (item1.quantity_type._p,) + tuple(shape)
            _nptype = item1.numeric_type._nptype

            item1._components = np.asarray(
                item1._components.reshape(_shape), dtype=_nptype
            )

# ----------- Public Methods -------------- #

    def add_independent_variable(self, *arg, **kwargs):
        """
        Add a new :ref:`iv_api` instance to the :ref:`csdm_api` instance.

        There are three ways to add a new independent variable.

        *From a python dictionary containing valid keywords.*

        .. doctest::

            >>> import csdfpy as cp
            >>> datamodel = cp.new()

            >>> py_dictionary = {
            ...     'type': 'linear_spacing',
            ...     'sampling_interval': '5 G',
            ...     'number_of_points': 50,
            ...     'reference_offset': '-10 mT'
            ... }
            >>> datamodel.add_independent_variable(py_dictionary)

        *From valid keyword arguaments.*

        .. doctest::

            >>> datamodel.add_independent_variable(
            ...     type = 'linear_spacing',
            ...     sampling_interval = '5 G',
            ...     number_of_points = 50,
            ...     reference_offset = '-10 mT'
            ... )

        *From a* :ref:`iv_api` *instance.*

        .. doctest::

            >>> from csdfpy import IndependentVariable
            >>> var1 = IndependentVariable(type = 'linear_spacing',
            ...                            sampling_interval = '5 G',
            ...                            number_of_points = 50,
            ...                            reference_offset = '-10 mT')
            >>> datamodel.add_independent_variable(var1)
        """
        if arg != () and isinstance(arg[0], IndependentVariable):
            self._independent_variables += (arg[0], )

        else:
            self._independent_variables += (
                    IndependentVariable(*arg, **kwargs),
                    )

    def add_dependent_variable(self, *arg, **kwargs):
        """
        Add a new :ref:`dv_api` instance to the :ref:`csdm_api` instance.

        There are three ways to add a new dependent variable instance.

        *From a python dictionary containing valid keywords.*

        .. doctest::

            >>> import numpy as np

            >>> datamodel = cp.new()

            >>> numpy_array = (100*np.random.rand(3,50)).astype(np.uint8)
            >>> py_dictionary = {
            ...     'components': numpy_array,
            ...     'name': 'star',
            ...     'unit': 'W s',
            ...     'quantity': 'energy',
            ...     'quantity_type': 'RGB'
            ... }
            >>> datamodel.add_dependent_variable(py_dictionary)

        *From valid keyword arguaments.*

        .. doctest::

            >>> datamodel.add_dependent_variable(name='star',
            ...                                  unit='W s',
            ...                                  quantity_type='RGB',
            ...                                  components=numpy_array)

        *From a* :ref:`iv_api` *instance.*

        .. doctest::

            >>> from csdfpy import DependentVariable
            >>> var1 = DependentVariable(name='star',
            ...                          unit='W s',
            ...                          quantity_type='RGB',
            ...                          components=numpy_array)
            >>> datamodel.add_dependent_variable(var1)
        """
        if arg != () and isinstance(arg[0], DependentVariable):
            self._dependent_variables += (arg[0], )

        else:
            self._dependent_variables += (
                    DependentVariable(
                        filename=self.filename, *arg, **kwargs
                        ),
                    )

    def _get_python_dictionary(self, filename, print_function=False,
                               version=__version__):
        """Return the CSDModel instance as a python dictionary."""
        dictionary = {}

        dictionary["version"] = version
        dictionary["independent_variables"] = []
        dictionary["dependent_variables"] = []

        for i in range(len(self.independent_variables)):
            dictionary["independent_variables"].append(
                self.independent_variables[i]._get_python_dictionary()
            )

        _length_of_dependent_variables = len(self.dependent_variables)

        for i in range(_length_of_dependent_variables):
            dictionary["dependent_variables"].append(
                self.dependent_variables[i]._get_python_dictionary(
                    filename=filename,
                    dataset_index=i,
                    for_display=print_function,
                    version=self.__version__)
                )

        csdm = {}
        csdm['CSDM'] = dictionary
        return csdm

    def save(self, filename, version=__version__):
        """
        Serialize the :ref:`CSDM_api` instance as a JSON data-exchange file.

        The serialized file is saved with two file extensions.
        When every instance of the :ref:`dv_api` from the CSDModel instance has
        an internal subtype, the corresponding CSDModel instance is serialized
        with a `.csdf` file extension.
        If any one of the :ref:`dv_api` instances has an external subtype, the
        CSDModel instance is serialized with a `.csdfe` file extension.
        We use the two different file extensions to alert the end use of the
        possible deserialization error when the external data file is
        inaccessible.

        .. doctest::

            >>> datamodel.save('myfile')

        where ``datamodel`` is an instance of the CSDModel class.
        """
        dictionary = self._get_python_dictionary(filename, version=version)
        with open(filename, 'w', encoding='utf8') as outfile:
            json.dump(dictionary, outfile, ensure_ascii=False,
                      sort_keys=False, indent=2)

    def copy(self):
        """Return a copy of the current CSDModel instance."""
        return deepcopy(self)

    def replace(self,
                controlled_variable=None,
                cv_index=-1,
                uncontrolled_variable=None,
                uv_index=-1):
        """
        Repalce the controlled or the uncontrolled variable at the index.

        :params: controlled_variable: A new ControlledVariable object or a
            python dictionary corresponding to a new ControlledVariable object.
        :params: cv_index: An integer corresponding to the
            UncontrolledVariable object to the updated.
        :params: uncontrolled_variable: A new UncontrolledVariable object or a
            python dictionary corresponding to a new UncontrolledVariable
            object.
        :params: uv_index: An integer corresponding to the
            UncontrolledVariable object to the updated.

        .. todo::
            Well, write the method.
        """
        pass

    def sum(self, cv=-1):
        """
        Project the data values onto the control variable at index, `cv`.

        :params: cv: An integer cooresponding to the control variable onto
            which the data values are projected.
        :returns: A ``CSDModel`` object.
        """
        new = CSDModel()
        d = len(self.independent_variables)
        if cv > d:
            raise ValueError(
                (
                    "`cv` {0} cannot be greater than number of control"
                    "variables, {1}."
                ).format(cv, d)
            )
        for variable in self.dependent_variables:
            y = variable.components.sum(axis=-1-cv)
            new.add_dependent_variable(
                components=y,
                name=variable.name,
                quantity=variable.quantity,
                encoding=variable.encoding,
                numeric_type=variable.numeric_type,
                quantity_type=variable.quantity_type,
                component_labels=variable.component_labels,
                components_uri=variable.components_uri,
            )
        for i, variable in enumerate(self.independent_variables):
            if i != cv:
                new.add_independent_variable(variable)

        return new

    def fft(self, cv=0):
        """
        Perform a FFT along the specified control variable (cv).

        Needs debugging.
        """
        if not self.independent_variables[cv].is_quantitative():
            raise ValueError(
                'Non-quantitative dimensions cannot be Fourier transformed.'
            )

        s = "Arbitrarily sampled grid controlled variable"
        if self.independent_variables[cv].variable_type == s:
            raise NotImplementedError(
                (
                    "Fourier tranform of an arbitrarily sampled "
                    "grid dimension is not implemanted."
                )
            )

        if self.independent_variables[cv].sampling_type == 'scatter':
            raise NotImplementedError(
                (
                    "Fourier transform of a scattered "
                    "dimensions is not implemented."
                )
            )

        cs = self.independent_variables[cv].reciprocal_coordinates

        # + \
        # self.independent_variables[cv].reciprocal_reference_offset

        phase = np.exp(
            1j * 2*np.pi *
            self.independent_variables[cv].reference_offset * cs
        )

        ndim = len(self.independent_variables)

        for i in range(len(self.dependent_variables)):
            signal_ft = fftshift(
                fft(self.dependent_variables[i].components,
                    axis=-cv-1), axes=-cv-1
                ) * get_broadcase_shape(phase, ndim, axis=-cv-1)

            self.dependent_variables[i].uv.set_attribute(
                '_components', signal_ft
            )

        self.independent_variables[cv].gcv._reciprocal()
        self._toggle_fft_output_order(self.independent_variables[cv])

    def _toggle_fft_output_order(self, control_variable):
        if control_variable.fft_output_order:
            control_variable.fft_output_order = False
        else:
            control_variable.fft_output_order = True

    def __add__(self, other):
        """
        Add two CSDModel instances.

        We follow a safe rule---the addition of two CSDModel instances
        will only be successfull when the attributes of the corresponding
        ControlledVariable instances are identical.
        """
        if not _compare_cv_objects(self, other):
            raise Exception("Cannot add")

        dim1 = len(self.dependent_variables)
        dim2 = len(other.dependent_variables)

        if dim1 != dim2:
            raise Exception(
                (
                    "Cannot add {0} and {1}. They have differnet "
                    "number of uncontrolled variables."
                ).format(self.__class__.__name__, other.__class__.__name__)
            )

        d1 = deepcopy(self)
        for i in range(dim1):
            if _compare_uv(
                self.dependent_variables[i],
                other.dependent_variables[i]
            ):
                d1.dependent_variables[i].components += \
                    other.dependent_variables[i].components

        return d1

    def __sub__(self, other):
        """
        Subtract two CSDModel instances.

        We follow a safe rule---the subtraction of two CSDModel instances
        will only be successfull when the attributes of the corresponding
        ControlledVariable instances are identical.
        """
        pass

    def __mul__(self, other):
        """
        Multiply two CSDModel instances.

        We follow a safe rule---the multiplication of two CSDModel instances
        will only be successfull when the attributes of the corresponding
        ControlledVariable instances are identical.
        """
        pass

    def __div__(self, other):
        """
        Divide two CSDModel instances.

        We follow a safe rule---the division of two CSDModel instances
        will only be successfull when the attributes of the corresponding
        ControlledVariable instances are identical.
        """
        pass


def get_broadcase_shape(array, ndim, axis):
    """Return the broadcast array for numpy ndarray operations."""
    s = [None for i in range(ndim)]
    s[axis] = slice(None, None, None)
    return array[tuple(s)]


def _compare_cv_object(cv1, cv2):
    if cv1.gcv._getparams == cv2.gcv._getparams:
        return True
    return False


def _compare_cv_objects(object1, object2):
    dim1 = len(object1.independent_variables)
    dim2 = len(object2.independent_variables)

    message = (
        "{0} and {1} do not have the same set of "
        "controlled variables."
    ).format(object1.__name__, object2.__name__)

    if dim1 != dim2:
        raise Exception(message)

    for i in range(dim1):
        if not _compare_cv_object(
            object1.independent_variables[i],
            object2.independent_variables[i]
        ):
            raise Exception(message)

    return True


def _compare_uv(uv1, uv2):
    # a = {
    #     'unit': True,
    #     'quantity': True,
    #     'quantity_type': True
    # }
    a = True
    if uv1.unit.physical_type != uv2.unit.physical_type:
        a = False
    if uv1.quantity != uv2.quantity:
        raise Exception(
            (
                "Binary operates are not supported for "
                "objects with different quantity."
            )
        )
    if uv1.quantity_type != uv2.quantity_type:
        raise Exception(
            (
                "Binary operates are not supported for "
                "objects with different quantity_type."
            )
        )
    return a


# def _compare_uv_objects(object1, object2):
#     dim1 = len(object1.dependent_variables)
#     dim2 = len(object2.dependent_variables)

#     for j in range(dim1):
#         for i in range(dim2):
#             a = _compare_uv(
#                 object1.dependent_variables[i],
#                 object2.dependent_variables[j]
#             )
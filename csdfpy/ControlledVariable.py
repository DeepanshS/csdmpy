
"""The base ControlledVariable object: attributes and methods."""

from ._LinearlySampledDimension import _LinearlySampledDimension
from ._ArbitrarilySampledDimension import _ArbitrarilySampledDimension
from ._NonQuantitativeDimension import _NonQuantitativeDimension

from copy import deepcopy

import warnings

from .unit import (
    _ppm,
    string_to_unit
)

import json

from numpy import inf

from ._utils import (
    _assign_and_check_unit_consistency,
    _check_unit_consistency,
    _check_and_assign_bool,
    _check_value_object,
    _axis_label,
    _type_message,
    _attribute_message,
    _get_dictionary
)

_quantitative_variable_types = ['Linearly sampled grid controlled variable',
                                'Arbitrarily sampled grid controlled variable']


def _check_quantitative(dictionary):
    if not _check_non_quantitative(dictionary):
        if dictionary['number_of_points'] is None and \
                dictionary['sampling_interval'] is None and \
                dictionary['values'] is None:
            raise Exception("either 'number_of_points, sampling_interval' \
or 'values' key is required.")
        return True
    return False


def _check_quantitative_linear(dictionary):
    if _check_quantitative(dictionary) and \
            dictionary['number_of_points'] is not None and \
            dictionary['sampling_interval'] is not None:
        return True
    return False


def _check_quantitative_arbitrary(dictionary):
    if _check_quantitative(dictionary) and \
            dictionary['values'] is not None:
        return True
    return False


def _check_non_quantitative(dictionary):
    is_false = False
    if dictionary['non_quantitative']:
        is_false = True
        if dictionary['values'] is None:
            raise Exception("'values' key is required for \
non-quantitative dimension.")
    return is_false


class ControlledVariable:
    r"""
    The base ControlledVariable class.

    This class returns an object which represents a control variable. There are
    three types of controlled variables based on the three types ofdimensions:
    a linearly sampled, an arbitrarily sampled, and a
    non-quantitative dimension, respectively.

    **A linearly sampled control variable**

    Let :math:`m_k` be the sampling interval, :math:`N_k \ge 1` be the
    number of points, :math:`c_k` be the reference offset, and
    :math:`o_k` be the origin offset along the :math:`k^{th}`
    grid dimension, then the corresponding coordinates along the
    dimension are given as,

    .. math ::
        \begin{align}
        \mathbf{X}_k &= [m_k j ]_{j=0}^{N_k-1} - c_k \mathbf{1}, \\
        \mathbf{X}_k^\mathrm{abs} &= \mathbf{X}_k + o_k \mathbf{1}.
        \end{align}
        :label: eq_linear_gcv

    Here :math:`\mathbf{X}_k` and :math:`\mathbf{X}_k^\mathrm{abs}` are the
    ordered arrays of the reference and absolute control variable coordinates,
    respectively, and :math:`\mathbf{1}` is an array of ones.

    **An arbitrarily sampled control variable**

    Let :math:`\mathbf{A}_k` be an ordered array of ascending
    quantities, :math:`c_k` be the reference offset, and
    :math:`o_k` be the origin offset along the :math:`k^{th}`
    grid dimension, then the coordinates along this dimension
    are given as,

    .. math ::
        \begin{align}
        \mathbf{X}_k = \mathbf{A}_k - c_k \mathbf{1},\\
        \mathbf{X}_k^\mathrm{abs} = \mathbf{X}_k + o_k \mathbf{1},
        \end{align}

    where :math:`\mathbf{X}_k`, :math:`\mathbf{X}_k^\mathrm{abs}`,
    and :math:`\mathbf{1}` are the same as described in :eq:`eq_linear_gcv`.


    **A non-quantitative control variable**

    For non-quantitative grid dimensions, there is no reference and absolute
    control variable coordinates. Here, we only define the coordinate.
    Let :math:`\mathbf{A}_k` be an array of non-quantitative entities, then
    the corresponding coordinates along this dimension follow,

    .. math ::
        \mathbf{X}_k = \mathbf{A}_k.

    **Creating a new control variable.**

    There are two ways to create a new control variable using this class, but
    it always returns a ControlledVariable instance.

    `From a python dictionary containing valid keywords.` ::

        >>> from csdfpy import ControlledVariable
        >>> py_dictionary = {
        ...     'sampling_interval': '5 G',
        ...     'number_of_points': 10,
        ...     'reference_offset': '-10 mT',
        ...     'origin_offset': '10 T'
        ... }
        >>> x = ControlledVariable(py_dictionary)

    `From valid keyword arguaments.` ::

        >>> x = ControlledVariable(sampling_interval = '5 G',
        ...                        number_of_points = 10,
        ...                        reference_offset = '-10 mT',
        ...                        origin_offset = '10 T')

    """

    __slots__ = ['gcv']

    def __new__(cls, *args, **kwargs):
        """Create a new instance of ControlVariable object."""
        # if args != () and isinstance(args[0], ControlledVariable):
        #     print('inside __new__. arg')
        #     return args[0]
        # else:
        instance = super(ControlledVariable, cls).__new__(cls)
        # instance.__init__(*args, **kwargs)
        return instance

    def __init__(self, *args, **kwargs):
        """Initialize an instance of ControlVariable object."""
        dictionary = {
            'sampling_type': "grid",
            'non_quantitative': False,
            'number_of_points': None,
            'sampling_interval': None,
            'values': None,
            'reference_offset': None,
            'origin_offset': None,
            'made_dimensionless': False,
            'reverse': False,
            'fft_output_order': False,
            'period': None,
            'quantity': None,
            'label': '',
            'reciprocal': {
                'sampling_interval': None,
                'reference_offset': None,
                'origin_offset': None,
                'made_dimensionless': False,
                'reverse': False,
                'period': None,
                'quantity': None,
                'label': ''}
        }

        default_keys = dictionary.keys()
        input_dict = _get_dictionary(*args, **kwargs)
        input_keys = input_dict.keys()

        if 'reciprocal' in input_keys:
            input_subkeys = input_dict['reciprocal'].keys()
        for key in input_keys:
            if key in default_keys:
                if key == 'reciprocal':
                    for subkey in input_subkeys:
                        dictionary[key][subkey] = input_dict[key][subkey]
                else:
                    dictionary[key] = input_dict[key]

        # print(dictionary)

        if _check_non_quantitative(dictionary):
            _gcv_object = _NonQuantitativeDimension(
                    _sampling_type=dictionary['sampling_type'],
                    _non_quantitative=dictionary['non_quantitative'],
                    _values=dictionary['values'],
                    _reverse=dictionary['reverse'],
                    _label=dictionary['label']
                    )

        if _check_quantitative_arbitrary(dictionary):
            _gcv_object = _ArbitrarilySampledDimension(

                _sampling_type=dictionary['sampling_type'],
                _non_quantitative=dictionary['non_quantitative'],

                _values=dictionary['values'],
                _reference_offset=dictionary['reference_offset'],
                _origin_offset=dictionary['origin_offset'],
                _quantity=dictionary['quantity'],
                _reverse=dictionary['reverse'],
                _label=dictionary['label'],
                _period=dictionary['period'],
                _made_dimensionless=dictionary['made_dimensionless'],

                _reciprocal_reference_offset=dictionary['reciprocal']
                                                       ['reference_offset'],
                _reciprocal_origin_offset=dictionary['reciprocal']
                                                    ['origin_offset'],
                _reciprocal_quantity=dictionary['reciprocal']['quantity'],
                _reciprocal_reverse=dictionary['reciprocal']['reverse'],
                _reciprocal_period=dictionary['reciprocal']['period'],
                _reciprocal_label=dictionary['reciprocal']['label'],
                _reciprocal_made_dimensionless=dictionary[
                                                'reciprocal'][
                                                'made_dimensionless']
            )

        if _check_quantitative_linear(dictionary):
            _gcv_object = _LinearlySampledDimension(
                _sampling_type=dictionary['sampling_type'],
                _non_quantitative=dictionary['non_quantitative'],

                _number_of_points=dictionary['number_of_points'],
                _sampling_interval=dictionary['sampling_interval'],
                _reference_offset=dictionary['reference_offset'],
                _origin_offset=dictionary['origin_offset'],
                _quantity=dictionary['quantity'],
                _reverse=dictionary['reverse'],
                _label=dictionary['label'],
                _period=dictionary['period'],
                _fft_output_order=dictionary['fft_output_order'],
                _made_dimensionless=dictionary['made_dimensionless'],

                _reciprocal_sampling_interval=dictionary['reciprocal']
                                                        ['sampling_interval'],
                _reciprocal_reference_offset=dictionary['reciprocal']
                                                       ['reference_offset'],
                _reciprocal_origin_offset=dictionary['reciprocal']
                                                    ['origin_offset'],
                _reciprocal_quantity=dictionary['reciprocal']['quantity'],
                _reciprocal_reverse=dictionary['reciprocal']['reverse'],
                _reciprocal_period=dictionary['reciprocal']['period'],
                _reciprocal_label=dictionary['reciprocal']['label'],
                _reciprocal_made_dimensionless=dictionary[
                                                'reciprocal'][
                                                'made_dimensionless'])

        super(ControlledVariable, self).__setattr__('gcv', _gcv_object)

#               Attributes defining the controlled variable type              #
# --------------------------------------------------------------------------- #

# Variables type #
    @property
    def variable_type(self):
        r"""
        Return the control variable type.

        There are three types of controlled variables base on the types of
        dimensions, linearly and arbitrarily sampled quantitative grid
        dimensions and non-quantitative dimension.
        This attribute cannot be modified. ::

            >>> print(x.variable_type)
            Linearly sampled grid controlled variable

        In the above example, ``x`` is an instance of the ControlledVariable
        class associated with a linearly sampled controlled variable.

        :returns: A string.
        :raises AttributeError: When the attribute is modified.
        """
        return deepcopy(self.gcv.variable_type)

#           Attributes defining the control variable sampling type            #
# --------------------------------------------------------------------------- #

# Sampling type #
    @property
    def sampling_type(self):
        r"""
        Return sampling type of the controlled variable.

        This attribute cannot be modified. ::

            >>> print(x.sampling_type)
            grid

        :returns: A string.
        :raises AttributeError: When the attribute is modified.
        """
        return deepcopy(self.gcv._sampling_type)

# =========================================================================== #
#                             Derived Attributes                              #
# =========================================================================== #

# coordinates #
    @property
    def coordinates(self):
        r"""
        Return an array of reference coordinates, :math:`\mathbf{X}_k`, along the dimension.

        The order of these coordinates
        depends on the value of the ``reverse`` and the ``fft_output_order``
        (only applicable when sampling is linear along the dimension)
        attributes of the class. This attribute cannot be modified. ::

            >>> print(x.coordinates)
            [100. 105. 110. 115. 120. 125. 130. 135. 140. 145.] G

        :returns: A ``Quantity array`` when the controlled variable is
                  quantitative.
        :returns: A ``Numpy array`` when the controlled variable is
                  non-quantitative.
        :raises AttributeError: When the attribute is modified.
        """
        return self.gcv.coordinates

# absolute_coordinates
    @property
    def absolute_coordinates(self):
        r"""
        Return an array of absolute coordinates, :math:`\mathbf{X}_k^\mathrm{abs}`, along the dimension.

        This attribute is
        only `valid` for the quantitative controlled variables. The order of
        these coordinates depends on the value of the ``reverse`` and the
        ``fft_output_order`` (only applicable when sampling is linear along
        the dimension) attributes of the class. This attribute cannot be
        modified. ::

            >>> print(x.origin_offset)
            10.0 T
            >>> print(x.absolute_coordinates)
            [100100. 100105. 100110. 100115. 100120. 100125. 100130. 100135. 100140. 100145.] G

        In the above example, the absolute coordinate is ``coordinates
        + origin_offset``.

        :returns: A ``Quantity array`` when the controlled
                  variable is quantitative.
        :raises AttributeError: For non-quantitative controlled variables.
        :raises AttributeError: When the attribute is modified.
        """
        if self.variable_type in _quantitative_variable_types:
            return self.gcv.coordinates + \
                self.gcv._origin_offset.to(self.gcv.unit)

        raise AttributeError(_attribute_message(self.variable_type,
                                                'absolute_coordinates'))

# reciprocal_coordinates
    @property
    def reciprocal_coordinates(self):
        r"""
        Return an array of coordinates, :math:`\mathbf{X_r}_k^\mathrm{abs}`, along the reciprocal dimension.

        This attribute is
        only `valid` for the quantitative controlled variabes. The order of
        these coordinates depends on the value of the ``reciprocal_reverse``
        attributes of the class. This attribute cannot be modified.

        :returns: A ``Quantity`` object when the controlled
                  variable is quantitative.
        :raises AttributeError: For non-quantitative controlled variables.
        :raises AttributeError: When the attribute is modified.
        """
        if self.variable_type in _quantitative_variable_types[0]:
            return self.gcv.reciprocal_coordinates

        raise AttributeError(_attribute_message(self.variable_type,
                                                'reciprocal_coordinates'))

# reciprocal_absolute_coordinates
    @property
    def reciprocal_absolute_coordinates(self):
        r"""
        Return an array of absolute coordinates, :math:`\mathbf{X_r}_k^\mathrm{abs}`, along the reciprocal dimension.

        This attribute is only `valid` for the quantitative controlled
        variabes. The order of these coordinates depends on the value of the
        ``reciprocal_reverse`` attributes of the class. This attribute cannot
        be modified.

        :returns: A ``Quantity`` object when the controlled
                  variable is quantitative.
        :raises AttributeError: For non-quantitative controlled variables.
        :raises AttributeError: When the attribute is modified.
        """
        return self.gcv.reciprocal_coordinates + \
            self.gcv._reciprocal_origin_offset.to(self.gcv.reciprocal_unit)

# =========================================================================== #
#           Attributes affecting the controlled variable coordinates          #
# =========================================================================== #

# reference offset
    @property
    def reference_offset(self):
        r"""
        Return the reference offset, :math:`c_k`, along the dimension.

        The attribute is only `valid` for quantitative
        dimensions. When assigning a value, the dimensionality of the value
        must be consistent with the dimensionality of the other members
        specifying the dimension. The value is assigned with a string
        containing the reference offset,
        for example, ::

            >>> print(x.reference_offset)
            -10.0 mT
            >>> x.reference_offset = "0 T"
            >>> print(x.coordinates)
            [ 0.  5. 10. 15. 20. 25. 30. 35. 40. 45.] G

        :returns: A ``Quantity`` object with the reference offset.
        :raises AttributeError: For non-quantitative controlled variables.
        :raises TypeError: When the assigned value is not a string.
        """
        if self.variable_type in _quantitative_variable_types:
            return deepcopy(self.gcv._reference_offset)

        raise AttributeError(_attribute_message(self.variable_type,
                                                'reference_offset'))

    @reference_offset.setter
    def reference_offset(self, value):
        if self.variable_type in _quantitative_variable_types:
            if not isinstance(value, str):
                raise TypeError(_type_message(str, type(value)))

            _value = _assign_and_check_unit_consistency(
                value, self.gcv.unit
            )
            self.gcv.set_attribute('_reference_offset', _value)
            return

        raise AttributeError(_attribute_message(self.variable_type,
                                                'reference_offset'))

# reciprocal reference offset
    @property
    def reciprocal_reference_offset(self):
        r"""
        Return the reference offset along the reciprocal dimension.

        This attribute is only `valid` for the quantitative
        dimensions. When assigning a value, the dimensionality of the value
        must be consistent with the dimensionality of other members
        specifying the reciprocal dimension. The value is assigned with a
        string containing the reference offset of the reciprocal
        dimension, for example, ::

            >>> print(x.reciprocal_reference_offset)
            0.0 1 / G
            >>> x.reciprocal_reference_offset = "5 (1/T)"

        :returns: A ``Quantity`` object with the reference offset
                  of the reciprocal dimension.
        :raises TypeError: When the assigned value is not a string.
        """
        if self.variable_type in _quantitative_variable_types:
            return deepcopy(self.gcv._reciprocal_reference_offset)

        raise AttributeError(
            _attribute_message(
                self.variable_type, 'reciprocal_reference_offset')
        )

    @reciprocal_reference_offset.setter
    def reciprocal_reference_offset(self, value):
        if self.variable_type in _quantitative_variable_types:
            if not isinstance(value, str):
                raise TypeError(_type_message(str, type(value)))

            _value = _assign_and_check_unit_consistency(
                value, self.gcv.reciprocal_unit)
            self.gcv.set_attribute('_reciprocal_reference_offset', _value)
            return

        raise AttributeError(
            _attribute_message(
                self.variable_type, 'reciprocal_reference_offset')
        )
# --------------------------------------------------------------------------- #

# origin offset
    @property
    def origin_offset(self):
        r"""
        Return the origin offset, :math:`o_k`, along the dimension.

        The attribute is only `valid` for quantitative
        dimensions. When assigning a value, the dimensionality of the value
        must be consistent with the dimensionality of other members specifying
        the dimension. The value is assigned with a string containing the
        origin offset, for example, ::

            >>> print(x.origin_offset)
            10.0 T
            >>> x.origin_offset = "1e5 G"
            >>> print(x.absolute_coordinates)
            [100000. 100005. 100010. 100015. 100020. 100025. 100030. 100035. 100040. 100045.] G

        :returns: A ``Quantity`` object with the origin offset.
        :raises AttributeError: For non-quantitative controlled variables.
        :raises TypeError: When the assigned value is not a string.
        """
        if self.variable_type in _quantitative_variable_types:
            return deepcopy(self.gcv._origin_offset)

        raise AttributeError(_attribute_message(self.variable_type,
                                                'origin_offset'))

    @origin_offset.setter
    def origin_offset(self, value):
        if self.variable_type in _quantitative_variable_types:
            if not isinstance(value, str):
                raise TypeError(_type_message(str, type(value)))

            _value = _assign_and_check_unit_consistency(value, self.gcv.unit)
            self.gcv.set_attribute('_origin_offset', _value)
            return

        raise AttributeError(_attribute_message(self.variable_type,
                                                'origin_offset'))

# reciprocal origin offset
    @property
    def reciprocal_origin_offset(self):
        r"""
        Return the origin offset along the reciprocal dimension.

        This attribute is only `valid` for the quantitative dimensions. When
        assigning a value, the dimensionality of the value must be consistent
        with the dimensionality of the other members specifying the reciprocal
        dimension. The value is assigned with a string containing the origin
        offset of the reciprocal dimension, for example, ::

            >>> print(x.reciprocal_origin_offset)
            0.0 1 / G
            >>> x.reciprocal_origin_offset = "400 (1/µT)"

        :returns: A ``Quantity`` object with the origin offset of
                  the reciprocal dimension.
        :raises AttributeError: For non-quantitative controlled variables.
        :raises TypeError: When the assigned value is not a string.
        """
        if self.variable_type in _quantitative_variable_types:
            return deepcopy(self.gcv._reciprocal_origin_offset)

        raise AttributeError(_attribute_message(self.variable_type,
                                                'reciprocal_origin_offset'))

    @reciprocal_origin_offset.setter
    def reciprocal_origin_offset(self, value):
        if self.variable_type in _quantitative_variable_types:
            if not isinstance(value, str):
                raise TypeError(_type_message(str, type(value)))

            _value = _assign_and_check_unit_consistency(
                value, self.gcv.reciprocal_unit
            )
            self.gcv.set_attribute('_reciprocal_origin_offset', _value)
            return

        raise AttributeError(_attribute_message(self.variable_type,
                                                'reciprocal_origin_offset'))
# --------------------------------------------------------------------------- #

# sampling interval
    @property
    def sampling_interval(self):
        r"""
        Return the sampling interval, :math:`m_k`, along the dimension.

        The attribute is only `valid` for instances with linearly sampled
        controlled-variable dimensions. When assigning a value,
        the dimensionality of the value must be consistent with the
        dimensionality of other members specifying the grid dimension.
        Additionally, the sampling interval must be a positive real number.
        The value is assigned with a string containing the sampling interval,
        for example, ::

            >>> print(x.sampling_interval)
            5.0 G
            >>> x.sampling_interval = "0.1 G"
            >>> print(x.coordinates)
            [0.  0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9] G

        Here, the original sampling interval, '5 G' is modified to
        '0.1 G'.

        .. note:: The sampling interval along a grid dimension and the
            respective reciprocal grid dimension follow the Nyquist–Shannon
            sampling theorem. Therefore, updating the ``sampling_interval``
            will automatically trigger an update on its reciprocal counterpart.

        :returns: A ``Quantity`` object with the sampling interval.
        :raises AttributeError: For non-quantitative and arbitrarily
                                sampled controlled variables.
        :raises TypeError: When the assigned value is not a string.
        """
        if self.variable_type == _quantitative_variable_types[0]:
            return deepcopy(self.gcv._sampling_interval)

        raise AttributeError(_attribute_message(self.variable_type,
                                                'sampling_interval'))

    @sampling_interval.setter
    def sampling_interval(self, value):
        if self.variable_type == _quantitative_variable_types[0]:
            if not isinstance(value, str):
                raise TypeError(_type_message(str, type(value)))
            self.gcv.sampling_interval = value
            return

        raise AttributeError(_attribute_message(self.variable_type,
                                                'sampling_interval'))
# --------------------------------------------------------------------------- #

# number_of_points
    @property
    def number_of_points(self):
        r"""
        Return the number of points along the dimension.

        The number of points, :math:`N_k \ge 1`, along the controlled
        variable dimension. The attribute is updated with an
        integer specifying the number of points, for example ::

            >>> print(x.number_of_points)
            10
            >>> x.number_of_points = 5
            >>> print(x.coordinates)
            [0.  0.1 0.2 0.3 0.4] G

        :returns: An ``Integer`` with the number of points.
        :raises TypeError: When the assigned value is not an integer.
        """
        return deepcopy(self.gcv._number_of_points)

    @number_of_points.setter
    def number_of_points(self, value):
        if not isinstance(value, int):
            raise TypeError(_type_message(int, type(value)))

        if value <= 0:
            raise ValueError(
                (
                    "An positive integer value is required, "
                    "a value of {0} is provided."
                ).format(value)
            )

        if self.variable_type != _quantitative_variable_types[0]:
            if value > self.number_of_points:
                raise ValueError(
                    (
                        "Cannot set the number of points, {0}, more "
                        "than the number of controlled variable coordinates, "
                        "{1}, when sampled arbitrarily along the dimension."
                    ).format(value, self.number_of_points)
                )

            if value < self.number_of_points:
                warnings.warn(
                    (
                        "The number of controlled variable "
                        "coordinates, {0}, are truncated to {1}."
                    ).format(self.number_of_points, value)
                )
            self.gcv.set_attribute('_number_of_points', value)

        else:
            self.gcv.set_attribute('_number_of_points', value)
            self.gcv._get_coordinates()
# --------------------------------------------------------------------------- #

# values arrat
    @property
    def values(self):
        r"""
        Return the values along the dimension.

        An ordered array, :math:`\mathbf{A}_k`, of strings
        containing the values. Depending on the values, either a
        quantitative or a non-quantitative controlled variable dimension
        is created. For example,

        .. math::
            \mathbf{A}_k = [\mathrm{"0~cm"}, \mathrm{"4.1~µm"},
            \mathrm{"0.3~mm"}, \mathrm{"5.8~m"}, \mathrm{"32.4~km"}]

        will generate an arbitrarily sampled controlled variable dimension,
        while,

        .. math::
            \mathbf{A}_k = [\mathrm{"Cu"}, \mathrm{"Ag"}, \mathrm{"Au"}]

        will generate a non-quantitative dimension. For
        an arbitrarily sampled quantitative variables,
        :math:`\mathbf{A}_k` is an ascending order of quantities. ::

            >>> x1 = ControlledVariable(values=['cm'])
            >>> x1.values = ['0cm', '4.1µm', '0.3mm', '5.8m', '32.4km']

            >>> x2 = ControlledVariable(values=[''], non_quantitative=True)
            >>> x2.values = ['Cu', 'Ag', 'Au']

        In the above examples, ``x1`` and ``x2`` are the instances of the
        ControlledVariable class associated with the arbitrarily sampled
        and the non-quantitative controlled variable respectively.

        :returns: A ``Quantity array`` for arbitrarily sampled controlled
                        variables.
        :returns: A ``Numpy array`` for non-quantitative controlled variables.
        :raises AttributeError: For linearly sampled controlled variables.

        .. todo:
            raise type error if the values are not strings or numpy array
            of stings.
        """
        if self.variable_type == _quantitative_variable_types[0]:
            raise AttributeError(_attribute_message(self.variable_type,
                                                    'values'))

        return deepcopy(self.gcv._values)

    @values.setter
    def values(self, array):
        if self.variable_type == _quantitative_variable_types[0]:
            raise AttributeError(_attribute_message(self.variable_type,
                                                    'values'))

        self.gcv._get_coordinates(array)

# ===================================================================== #
# Attributes affecting the order of the controlled variable coordinates #
# ===================================================================== #

# fft_ouput_order
    @property
    def fft_output_order(self):
        r"""
        Return the coordinates along the dimension according to the fft order.

        A boolean specifying if the coordinates along the controlled
        variable dimension are ordered according to the output of a
        fast Fourier transform (FFT) routine. This attribute is only
        *valid* for linearly sampled controlled variable dimensions. The
        universal behavior of the FFT routine is to order the :math:`N_k`
        output amplitudes by placing the zero `frequency` at the start
        of the output array, with positive `frequencies` increasing in
        magnitude placed at increasing array offset until reaching
        :math:`\frac{N_k}{2} -1` if :math:`N_k` is even, otherwise
        :math:`\frac{N_k-1}{2}`, followed by negative frequencies
        decreasing in magnitude until reaching :math:`N_k-1`.
        This is also the ordering needed for the input of the inverse FFT.
        For example, consider

        .. math ::
            \mathbf{X}_k^\mathrm{ref} = [0, 1, 2, 3, 4, 5] \mathrm{~m/s}

        when the fft output order is false. When the fft output
        order is true, the order follows,

        .. math ::
            \mathbf{X}_k^\mathrm{ref} = [0 ,1, 2, -3, -2, -1] \mathrm{~m/s}

        The following is a test example. ::

            >>> test = ControlledVariable(sampling_interval = '1',
            ...                           number_of_points = 10)

            >>> print(test.coordinates)
            [0. 1. 2. 3. 4. 5. 6. 7. 8. 9.]
            >>> test.fft_output_order
            False

            >>> test.fft_output_order = True
            >>> print(test.coordinates)
            [ 0.  1.  2.  3.  4. -5. -4. -3. -2. -1.]

        :returns: A ``Boolean``.
        :raises TypeError: When the assigned value is not a boolean.
        """
        if self.variable_type == _quantitative_variable_types[0]:
            return deepcopy(self.gcv._fft_output_order)

        raise AttributeError(_attribute_message(self.variable_type,
                                                'fft_output_order'))

    @fft_output_order.setter
    def fft_output_order(self, value):
        if self.variable_type == _quantitative_variable_types[0]:
            if not isinstance(value, bool):
                raise TypeError(_type_message(bool, type(value)))

            # print('in fft output order')

            self.gcv.set_attribute('_fft_output_order', value)
            self.gcv._get_coordinates()
            return

        raise AttributeError(_attribute_message(self.variable_type,
                                                'fft_output_order'))
# --------------------------------------------------------------------------- #

# reverse
    @property
    def reverse(self):
        r"""
        Return the coordinates along the dimension in the reverse order.

        The order in which the :math:`\mathbf{X}_k` and
        :math:`\mathbf{X}_k^\mathrm{abs}` coordinates map to the grid indices,
        :math:`\mathbf{G}_k = [0,1,2,...,N_k-1]`. For example, consider

        .. math ::
            \mathbf{X}_k^\mathrm{ref} = [0, 1, 2, 3,...N_{k-1}] \mathrm{~m/s},

        when the reverse is false. We the reverse is true, the mapping is

        .. math ::
            \mathbf{X}_k^\mathrm{ref} = [N_{k-1},...3, 2, 1, 0] \mathrm{~m/s}.

            >>> x.reverse
            False
            >>> print(x.coordinates)
            [0.  0.1 0.2 0.3 0.4] G
            >>> x.reverse = True
            >>> print(x.coordinates)
            [0.4 0.3 0.2 0.1 0. ] G

        :returns: A ``Boolean``.
        :raises TypeError: When the assigned value is not a boolean.
        """
        return deepcopy(self.gcv._reverse)

    @reverse.setter
    def reverse(self, value=False):
        if not isinstance(value, bool):
            raise TypeError(_type_message(bool, type(value)))

        _value = _check_and_assign_bool(value)
        self.gcv.set_attribute('_reverse', _value)

# reciprocal reverse
    @property
    def reciprocal_reverse(self):
        r"""
        Return the coordinates along the reciprocal dimension in reverse order.

        The order in which the :math:`\mathbf{X_r}_k` and
        :math:`\mathbf{X_r}_k^\mathrm{abs}` (for quantitative dimensions)
        coordinates are mapped to the grid indices. Let, the grid
        indices be :math:`[0,1,2,...,N_k-1]`, then when reverse
        is false, the mapping follows,

        .. math ::
            \mathbf{X}_k^\mathrm{ref} = [0, 1, 2, 3, 4] \mathrm{~s/m}

        and when reverse is false, then the mapping is

        .. math ::
            \mathbf{X}_k^\mathrm{ref} = [4, 3, 2, 1, 0] \mathrm{~s/m}

        :returns: A ``boolean``.
        :raises TypeError: When the assigned value is not a boolean.
        """
        return deepcopy(self.gcv._reciprocal_reverse)

    @reciprocal_reverse.setter
    def reciprocal_reverse(self, value=False):
        if not isinstance(value, bool):
            raise TypeError(_type_message(bool, type(value)))

        _value = _check_and_assign_bool(value)
        self.gcv.set_attribute('_reciprocal_reverse', _value)

# =========================================================================== #
#                            Additional Attributes                            #
# =========================================================================== #

# period
    @property
    def period(self):
        r"""
        Return the period of a quantitative controlled variable dimension.

        The default value of the period is infinity, i.e., the controlled
        variable dimension is non-periodic. The attribute is updated with a
        string containing a quantity which represents the period of the
        controlled variable. For example, ::

            >>> print(x.period)
            inf G
            >>> x.period = '1 T'

        To assign a dimension as non-periodic, one of the following may be
        used, ::

            >>> x.period = '1/0 T'
            >>> x.period = 'infinity µT'
            >>> x.period = '∞ G'

        :return: A ``Quantity`` object with the period of quantitative
            controlled variables.
        :raises AttributeError: For non-quantitative controlled variables.
        :raises TypeError: When the assigned value is not a string.
        """
        if self.variable_type in _quantitative_variable_types:
            return deepcopy(self.gcv._period)

        raise AttributeError(_attribute_message(
                            self.variable_type, 'period'))

    @period.setter
    def period(self, value=None):
        if self.variable_type in _quantitative_variable_types:
            if not isinstance(value, str):
                raise TypeError(_type_message(str, type(value)))

            lst = ['inf', 'Inf', 'infinity', 'Infinity', '∞']
            if value.strip().split()[0] in lst:
                value = inf*self.gcv.unit
                self.gcv.set_attribute('_period', value)
            else:
                self.gcv.set_attribute(
                    '_period', _check_value_object(
                        value, self.gcv.unit)
                    )
            return
        raise AttributeError(_attribute_message(
                            self.variable_type, 'period'))

# reciprocal period
    @property
    def reciprocal_period(self):
        r"""
        Return the period of the reciprocal dimension.

        The period of the reciprocal controlled variable along
        the dimension, if any. The default value is infinity,
        that is, the reciprocal dimension is considered non-periodic.
        This attribute can be updated with a string containing
        a physical quantity representing the period, for example,
        the reciprocal_period of "0.1 h/km". A period of "1/0 h/km"
        or "inf h/km" or "infinity h/km" will make the dimension
        non-periodic.

        :return: A ``Quantity`` object with physical quantity
                 representing a period.
        :raises AttributeError: For non-quantitative controlled variables.
        :raises TypeError: When the assigned value is not a string.
        """
        if self.variable_type in _quantitative_variable_types:
            return deepcopy(self.gcv._reciprocal_period)

        raise AttributeError(_attribute_message(self.variable_type,
                                                'reciprocal_period'))

    @reciprocal_period.setter
    def reciprocal_period(self, value=True):
        if self.variable_type in _quantitative_variable_types:
            if not isinstance(value, str):
                raise TypeError(_type_message(str, type(value)))

            lst = ['inf', 'Inf', 'infinity', 'Infinity', '∞']
            if value.strip().split()[0] in lst:
                value = inf*self.gcv.reciprocal_unit
                self.gcv.set_attribute('_reciprocal_period', value)

            else:
                self.gcv.set_attribute(
                    '_reciprocal_period', _check_value_object(
                        value, self.gcv.reciprocal_unit)
                    )
            return
        raise AttributeError(_attribute_message(self.variable_type,
                                                'reciprocal_period'))
# --------------------------------------------------------------------------- #

# Quantity
    @property
    def quantity(self):
        r"""
        Return the quantity name associated with the dimension.

        The attribute is only `valid` for the quantitative
        controlled variables. ::

            >>> print(x.quantity)
            magnetic flux density

        :returns: A string with the quantity name.
        :raises AttributeError: For non-quantitative controlled variables.
        :raises NotImplementedError: When assigning a value.
        """
        if self.variable_type in _quantitative_variable_types:
            return deepcopy(self.gcv._quantity)

        raise AttributeError(_attribute_message(self.variable_type,
                                                'quantity'))

    @quantity.setter
    def quantity(self, value):
        raise NotImplementedError('This attribute is not yet implemented.')

# reciprocal Quantity
    @property
    def reciprocal_quantity(self):
        r"""
        Return the quantity name associated with the reciprocal dimension.

        For example, the reciprocal quantity name, "inverse speed".
        This value cannot be updated.

        :returns: A string with the quantity name.
        :raises AttributeError: For non-quantitative controlled variables.
        """
        # """
        # When assigning a value, the
        # quantity name must be consistent with the other
        # physical quantities specifying the reciprocal
        # grid dimension.
        # """
        if self.variable_type in _quantitative_variable_types:
            return deepcopy(self.gcv._reciprocal_quantity)

        raise AttributeError(_attribute_message(self.variable_type,
                                                'reciprocal_quantity'))

    @reciprocal_quantity.setter
    def reciprocal_quantity(self, value):
        raise NotImplementedError('This attribute is not yet implemented.')

    # @reciprocal_quantity.setter
    # def reciprocal_quantity(self, string = ''):
    #     ## To do: add a check for reciprocal quantity
    #     self.set_attribute('_reciprocal_quantity', string)
# --------------------------------------------------------------------------- #

# label
    @property
    def label(self):
        r"""
        Return the label associated with the dimension.

        The attribute is updated with a string containing the label, for
        example, ::

            >>> x.label
            ''
            >>> x.label = 'field strength'

        :returns: A ``String`` containing the label.
        :raises TypeError: When the assigned value is not a string.
        """
        return deepcopy(self.gcv._label)

    @label.setter
    def label(self, label=''):
        if not isinstance(label, str):
            raise TypeError(_type_message(str, type(label)))
        self.gcv.set_attribute('_label', label)

# reciprocal_label
    @property
    def reciprocal_label(self):
        r"""
        Return the label associated with the reciprocal dimension.

        This attribute can be updated with a string
        containing the label of the reciprocal dimension,
        for example, the reciprocal label, "inverse velocity".

        :returns: A ``string`` containing the label.
        :raises TypeError: When the assigned value is not a string.
        """
        return deepcopy(self.gcv._reciprocal_label)

    @reciprocal_label.setter
    def reciprocal_label(self, label=''):
        self.gcv.set_attribute('_reciprocal_label', label)

# axis label
    @property
    def axis_label(self):
        r"""
        Return a formatted string for displaying the label along the dimension.

        This supplementary attribute is convenient for labeling axes.
        For quantitative controlled variables, this attributes returns a
        string, 'label / unit',  if the `label` is not an empty string. If the
        `label` is an empty string, 'quantity / unit’ is returned instead. Here
        `quantity` and `label` are the attributes of the :ref:`cv_api`
        instances described before, and `unit` is the unit associated with the
        control variable.
        For example, consider a temporal controlled variable where ::

            >>> x.label
            'field strength'
            >>> x.axis_label
            'field strength / ( G)'

        For non-quantitative controlled variables, this attribute returns
        the `label`.

        :returns: A ``String``.
        :raises AttributeError: When assigned a value.
        """
        if self.label.strip() == '':
            label = self.quantity
        else:
            label = self.label
        if self.variable_type in _quantitative_variable_types:
            return _axis_label(
                label,
                self.gcv._unit,
                self.gcv.made_dimensionless,
                self.gcv._dimensionless_unit
            )
        return deepcopy(self.label)

# data_structure()
    @property
    def data_structure(self):
        r"""
        Return the ControlledVariable object as a json object.

        This supplementary attribute is useful for a quick preview of the data
        structure. The attribute cannot be modified. ::

            >>> print(x.data_structure)
            {
                "reciprocal": {
                    "reference_offset": "5.0 T^-1",
                    "origin_offset": "400.0 µT^-1"
                },
                "number_of_points": 5,
                "sampling_interval": "0.1 G",
                "origin_offset": "100000.0 G",
                "reverse": true,
                "quantity": "magnetic flux density",
                "label": "field strength"
            }

        :raises AttributeError: When modified.
        """
        dictionary = self.get_python_dictionary()
        return (json.dumps(dictionary, ensure_ascii=False,
                           sort_keys=False, indent=2))

# =========================================================================== #
#                                  Methods                                    #
# =========================================================================== #

# _get_python_dictionary()
    def get_python_dictionary(self):
        r"""Return the ControlledVariable object as a python dictionary."""
        return self.gcv._get_python_dictionary()

# is_quantitative()
    def is_quantitative(self):
        r"""
        Verify if the control variable dimension is quantitative.

        Returns `True`, if the control variable is quantitative,
        otherwise `False`.

        :returns: A Boolean.
        """
        if self.variable_type in _quantitative_variable_types:
            return True
        return False

# to()
    def to(self, unit='', equivalencies=None):
        r"""
        Convert the unit of the controlled variable coordinates to `unit`.

        This method is a wrapper of the `to` method from the
        `Quantity <http://docs.astropy.org/en/stable/api/\
        astropy.units.Quantity.html#astropy.units.Quantity.to>`_ class
        and is only `valid` for physical dimensions.

        For example, if ::

            >>> print(x.coordinates)
            [0.4 0.3 0.2 0.1 0. ] G
            >>> x.to('µT')
            >>> print(x.coordinates)
            [40. 30. 20. 10.  0.] uT

        :params: `unit` : A string containing a unit with the same
            dimensionality as the controlled variable coordinates.
        :raise AttributeError: For non-quantitative controlled variables.
        """
        if self.variable_type in _quantitative_variable_types:
            if not isinstance(unit, str):
                raise TypeError(_type_message(str, type(unit)))

            if unit.strip() == 'ppm':
                self.gcv.set_attribute('_dimensionless_unit', _ppm)
            else:
                self.gcv.set_attribute(
                    '_unit', _check_unit_consistency(
                        1.0*string_to_unit(unit), self.gcv.unit
                    ).unit
                )
                self.gcv.set_attribute('_equivalencies', equivalencies)

        else:
            raise AttributeError(_attribute_message(self.variable_type, 'to'))

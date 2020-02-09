
-----------------------------
Interacting with CSDM objects
-----------------------------

Basic math operations
"""""""""""""""""""""

The csdm object supports basic mathematical operations such as additive and
multiplicative operations.

.. note:: All operation applied to or involving the csdm object applies only to
    the components of the dependent variables within the csdm object. These
    operations do not apply to the dimensions within the csdm object.

.. doctest::

    >>> arr1 = np.arange(6, dtype=np.float32).reshape(2, 3)
    >>> csdm_obj1 = cp.as_csdm(arr1)
    >>> # converting the dimension to proper physical dimensions.
    >>> csdm_obj1.dimensions[0]*=cp.ScalarQuantity('2.64 m')
    >>> csdm_obj1.dimensions[0].coordinates_offset = '1 km'
    >>> # converting the dimension to proper physical dimensions.
    >>> csdm_obj1.dimensions[1]*=cp.ScalarQuantity('10 µs')
    >>> csdm_obj1.dimensions[1].coordinates_offset = '-0.5 ms'
    >>> print(csdm_obj1)
    CSDM(
    DependentVariable(
    [[[0. 1. 2.]
      [3. 4. 5.]]], quantity_type=scalar, numeric_type=float32),
    LinearDimension([1000.   1002.64 1005.28] m),
    LinearDimension([-500. -490.] us)
    )


Additive operations involving a scalar
''''''''''''''''''''''''''''''''''''''

.. doctest::

    >>> csdm_obj1 += np.pi
    >>> print(csdm_obj1)
    CSDM(
    DependentVariable(
    [[[3.1415927 4.141593  5.141593 ]
      [6.141593  7.141593  8.141593 ]]], quantity_type=scalar, numeric_type=float32),
    LinearDimension([1000.   1002.64 1005.28] m),
    LinearDimension([-500. -490.] us)
    )

.. doctest::

    >>> csdm_obj2 = csdm_obj1 + (2 - 4j)
    >>> print(csdm_obj2)
    CSDM(
    DependentVariable(
    [[[ 5.141593-4.j  6.141593-4.j  7.141593-4.j]
      [ 8.141593-4.j  9.141593-4.j 10.141593-4.j]]], quantity_type=scalar, numeric_type=complex64),
    LinearDimension([1000.   1002.64 1005.28] m),
    LinearDimension([-500. -490.] us)
    )

Multiplicative operations involving scalar / ScalarQuantity
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

**Scalar multiplication**

.. doctest::

    >>> csdm_obj1 = cp.as_csdm(np.ones(6).reshape(2, 3))
    >>> csdm_obj2 = csdm_obj1 * 4.693
    >>> print(csdm_obj2)
    CSDM(
    DependentVariable(
    [[[4.693 4.693 4.693]
      [4.693 4.693 4.693]]], quantity_type=scalar, numeric_type=float64),
    LinearDimension([0. 1. 2.]),
    LinearDimension([0. 1.])
    )

.. doctest::

    >>> csdm_obj2 = csdm_obj1 * 3j/2.4
    >>> print(csdm_obj2)
    CSDM(
    DependentVariable(
    [[[0.+1.25j 0.+1.25j 0.+1.25j]
      [0.+1.25j 0.+1.25j 0.+1.25j]]], quantity_type=scalar, numeric_type=complex128),
    LinearDimension([0. 1. 2.]),
    LinearDimension([0. 1.])
    )

**ScalarQuantity multiplication**

You can change the dimensionality of the dependent variables by mutliplying the
csdm object with the appropriate scalar quantity, for example,

.. doctest::

    >>> csdm_obj1 *= cp.ScalarQuantity('3.23 m')
    >>> print(csdm_obj1)
    CSDM(
    DependentVariable(
    [[[3.23 3.23 3.23]
      [3.23 3.23 3.23]]] m, quantity_type=scalar, numeric_type=float64),
    LinearDimension([0. 1. 2.]),
    LinearDimension([0. 1.])
    )

.. doctest::

    >>> csdm_obj1 /= cp.ScalarQuantity('3.23 m')
    >>> print(csdm_obj1)
    CSDM(
    DependentVariable(
    [[[1. 1. 1.]
      [1. 1. 1.]]], quantity_type=scalar, numeric_type=float64),
    LinearDimension([0. 1. 2.]),
    LinearDimension([0. 1.])
    )


The additive operations are supported between two
csdm objects with exactly identical set of Dimension objects. For examples,

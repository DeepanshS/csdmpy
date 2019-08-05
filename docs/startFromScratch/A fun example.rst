
----------------
A fun 🤪 example
----------------

Let's make use of what we learnt so far and create a simple 1D{1} dataset.
To make it interesting, let's create an emoji dataset.

Start by importing the `csdmpy` package.

.. doctest::

    >>> import csdmpy as cp

Create a new dataset with the :meth:`~csdmpy.new` method.

.. doctest::

    >>> fundata = cp.new(description='An emoji dataset')

Here, `fundata` is an instance of the :ref:`csdm_api` class with a 0D{0} dataset.
The data structure of this instance is

.. doctest::

    >>> print(fundata.data_structure)
    {
      "csdm": {
        "version": "1.0",
        "description": "An emoji dataset",
        "dimensions": [],
        "dependent_variables": []
      }
    }

Add a labeled dimension to the `fundata` instance. Here, we'll make use of
python dictionary.

.. doctest::

    >>> x = {
    ...     'type': 'labeled',
    ...     'labels': ['🍈','🍉','🍋','🍌','🥑','🍍']
    ... }

The above python dictionary contains two keys. The `type` key identifies the
dimension as a labeled dimension while the `labels` key holds an
array of labels. In this example, the labels are emoji. Add this dictionary
as an argument of the :meth:`~csdmpy.csdm.CSDM.add_dimension` method
of the `fundata` instance.

.. doctest::

    >>> fundata.add_dimension(x)
    >>> print(fundata.data_structure)
    {
      "csdm": {
        "version": "1.0",
        "description": "An emoji dataset",
        "dimensions": [
          {
            "type": "labeled",
            "labels": [
              "🍈",
              "🍉",
              "🍋",
              "🍌",
              "🥑",
              "🍍"
            ]
          }
        ],
        "dependent_variables": []
      }
    }

We have successfully added a labeled dimension to the `fundata`
instance.

Next, add a dependent variable. Set up a python dictionary corresponding to the
dependent variable object and add this dictionary as an argument of the
:meth:`~csdmpy.csdm.CSDM.add_dependent_variable` method of the `fundata`
instance.

.. doctest::

    >>> y ={
    ...     'type': 'internal',
    ...     'numeric_type': 'float32',
    ...     'quantity_type': 'scalar',
    ...     'components': [[0.5, 0.25, 1, 2, 1, 0.25]]
    ... }
    >>> fundata.add_dependent_variable(y)

Here, the python dictionary contains `type`, `numeric_type` and
`components` key. The value of the `components` holds an array of data values
corresponding to the labels from the labeled dimension.

Now, we have a 😂 dataset...

.. doctest::

    >>> print(fundata.data_structure)
    {
      "csdm": {
        "version": "1.0",
        "description": "An emoji dataset",
        "dimensions": [
          {
            "type": "labeled",
            "labels": [
              "🍈",
              "🍉",
              "🍋",
              "🍌",
              "🥑",
              "🍍"
            ]
          }
        ],
        "dependent_variables": [
          {
            "type": "internal",
            "numeric_type": "float32",
            "quantity_type": "scalar",
            "components": [
              [
                "0.5, 0.25, ..., 1.0, 0.25"
              ]
            ]
          }
        ]
      }
    }

To serialize this file, use the :meth:`~csdmpy.csdm.CSDM.save` method of the
`fundata` instance as

.. doctest::

    >>> fundata.dependent_variables[0].encoding = 'base64'
    >>> fundata.save('my_file.csdf')

.. testcleanup::

    import os
    os.remove('csdmpy/my_file.csdf')

In the above code, the data values from the
:attr:`~csdmpy.csdm.CSDM.dependent_variables` attribute are first encoded as
a `base64` string prior to serializing to `my_file.csdf` file.
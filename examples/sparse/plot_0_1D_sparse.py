# -*- coding: utf-8 -*-
"""
Sparse along one dimension, 2D{1,1} dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
"""
#%%
# The following is an example [#f2]_ of a 2D{1,1} sparse dataset with two-dimensions,
# :math:`d=2`, and two, :math:`p=2`, sparse single-component dependent-variables,
# where the component is sparsely sampled along one dimension.

#%%
# Let's import the CSD model data-file.
import csdmpy as cp

filename = "https://osu.box.com/shared/static/1ltzzbdyeo5bn7xuxmdkxj3e4o1xvvjc.csdf"
sparse_1d = cp.load(filename)

#%%
# There are two linear dimensions and two single-component sparse dependent variables.
# The tuple of the dimension and the dependent variable instances are

x = sparse_1d.dimensions
y = sparse_1d.dependent_variables

#%%
# The coordinates, viewed only for the first ten coordinates, are

print(x[0].coordinates[:10])

#%%
print(x[1].coordinates[:10])

#%%
# Converting the coordinates to `ms`.

x[0].to("ms")
x[1].to("ms")

#%%
# **Visualizing the dataset**

import matplotlib.pyplot as plt

plt.contourf(
    x[0].coordinates.value,
    x[1].coordinates.value,
    y[0].components[0].real,
    cmap="gray_r",
)
plt.xlabel(x[0].axis_label)
plt.ylabel(x[1].axis_label)
plt.title(y[0].name)
plt.show()

#%%
# .. rubric:: Citation
#
# .. [#f2] Balsgart NM, Vosegaard T., Fast Forward Maximum entropy reconstruction
#          of sparsely sampled data., J Magn Reson. 2012, 223, 164-169.
#          doi: 10.1016/j.jmr.2012.07.002
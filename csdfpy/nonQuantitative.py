from __future__ import print_function, division
import numpy as np
import json
from .unit import unitToLatex
from ._csdmChecks import _checkAndAssignBool

class _nonQuantitativeControlledVariable:

    __slots__ = ['_sampling_type',
                 '_non_quantitative',
                 '_number_of_points',
                 '_coordinates', 
                 '_reverse',
                 '_label'
                 ]

    def __init__(self,  _coordinates, 
                        _sampling_type='grid',
                        _non_quantitative=True,
                        _reverse=False, 
                        _label=''):

        self.set_attribute('_sampling_type', _sampling_type)
        self.set_attribute('_non_quantitative', _non_quantitative)

        self.set_attribute('_number_of_points', len(_coordinates))

        ### reverse
        _value = _checkAndAssignBool(_reverse)
        self.set_attribute('_reverse', _value)

        ## label
        self.set_attribute('_label', _label)

        # print (_value)
        _value = np.asarray(_coordinates)
        self.set_attribute('_coordinates', _value)

    def set_attribute(self, name, value):
        super(_nonQuantitativeControlledVariable, self).__setattr__(name, value)

    def __delattr__(self, name):
        if name in __class__.__slots__:
            raise AttributeError("attribute '{0}' of class '{1}' cannot be deleted.".format(name, __class__.__name__))

    def __setattr__(self, name, value):
        if name in __class__.__slots__:
            raise AttributeError("attribute '{0}' cannot be modified".format(name))
        elif name in __class__.__dict__.keys():
            return self.set_attribute(name, value)
        else:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(__class__.__name__, name))


### --------------- Attributes ------------------ ###
    ## sampling_type
    @property
    def sampling_type(self):
        return self._sampling_type

    ## non_quantitative
    @property
    def non_quantitative(self):
        return self._non_quantitative

    ## label
    @property
    def label(self):
        return self._label
    @label.setter
    def label(self, label=''):
        self.set_attribute('_label', label)
    
    @property
    def axis_label(self):
        return self.label

    ## reverse
    @property
    def reverse(self):
        return self._reverse
    @reverse.setter
    def reverse(self, value=False):
        _value = _checkAndAssignBool(value)
        self.set_attribute('_reverse', _value)

    ## number_of_points
    @property
    def number_of_points(self):
        return self._number_of_points

    ## coordinates
    @property
    def coordinates(self):
        return self._coordinates


###--------------Private Methods------------------###

    def _info(self):
        _response =[self.sampling_type,
                    self.non_quantitative,
                    self.number_of_points,
                    self.reverse,
                    str(self._label)]
        return _response

    def _get_python_dictonary(self):
        dictionary = {}

        dictionary['coordinates'] = self.coordinates.tolist()
        dictionary['non_quantitative'] = True
        if self.reverse is True:
            dictionary['reverse'] = True

        if self._label.strip() != "":
            dictionary['label'] = self._label

        return dictionary

### ------------- Public Methods ------------------ ###

    def __str__(self):
        dictionary = self._get_python_dictonary()
        return (json.dumps(dictionary, sort_keys=False, indent=2))
from __future__ import print_function, division
import numpy as np
from unit import stringToQuantity, quantityFormat, unitToLatex, _ppm
from ._studium import (_assignAndCheckUnitConsistency, 
                      _checkAndAssignBool,
                      _checkQuantity,
                      _checkAssignmentAndThenCheckUnitConsistency)


class _nonLinearQuantitativeControlledVariable:

    __slots__ = ['_sampling_type',
                 '_quantitative',
                 '_quantity',
                 '_number_of_points',
                 '_coordinates',
                 '_reference_offset',
                 '_origin_offset', 
                 '_reverse',
                 '_label',
                 '_periodic',
                 '_made_dimensionless',

                 '_reciprocal_coordinates',
                 '_reciprocal_quantity',
                 '_reciprocal_number_of_points', 
                 '_reciprocal_origin_offset',
                 '_reciprocal_reference_offset', 
                 '_reciprocal_reverse',
                 '_reciprocal_label',
                 '_reciprocal_periodic',
                 '_reciprocal_made_dimensionless',

                 '_unit',
                 '_reciprocal_unit',
                 
                 '_absolute_coordinates',
                 '_reciprocal_absolute_coordinates']

    def __init__(self,  _coordinates, 
                        _reference_offset = None,
                        _origin_offset = None,
                        _quantity=None, 
                        _reverse=False, 
                        _label='',
                        _periodic=False,
                        _made_dimensionless = False,
                         
                        _sampling_type = 'grid',
                        _quantitative=False,

                        _reciprocal_reference_offset = None, 
                        _reciprocal_origin_offset = None,
                        _reciprocal_quantity = None,
                        _reciprocal_reverse = False, 
                        _reciprocal_label='',
                        _reciprocal_periodic = False,
                        _reciprocal_made_dimensionless = False):

        self.setAttribute('_sampling_type', _sampling_type)
        self.setAttribute('_quantitative', True)

        self.setAttribute('_number_of_points', len(_coordinates))
        self.setAttribute('_reciprocal_number_of_points', self.number_of_points)

        _unit = _assignAndCheckUnitConsistency(_coordinates[0], None).unit
        _reciprocal_unit = _unit**-1

        self.setAttribute('_unit', _unit)
        self.setAttribute('_reciprocal_unit', _reciprocal_unit)

        ## reference
        _value = _checkAssignmentAndThenCheckUnitConsistency(_reference_offset, _unit)
        self.setAttribute('_reference_offset', _value)
        _value = _checkAssignmentAndThenCheckUnitConsistency(_reciprocal_reference_offset, _reciprocal_unit)
        self.setAttribute('_reciprocal_reference_offset', _value)
        
        ## origin offset
        _value = _checkAssignmentAndThenCheckUnitConsistency(_origin_offset, _unit)
        self.setAttribute('_origin_offset', _value)
        _value =  _checkAssignmentAndThenCheckUnitConsistency(_reciprocal_origin_offset, _reciprocal_unit)
        self.setAttribute('_reciprocal_origin_offset', _value)

        ### made dimensionless
        _value = _checkAndAssignBool(_made_dimensionless)
        self.setAttribute('_made_dimensionless', _value)
        _value = _checkAndAssignBool(_reciprocal_made_dimensionless)
        self.setAttribute('_reciprocal_made_dimensionless', _value)
       
        ### reverse
        _value = _checkAndAssignBool(_reverse)
        self.setAttribute('_reverse', _value)
        _value = _checkAndAssignBool(_reciprocal_reverse)
        self.setAttribute('_reciprocal_reverse', _value)

        ## periodic 
        _value = _checkAndAssignBool(_periodic)
        self.setAttribute('_periodic', _value)
        _value = _checkAndAssignBool(_reciprocal_periodic)
        self.setAttribute('_reciprocal_periodic', _value)

        ## quantity
        _value = _checkQuantity(_quantity, _unit)
        self.setAttribute('_quantity', _value)
        _value = _checkQuantity(_reciprocal_quantity, _reciprocal_unit)
        self.setAttribute('_reciprocal_quantity', _value)
    
        ## label
        self.setAttribute('_label', _label)
        self.setAttribute('_reciprocal_label', _reciprocal_label)

        # [print (item) for item in _coordinates]
        _value = [_assignAndCheckUnitConsistency(item, _unit).to(_unit).value \
                                for item in _coordinates]
        # print (_value)
        _value = np.asarray(_value, dtype=np.float64)*_unit
        self.setAttribute('_coordinates', _value)
        self.setAttribute('_reciprocal_coordinates', None)
        self.setAttribute('_reciprocal_absolute_coordinates', None)
        self._getCoordinates()

    def setAttribute(self, name, value):
        super(_nonLinearQuantitativeControlledVariable, self).__setattr__(name, value)

    def __delattr__(self, name):
        if name in __class__.__slots__:
            raise AttributeError("attribute '{0}' of class '{1}' cannot be deleted.".format(name, __class__.__name__))

    def __setattr__(self, name, value):
        if name in __class__.__slots__:
            raise AttributeError("attribute '{0}' cannot be modified".format(name))
        elif name in __class__.__dict__.keys():
            return self.setAttribute(name, value)
        else:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(__class__.__name__, name))


### --------------- Attributes ------------------ ###
    ## sampling_type
    @property
    def sampling_type(self):
        return self._sampling_type

    ## quantitative
    @property
    def quantitative(self):
        return self._quantitative

    ## Periodic
    @property
    def periodic(self):
        return self._periodic
    @periodic.setter
    def periodic(self, value = True):
        self.setAttribute('_periodic', _checkAndAssignBool(value))
    
    ## reciprocal Periodic
    @property
    def reciprocal_periodic(self):
        return self._reciprocal_periodic
    @reciprocal_periodic.setter
    def reciprocal_periodic(self, value = True):
        self.setAttribute('_reciprocal_periodic', _checkAndAssignBool(value))

    ## Quantity
    @property
    def quantity(self):
        return self._quantity
    @quantity.setter
    def quantity(self, string = ''):
        self.setAttribute('_quantity', string)

    ## reciprocal Quantity
    @property
    def reciprocal_quantity(self):
        return self._reciprocal_quantity
    @reciprocal_quantity.setter
    def reciprocal_quantity(self, string = ''):
        self.setAttribute('_reciprocal_quantity', string)


    @property
    def unit(self):
        return self._unit

    @property
    def reciprocal_unit(self):
        return self._reciprocal_unit

    ## label
    @property
    def label(self):
        if self._label.strip() == '':
            return self.quantity + ' / ' + unitToLatex(self.coordinates.unit)
        else:
            return self._label + ' / ' + unitToLatex(self.coordinates.unit)
    @label.setter
    def label(self, label=''):
        self.setAttribute('_label', label)
    
    ## reciprocalLabel
    @property
    def reciprocal_label(self):
        return self._reciprocal_label
    @reciprocal_label.setter
    def reciprocal_label(self, label=''):
        self.setAttribute('_reciprocal_label', label)

    ## made dimensionless
    @property
    def made_dimensionless(self):
        return self._made_dimensionless
    @made_dimensionless.setter
    def made_dimensionless(self, value=False):
        _oldValue = self._made_dimensionless
        _value = _checkAndAssignBool(value)
        self.setAttribute('_made_dimensionless', _value)
        self._dimensionlessConversion(self.unit, _oldValue)

    ## reciprocal made dimensionless
    @property
    def reciprocal_made_dimensionless(self):
        return self._reciprocal_made_dimensionless
    @reciprocal_made_dimensionless.setter
    def reciprocal_made_dimensionless(self, value=False):
        _oldValue = self._reciprocal_made_dimensionless
        _value = _checkAndAssignBool(value)
        self.setAttribute('_reciprocal_made_dimensionless', _value)
        # self._dimensionlessConversion(self._reciprocal_unit, _oldValue)

    ## reverse
    @property
    def reverse(self):
        return self._reverse
    @reverse.setter
    def reverse(self, value=False):
        _value = _checkAndAssignBool(value)
        self.setAttribute('_reverse', _value)

    ## reciprocal reverse
    @property
    def reciprocal_reverse(self):
        return self._reciprocal_reverse
    @reciprocal_reverse.setter
    def reciprocal_reverse(self, value=False):
        _value = _checkAndAssignBool(value)
        self.setAttribute('_reciprocal_reverse', _value)
    
    ## reference offset
    @property
    def reference_offset(self):
        return self._reference_offset
    @reference_offset.setter
    def reference_offset(self, value):
        _value = _assignAndCheckUnitConsistency(value, self.unit)
        self.setAttribute('_reference_offset', _value)
        self._getCoordinates()

    ## reciprocal reference offset
    @property
    def reciprocal_reference_offset(self):
        return self._reciprocal_reference_offset
    @reciprocal_reference_offset.setter
    def reciprocal_reference_offset(self, value):
        _value = _assignAndCheckUnitConsistency(value, self.reciprocal_unit)
        self.setAttribute('_reciprocal_reference_offset', _value)
        self._getreciprocalCoordinates()

    ## origin offset
    @property
    def origin_offset(self):
        return self._origin_offset
    @origin_offset.setter
    def origin_offset(self, value):
        _value = _assignAndCheckUnitConsistency(value, self.unit)
        self.setAttribute('_origin_offset', _value)
        self._getCoordinates()

    ## reciprocal origin offset
    @property
    def reciprocal_origin_offset(self):
        return self._reciprocal_origin_offset
    @reciprocal_origin_offset.setter
    def reciprocal_origin_offset(self, value):
        _value = _assignAndCheckUnitConsistency(value, self.reciprocal_unit)
        self.setAttribute('_reciprocal_origin_offset', _value)
        self._getreciprocalCoordinates()

    ## number_of_points
    @property
    def number_of_points(self):
        return self._number_of_points

    ## coordinates
    @property
    def coordinates(self):
        return self._coordinates

    ## absolute_coordinates
    @property
    def absolute_coordinates(self):
        return self._absolute_coordinates

    ## reciprocal_coordinates
    @property
    def reciprocal_coordinates(self):
        return self._reciprocal_coordinates

    ## reciprocal_absolute_coordinates
    @property
    def reciprocal_absolute_coordinates(self):
        return self._reciprocal_absolute_coordinates

###--------------Methods------------------###

    def _dimensionlessConversion(self, unit, _oldValue):
        denominator = (self.origin_offset + self.reference_offset)
        if denominator.value != 0:
            if self.made_dimensionless and _oldValue: return
            if not self.made_dimensionless and not _oldValue: return
            if self.made_dimensionless and not _oldValue:
                _value = (self.coordinates/ denominator).to(_ppm)
                self.setAttribute('_coordinates', _value)
                return
            if not self.made_dimensionless and _oldValue:
                _value = (self.coordinates * denominator).to(unit)
                self.setAttribute('_coordinates', _value)
        else:
            self._made_dimensionless=_oldValue
            print("Zero division encountered: Dimension cannot be made dimensionsless with \n'origin_offset' {0} and 'reference_offset' {1}. No changes made.".format(self.origin_offset, self.reference_offset))

    def _info(self):
        _response =[self.sampling_type,
                    self.quantitative,
                    self.number_of_points, 
                    str(self.reference_offset),
                    str(self.origin_offset),
                    self.made_dimensionless,
                    self.reverse,
                    self.quantity,
                    str(self._label),
                    self.periodic]
        return _response
        
    def __str__(self):
        
        block = ['\tsampling_type \t\t= {0}\n', \
                 '\tquantitative \t\t= {1}\n', \
                 '\tnumber_of_points \t= {2}\n',\
                 '\treference_offset \t= {3}\n', \
                 '\torigin_offset \t\t= {4}\n', \
                 '\tmade_dimensionless \t= {5}\n', \
                 '\treverse \t\t= {6}\n', \
                 '\tquantity \t\t= {7}\n', \
                 '\tlabel \t\t\t= {8}\n', \
                 '\tperiodic \t\t= {9}\n']

        string = ''.join(block).format(self.sampling_type,
                                    self.quantitative,
                                    self.number_of_points, 
                                    self.reference_offset,
                                    self.origin_offset,
                                    self.made_dimensionless,
                                    self.reverse,
                                    self.quantity,
                                    self._label,
                                    self.periodic)
        return string

    def _getCoordinates(self):
        _unit = self.unit
        _reference_offset = self.reference_offset.to(_unit)
        _value = ( self.coordinates - _reference_offset )
        _origin_offset = self.origin_offset.to(_unit)
        if self.made_dimensionless:
            _value/=(_origin_offset + _reference_offset)
            # _value = _value.to(_ppm)
        self.setAttribute('_coordinates', _value)
        self.setAttribute('_absolute_coordinates', _value + _origin_offset)
### ------------- Public Methods ------------------ ###

    def getJsonDictionary(self):
        d = {}
        d['reciprocal'] = {}

        d['coordinates'] = [quantityFormat(item) for item in self.coordinates]

        if self.reference_offset is not None and self.reference_offset.value != 0:
            d['reference_offset'] = quantityFormat(self.reference_offset)
        if self.reciprocal_reference_offset is not None and self.reciprocal_reference_offset.value != 0:
            d['reciprocal']['reference_offset'] = quantityFormat(self.reciprocal_reference_offset)

        if self.origin_offset is not None and self.origin_offset.value != 0:
            d['origin_offset'] = quantityFormat(self.origin_offset)
        if self.reciprocal_origin_offset is not None and self.reciprocal_origin_offset.value != 0:
            d['reciprocal']['origin_offset'] = quantityFormat(self.reciprocal_origin_offset)

        # if self.made_dimensionless is True:
        #     d['made_dimensionless'] = True
    
        if self.reverse is True:
            d['reverse'] = True
        if self.reciprocal_reverse is True:
            d['reciprocal']['reverse'] = True


        if self.periodic is True:
            d['periodic'] = True
        if self.reciprocal_periodic is True:
            d['reciprocal']['periodic'] = True


        if self.quantity is not None:
            d['quantity'] = self.quantity
        if self.reciprocal_quantity not in [None, "unknown", "dimensionless"]:
            d['reciprocal']['quantity'] = self.reciprocal_quantity

        if self._label.strip() != "":
            d['label'] = self._label
        if self.reciprocal_label.strip() != "":
            d['reciprocal']['label'] = self.reciprocal_label

        if d['reciprocal'] == {}:
            del d['reciprocal']

        return d

    def to(self, unit):
        _values = self.coordinates.to(unit)
        self.setAttribute('_coordinates', _values)

    def __iadd__(self, other):
        self.reference_offset -= _assignAndCheckUnitConsistency(other, self.unit) 

    def __isub__(self, other):
        self.reference_offset += _assignAndCheckUnitConsistency(other, self.unit) 
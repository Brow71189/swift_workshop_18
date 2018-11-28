# system imports
import gettext
import numpy as np
from nion.swift.model import DataItem
from nion.swift.model import DocumentModel
from nion.swift.model import Symbolic
from nion.swift import Facade

# local libraries
from nion.typeshed import API_1_0 as API

_ = gettext.gettext

correct_dark_script = """
import numpy as np

data = src1.xdata.data
data_shape = np.array(src1.xdata.data.shape)
dark_area = np.rint(np.array(dark_area_region.bounds) * np.array((data_shape[:2], data_shape[:2]))).astype(np.int)
crop_area = np.rint(np.array(crop_region.bounds) * np.array((data_shape[2:], data_shape[2:]))).astype(np.int)

dark_image = np.mean(data[dark_area[0, 0]:dark_area[0, 0]+dark_area[1, 0],
                          dark_area[0, 1]:dark_area[0, 1]+dark_area[1, 1],
                          crop_area[0, 0]:crop_area[0, 0]+crop_area[1, 0],
                          crop_area[0, 1]:crop_area[0, 1]+crop_area[1, 1]], axis=(0, 1))

new_data = data[..., crop_area[0, 0]:crop_area[0, 0]+crop_area[1, 0],
                     crop_area[0, 1]:crop_area[0, 1]+crop_area[1, 1]] - dark_image
if gain_image:
    gain_data = gain_image.xdata.data
    if gain_data.shape == new_data.shape[2:]:
        new_data *= gain_image.xdata.data
    elif gain_data.shape == data.shape[2:]:
        new_data *= gain_image.xdata.data[crop_area[0, 0]:crop_area[0, 0]+crop_area[1, 0],
                                          crop_area[0, 1]:crop_area[0, 1]+crop_area[1, 1]]
    else:
        raise ValueError('Shape of gain image has to match last two dimensions input data.')

if bin_spectrum:
    target.set_data(np.sum(new_data, axis=-2))
    target.set_dimensional_calibrations(src1.xdata.dimensional_calibrations[:2] + src1.xdata.dimensional_calibrations[3:])
else:
    target.set_data(new_data)
    target.set_dimensional_calibrations(src1.xdata.dimensional_calibrations[:])
target.set_intensity_calibration(src1.xdata.intensity_calibration)
"""

correct_dark_processing_descriptions = {
    "nion.4d_dark_correction":
        {'script': correct_dark_script,
         'sources': [
                     {'name': 'src1', 'label': 'Source',
                      'regions': [{'name': 'crop_region', 'type': 'rectangle'}]},
                      #'requirements': [{'type': 'dimensionality', 'min': 4, 'max': 4}]},
                     {'name': 'src2', 'label': 'Total Bin Data Item',
                      'regions': [{'name': 'dark_area_region', 'type': 'rectangle'}]}
                      #'requirements': [{'type': 'dimensionality', 'min': 2, 'max': 2}]}
                     ],
         #'out_regions': [{'name': 'display_slice', 'type': 'point', 'params': {'label': 'Display Slice'}}],
         #'connections': [{'type': 'property', 'src': 'display', 'src_prop': 'collection_index', 'dst': 'display_slice', 'dst_prop': 'position'}],
         'parameters': [{'name': 'bin_spectrum', 'type': 'boolean', 'value_default': True, 'value': True,
                         'label': 'bin spectrum to 1d'},
                        {'name': 'gain_image', 'type': 'data_item', 'label': 'gain image', 'value': None,
                         'value_default': None}],
         'title': '4D dark correction'
         }
}

total_bin_4D_SI_script = """
import numpy as np
target.set_data(np.mean(src.xdata.data, axis=(-2, -1)))
target.set_dimensional_calibrations(src.xdata.dimensional_calibrations[:2])
target.set_intensity_calibration(src.xdata.intensity_calibration)
"""
calculate_average_processing_descriptions = {
    "nion.total_bin_4d_SI":
        {'script': total_bin_4D_SI_script,
         'sources': [
                     {'name': 'src', 'label': 'Source',
                      'regions': [],
                      'requirements': [{'type': 'dimensionality', 'min': 4, 'max': 4}]}
                     ],
         #'out_regions': [{'name': 'display_slice', 'type': 'point', 'params': {'label': 'Display Slice'}}],
         #'connections': [{'type': 'property', 'src': 'display', 'src_prop': 'collection_index', 'dst': 'display_slice', 'dst_prop': 'position'}],
         'title': 'Total bin 4D'
         }
}

class TotalBin4D:
    def __init__(self, computation, **kwargs):
        self.computation = computation
        
    def execute(self, src, test):
        self.__new_data = np.mean(src.xdata.data, axis=(-2, -1))
    
    def commit(self):
        self.computation.set_referenced_data('target', self.__new_data)
        
class DarkCorrection4DMenuItem:

    menu_id = "_processing_menu"  # required, specify menu_id where this item will go
    menu_item_name = _("4D Dark Correction")  # menu item name

    DocumentModel.DocumentModel.register_processing_descriptions(correct_dark_processing_descriptions)
    #DocumentModel.DocumentModel.register_processing_descriptions(calculate_average_processing_descriptions)
    
    def __init__(self, api):
        self.__api = api

    def menu_item_execute(self, window: API.DocumentWindow) -> None:
        try:
            document_controller = window._document_controller
            display_specifier = document_controller.selected_display_specifier
            data_item = window.target_data_item
            if data_item:
                total_bin_data_item = self.__api.library.create_data_item(title='Total bin 4D of' + display_specifier.data_item.title)
                computation = self.__api.library.create_computation('nion.total_bin_4d_SI',
                                                                    inputs={'src': data_item,
                                                                            'test': True},
                                                                    outputs={'target': total_bin_data_item})
                computation._computation.source = data_item._data_item
                window.display_data_item(total_bin_data_item)
                
                api_total_bin_data_item = total_bin_data_item
                api_data_item = data_item
                dark_subtract_area_graphic = api_total_bin_data_item.add_rectangle_region(0.8, 0.5, 0.4, 1.0)
                dark_subtract_area_graphic.label = 'Dark subtract area'
                crop_region = api_data_item.add_rectangle_region(0.5, 0.5, 1.0, 1.0)
                crop_region.label = 'Crop'
                
                dark_corrected_data_item = document_controller.document_model.make_data_item_with_computation(
                        "nion.4d_dark_correction", [(display_specifier.data_item, None), (total_bin_data_item._data_item, None)],
                        {"src1": [crop_region._graphic], "src2": [dark_subtract_area_graphic._graphic]})
                new_display_specifier2 = DataItem.DisplaySpecifier.from_data_item(dark_corrected_data_item)
                document_controller.display_data_item(new_display_specifier2)
                
                dark_subtract_area_graphic._graphic.is_bounds_constrained = True
                crop_region._graphic.is_bounds_constrained = True
        except Exception as e:
            print(e)
            raise

class DarkCorrection4DExtension:

    # required for Swift to recognize this as an extension class.
    extension_id = "nion.extension.4d_dark_correction"

    def __init__(self, api_broker):
        # grab the api object.
        api = api_broker.get_api(version="1", ui_version="1")
        # be sure to keep a reference or it will be closed immediately.
        self.__menu_item_ref = api.create_menu_item(DarkCorrection4DMenuItem(api))

    def close(self):
        self.__menu_item_ref.close()
        
Symbolic.register_computation_type('nion.total_bin_4d_SI', TotalBin4D)
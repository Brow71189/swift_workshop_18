# system imports
import gettext
import time
from nion.swift.model import DataItem
from nion.swift.model import DocumentModel
from nion.swift import Facade

# local libraries
from nion.typeshed import API_1_0 as API

_ = gettext.gettext

correct_dark_script = """
import numpy as np
data = src1.xdata.data
data_shape = np.array(src1.xdata.data.shape)
cam_center = int(round(data_shape[-2]/2)) if camera_center == -1 else camera_center
spectrum_area = np.rint(np.array(spectrum_region.bounds) * data_shape[2:]).astype(np.int)
top_dark_area = np.rint(np.array(top_dark_region.bounds) * data_shape[2:]).astype(np.int)
bottom_dark_area = np.rint(np.array(bottom_dark_region.bounds) * data_shape[2:]).astype(np.int)
spectrum_range_y = np.array((spectrum_area[0,0], spectrum_area[0,0] + spectrum_area[1, 0]))
top_dark_area_range_y = np.array((top_dark_area[0,0], top_dark_area[0,0] + top_dark_area[1, 0]))
bottom_dark_area_range_y = np.array((bottom_dark_area[0,0], bottom_dark_area[0,0] + bottom_dark_area[1, 0]))
if (cam_center >= spectrum_range_y).all(): # spectrum is above center
    dark_image = np.mean(data[..., top_dark_area_range_y[0]:top_dark_area_range_y[1], :], axis=-2, keepdims=True)
    corrected_image = data[..., spectrum_range_y[0]:spectrum_range_y[1], :] - np.repeat(dark_image, spectrum_range_y[1]-spectrum_range_y[0], axis=-2)
elif (cam_center <= spectrum_range_y).all(): # spectrum is below center
    dark_image = np.mean(data[..., bottom_dark_area_range_y[0]:bottom_dark_area_range_y[1], :], axis=-2, keepdims=True)
    corrected_image = data[..., spectrum_range_y[0]:spectrum_range_y[1], :] - np.repeat(dark_image, spectrum_range_y[1]-spectrum_range_y[0], axis=-2)
else: # spectrum is on top of center
    dark_image = np.mean(data[..., top_dark_area_range_y[0]:top_dark_area_range_y[1], :], axis=-2, keepdims=True)
    corrected_image_top = data[..., spectrum_range_y[0]:cam_center, :] - np.repeat(dark_image, cam_center-spectrum_range_y[0], axis=-2)
    dark_image = np.mean(data[..., bottom_dark_area_range_y[0]:bottom_dark_area_range_y[1], :], axis=-2, keepdims=True)
    corrected_image_bot = data[..., cam_center:spectrum_range_y[1], :] - np.repeat(dark_image, spectrum_range_y[1]-cam_center, axis=-2)
    corrected_image = np.concatenate((corrected_image_top, corrected_image_bot), axis=-2)
    corrected_image_top = None
    corrected_image_bot = None
dark_image = None # don't hold references to unused objects so that garbage collector can free the memorz
if bin_spectrum:
    target.set_data(np.sum(corrected_image, axis=-2))
    target.set_dimensional_calibrations(src1.xdata.dimensional_calibrations[:2] + src1.xdata.dimensional_calibrations[3:])
else:
    target.set_data(corrected_image)
    target.set_dimensional_calibrations(src1.xdata.dimensional_calibrations[:])
    
target.set_intensity_calibration(src1.xdata.intensity_calibration)
"""

correct_dark_processing_descriptions = {
    "nion.framewise_dark_correction":
        {'script': correct_dark_script,
         'sources': [
                     {'name': 'src1', 'label': 'Source',
                      'regions': []},
                      #'requirements': [{'type': 'dimensionality', 'min': 4, 'max': 4}]},
                     {'name': 'src2', 'label': 'Average Data Item',
                      'regions': [{'name': 'spectrum_region', 'type': 'rectangle'},
                                  {'name': 'top_dark_region', 'type': 'rectangle'},
                                  {'name': 'bottom_dark_region', 'type': 'rectangle'}]}
                      #'requirements': [{'type': 'dimensionality', 'min': 2, 'max': 2}]}
                     ],
         #'out_regions': [{'name': 'display_slice', 'type': 'point', 'params': {'label': 'Display Slice'}}],
         #'connections': [{'type': 'property', 'src': 'display', 'src_prop': 'collection_index', 'dst': 'display_slice', 'dst_prop': 'position'}],
         'parameters': [{'name': 'bin_spectrum', 'type': 'boolean', 'value_default': True, 'value': True,
                         'label': 'bin spectrum to 1d'},
                        {'name': 'camera_center', 'type': 'integral', 'value_default': -1, 'value': -1,
                         'label': 'camera center', 'value_min': -1, 'value_max': 2048}],
         'title': 'Framewise dark correction'
         }
}

calculate_average_script = """
import numpy as np
target.set_data(np.mean(src.xdata.data, axis=(0, 1)))
target.set_dimensional_calibrations(src.xdata.dimensional_calibrations[2:])
target.set_intensity_calibration(src.xdata.intensity_calibration)
"""
calculate_average_processing_descriptions = {
    "nion.calculate_4d_average":
        {'script': calculate_average_script,
         'sources': [
                     {'name': 'src', 'label': 'Source',
                      'regions': [],
                      'requirements': [{'type': 'dimensionality', 'min': 4, 'max': 4}]}
                     ],
         #'out_regions': [{'name': 'display_slice', 'type': 'point', 'params': {'label': 'Display Slice'}}],
         #'connections': [{'type': 'property', 'src': 'display', 'src_prop': 'collection_index', 'dst': 'display_slice', 'dst_prop': 'position'}],
         'title': 'Frame Average'
         }
}

class FramewiseDarkMenuItem:

    menu_id = "_processing_menu"  # required, specify menu_id where this item will go
    menu_item_name = _("Framewise Dark Correction")  # menu item name

    DocumentModel.DocumentModel.register_processing_descriptions(correct_dark_processing_descriptions)
    DocumentModel.DocumentModel.register_processing_descriptions(calculate_average_processing_descriptions)

    def menu_item_execute(self, window: API.DocumentWindow) -> None:
        try:
            document_controller = window._document_controller
            display_specifier = document_controller.selected_display_specifier

            if display_specifier.data_item:
                average_data_item = document_controller.document_model.make_data_item_with_computation(
                    "nion.calculate_4d_average", [(display_specifier.data_item, None)],
                    {'src': []})
                new_display_specifier = DataItem.DisplaySpecifier.from_data_item(average_data_item)
                document_controller.display_data_item(new_display_specifier)
                api_average_data_item = Facade.DataItem(average_data_item)
                spectrum_graphic = api_average_data_item.add_rectangle_region(0.5, 0.5, 0.1, 1.0)
                spectrum_graphic.label = 'Spectrum'
                bottom_dark_graphic = api_average_data_item.add_rectangle_region(0.7, 0.5, 0.1, 1.0)
                bottom_dark_graphic.label = 'Bottom dark area'
                top_dark_graphic = api_average_data_item.add_rectangle_region(0.3, 0.5, 0.1, 1.0)
                top_dark_graphic.label = 'Top dark area'
                dark_corrected_data_item = document_controller.document_model.make_data_item_with_computation(
                        "nion.framewise_dark_correction", [(display_specifier.data_item, None), (average_data_item, None)],
                        {"src1": [], "src2": [spectrum_graphic._graphic, top_dark_graphic._graphic, bottom_dark_graphic._graphic]})
                new_display_specifier2 = DataItem.DisplaySpecifier.from_data_item(dark_corrected_data_item)
                document_controller.display_data_item(new_display_specifier2)
                spectrum_graphic._graphic.is_bounds_constrained = True
                bottom_dark_graphic._graphic.is_bounds_constrained = True
                top_dark_graphic._graphic.is_bounds_constrained = True
        except Exception as e:
            print(e)
            raise

class FramewiseDarkExtension:

    # required for Swift to recognize this as an extension class.
    extension_id = "nion.extension.framewise_dark_correction"

    def __init__(self, api_broker):
        # grab the api object.
        api = api_broker.get_api(version="1", ui_version="1")
        # be sure to keep a reference or it will be closed immediately.
        self.__menu_item_ref = api.create_menu_item(FramewiseDarkMenuItem())

    def close(self):
        self.__menu_item_ref.close()
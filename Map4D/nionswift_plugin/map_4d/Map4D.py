# system imports
import gettext
from nion.swift.model import DataItem
from nion.swift.model import DocumentModel

# local libraries
from nion.typeshed import API_1_0 as API

_ = gettext.gettext

map_4d_script = """
import numpy
mask_data = region.mask_xdata_with_shape(src.xdata.data_shape[2:]).data
new_data = numpy.sum(src.xdata.data * mask_data, axis=(-2, -1))
target.set_data(new_data)
target.set_dimensional_calibrations(src.xdata.dimensional_calibrations[:2])
target.set_intensity_calibration(src.xdata.intensity_calibration)
"""

processing_descriptions = {
    "nion.map_4d":
        {'script': map_4d_script,
         'sources': [
                     {'name': 'src', 'label': 'Source',
                      'regions': [{'name': 'region', 'type': 'rectangle', 'params': {'label': 'Map Region'}}],
                      'requirements': [{'type': 'dimensionality', 'min': 4, 'max': 4}]}
                     ],
         #'out_regions': [{'name': 'display_slice', 'type': 'point', 'params': {'label': 'Display Slice'}}],
         #'connections': [{'type': 'property', 'src': 'display', 'src_prop': 'collection_index', 'dst': 'display_slice', 'dst_prop': 'position'}],
         'title': 'Map 4D'
         }
}

class Map4DMenuItem:

    menu_id = "_processing_menu"  # required, specify menu_id where this item will go
    menu_item_name = _("Map 4D")  # menu item name

    DocumentModel.DocumentModel.register_processing_descriptions(processing_descriptions)

    def menu_item_execute(self, window: API.DocumentWindow) -> None:
        try:
            document_controller = window._document_controller
            display_specifier = document_controller.selected_display_specifier

            if display_specifier.data_item:
                data_item = document_controller.document_model.make_data_item_with_computation("nion.map_4d", [(display_specifier.data_item, None)], {'src': [None]})
                new_display_specifier = DataItem.DisplaySpecifier.from_data_item(data_item)
                document_controller.display_data_item(new_display_specifier)
        except Exception as e:
            print(e)
            raise

class Map4DExtension:

    # required for Swift to recognize this as an extension class.
    extension_id = "nion.extension.map_4d"

    def __init__(self, api_broker):
        # grab the api object.
        api = api_broker.get_api(version="1", ui_version="1")
        # be sure to keep a reference or it will be closed immediately.
        self.__menu_item_ref = api.create_menu_item(Map4DMenuItem())

    def close(self):
        self.__menu_item_ref.close()
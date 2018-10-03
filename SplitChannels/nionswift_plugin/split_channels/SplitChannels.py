# system imports
import gettext
from nion.swift.model import DataItem
from nion.swift.model import DocumentModel

# local libraries
from nion.typeshed import API_1_0 as API

_ = gettext.gettext

split_channels_script = """
import copy
channel_remove = [(1, 2), (0, 2), (0, 1)]
xdata = copy.deepcopy(src.display_xdata)
xdata.data[..., channel_remove[channel]] = 0
target.xdata = xdata
target.set_dimensional_calibrations(src.display_xdata.dimensional_calibrations)
target.set_intensity_calibration(src.display_xdata.intensity_calibration)
target.title = ['Blue', 'Green', 'Red'][channel] + ' Channel of ' + src.data_item.title
"""

processing_descriptions = {
    "univie.extension.split_channels":
        {'script': split_channels_script,
         'sources': [
                     {'name': 'src', 'label': 'Source', 'requirements': [{'type': 'rgb'}]}
                     ],
         'parameters': [
                        {'name': 'channel', 'label': 'Channel', 'type': 'integral', 'value': 2, 'value_default': 2, 'value_min': 0, 'value_max': 2, 'control_type': 'slider'}
                        ],
         'title': 'Split Channel'
         }
}

class SplitChannelsMenuItem:

    menu_id = "_processing_menu"  # required, specify menu_id where this item will go
    menu_item_name = _("Split Channels")  # menu item name

    DocumentModel.DocumentModel.register_processing_descriptions(processing_descriptions)

    def menu_item_execute(self, window: API.DocumentWindow) -> None:
        try:
            document_controller = window._document_controller
            display_specifier = document_controller.selected_display_specifier

            if display_specifier.data_item and display_specifier.data_item.xdata.is_data_rgb:
                data_item = document_controller.document_model.make_data_item_with_computation("univie.extension.split_channels", [(display_specifier.data_item, None)])
                new_display_specifier = DataItem.DisplaySpecifier.from_data_item(data_item)
                document_controller.display_data_item(new_display_specifier)
        except Exception as e:
            print(e)


class SplitChannelsExtension:

    # required for Swift to recognize this as an extension class.
    extension_id = "univie.split_channels"

    def __init__(self, api_broker):
        # grab the api object.
        api = api_broker.get_api(version="1", ui_version="1")
        # be sure to keep a reference or it will be closed immediately.
        self.__menu_item_ref = api.create_menu_item(SplitChannelsMenuItem())

    def close(self):
        self.__menu_item_ref.close()
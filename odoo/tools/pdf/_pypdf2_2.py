from PyPDF2 import errors, filters, generic, PdfReader, PdfWriter as _Writer
from PyPDF2.generic import create_string_object
from PyPDF2 import __version__  # noqa: F401

# PyPDF2 3.0+ uses get_object/set_data/get_data; 2.x uses getObject/setData/getData
if not hasattr(generic.PdfObject, 'get_object'):
    generic.PdfObject.get_object = lambda self: self.getObject()
if not hasattr(generic.StreamObject, 'set_data'):
    generic.StreamObject.set_data = lambda self, data: self.setData(data)
if not hasattr(generic.StreamObject, 'get_data'):
    generic.StreamObject.get_data = lambda self: self.getData()

__all__ = [
    "PdfReader",
    "PdfWriter",
    "create_string_object",
    "errors",
    "filters",
    "generic",
]


class PdfWriter(_Writer):
    def getFields(self, *args, **kwargs):
        return self.get_fields(*args, **kwargs)

    def _addObject(self, *args, **kwargs):
        return self._add_object(*args, **kwargs)

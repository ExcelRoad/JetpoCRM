import openpyxl
from django.http import HttpResponse
from django.utils import timezone

def export_to_excel(queryset, filename_prefix="export"):
    """
    Generic function to export a queryset to an Excel file.
    """
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    timestamp = timezone.now().strftime('%Y-%m-%d_%H-%M')
    response['Content-Disposition'] = f'attachment; filename={filename_prefix}_{timestamp}.xlsx'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = filename_prefix.capitalize()

    # Get model fields
    model = queryset.model
    opts = model._meta
    fields = [field for field in opts.fields if not field.many_to_many and not field.one_to_many]
    
    # Write Hedaer
    header = [field.verbose_name.title() for field in fields]
    ws.append(header)

    # Write Data
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field.name)
            if value is None:
                value = ""
            elif hasattr(value, 'strftime'): # Handle dates
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif hasattr(value, '__str__'):
                value = str(value)
            
            row.append(value)
        ws.append(row)

    wb.save(response)
    return response

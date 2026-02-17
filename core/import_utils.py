import csv
import io
import logging
from django.http import HttpResponse
from django.db import models

logger = logging.getLogger(__name__)

def generate_csv_template(model, excluded_fields=None):
    """
    Generates a CSV template file for a given model with only mandatory fields.
    """
    if excluded_fields is None:
        excluded_fields = ['id', 'created_at', 'updated_at']
    
    opts = model._meta
    fields = []
    
    for field in opts.fields:
        if field.name in excluded_fields or field.auto_created:
            continue
        
        fields.append(field.name)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{opts.model_name}_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow(fields)
    return response

def parse_csv_row_count(file_content):
    """
    Returns the number of rows in the CSV file (excluding header), detecting delimiter.
    """
    try:
        try:
            decoded_file = file_content.decode('utf-8-sig')
        except UnicodeDecodeError:
            try:
                # Try Hebrew codepage (Standard Excel CSV in Hebrew)
                decoded_file = file_content.decode('cp1255')
            except UnicodeDecodeError:
                try:
                    decoded_file = file_content.decode('iso-8859-8')
                except UnicodeDecodeError:
                    decoded_file = file_content.decode('latin-1')
            
        if not decoded_file.strip():
            return 0
            
        io_string = io.StringIO(decoded_file)
        
        # Detect delimiter
        try:
            sample = decoded_file[:4096]
            dialect = csv.Sniffer().sniff(sample, delimiters=',;\t')
        except:
            dialect = 'excel'
            
        reader = csv.reader(io_string, dialect=dialect)
        header = next(reader, None)
        if header is None:
            return 0
            
        count = 0
        for row in reader:
            if any(cell.strip() for cell in row):
                count += 1
        return count
    except Exception as e:
        logger.error(f"Error parsing CSV count: {e}")
        return 0

def get_csv_data(file_content):
    """
    Parses CSV content and returns a list of dictionaries, detecting delimiter.
    """
    try:
        try:
            decoded_file = file_content.decode('utf-8-sig')
        except UnicodeDecodeError:
            try:
                # Try Hebrew codepage (Standard Excel CSV in Hebrew)
                decoded_file = file_content.decode('cp1255')
            except UnicodeDecodeError:
                try:
                    decoded_file = file_content.decode('iso-8859-8')
                except UnicodeDecodeError:
                    decoded_file = file_content.decode('latin-1')
            
        io_string = io.StringIO(decoded_file)
        
        try:
            sample = decoded_file[:4096]
            dialect = csv.Sniffer().sniff(sample, delimiters=',;\t')
        except:
            dialect = 'excel'
            
        reader = csv.DictReader(io_string, dialect=dialect)
        return [row for row in reader if any(val.strip() for val in row.values() if val)]
    except Exception as e:
        logger.error(f"Error getting CSV data: {e}")
        return []

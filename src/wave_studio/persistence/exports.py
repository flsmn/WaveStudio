import csv
import io
import json
from .projects import atomic_write,validate_reference


def export_csv(path,result,quantity='Intensity'):
    validate_reference(result)
    if quantity not in ('Intensity','Field'):raise ValueError('Unsupported export quantity.')
    field=quantity=='Field'
    if field and 'field_values' not in result:raise ValueError('This profile contains intensity only; no field snapshot is available.')
    values=result['field_values'] if field else result['values']
    stream=io.StringIO(newline='')
    stream.write('# Wave Studio signed field snapshot; position: project reference length; field: relative\n' if field else '# Wave Studio relative intensity; position: project reference length; intensity: relative field squared\n')
    metadata={k:v for k,v in result.items() if k not in ('values','field_values','axis','positions')}
    if field:metadata.update(quantity='Field',method='bilinear signed field snapshot',time=result['field_time'])
    stream.write('# metadata: '+json.dumps(metadata,allow_nan=False)+'\n')
    writer=csv.writer(stream)
    writer.writerow(['distance_reference_length','x_reference_length','y_reference_length','relative_field' if field else 'relative_mean_field_squared'])
    for distance,point,value in zip(result['axis'],result['positions'],values): writer.writerow([distance,*point,value])
    atomic_write(path,stream.getvalue().encode('utf8'))

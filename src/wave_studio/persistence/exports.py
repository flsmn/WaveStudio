import csv
import io
import json
from .projects import atomic_write,validate_reference


def export_csv(path,result):
    validate_reference(result)
    stream=io.StringIO(newline='')
    stream.write('# Wave Studio relative intensity; position: project reference length; intensity: relative field squared\n')
    stream.write('# metadata: '+json.dumps({k:v for k,v in result.items() if k not in ('values','axis','positions')},allow_nan=False)+'\n')
    writer=csv.writer(stream)
    writer.writerow(['distance_reference_length','x_reference_length','y_reference_length','relative_mean_field_squared'])
    for distance,point,value in zip(result['axis'],result['positions'],result['values']): writer.writerow([distance,*point,value])
    atomic_write(path,stream.getvalue().encode('utf8'))

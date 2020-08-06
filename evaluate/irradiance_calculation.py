"""
Scripts to evaluate the calculated irradiance across the output.
This may eventually be done directly from MongoDB

"""
import os
import json
from statistics import mean

root_dir = '/home/edward/pv/alcf/output_analysis'
this_dir = os.path.join(root_dir, 'output_040520')


def evaluate_irradiance_from_directory(input_path):

    # Get the file paths
    file_paths = [os.path.join(input_path, file) for file in os.listdir(input_path)]

    total_success = 0
    total_fail = 0
    failure_info = [['html_link', 'voc', 'jsc', 'ff', 'pce', 'extracted_ss', 'calc_ss', 'calc_ss_error']]
    for file in file_paths:
        with open(file, 'r') as f:
            json_text = f.read()

        json_info = json.loads(json_text)

        local_success = 0
        local_fail = 0
        # Get the irradiance info if available
        for record in json_info:
            if 'solar_simulator' in record['device_metrology'].keys():
                if all(key in record['device_metrology']['solar_simulator'].keys() for key in ['calculated_value', 'calculated_units', 'std_value']):
                    test_values = record['device_metrology']['solar_simulator']['std_value']
                    calc_values = record['device_metrology']['solar_simulator']['calculated_value']
                    calc_error = record['device_metrology']['solar_simulator']['calculated_error']

                    for i, val in enumerate(test_values):

                        if (calc_values[i] - calc_error) <= val <= (calc_values[i] + calc_error):
                            local_success += 1
                        else:
                            local_fail += 1
                            html_link = record['article_info']['html_url']
                            device_characteristics = record['device_characteristics']
                            failure_info.append([html_link, device_characteristics['voc'], device_characteristics['jsc'], \
                                                 device_characteristics['ff'], device_characteristics['pce'], test_values, calc_values, calc_error])


        print('For document %s the results are...' % file)
        print('Successes: %s' % str(local_success))
        print('Failures: %s' % str(local_fail))
        total_success += local_success
        total_fail += local_fail

    print('Total stats are...')
    print('Successes: %s' % str(total_success))
    print('Failures: %s' % str(total_fail))




if __name__ == '__main__':
    evaluate_irradiance_from_directory(this_dir)

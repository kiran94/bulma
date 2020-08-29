import json
import subprocess
import os
import re
import argparse
import base64
import pandas as pd
import shutil
import pprint


def run_corpus(configuration, **kwargs):
    for index, case in enumerate(configuration['Corpus']):
        case['desc'] = kwargs.get('description_sub_regex').sub('_', case['desc']).lower()

        print(index+1, '-', case['desc'])

        append_headers = kwargs.get('append_headers', None)
        if append_headers:
            print('Appending Headers')
            case['header'].update(append_headers)

        if 'body_file' in case:
            print('Fetching Body File')
            body_file_path = case['body_file']
            with open(body_file_path, 'r') as f:
                case['body'] = f.read()
            del case['body_file']

        if 'body' in case:
            print('Encoding Body')
            message_bytes = case['body'].encode('ascii')
            base64_bytes = base64.b64encode(message_bytes)
            case['body'] = base64_bytes.decode('ascii')

        with open(args.temp_file, mode='w') as f:
            json.dump(case, f, indent=None)

        output_file = os.path.join(kwargs.get("output_path"), case["desc"]) + ".bin"

        cmd = f'cat {kwargs.get("temp_file")} | jq -cM | {kwargs.get("vegeta_path")} attack -duration {configuration["Duration"]} -format json > {output_file}'
        print(cmd)
        subprocess.run(cmd, shell=True, encoding='utf-8')

        os.remove(args.temp_file)
        yield {'desc': case['desc'], 'file': output_file}


def generate_report(output_files, **kwargs):
    for result in output_files:
        output_file = os.path.join(kwargs.get("output_path"), result["desc"]) + "_report.json"
        cmd = f'cat {result["file"]} | {kwargs.get("vegeta_path")} report -type json > {output_file}'
        print(cmd)
        subprocess.run(cmd, shell=True, encoding='utf-8')
        result['report_json'] = output_file
        yield result


def write_report(results, **kwargs):
    frames = []

    for res in results:
        with open(res['report_json'], 'r') as f:
            raw = f.read()
            json_raw = json.loads(raw)
            frame = pd.json_normalize(json_raw)
            frame['desc'] = res['desc']
            frame.set_index('desc', inplace=True)
            frames.append(frame)

    results = pd.concat(frames)

    if kwargs.get('output') == 'csv':
        results.to_csv('output.csv')
    else:
        with open('output.md', 'w') as f:
            f.write(f'# {kwargs.get("title", "Project")} \n')
            f.write(f'## Results \n')
            results.to_markdown(f)
            f.write('\n')
            f.write(f'## Configuration \n')
            f.write(f'```json \n')
            f.write(pprint.pformat(kwargs.get('configuration'), indent=2))
            f.write(f'``` \n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='bulma.config.json')
    parser.add_argument('-t', '--temp_file', default='temp.json')
    parser.add_argument('--vegeta_path', default='vegeta')
    parser.add_argument('--output_path', default='output/')
    parser.add_argument('--description_sub_regex', default='[^A-Za-z0-9]+')
    parser.add_argument('--output', choices=['csv', 'md'], default='md')

    args = parser.parse_args()

    with open(args.config, mode='r') as f:
        configuration = json.loads(f.read())

    print(f'Running {configuration["Project"]}')
    print(f'Duration {configuration["Duration"]}')

    os.makedirs(args.output_path, exist_ok=True)

    custom_header = {'header1': ['value1'], 'header2': ['value2']}
    results = run_corpus(configuration,
                         temp_file=args.temp_file,
                         vegeta_path=args.vegeta_path,
                         append_headers=custom_header,
                         description_sub_regex=re.compile(args.description_sub_regex),
                         output_path=args.output_path)

    results = generate_report(results,
                              vegeta_path=args.vegeta_path,
                              output_path=args.output_path)

    write_report(results, output=args.output, title=configuration['Project'], configuration=configuration)

    shutil.rmtree(args.output_path)
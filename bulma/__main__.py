import json
import subprocess
import os
import re
import argparse
import base64
import pandas as pd
import shutil
import pprint
import logging
from bulma.logger import LOGGING_EXTRA

logger = logging.getLogger("bulma")

def run_corpus(configuration, **kwargs):
    logger.info(f'[bold green]Running {len(configuration["Corpus"])} Tests(s)', **LOGGING_EXTRA)

    for index, case in enumerate(configuration['Corpus']):
        case['id'] = kwargs.get('description_sub_regex').sub('_', case['id']).lower()

        logger.info(f'{index+1} - {case["id"]}')

        append_headers = kwargs.get('append_headers', None)
        if append_headers:
            logger.debug(case['header'])
            logger.debug(f'Appending Headers {append_headers}')
            case['header'] = {**case['header'], **append_headers}

        if 'body_graphql' in case:
            logger.debug('Fetching GraphQL File')
            with open(case['body_graphql'], 'r') as f:
                case['body'] = json.dumps({ 'query': f.read() })
            del case['body_graphql']

        if 'body_file' in case:
            logger.debug('Fetching Body File')
            with open(case['body_file'], 'r') as f:
                case['body'] = f.read()
            del case['body_file']

        if 'body' in case:
            logger.debug('Encoding Body')
            message_bytes = case['body'].encode('ascii')
            base64_bytes = base64.b64encode(message_bytes)
            case['body'] = base64_bytes.decode('ascii')

        with open(args.temp_file, mode='w') as f:
            json.dump(case, f, indent=None)

        output_file = os.path.join(kwargs.get("output_path"), case["id"]) + ".bin"
        duration = configuration["Duration"] or '5s'
        rate = configuration["Rate"] or '50/1s'

        cmd = f'cat {kwargs.get("temp_file")} | jq -cM | {kwargs.get("vegeta_path")} attack -duration {duration} -rate {rate} -format json > {output_file}'
        logger.debug(cmd)
        subprocess.run(cmd, shell=True, encoding='utf-8')

        os.remove(args.temp_file)
        yield {'id': case['id'], 'file': output_file}


def generate_report(output_files, **kwargs):
    logger.info('[green]Generating Vegeta Report', **LOGGING_EXTRA)
    for result in output_files:
        output_file = os.path.join(kwargs.get("output_path"), result["id"]) + "_report.json"
        cmd = f'cat {result["file"]} | {kwargs.get("vegeta_path")} report -type json > {output_file}'
        logger.debug(cmd)
        subprocess.run(cmd, shell=True, encoding='utf-8')
        result['report_json'] = output_file
        yield result


def write_report(results, **kwargs):
    logger.info('[green]Writing Report', **LOGGING_EXTRA)
    frames = []
    for res in results:
        with open(res['report_json'], 'r') as f:
            raw = f.read()
            json_raw = json.loads(raw)
            frame = pd.json_normalize(json_raw)
            frame['id'] = res['id']
            frame.set_index('id', inplace=True)
            frames.append(frame)

    results = pd.concat(frames)
    output_file = kwargs.get('output_name') + '.' + kwargs.get('output_type')

    if kwargs.get('output_type') == 'csv':
        results.to_csv(output_file)
    else:
        with open(output_file, 'w') as f:
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
    parser.add_argument('--output_type', choices=['csv', 'md'], default='md')
    parser.add_argument('--output_name', default='output')

    args = parser.parse_args()

    with open(args.config, mode='r') as f:
        configuration = json.loads(f.read())

    logger.info(f'Running {configuration["Project"]}')
    logger.info(f'Duration {configuration["Duration"]}')

    os.makedirs(args.output_path, exist_ok=True)

    results = run_corpus(configuration,
                         temp_file=args.temp_file,
                         vegeta_path=args.vegeta_path,
                         append_headers=configuration['Header'],
                         description_sub_regex=re.compile(args.description_sub_regex),
                         output_path=args.output_path)

    results = list(results)
    results = generate_report(results,
                              vegeta_path=args.vegeta_path,
                              output_path=args.output_path)
    write_report(results,
                title=configuration['Project'],
                configuration=configuration,
                output_name=args.output_name or configuration['OutputName'],
                output_type=args.output_type or configuration['OutputType'])

    shutil.rmtree(args.output_path)
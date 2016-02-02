import requests
import boto3
import os

os.environ.setdefault('AWS_DEFAULT_REGION', 'us-east-1')


def _get_metadata(endpoint):
    base = 'http://169.254.169.254/latest/meta-data'
    url = os.path.join(base, endpoint)
    r = requests.get(url)
    r.raise_for_status()
    return r.text


def get_this_instance_id():
    return _get_metadata('instance-id')


def get_this_instance_local_ip():
    return _get_metadata('local-ipv4')


def get_single_tag(tag_key, instance_id=None):
    """
    get a single tag on an instance
    :param tag_key: tag key to query
    :param instance_id: aws instance-id or None (defaults to current instance)
    :return:
    """
    c = boto3.client('ec2')
    if instance_id is None:
        instance_id = get_this_instance_id()
    tags = c.describe_tags(
        Filters=[
            {"Name": "resource-type", "Values": ["instance"]},
            {"Name": "resource-id", "Values": [instance_id]}
        ]
    )['Tags']
    tags = filter(lambda d: d.get('Key') == tag_key, tags)
    assert tags, "No tag '{}' found".format(tag_key)
    return tags[0]['Value']


def is_reachable(host):
    if os.system("ping -c 1 {}".format(host)) is 0:
        return True
    return False


def update_record_set(name, DNSName, type="A"):
    """
    update a route53 resource set with this instance's private IP addr.
    Operation will be UPSERT, and additionally include any previously defined
    records that are still valid (pingable).
    :param name: first part of the record name
    :param DNSName: hosted zone name (second part of the record name)
    :param type: record type [A]
    :return: JSON response from change_resource_record_sets call
    """
    c = boto3.client('route53')
    id = c.list_hosted_zones_by_name(DNSName=DNSName)['HostedZones'][0]['Id']
    ip = get_this_instance_local_ip()
    name = "{}.{}.".format(name, DNSName)

    current_records = c.list_resource_record_set(
        HostedZoneId=id,
        StartRecordName=name,
        StartRecordType=type,
        MaxItems='5',
    )['ResourceRecordSets']

    # necessary since list_resource_record_set is actually a fuzzy match
    current_records = filter(lambda d: d['Name'] == name, current_records)

    updates = {ip}
    for record in current_records:
        if is_reachable(record["Value"]):
            updates.add(record["Value"])

    rv = c.change_resource_record_sets(
        HostedZoneId=id,
        ChangeBatch={
            'Comment': 'toolbox-update record',
            'Changes': [
                {
                    'Action': "UPSERT",
                    'ResourceRecordSet': {
                        'Name': name,
                        'Type': type,
                        'ResourceRecords': [{"Value": v} for v in updates]
                    }
                },
            ]
        }
    )
    return rv

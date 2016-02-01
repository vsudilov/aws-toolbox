import requests
import boto3


def get_this_instance_id():
    r = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
    r.raise_for_status()
    return r.text


def get_single_tag(tag_key=None, instance_id=None):
    c = boto3.client('ec2')
    if instance_id is None:
        instance_id = get_this_instance_id()
    tags = c.describe_tags(
        Filters=[
            {"Name": "resource-type", "Values": ["instance"]},
            {"Name": "resource-id", "Values": [instance_id]}
        ]
    )['Tags']
    if tag_key is not None:
        tags = filter(lambda d: d.get('Key') == tag_key, tags)
    return tags


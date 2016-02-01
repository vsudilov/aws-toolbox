import argparse
from utils import get_this_instance_id
from utils import get_single_tag
import sys


def get_args():
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument(
        '--get-instance-tag',
        default=None,
        nargs=1,
        dest='get_instance_tag',
        metavar=('tag', ),
        help='\n'.join([
            'tag: The tag to query on this instance (returns VALUE in TAG:VALUE)',
        ]),
    )

    g.add_argument(
        '--update-dns',
        nargs=2,
        dest='update_dns',
        metavar=('name', 'hostedZone'),
        help='\n'.join([
            "update the route53 zone with this instance\'s hostname",
            'name: desired DNS name',
            'hostedZone: route53 hosted zone to target',
        ]),
    )

    return parser.parse_args()


def main():
    args = get_args()
    if args.get_instance_tag:
        print(get_single_tag(tag_key=args.get_instance_tag))
        sys.exit(0)


if __name__ == '__main__':
    main()

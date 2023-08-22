import boto3
import datetime
import os

if __name__ == '__main__':
    environment = os.environ["env"]
    bucket_name = os.environ["bucket"]

    dns_counter = 0
    current_date_time = datetime.datetime.now()

    main_session = boto3.Session()

    s3 = boto3.resource('s3')
    route53 = main_session.client('route53')
    hosted_zones = route53.list_hosted_zones_by_name()

    dns_counter = 0

    # Loop through the Hosted Zones.
    for hosted_zone in hosted_zones['HostedZones']:
        data_text = ''

        zone_id = hosted_zone['Id'].replace('/hostedzone/','')
        print('Starting ' + hosted_zone['Name'][:-1] + ' == ' + zone_id)

        # Get the ResourceRecordsSets for the Hosted Zone.
        dns_record_list = ''
        dns_records = route53.list_resource_record_sets(
            HostedZoneId=zone_id
        )

        # Replace periods with underscores
        dns_file_name = str(int(current_date_time.timestamp())) + '/' + hosted_zone['Name'].replace('.','_') + '.txt'

        # Add the Zone
        data_text =  data_text + '$ORIGIN ' + hosted_zone['Name'] + '\n'
        data_text =  data_text + '$TTL 1h' + '\n'

        # Loop through the Resource Record Sets
        for dns_record in dns_records['ResourceRecordSets']:
            dns_counter = dns_counter + 1

            # If there is an AliasTarget we do not need the TTL and should just end wit hthe DNSName.
            if 'AliasTarget' in dns_record.keys():
                value = dns_record['AliasTarget']['DNSName']

                if "v=DKIM1" in value:
                    value = value.replace(' ','\\" \\"')

                # Create the DNS Alias Record.
                data_text =  data_text + dns_record['Name'] + ' IN ' + dns_record['Type'] + ' ' + value + '\n'
            else:
                for resource_record in dns_record['ResourceRecords']:
                    value = resource_record['Value']

                    if "v=DKIM1" in value:
                        value = value.replace(' ','\\" \\"')

                # Create the DNS Record.
                data_text =  data_text + dns_record['Name'] + ' ' + str(dns_record['TTL']) + ' IN ' + dns_record['Type'] + ' ' + value + '\n'

            # Create the Bucket Object
            file = s3.Bucket(bucket_name).put_object(Key=dns_file_name, Body=data_text)
        print('Done! ' + str(dns_counter) + ' ' + environment + ' DNS Records')

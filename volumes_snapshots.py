import boto3

def lambda_handler(event, context):
    AWS_REGION = 'eu-west-1'
    EC2_RESOURCE = boto3.resource('ec2', region_name = AWS_REGION)
    CUSTOM_METRICS = boto3.client('cloudwatch', region_name = AWS_REGION)
    
    ebs_nonencrypted = 0
    ebs_available = 0
    ebs_size = 0

    for volume in EC2_RESOURCE.volumes.all():
        #	Number of not encrypted EBS Volumes
        if volume.encrypted == False:
            ebs_nonencrypted = ebs_nonencrypted + 1
        
        #	Number and overall size of EBS volumes not attached to any EC2 instance
        if volume.state == "available":
            ebs_available = ebs_available + 1
            ebs_size = ebs_size + volume.size
        #print(f'Volume {volume.id} ({volume.size} GiB) -> {volume.state}')
    
    #	Number of nonencrypted volume snapshots
    snapshot_nonencrypted = 0
    
    EC2_SNAPSHOT = boto3.client('ec2', region_name = AWS_REGION) 
    snapshots=EC2_SNAPSHOT.describe_snapshots(OwnerIds=['self',],).get('Snapshots',[])
    
    for snapshot in snapshots:
        if snapshot.get('Encrypted') == False:
            snapshot_nonencrypted = snapshot_nonencrypted + 1
        #print(f'Snapshot {snapshot.get('SnapshotId')}')


    #   Put metrics to CloudWatch
    response = CUSTOM_METRICS.put_metric_data(
    Namespace='VolumesAndSnapshots',
    MetricData=[
        {
            'MetricName': 'NonEncryptedVolumes',
            'Dimensions': [
                {
                    'Name': 'NonEncryptedVolumes',
                    'Value': 'Number'
                },
            ],
            'Value': ebs_nonencrypted,
            'Unit': 'Count'
        },
        {
            'MetricName': 'NumberAvailableVolumes',
            'Dimensions': [
                {
                    'Name': 'NumberAvailableVolumes',
                    'Value': 'Number'
                },
            ],
            'Value': ebs_available,
            'Unit': 'Count'
        },
        {
            'MetricName': 'OverallSizeVolumes',
            'Dimensions': [
                {
                    'Name': 'OverallSizeVolumes',
                    'Value': 'Number'
                },
            ],
            'Value': ebs_size,
            'Unit': 'Count'
        },
        {
            'MetricName': 'NonEncryptedSnapshots',
            'Dimensions': [
                {
                    'Name': 'NonEncryptedSnapshots',
                    'Value': 'Number'
                },
            ],
            'Value': snapshot_nonencrypted,
            'Unit': 'Count'
        },
    ]
    )
    print(response)



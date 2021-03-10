from aws_cdk import aws_lambda as _lambda, aws_dynamodb as ddb, aws_ec2 as ec2, core


class HitCounter(core.Construct):
    def __init__(self, scope: core.Construct, id: str, downstream: _lambda.IFunction, vpc: ec2.IVpc, sg: ec2.ISecurityGroup, **kwargs):
        super(HitCounter, self).__init__(scope, id, **kwargs)

        self.table = ddb.Table(
            self, 'Hits',
            partition_key={'name': 'path', 'type': ddb.AttributeType.STRING},
        )

        self.handler = _lambda.Function(
            self, 'HitCountHandler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler='hitcount.handler',
            code=_lambda.Code.asset('lambda'),
            timeout=core.Duration.seconds(60),
            environment={
                'DOWNSTREAM_FUNCTION_NAME': downstream.function_name,
                'HITS_TABLE_NAME': self.table.table_name,
                'PYTHONUNBUFFERED': 'True'
            },
            vpc=vpc,
            security_group=sg
        )
        self.table.grant_read_write_data(self.handler)
        downstream.grant_invoke(self.handler)

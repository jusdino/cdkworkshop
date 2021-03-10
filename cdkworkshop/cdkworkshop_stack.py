from aws_cdk import core, aws_lambda as _lambda, aws_apigateway as apigw, aws_ec2 as ec2
from aws_cdk.core import Tags
from hitcounter import HitCounter


class CdkworkshopStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, 'public', vpc_name='dev')

        sg = ec2.SecurityGroup(
            self, 'LambdaInternalSG',
            vpc=vpc,
            allow_all_outbound=True,
            description=f'{construct_id}LambdaSG',
            security_group_name=f'{construct_id}LambdaSG'
        )

        my_lambda = _lambda.Function(
            self, 'HelloHandler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset('lambda'),
            timeout=core.Duration.seconds(60),
            environment={
                'PYTHONUNBUFFERED': 'True'
            },
            handler='hello.handler',
            security_group=sg,
            vpc=vpc
        )

        hello_with_counter = HitCounter(
            self, 'HelloHitCounter',
            downstream=my_lambda,
            vpc=vpc,
            sg=sg
        )

        apigw.LambdaRestApi(
            self, 'Endpoint',
            handler=hello_with_counter.handler
        )

        Tags.of(self).add("Env", "dev")

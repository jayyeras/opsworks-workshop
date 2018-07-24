import boto3
import botocore
import json
import base64

def launch_server():
    
    iam = boto3.client('iam')
    
    # Create the EC2 instance role
    role = {}
    role['Version'] = '2012-10-17'
    statements = []
    statements.append({'Effect': 'Allow', 'Action': ['sts:AssumeRole'], 'Principal': { "Service": "ec2.amazonaws.com" }})
    role['Statement'] = statements
    finalrole = json.dumps(role, indent=2)
    
    instance_role = iam.create_role(
        RoleName = 'aws-opsworks-cm-devday-ec2-role',
        AssumeRolePolicyDocument = finalrole
    )
    
    policy = {}
    policy['Version'] = '2012-10-17'
    statements = []
    statements.append({'Effect': 'Allow', 'Action': ['opsworks-cm:DisassociateNode','opsworks-cm:DescribeNodeAssociationStatus','opsworks-cm:AssociateNode'], 'Resource': '*'})
    policy['Statement'] = statements
    finalpolicy = json.dumps(policy, indent=2)
    print(finalpolicy)
    
    instance_policy = iam.create_policy(
        PolicyName = 'aws-opsworks-cm-devday-ec2-policy',
        PolicyDocument = finalpolicy
    )
    
    policyarn = instance_policy['Policy']['Arn']
    print(policyarn)
    
    iam.attach_role_policy(
        RoleName = 'aws-opsworks-cm-devday-ec2-role',
        PolicyArn = policyarn
    )
    
    iam.attach_role_policy(
        RoleName = 'aws-opsworks-cm-devday-ec2-role',
        PolicyArn = 'arn:aws:iam::aws:policy/AWSOpsWorksCMInstanceProfileRole'
    )
    
    iam.attach_role_policy(
        RoleName = 'aws-opsworks-cm-devday-ec2-role',
        PolicyArn = 'arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM'
    )
    
    instance_profile = iam.create_instance_profile(InstanceProfileName = 'aws-opsworks-cm-devday-instance-profile')
    profilearn = instance_profile['InstanceProfile']['Arn']
    
    addrole_client = iam.add_role_to_instance_profile(
        InstanceProfileName = 'aws-opsworks-cm-devday-instance-profile',
        RoleName = 'aws-opsworks-cm-devday-ec2-role'
    )
    
    #Create service role
    
    role = {}
    role['Version'] = '2012-10-17'
    statements = []
    statements.append({'Effect': 'Allow', 'Action': ['sts:AssumeRole'], 'Principal': { "Service": "opsworks-cm.amazonaws.com" }})
    role['Statement'] = statements
    servicepolicy = json.dumps(role, indent=2)
    
    servicerole_client = iam.create_role(
        RoleName = 'aws-opsworks-cm-devday-service-role',
        AssumeRolePolicyDocument = servicepolicy
    )
    servicearn = servicerole_client['Role']['Arn']
    
    iam.attach_role_policy(
        RoleName = 'aws-opsworks-cm-devday-service-role',
        PolicyArn = 'arn:aws:iam::aws:policy/service-role/AWSOpsWorksCMServiceRole'
    )
    
    opsworks_client = boto3.client('opsworkscm', 'us-east-1')
    opsworks_response = opsworks_client.create_server(
        AssociatePublicIpAddress = True,
        DisableAutomatedBackup = False,
        Engine = 'Chef',
        EngineModel = 'Single',
        EngineVersion = '12',
        BackupRetentionCount = 10,
        ServerName = 'DevDay-OpsWorks-CM01',
        InstanceProfileArn = profilearn,
        InstanceType = 'm4.large',
        PreferredMaintenanceWindow = 'Sun:09:00',
        PreferredBackupWindow = '08:00',
        ServiceRoleArn = servicearn
    )
    
    print(opsworks_response['Server']['Endpoint'])
    
    for x in opsworks_response['Server']['EngineAttributes']:
        if x['Name'] == 'CHEF_DELIVERY_ADMIN_PASSWORD':
            print('Admin password: ' + x['Value'])
        if x['Name'] == 'CHEF_STARTER_KIT':
            with open("starter_kit.zip", "wb") as f:
                f.write(base64.b64decode(x['Value']))


launch_server()


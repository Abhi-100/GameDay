#!/usr/bin/env python3
"""
Unified setup script for Carmen Pizza Caper A2A system
Combines: IAM role, Cognito, Location Service, and DynamoDB setup
"""

import boto3
import json
import uuid
from datetime import datetime

def create_pizza_role(role_name="PizzaRoll"):
    """Create IAM role with all required permissions"""
    print(f"🔧 Creating IAM role: {role_name}")
    
    iam = boto3.client('iam')
    sts = boto3.client('sts')
    
    # Get dynamic values
    account_id = sts.get_caller_identity()['Account']
    region = boto3.Session().region_name or 'us-east-1'
    
    # Trust policy
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AssumeRolePolicy",
                "Effect": "Allow",
                "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {"aws:SourceAccount": account_id},
                    "ArnLike": {"aws:SourceArn": f"arn:aws:bedrock-agentcore:{region}:{account_id}:*"}
                }
            }
        ]
    }
    
    try:
        # Create role
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=f"Execution role for BedrockAgentCore Runtime - {role_name}"
        )
        
        # Main execution policy
        execution_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Sid": "ECRImageAccess", "Effect": "Allow", "Action": ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"], "Resource": [f"arn:aws:ecr:{region}:{account_id}:repository/*"]},
                {"Effect": "Allow", "Action": ["logs:DescribeLogStreams", "logs:CreateLogGroup"], "Resource": [f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*"]},
                {"Effect": "Allow", "Action": ["logs:DescribeLogGroups"], "Resource": [f"arn:aws:logs:{region}:{account_id}:log-group:*"]},
                {"Effect": "Allow", "Action": ["logs:CreateLogStream", "logs:PutLogEvents"], "Resource": [f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"]},
                {"Sid": "ECRTokenAccess", "Effect": "Allow", "Action": ["ecr:GetAuthorizationToken"], "Resource": "*"},
                {"Effect": "Allow", "Action": ["xray:PutTraceSegments", "xray:PutTelemetryRecords", "xray:GetSamplingRules", "xray:GetSamplingTargets"], "Resource": ["*"]},
                {"Effect": "Allow", "Resource": "*", "Action": "cloudwatch:PutMetricData", "Condition": {"StringEquals": {"cloudwatch:namespace": "bedrock-agentcore"}}},
                {"Sid": "BedrockAgentCoreRuntime", "Effect": "Allow", "Action": ["bedrock-agentcore:InvokeAgentRuntime", "bedrock-agentcore:InvokeAgentRuntimeForUser"], "Resource": [f"arn:aws:bedrock-agentcore:{region}:{account_id}:runtime/*"]},
                {"Sid": "BedrockAgentCoreMemoryCreateMemory", "Effect": "Allow", "Action": ["bedrock-agentcore:CreateMemory"], "Resource": "*"},
                {"Sid": "BedrockAgentCoreMemory", "Effect": "Allow", "Action": ["bedrock-agentcore:CreateEvent", "bedrock-agentcore:GetEvent", "bedrock-agentcore:GetMemory", "bedrock-agentcore:GetMemoryRecord", "bedrock-agentcore:ListActors", "bedrock-agentcore:ListEvents", "bedrock-agentcore:ListMemoryRecords", "bedrock-agentcore:ListSessions", "bedrock-agentcore:DeleteEvent", "bedrock-agentcore:DeleteMemoryRecord", "bedrock-agentcore:RetrieveMemoryRecords"], "Resource": [f"arn:aws:bedrock-agentcore:{region}:{account_id}:memory/*"]},
                {"Sid": "BedrockAgentCoreIdentityGetResourceApiKey", "Effect": "Allow", "Action": ["bedrock-agentcore:GetResourceApiKey"], "Resource": [f"arn:aws:bedrock-agentcore:{region}:{account_id}:token-vault/default", f"arn:aws:bedrock-agentcore:{region}:{account_id}:token-vault/default/apikeycredentialprovider/*", f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default", f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default/workload-identity/{role_name}-*"]},
                {"Sid": "BedrockAgentCoreIdentityGetCredentialProviderClientSecret", "Effect": "Allow", "Action": ["secretsmanager:GetSecretValue"], "Resource": [f"arn:aws:secretsmanager:{region}:{account_id}:secret:bedrock-agentcore-identity!default/oauth2/*"]},
                {"Sid": "BedrockAgentCoreIdentityGetResourceOauth2Token", "Effect": "Allow", "Action": ["bedrock-agentcore:GetResourceOauth2Token"], "Resource": [f"arn:aws:bedrock-agentcore:{region}:{account_id}:token-vault/default", f"arn:aws:bedrock-agentcore:{region}:{account_id}:token-vault/default/oauth2credentialprovider/*", f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default", f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default/workload-identity/{role_name}-*"]},
                {"Sid": "BedrockModelInvocation", "Effect": "Allow", "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream", "bedrock:ApplyGuardrail"], "Resource": ["arn:aws:bedrock:*::foundation-model/*", "arn:aws:bedrock:*:*:inference-profile/*", f"arn:aws:bedrock:{region}:{account_id}:*"]},
                {"Sid": "BedrockAgentCoreCodeInterpreter", "Effect": "Allow", "Action": ["bedrock-agentcore:CreateCodeInterpreter", "bedrock-agentcore:StartCodeInterpreterSession", "bedrock-agentcore:InvokeCodeInterpreter", "bedrock-agentcore:StopCodeInterpreterSession", "bedrock-agentcore:DeleteCodeInterpreter", "bedrock-agentcore:ListCodeInterpreters", "bedrock-agentcore:GetCodeInterpreter", "bedrock-agentcore:GetCodeInterpreterSession", "bedrock-agentcore:ListCodeInterpreterSessions"], "Resource": [f"arn:aws:bedrock-agentcore:{region}:aws:code-interpreter/*", f"arn:aws:bedrock-agentcore:{region}:{account_id}:code-interpreter/*", f"arn:aws:bedrock-agentcore:{region}:{account_id}:code-interpreter-custom/*"]}
            ]
        }
        
        # DynamoDB policy
        dynamodb_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["dynamodb:*"], "Resource": "*"}
            ]
        }
        
        # Location services policy
        location_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["geo:*"], "Resource": "*"}
            ]
        }
        
        # Attach policies
        iam.put_role_policy(RoleName=role_name, PolicyName=f"BedrockAgentCoreRuntimeExecutionPolicy-{role_name}", PolicyDocument=json.dumps(execution_policy))
        iam.put_role_policy(RoleName=role_name, PolicyName="AmazonDynamoDBFullAccess", PolicyDocument=json.dumps(dynamodb_policy))
        iam.put_role_policy(RoleName=role_name, PolicyName="AmazonLocationServiceFullAccess", PolicyDocument=json.dumps(location_policy))
        
        # Attach AWS managed policies
        iam.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess")
        iam.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/BedrockAgentCoreFullAccess")
        iam.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess")
        
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
        print(f"✅ Role {role_name} created successfully")
        print(f"   ARN: {role_arn}")
        return role_arn
        
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"⚠️  Role {role_name} already exists")
        return f"arn:aws:iam::{account_id}:role/{role_name}"

def setup_cognito():
    """Setup Cognito User Pool and App Client"""
    print(f"🔧 Setting up Cognito: PizzaUserPool")
    
    region = boto3.Session().region_name or 'us-east-1'
    cognito = boto3.client('cognito-idp', region_name=region)
    
    # Check if user pool already exists
    pool_id = None
    try:
        pools = cognito.list_user_pools(MaxResults=60)
        for pool in pools['UserPools']:
            if pool['Name'] == 'PizzaUserPool':
                pool_id = pool['Id']
                print(f"⚠️  User pool PizzaUserPool already exists: {pool_id}")
                break
    except Exception as e:
        print(f"Error checking existing pools: {e}")
    
    # Create user pool if it doesn't exist
    if not pool_id:
        try:
            user_pool = cognito.create_user_pool(
                PoolName="PizzaUserPool",
                Policies={'PasswordPolicy': {'MinimumLength': 8}}
            )
            pool_id = user_pool['UserPool']['Id']
            print(f"✅ Created new user pool: {pool_id}")
        except Exception as e:
            print(f"❌ Failed to create user pool: {e}")
            return None, None, None
    
    # Check if app client already exists
    client_id = None
    try:
        clients = cognito.list_user_pool_clients(UserPoolId=pool_id, MaxResults=60)
        for client in clients['UserPoolClients']:
            if client['ClientName'] == 'MyClient':
                client_id = client['ClientId']
                print(f"⚠️  App client MyClient already exists: {client_id}")
                break
    except Exception as e:
        print(f"Error checking existing clients: {e}")
    
    # Create app client if it doesn't exist
    if not client_id:
        try:
            app_client = cognito.create_user_pool_client(
                UserPoolId=pool_id,
                ClientName="MyClient",
                GenerateSecret=False,
                ExplicitAuthFlows=['ALLOW_USER_PASSWORD_AUTH', 'ALLOW_REFRESH_TOKEN_AUTH'],
                AccessTokenValidity=1440,
                TokenValidityUnits={'AccessToken': 'minutes'}
            )
            client_id = app_client['UserPoolClient']['ClientId']
            print(f"✅ Created new app client: {client_id}")
        except Exception as e:
            print(f"❌ Failed to create app client: {e}")
            return None, None, None
    
    # Check if test user exists, create if not
    try:
        cognito.admin_get_user(UserPoolId=pool_id, Username='testuser')
        print(f"⚠️  Test user already exists")
    except cognito.exceptions.UserNotFoundException:
        try:
            # Create test user
            cognito.admin_create_user(
                UserPoolId=pool_id,
                Username='testuser',
                TemporaryPassword='Temppassw0rd',
                MessageAction='SUPPRESS'
            )
            
            # Set permanent password
            cognito.admin_set_user_password(
                UserPoolId=pool_id,
                Username='testuser',
                Password='Permpassw0rd',
                Permanent=True
            )
            print(f"✅ Created test user")
        except Exception as e:
            print(f"❌ Failed to create test user: {e}")
    except Exception as e:
        print(f"Error checking test user: {e}")
    
    # Get bearer token
    try:
        auth_response = cognito.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME': 'testuser', 'PASSWORD': 'Permpassw0rd'}
        )
        
        bearer_token = auth_response['AuthenticationResult']['AccessToken']
        discovery_url = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/openid-configuration"
        
        print(f"✅ Cognito setup complete")
        print(f"   Pool ID: {pool_id}")
        print(f"   Discovery URL: {discovery_url}")
        print(f"   Client ID: {client_id}")
        print(f"   Bearer Token: {bearer_token}")
        
        return pool_id, client_id, bearer_token
        
    except Exception as e:
        print(f"❌ Cognito setup failed: {e}")
        return None, None, None

def setup_location_service():
    """Setup Amazon Location Service Place Index and Route Calculator"""
    region = boto3.Session().region_name or 'us-east-1'
    place_index_name = "PizzaPlaceIndex"
    route_calculator_name = "PizzaRouteCalculator"
    
    print(f"🔧 Setting up Amazon Location Service resources in region: {region}")
    print(f"Creating Place Index: {place_index_name}")
    print(f"Creating Route Calculator: {route_calculator_name}")
    
    location = boto3.client('location', region_name=region)
    
    try:
        # Create Place Index
        location.create_place_index(
            IndexName=place_index_name,
            DataSource='Esri',
            Description='Place index for pizza delivery locations'
        )
        
        # Create Route Calculator
        location.create_route_calculator(
            CalculatorName=route_calculator_name,
            DataSource='Esri',
            Description='Route calculator for pizza delivery routes'
        )
        
        print(f"✅ Resources created successfully")
        
        # Check if resources are active
        import time
        for _ in range(30):
            try:
                place_response = location.describe_place_index(IndexName=place_index_name)
                route_response = location.describe_route_calculator(CalculatorName=route_calculator_name)
                if place_response.get('Status') == 'Active' and route_response.get('Status') == 'Active':
                    break
            except:
                pass
            time.sleep(2)
        
        print(f"✅ Amazon Location Service setup complete!")
        print(f"   Place Index: {place_index_name}")
        print(f"   Route Calculator: {route_calculator_name}")
        print(f"   Region: {region}")
        
        return place_index_name
        
    except location.exceptions.ConflictException:
        print(f"⚠️  Resources already exist")
        return place_index_name
    except Exception as e:
        print(f"❌ Location Service setup failed: {e}")
        return None

def create_pizza_orders_table(table_name="pizza_orders"):
    """Create DynamoDB table and populate with sample data"""
    print(f"🔧 Creating DynamoDB table: {table_name}")
    
    import random
    from decimal import Decimal
    dynamodb = boto3.resource('dynamodb')
    
    try:
        # Create table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'customer_id', 'KeyType': 'HASH'},
                {'AttributeName': 'order_id', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'customer_id', 'AttributeType': 'S'},
                {'AttributeName': 'order_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Wait for table to be created
        table.wait_until_exists()
        
        # Store locations
        stores = [
            ('Amazon Go #ISE9', '1122 Madison St, Seattle, WA 98104'),
            ('Amazon Go #IBF3', '1906 Terry Ave, Seattle, WA 98101'),
            ('Amazon Go #ISE1', '2131 7th Ave, Seattle, WA 98121'),
            ('Amazon Go #ISE6', '300 Boren Ave N, Seattle, WA 98109'),
            ('Amazon Go #IBF2', '10819 4th St. NE, Bellevue, WA 98004'),
            ('Amazon Go #ILS4', '13209 39th Ave SE, Mill Creek, WA 98012'),
            ('Amazon Go #IWA2', '15518 Meridian Ave, Puyallup, WA 98375'),
            ('Amazon Go #IWA3', '17710 Canyon Road E #400, Puyallup, WA 98375'),
            ('Amazon Go #ISF1', '2201 Westlake Ave, Seattle, WA 98121'),
            ('Amazon Go #ISF2', '1200 12th Ave S, Seattle, WA 98144'),
            ('Amazon Go #ISF3', '4000 E Madison St, Seattle, WA 98112'),
            ('Amazon Go #IBF4', '500 110th Ave NE, Bellevue, WA 98004'),
            ('Amazon Go #IBF5', '15600 NE 8th St, Bellevue, WA 98008'),
            ('Amazon Go #ILS5', '12000 SE 38th St, Bellevue, WA 98006'),
            ('Amazon Go #IWA4', '3500 S Meridian, Puyallup, WA 98373'),
            ('Amazon Go #IWA5', '1901 S 72nd St, Tacoma, WA 98408'),
            ('Amazon Go #IWA6', '4502 S Steele St, Tacoma, WA 98409'),
            ('Amazon Go #IOR1', '1000 SW Broadway, Portland, OR 97205'),
            ('Amazon Go #IOR2', '2200 NW Glisan St, Portland, OR 97210'),
            ('Amazon Go #IOR3', '3300 SE Hawthorne Blvd, Portland, OR 97214')
        ]
        
        # Pizza items
        items = ['Margherita Pizza', 'Pepperoni Pizza', 'Veggie Pizza', 'Hawaiian Pizza', 'Meat Lovers Pizza']
        
        # Create 20 orders
        orders = []
        for i in range(20):
            store_name, address = random.choice(stores)
            item_name = random.choice(items)
            quantity = random.randint(1, 3)
            order_total = Decimal(str(round(random.uniform(15.99, 49.99), 2)))
            
            order = {
                'customer_id': f'CUST_{i+1:03d}',
                'order_id': str(uuid.uuid4()),
                'item_name': item_name,
                'quantity': quantity,
                'order_total': order_total,
                'store_name': store_name,
                'address': address
            }
            orders.append(order)
        
        # Insert orders
        for order in orders:
            table.put_item(Item=order)
        
        print(f"✅ DynamoDB table created with {len(orders)} orders")
        return table_name
        
    except Exception as e:
        print(f"❌ DynamoDB setup failed: {e}")
        return None

def create_evidence_bucket(bucket_name=None):
    """Create S3 bucket for evidence storage"""
    if bucket_name is None:
        sts = boto3.client('sts')
        account_id = sts.get_caller_identity()['Account']
        bucket_name = f"pizza-images-{account_id}"
    
    print(f"🔧 Creating S3 bucket: {bucket_name}")
    
    s3 = boto3.client('s3')
    region = boto3.Session().region_name or 'us-east-1'
    
    try:
        if region == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        print(f"✅ S3 bucket created: {bucket_name}")
        return bucket_name
        
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"⚠️  S3 bucket already exists: {bucket_name}")
        return bucket_name
    except Exception as e:
        print(f"❌ S3 bucket creation failed: {e}")
        return None

def main():
    """Run complete setup"""
    print("🚀 Starting Carmen Pizza Caper A2A Setup")
    print("=" * 50)
    
    # 1. Create IAM Role
    role_arn = create_pizza_role()
    
    # 2. Setup Cognito
    user_pool_id, client_id, bearer_token = setup_cognito()
    
    # 3. Setup Location Service
    place_index = setup_location_service()
    
    # 4. Create DynamoDB table
    table_name = create_pizza_orders_table()
    
    # 5. Create S3 bucket for evidence
    bucket_name = create_evidence_bucket()
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("=" * 50)
    
    if all([role_arn, user_pool_id, client_id, place_index, table_name, bucket_name]):
        print("✅ All services configured successfully")
        print(f"\n🔧 Environment Variables:")
        print(f"export AWS_REGION={boto3.Session().region_name}")
        print(f"export PLACE_INDEX_NAME={place_index}")
        print(f"export EVIDENCE_BUCKET={bucket_name}")
        print(f"export COGNITO_USER_POOL_ID={user_pool_id}")
        print(f"export COGNITO_CLIENT_ID={client_id}")
        print(f"export PIZZA_ROLE_ARN={role_arn}")
        if bearer_token:
            print(f"export BEARER_TOKEN={bearer_token}")
        
        print(f"\n🚀 Next Steps:")
        print(f"1. Deploy agents using the PizzaRoll")
        print(f"2. Run frontend: streamlit run a2a_frontend.py")
    else:
        print("❌ Some services failed to configure")

if __name__ == "__main__":
    main()

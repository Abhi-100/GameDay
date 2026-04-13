import os
import boto3
import logging
from boto3.dynamodb.conditions import Key
from strands import Agent, tool
from strands.multiagent.a2a import A2AServer
import uvicorn
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)

# DynamoDB setup
region = os.environ.get('AWS_REGION', 'us-east-1')
dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table('pizza_orders')

@tool
def get_customer_orders(customer_id: str) -> str:
    """Get all orders for customer"""
    try:
        response = table.query(
            KeyConditionExpression=Key('customer_id').eq(customer_id)
        )
        return f"Orders for {customer_id}: {response['Items']}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_orders_by_location(location: str) -> str:
    """Get orders by delivery location"""
    try:
        response = table.scan(
            FilterExpression='contains(delivery_address, :loc)',
            ExpressionAttributeValues={':loc': location}
        )
        return f"Orders for {location}: {response['Items']}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_all_orders() -> str:
    """Get all pizza orders"""
    try:
        response = table.scan()
        return f"All orders: {response['Items']}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def place_order(customer_id: str, items: str, address: str) -> str:
    """Place new pizza order"""
    try:
        table.put_item(Item={
            'customer_id': customer_id,
            'items': items,
            'delivery_address': address,
            'status': 'placed'
        })
        return f"Order placed for {customer_id}: {items} to {address}"
    except Exception as e:
        return f"Error: {str(e)}"

# Create orders agent
strands_agent = Agent(
    name="Orders Agent",
    description="Handles pizza orders, order status, address and store information, and order management with DynamoDB access",
    tools={TODO}
)

runtime_url = os.environ.get('AGENTCORE_RUNTIME_URL', 'http://127.0.0.1:9000/')

# Create A2A server
a2a_server = A2AServer(
    {TODO}
)

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "healthy", "agent": "orders"}

app.mount("/", a2a_server.to_fastapi_app())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)

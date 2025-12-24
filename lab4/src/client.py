import asyncio
import uuid
import json
import logging
from aio_pika import connect, Message, IncomingMessage
from src.core.config import settings
from src.schemas.protocol import RequestMessage, ResponseMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    connection = await connect(settings.rabbitmq_url)

    async with connection:
        channel = await connection.channel()
        
        # Declare callback queue
        callback_queue = await channel.declare_queue(exclusive=True)

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        async def on_response(message: IncomingMessage):
            async with message.process():
                logger.info(f"Received response: {message.body.decode()}")
                future.set_result(message.body.decode())

        await callback_queue.consume(on_response)

        # Create request
        request_id = str(uuid.uuid4())
        
        # Example 1: Create User
        request_data = {
            "id": request_id,
            "version": "v1",
            "action": "create_user",
            "data": {
                "name": "Test User",
                "email": "test@example.com"
            },
            "auth": settings.default_api_key
        }
        
        logger.info(f"Sending request: {request_data}")
        
        await channel.default_exchange.publish(
            Message(
                body=json.dumps(request_data).encode(),
                reply_to=callback_queue.name,
                correlation_id=request_id,
            ),
            routing_key=settings.queue_requests,
        )

        response_body = await future
        logger.info(f"Response: {response_body}")
        
         # Create request
        request_id = str(uuid.uuid4())
        
        # Example 1: Create User
        request_data = {
            "id": request_id,
            "version": "v1",
            "action": "create_user",
            "data": {
                "name": "Test User",
                "email": "test@example.com"
            },
            "auth": settings.default_api_key
        }
        
        logger.info(f"Sending request: {request_data}")
        
        await channel.default_exchange.publish(
            Message(
                body=json.dumps(request_data).encode(),
                reply_to=callback_queue.name,
                correlation_id=request_id,
            ),
            routing_key=settings.queue_requests,
        )

        response_body = await future
        logger.info(f"Response: {response_body}")

        # Parse response
        response = ResponseMessage.model_validate_json(response_body)
        if response.status == "ok":
            logger.info(f"User created: {response.data}")
        else:
            logger.error(f"Error: {response.error}")

        # Example 2: List Users
        future = loop.create_future() # Reset future
        request_id = str(uuid.uuid4())
        request_data = {
            "id": request_id,
            "version": "v1",
            "action": "list_users",
            "data": {},
            "auth": settings.default_api_key
        }
        
        logger.info(f"Sending request: {request_data}")
        
        await channel.default_exchange.publish(
            Message(
                body=json.dumps(request_data).encode(),
                reply_to=callback_queue.name,
                correlation_id=request_id,
            ),
            routing_key=settings.queue_requests,
        )
        
        response_body = await future
        logger.info(f"Response: {response_body}")

if __name__ == "__main__":
    asyncio.run(main())


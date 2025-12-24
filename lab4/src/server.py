import asyncio
import json
import logging
import traceback
from aio_pika import connect, IncomingMessage, Message, ExchangeType
from pydantic import ValidationError

from src.core.config import settings
from src.core.storage import db
from src.schemas.protocol import RequestMessage, ResponseMessage
from src.handlers.registry import get_handler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def process_message(message: IncomingMessage):
    async with message.process(ignore_processed=True):
        try:
            body = message.body.decode()
            logger.info(f"Received message: {body}")
            
            try:
                request_data = json.loads(body)
                request = RequestMessage(**request_data)
            except (json.JSONDecodeError, ValidationError) as e:
                logger.error(f"Invalid message format: {e}")
                # Can't reply if we can't parse the ID/correlation info properly, 
                # but if we can parse enough to get correlation_id or we use message properties...
                # The prompt says request has "id". Response has "correlation_id".
                # If JSON fails, we might send to DLQ or just log.
                # We'll treat this as unrecoverable for now.
                await send_to_dlq(message, f"Invalid format: {str(e)}")
                return

            # 1. Auth
            if request.auth != settings.default_api_key:
                response = ResponseMessage(
                    correlation_id=request.id,
                    status="error",
                    error="Unauthorized"
                )
                await send_response(message, response)
                return

            # 2. Idempotency - check if request was already processed
            if request.id in db.idempotency:
                logger.info(f"Duplicate request {request.id}, returning cached response")
                cached_response_data = db.idempotency[request.id]
                response = ResponseMessage(**cached_response_data)
                await send_response(message, response)
                return

            # 3. Dispatch
            handler = get_handler(request.version, request.action)
            if not handler:
                response = ResponseMessage(
                    correlation_id=request.id,
                    status="error",
                    error=f"Unknown action: {request.action} for version {request.version}"
                )
                await send_response(message, response)
                return

            # 4. Execute
            try:
                result = handler(request.data)
                
                # Serialize result
                # If result is pydantic model, dump it. If list of models, dump them.
                data_out = None
                if result is not None:
                    if isinstance(result, list):
                        data_out = [item.model_dump() if hasattr(item, "model_dump") else item for item in result]
                    elif hasattr(result, "model_dump"):
                        data_out = result.model_dump()
                    else:
                        data_out = result

                response = ResponseMessage(
                    correlation_id=request.id,
                    status="ok",
                    data=data_out
                )
                
                # Cache response for idempotency
                db.idempotency[request.id] = response.model_dump()
                
                await send_response(message, response)

            except Exception as e:
                logger.error(f"Error executing handler: {e}")
                logger.error(traceback.format_exc())
                response = ResponseMessage(
                    correlation_id=request.id,
                    status="error",
                    error=str(e)
                )
                # Cache error response for idempotency too
                db.idempotency[request.id] = response.model_dump()
                await send_response(message, response)

        except Exception as e:
            logger.error(f"Critical error processing message: {e}")
            await send_to_dlq(message, str(e))

async def send_response(message: IncomingMessage, response: ResponseMessage):
    # Determine reply queue: message.reply_to or settings.queue_responses
    reply_to = message.reply_to or settings.queue_responses
    correlation_id = message.correlation_id or response.correlation_id
    
    connection = await connect(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        
        await channel.default_exchange.publish(
            Message(
                body=response.model_dump_json().encode(),
                correlation_id=correlation_id
            ),
            routing_key=reply_to
        )
    logger.info(f"Sent response to {reply_to}: {response.status}")

async def send_to_dlq(message: IncomingMessage, reason: str):
    connection = await connect(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(settings.queue_dlq, durable=True)
        
        # Add header with reason
        headers = message.headers or {}
        headers['x-dlq-reason'] = reason
        
        await channel.default_exchange.publish(
            Message(
                body=message.body,
                headers=headers
            ),
            routing_key=settings.queue_dlq
        )
    logger.info(f"Sent message to DLQ: {reason}")

async def main():
    logger.info("Starting Server...")
    
    # Retry connection logic
    retries = 5
    while retries > 0:
        try:
            connection = await connect(settings.rabbitmq_url)
            break
        except Exception as e:
            logger.warning(f"Failed to connect to RabbitMQ: {e}. Retrying in 5 seconds...")
            retries -= 1
            await asyncio.sleep(5)
    else:
        logger.error("Could not connect to RabbitMQ after multiple attempts.")
        return
    
    async with connection:
        channel = await connection.channel()
        
        # Declare queues
        queue = await channel.declare_queue(settings.queue_requests, durable=True)
        await channel.declare_queue(settings.queue_responses, durable=True)
        await channel.declare_queue(settings.queue_dlq, durable=True)
        
        logger.info(f"Listening on {settings.queue_requests}")
        
        await queue.consume(process_message)
        
        # Keep running
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

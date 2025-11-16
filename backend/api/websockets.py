import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.surreal_utils import get_document_version
from websocket import get_connection_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/{arxiv_id}/{version}")
async def document_status_websocket(websocket: WebSocket, arxiv_id: str, version: str):
    """
    WebSocket endpoint for real-time document status updates

    Client connects to: ws://localhost:8001/ws/{arxiv_id}/{version}

    Messages sent to client:
    {
        "paper_id": "2301.07041",
        "version": "1",
        "type": "document_update",
        "data": {
            "loading_status": "WAITING",
            "updated_timestamp": "2025-11-05T..."
        }
    }
    """
    manager = get_connection_manager()
    paper_key = f"{arxiv_id}_v{version}"

    await manager.connect(websocket, paper_key)

    message_count = 0
    try:
        # Send initial status
        logger.info(
            f"[WebSocket] Fetching initial document status for {arxiv_id} v{version}"
        )
        doc = await get_document_version(arxiv_id, version)
        if doc:
            # Database already returns camelCase keys
            if doc.get("loadingStatus") == "SUCCESS":
                logger.info(
                    f"[WebSocket] Document is SUCCESS, sending full document to {arxiv_id} v{version}"
                )
                await manager.send_update(paper_key, doc)
            else:
                # Extract only the necessary fields for non-SUCCESS status
                initial_data = {
                    "loadingStatus": doc.get("loadingStatus"),
                    "updatedTimestamp": doc.get("updatedTimestamp"),
                    "metadata": doc.get("metadata"),
                }
                logger.info(
                    f"[WebSocket] Sending initial status to {arxiv_id} v{version}: {initial_data}"
                )
                await manager.send_update(paper_key, initial_data)
        else:
            logger.warning(
                f"[WebSocket] No document found for {arxiv_id} v{version}, sending empty status"
            )
            await manager.send_update(
                paper_key,
                {
                    "loadingStatus": None,
                    "updatedTimestamp": None,
                },
            )

        while True:
            try:
                # Wait for client messages with timeout to allow periodic checks
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message_count += 1
                logger.info(
                    f"[WebSocket] Received message #{message_count} from {arxiv_id} v{version}: {data[:100]}..."
                )
            except TimeoutError:
                # Timeout is normal - send a ping to keep connection alive
                try:
                    await websocket.send_json({"type": "ping"})
                    logger.debug(f"[WebSocket] Sent ping to {arxiv_id} v{version}")
                except Exception as e:
                    # Connection is dead
                    logger.warning(
                        f"[WebSocket] Connection dead for {arxiv_id} v{version}: {e}"
                    )
                    break
    except WebSocketDisconnect:
        logger.info(
            f"[WebSocket] Client disconnected: {arxiv_id} v{version} (received {message_count} messages)"
        )
    except Exception as e:
        logger.error(
            f"[WebSocket] Error in WebSocket handler for {arxiv_id} v{version}: {e}",
            exc_info=True,
        )
    finally:
        # Always disconnect to ensure cleanup
        manager.disconnect(websocket, paper_key)

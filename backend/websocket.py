import json
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        # Map of paper_id -> set of connected websockets
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, paper_id: str):
        """Accept and register a new WebSocket connection"""
        client_info = (
            f"{websocket.client.host}:{websocket.client.port}"
            if websocket.client
            else "unknown"
        )
        logger.info(
            f"[WebSocket] Accepting connection for {paper_id} from {client_info}"
        )

        await websocket.accept()

        if paper_id not in self.active_connections:
            self.active_connections[paper_id] = set()

        self.active_connections[paper_id].add(websocket)
        total_connections = len(self.active_connections[paper_id])
        total_papers = len(self.active_connections)
        logger.info(
            f"[WebSocket] Connection registered: {paper_id} | Active connections for this paper: {total_connections} | Total papers with connections: {total_papers}"
        )

    def disconnect(self, websocket: WebSocket, paper_id: str):
        """Remove a WebSocket connection"""
        if paper_id in self.active_connections:
            was_present = websocket in self.active_connections[paper_id]
            self.active_connections[paper_id].discard(websocket)
            remaining = len(self.active_connections[paper_id])

            # Clean up empty sets
            if not self.active_connections[paper_id]:
                del self.active_connections[paper_id]
                logger.info(
                    f"[WebSocket] Disconnected: {paper_id} | No more connections for this paper"
                )
            else:
                logger.info(
                    f"[WebSocket] Disconnected: {paper_id} | Remaining connections: {remaining}"
                )

            if not was_present:
                logger.warning(
                    f"[WebSocket] Attempted to disconnect websocket that wasn't registered for {paper_id}"
                )

    async def send_update(self, paper_key: str, data: dict):
        """
        Send update to all connections watching a specific paper

        Args:
            paper_key: Paper key in format "{arxiv_id}_v{version}"
            data: Update data (status, progress, etc.) - should use camelCase keys
        """
        if paper_key not in self.active_connections:
            logger.debug(
                f"[WebSocket] No active connections for {paper_key}, skipping update"
            )
            return

        # Extract arxiv_id and version from paper_key for the message
        # paper_key format: "2301.07041_v1"
        parts = paper_key.rsplit("_v", 1)
        arxiv_id = parts[0] if len(parts) == 2 else paper_key
        version = parts[1] if len(parts) == 2 else "1"

        message = {
            "paper_id": arxiv_id,
            "version": version,
            "type": "document_update",
            "data": data,
        }
        message_str = json.dumps(message)

        connection_count = len(self.active_connections[paper_key])
        logger.info(
            f"[WebSocket] Sending update to {connection_count} connection(s) for {paper_key}: {json.dumps(data, indent=2)}"
        )

        # Send to all connected clients
        disconnected = set()
        sent_count = 0
        for websocket in self.active_connections[paper_key]:
            try:
                await websocket.send_text(message_str)
                sent_count += 1
            except Exception as e:
                logger.error(
                    f"[WebSocket] Error sending to websocket for {paper_key}: {e}"
                )
                disconnected.add(websocket)

        logger.info(
            f"[WebSocket] Successfully sent update to {sent_count}/{connection_count} connection(s) for {paper_key}"
        )

        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket, paper_key)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        message_str = json.dumps(message)

        for paper_connections in self.active_connections.values():
            for websocket in paper_connections:
                try:
                    await websocket.send_text(message_str)
                except Exception as e:
                    logger.error(f"Error broadcasting: {e}")


# Global connection manager instance
manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """Get connection manager for dependency injection"""
    return manager

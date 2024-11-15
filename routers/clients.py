from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, insert, delete
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from models.clients import Client
from routers.responses import BaseAPIResponse
from schemas.clients import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)

def get_db_session() -> Session: # type: ignore
    """
    Provides a database session for the duration of a request.

    Yields:
        Session: The SQLAlchemy session for the current request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", status_code=201, response_model=BaseAPIResponse)
def create_client(client: ClientCreate, db: Session = Depends(get_db_session)) -> BaseAPIResponse:
    """
    Creates a new client.

    Args:
        client (ClientCreate): The client data to create.
        db (Session, optional): The database session. Defaults to Depends(get_db_session).

    Returns:
        BaseAPIResponse: The created client.
    """
    try:
        new_client = Client(name=client.name, email=client.email, created_at=datetime.now())
        db.execute(insert(Client), new_client.__dict__)
        db.commit()

        created_client = db.execute(select(Client).filter(Client.email == client.email)).first()
        return BaseAPIResponse(
            data=ClientResponse(
                id=created_client[0].id,
                name=created_client[0].name,
                email=created_client[0].email,
                created_at=created_client[0].created_at
            )
        )
    except Exception as e:
        return BaseAPIResponse(error=str(e), status_code=400)

@router.get("/", response_model=BaseAPIResponse)
def get_clients(db: Session = Depends(get_db_session)) -> BaseAPIResponse:
    """
    Retrieves all clients.

    Args:
        db (Session, optional): The database session. Defaults to Depends(get_db_session).

    Returns:
        BaseAPIResponse[list[ClientResponse]]: The list of all clients.
    """
    try:
        result = db.execute(select(Client)).all()
        clients = [
            ClientResponse(
                id=client[0].id,
                name=client[0].name,
                email=client[0].email,
                created_at=client[0].created_at
            ) for client in result
        ]
        return BaseAPIResponse(data=clients)
    except Exception as e:
        return BaseAPIResponse(error=str(e), status_code=400)

@router.get("/{client_id}", response_model=BaseAPIResponse)
def get_client(client_id: int, db: Session = Depends(get_db_session)) -> BaseAPIResponse:
    """
    Retrieves a client by ID.

    Args:
        client_id (int): The ID of the client to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db_session).

    Returns:
        BaseAPIResponse: The client with the specified ID.
    """
    try:
        result = db.execute(select(Client).filter(Client.id == client_id)).first()
        if not result:
            return BaseAPIResponse(error="Client not found", status_code=404)

        return BaseAPIResponse(
            data=ClientResponse(
                id=result[0].id,
                name=result[0].name,
                email=result[0].email,
                created_at=result[0].created_at
            )
        )
    except Exception as e:
        return BaseAPIResponse(error=str(e), status_code=400)

@router.put("/{client_id}", response_model=BaseAPIResponse)
def update_client(client_id: int, client: ClientUpdate, db: Session = Depends(get_db_session)) -> BaseAPIResponse:
    """
    Updates an existing client.

    Args:
        client_id (int): The ID of the client to update.
        client (ClientUpdate): The updated client data.
        db (Session, optional): The database session. Defaults to Depends(get_db_session).

    Returns:
        BaseAPIResponse: The updated client.
    """
    try:
        db.execute(
            update(Client)
            .where(Client.id == client_id)
            .values(name=client.name, email=client.email)
        )
        db.commit()
        updated_client = db.execute(select(Client).filter(Client.id == client_id)).first()
        return BaseAPIResponse(
            data=ClientResponse(
                id=updated_client[0].id,
                name=updated_client[0].name,
                email=updated_client[0].email,
                created_at=updated_client[0].created_at
            )
        )
    except Exception as e:
        return BaseAPIResponse(error=str(e), status_code=400)

@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db_session)) -> BaseAPIResponse:
    """
    Deletes a client by ID.

    Args:
        client_id (int): The ID of the client to delete.
        db (Session, optional): The database session. Defaults to Depends(get_db_session).

    Returns:
        BaseAPIResponse[None]: An empty response.
    """
    try:
        db.execute(delete(Client).where(Client.id == client_id))
        db.commit()
        return BaseAPIResponse(data={"message": "Client deleted successfully."})
    except Exception as e:
        return BaseAPIResponse(error=str(e), status_code=400)
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from models.clients import Client
from routers.responses import BaseAPIResponse
from schemas.clients import ClientCreate, ClientUpdate

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)

def get_db_session() -> Session: # type: ignore
    """
    Provides a SQLAlchemy database session for the duration of the request.
    The session is yielded for use in handling requests and automatically
    closed once the request is completed.

    Yields:
        Session: The SQLAlchemy session object for interacting with the database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=dict, status_code=201)
def create_client(client: ClientCreate, db: Session = Depends(get_db_session)) -> dict:
    """
    Creates a new client and stores it in the database.
    
    This endpoint takes the client data (name, email), inserts a new client into the
    database, and returns the newly created client with the auto-generated ID.

    Args:
        client (ClientCreate): The client data to be added.
        db (Session, optional): The database session for the transaction.

    Returns:
        dict: A success response with the created client's details, including the ID.
    """
    try:
        # Prepare insert statement
        stmt = insert(Client).values(
            name=client.name,
            email=client.email,
            created_at=datetime.now()
        )

        # Execute the insert statement
        db.execute(stmt)
        db.commit()

        # Get the last inserted client to fetch the auto-generated ID
        new_client = db.query(Client).filter(Client.email == client.email).first()

        if not new_client:
            raise Exception("Failed to fetch the newly created client")

        # Return response with new client data
        return BaseAPIResponse.get_success_response(
            data={
                "id": new_client.id,
                "name": new_client.name,
                "email": new_client.email,
                "created_at": new_client.created_at.isoformat(),  # Ensure datetime is serialized properly
            },
            message="Client created successfully",
            status_code=201
        )
    except Exception as e:
        db.rollback()  # Rollback any changes if the operation fails
        return BaseAPIResponse.get_error_response(
            error="Failed to create client",
            details={"exception": str(e)},
            status_code=400
        )


@router.get("/", response_model=dict, status_code=200)
def get_clients(db: Session = Depends(get_db_session), limit: int = 10, offset: int = 0) -> dict:
    """
    Retrieves a paginated list of all clients from the database.

    This endpoint supports pagination by using `limit` (number of clients per page) and 
    `offset` (which page to fetch). It returns a list of clients along with metadata 
    about the pagination.

    Args:
        db (Session, optional): The database session.
        limit (int, optional): The number of clients to return per page.
        offset (int, optional): The offset from which to start retrieving clients.

    Returns:
        dict: A paginated response with a list of clients and pagination metadata.
    """
    try:
        result = db.query(Client).offset(offset).limit(limit).all()
        total_count = db.query(Client).count()

        clients = [
            {
                "id": client.id,
                "name": client.name,
                "email": client.email,
                "created_at": client.created_at.isoformat(),  # Convert datetime to ISO 8601 string
            }
            for client in result
        ]

        return BaseAPIResponse.get_paginated_response(
            data=clients,
            total_count=total_count,
            page=(offset // limit) + 1,
            items_per_page=limit,
            has_more=(offset + limit < total_count),
            status_code=200,
        )
    except Exception as e:
        return BaseAPIResponse.get_error_response(
            error="Error retrieving clients",
            details={"exception": str(e)},
            status_code=500,
        )


@router.get("/{client_id}", response_model=dict, status_code=200)
def get_client(client_id: int, db: Session = Depends(get_db_session)) -> dict:
    """
    Retrieves a specific client by ID.

    This endpoint fetches the client details based on the provided `client_id`. 
    If the client is not found, it returns a 404 error.

    Args:
        client_id (int): The ID of the client to retrieve.
        db (Session, optional): The database session.

    Returns:
        dict: A success response with the client's data, or an error message if not found.
    """
    try:
        # Query for the client by ID
        client = db.query(Client).filter(Client.id == client_id).first()

        # Handle case if client is not found
        if not client:
            return BaseAPIResponse.get_error_response(
                error="Client not found",
                status_code=404,
            )

        # Return the client data
        return BaseAPIResponse.get_success_response(
            data={
                "id": client.id,
                "name": client.name,
                "email": client.email,
                "created_at": client.created_at.isoformat(),  # Ensure datetime is serialized properly
            },
            message="Client retrieved successfully",
            status_code=200,
        )
    except Exception as e:
        # Return error response with exception details
        return BaseAPIResponse.get_error_response(
            error="Error retrieving client",
            details={"exception": str(e)},
            status_code=500,
        )


@router.put("/{client_id}", response_model=dict, status_code=200)
def update_client(client_id: int, client: ClientUpdate, db: Session = Depends(get_db_session)) -> dict:
    """
    Updates an existing client's details.

    This endpoint allows for updating the `name` and `email` fields of a specific client 
    identified by `client_id`. It returns the updated client data upon successful update.

    Args:
        client_id (int): The ID of the client to update.
        client (ClientUpdate): The updated client data.
        db (Session, optional): The database session.

    Returns:
        dict: A success response with the updated client's data, or an error message if not found.
    """
    try:
        # Update the client in the database
        db.execute(
            update(Client)
            .where(Client.id == client_id)
            .values(name=client.name, email=client.email)
        )
        db.commit()

        # Fetch the updated client
        updated_client = db.query(Client).filter(Client.id == client_id).first()

        # Handle case if client is not found
        if not updated_client:
            return BaseAPIResponse.get_error_response(
                error="Client not found",
                status_code=404,
            )

        # Return the updated client data
        return BaseAPIResponse.get_success_response(
            data={
                "id": updated_client.id,
                "name": updated_client.name,
                "email": updated_client.email,
                "created_at": updated_client.created_at.isoformat(),  # Ensure datetime is serialized properly
            },
            message="Client updated successfully",
            status_code=200,
        )
    except Exception as e:
        # Rollback any changes in case of error
        db.rollback()
        # Return error response with exception details
        return BaseAPIResponse.get_error_response(
            error="Error updating client",
            details={"exception": str(e)},
            status_code=500,
        )


@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db_session)):
    """
    Deletes a client by ID.

    This endpoint deletes the client specified by `client_id`. If the client is not 
    found, it returns a 404 error. On successful deletion, it returns a 204 status code 
    indicating that the request was successful and no content is returned.

    Args:
        client_id (int): The ID of the client to delete.
        db (Session, optional): The database session.

    Returns:
        dict: A success response with a 204 status code on successful deletion.
    """
    try:
        # Fetch the client to delete
        client = db.query(Client).filter(Client.id == client_id).first()

        # If client does not exist, return a not found error
        if not client:
            return BaseAPIResponse.get_error_response(
                error="Client not found",
                status_code=404,
            )

        # Delete the client from the database
        db.delete(client)
        db.commit()

        # Return success response (empty body for successful deletion)
        return BaseAPIResponse.get_success_response(
            message="Client deleted successfully",
            status_code=204,
        )
    except Exception as e:
        # Rollback any changes in case of error
        db.rollback()
        # Return error response with exception details
        return BaseAPIResponse.get_error_response(
            error="Error deleting client",
            details={"exception": str(e)},
            status_code=500,
        )

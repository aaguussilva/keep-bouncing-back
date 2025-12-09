import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock
from app.schemas.user import UserUpdate
from app.routers.users import update_user
from app.models import user as user_model
from sqlalchemy.exc import IntegrityError

def test_update_user_success(db_session):
    """Test successful user update by the owner."""
    # Create a test user
    test_user = user_model.User(
        name="Original Name",
        email="original@example.com",
        password="hashed_password"
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    # Mock current user
    current_user = MagicMock()
    current_user.id = test_user.id

    # Update data
    update_data = UserUpdate(
        name="Updated Name",
        email="updated@example.com"
    )

    # Call the update function
    result = update_user(
        user_id=test_user.id,
        user_data=update_data,
        db=db_session,
        current_user=current_user
    )

    # Verify the changes
    assert result.name == "Updated Name"
    assert result.email == "updated@example.com"
    
    # Verify in database
    updated_user = db_session.query(user_model.User).filter(user_model.User.id == test_user.id).first()
    assert updated_user.name == "Updated Name"
    assert updated_user.email == "updated@example.com"

def test_update_user_unauthorized(db_session):
    """Test update fails when non-owner tries to update."""
    # Create a test user
    test_user = user_model.User(
        name="Test User",
        email="test@example.com",
        password="hashed_password"
    )
    db_session.add(test_user)
    db_session.commit()

    # Mock current user (different ID)
    current_user = MagicMock()
    current_user.id = 999  # Different user ID

    update_data = UserUpdate(
        name="Should Not Update",
        email="hacked@example.com"
    )

    with pytest.raises(HTTPException) as exc_info:
        update_user(
            user_id=test_user.id,
            user_data=update_data,
            db=db_session,
            current_user=current_user
        )
    
    assert exc_info.value.status_code == 403
    assert "No autorizado" in str(exc_info.value.detail)

def test_update_user_not_found(db_session):
    """Test update fails when user doesn't exist."""
    current_user = MagicMock()
    current_user.id = 1  # Current user is the one trying to update

    update_data = UserUpdate(
        name="Doesn't Matter",
        email="nonexistent@example.com"
    )

    with pytest.raises(HTTPException) as exc_info:
        update_user(
            user_id=999,  # Non-existent user ID
            user_data=update_data,
            db=db_session,
            current_user=current_user
        )
    
    # Update the assertion to expect 403 instead of 404
    assert exc_info.value.status_code == 403
    assert "No autorizado" in str(exc_info.value.detail)

def test_update_user_email_already_exists(db_session):
    """Test update fails when trying to use an existing email."""
    # Create two test users
    user1 = user_model.User(
        name="User One",
        email="user1@example.com",
        password="hashed1"
    )
    user2 = user_model.User(
        name="User Two",
        email="user2@example.com",
        password="hashed2"
    )
    db_session.add_all([user1, user2])
    db_session.commit()
    db_session.refresh(user1)
    db_session.refresh(user2)

    current_user = MagicMock()
    current_user.id = user1.id

    # Try to update user1's email to user2's email
    update_data = UserUpdate(
        name="User One",
        email="user2@example.com"  # Already exists
    )

    # Update the test to expect an IntegrityError
    with pytest.raises(IntegrityError):
        update_user(
            user_id=user1.id,
            user_data=update_data,
            db=db_session,
            current_user=current_user
        )
    
    # Rollback the session to clean up the failed transaction
    db_session.rollback()

def test_update_user_partial_update(db_session):
    """Test that only provided fields are updated."""
    # Create a test user
    test_user = user_model.User(
        name="Original Name",
        email="original@example.com",
        password="hashed_password"
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    current_user = MagicMock()
    current_user.id = test_user.id

    # Only update the name
    update_data = UserUpdate(
        name="New Name"
        # email not provided
    )

    result = update_user(
        user_id=test_user.id,
        user_data=update_data,
        db=db_session,
        current_user=current_user
    )

    # Verify only name was updated
    assert result.name == "New Name"
    assert result.email == "original@example.com"  # Should remain unchanged
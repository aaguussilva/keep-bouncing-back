import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock

from app.models import user as user_model
from app.schemas import user as user_schemas
from app.routers.users import create_user


class TestCreateUser:
    """Test cases for the create_user function"""

    def test_create_user_success(self, db_session):
        """Test successful user creation"""
        user_data = user_schemas.UserCreate(
            name="Test User",
            email="test@example.com",
            password="password123"
        )

        with patch('app.routers.users.auth.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"

            result = create_user(user_data, db_session)

            assert result.name == "Test User"
            assert result.email == "test@example.com"
            assert result.password == "hashed_password"
            assert result.id is not None

            mock_hash.assert_called_once_with("password123")

            saved_user = db_session.query(user_model.User).filter(
                user_model.User.email == "test@example.com"
            ).first()
            assert saved_user is not None
            assert saved_user.name == "Test User"

    def test_create_user_duplicate_email(self, db_session):
        """Test creating user with email that already exists"""
        existing_user = user_model.User(
            name="Existing User",
            email="existing@example.com",
            password="hashed_password"
        )
        db_session.add(existing_user)
        db_session.commit()

        user_data = user_schemas.UserCreate(
            name="New User",
            email="existing@example.com", 
            password="password123"
        )

        with pytest.raises(HTTPException) as exc_info:
            create_user(user_data, db_session)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Email already registered"

    def test_create_user_password_hashing(self, db_session):
        """Test that password is properly hashed"""
        user_data = user_schemas.UserCreate(
            name="Test User",
            email="test@example.com",
            password="mypassword"
        )

        with patch('app.routers.users.auth.hash_password') as mock_hash:
            mock_hash.return_value = "secure_hash_123"

            result = create_user(user_data, db_session)

            mock_hash.assert_called_once_with("mypassword")
            assert result.password == "secure_hash_123"

    def test_create_user_database_commit(self, db_session):
        """Test that user is committed to database"""
        user_data = user_schemas.UserCreate(
            name="Commit Test",
            email="commit@example.com",
            password="password"
        )

        with patch('app.routers.users.auth.hash_password') as mock_hash:
            mock_hash.return_value = "hashed"

            result = create_user(user_data, db_session)

            db_user = db_session.query(user_model.User).filter(
                user_model.User.id == result.id
            ).first()

            assert db_user is not None
            assert db_user.name == "Commit Test"
            assert db_user.email == "commit@example.com"

    def test_create_user_return_type(self, db_session):
        """Test that create_user returns a User model instance"""
        user_data = user_schemas.UserCreate(
            name="Return Test",
            email="return@example.com",
            password="password"
        )

        with patch('app.routers.users.auth.hash_password') as mock_hash:
            mock_hash.return_value = "hashed"

            result = create_user(user_data, db_session)

            assert isinstance(result, user_model.User)
            assert hasattr(result, 'id')
            assert hasattr(result, 'name')
            assert hasattr(result, 'email')
            assert hasattr(result, 'password')
            assert hasattr(result, 'created_at')

    def test_email_uppercase_treated_as_duplicate_after_normalization(self, db_session):
        """Uppercase email should be treated as duplicate if a lowercase equivalent already exists after normalization."""
        existing_user = user_model.User(
            name="Existing",
            email="existing@example.com",
            password="hashed"
        )
        db_session.add(existing_user)
        db_session.commit()

        user_data = user_schemas.UserCreate(
            name="New",
            email="EXISTING@EXAMPLE.COM",
            password="pw_secure123"
        )

        with pytest.raises(HTTPException) as exc_info:
            create_user(user_data, db_session)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Email already registered"

    def test_extremely_long_password(self, db_session):
        """Ensure an extremely long password does not break creation (it is hashed and stored)."""
        # Use a large password but within the limit (<=128)
        long_pw = "p" * 100
        user_data = user_schemas.UserCreate(
            name="LongPw",
            email="longpw@example.com",
            password=long_pw
        )

        with patch('app.routers.users.auth.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_long"

            result = create_user(user_data, db_session)

            mock_hash.assert_called_once_with(long_pw)
            assert result.password == "hashed_long"
            saved = db_session.query(user_model.User).filter(user_model.User.email == "longpw@example.com").first()
            assert saved is not None

    def test_password_too_long_rejected(self, db_session):
        """Very long password (> MAX) should be rejected with HTTP 400."""
        very_long = "p" * 500
        user_data = user_schemas.UserCreate(
            name="TooLong",
            email="toolong@example.com",
            password=very_long
        )

        with patch('app.routers.users.auth.hash_password') as mock_hash:
            mock_hash.return_value = "x"
            with pytest.raises(HTTPException) as exc_info:
                create_user(user_data, db_session)

            assert exc_info.value.status_code == 400
            assert "too long" in str(exc_info.value.detail)

    def test_name_with_special_characters_rejected(self, db_session):
        """Names containing disallowed special characters should be rejected with HTTP 400."""
        special_name = "Jöhn Dœ!@#€"
        user_data = user_schemas.UserCreate(
            name=special_name,
            email="special@example.com",
            password="pw_secure123"
        )

        with patch('app.routers.users.auth.hash_password') as mock_hash:
            mock_hash.return_value = "h"
            with pytest.raises(HTTPException) as exc_info:
                create_user(user_data, db_session)

            assert exc_info.value.status_code == 400
            assert "Invalid name" in str(exc_info.value.detail)


def test_delete_user_success(db_session):
    """Owner can delete their account successfully."""
    from app.routers.users import delete_user

    user_obj = user_model.User(name="ToDelete", email="del@example.com", password="h")
    db_session.add(user_obj)
    db_session.commit()
    db_session.refresh(user_obj)

    resp = delete_user(user_obj.id, db_session, user_obj)
    assert isinstance(resp, dict)
    assert resp.get("detail") == "User deleted"

    # Ensure the user is really deleted
    assert db_session.query(user_model.User).filter(user_model.User.id == user_obj.id).first() is None


def test_delete_user_unauthorized(db_session):
    """A different authenticated user cannot delete another user's account."""
    from app.routers.users import delete_user

    owner = user_model.User(name="Owner", email="owner@example.com", password="h")
    other = user_model.User(name="Other", email="other@example.com", password="h")
    db_session.add_all([owner, other])
    db_session.commit()
    db_session.refresh(owner)
    db_session.refresh(other)

    with pytest.raises(HTTPException) as exc:
        delete_user(owner.id, db_session, other)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Not authorized"


def test_delete_user_not_found(db_session):
    """Attempting to delete a non-existent user returns 404."""
    from app.routers.users import delete_user

    # Simulate an authenticated user whose id matches the requested id, but the DB has no record.
    non_existing_id = 999999
    fake_current_user = user_model.User()
    fake_current_user.id = non_existing_id

    with pytest.raises(HTTPException) as exc:
        delete_user(non_existing_id, db_session, fake_current_user)

    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"

"""API tests for Follow Stock endpoints.

Tests follow the Stocker project testing principles:
- Fixture isolation with yield-based cleanup
- AAA pattern (Arrange, Act, Assert)
- Security boundary validation (IDOR prevention)
- No manual `with app.app_context()` - environment managed by conftest.py
"""
import json
import pytest
from app import db
from app.follow_stock.models import Follow_Stock


# ============================================================================
# Yield-based Fixtures for Automatic Cleanup
# ============================================================================

@pytest.fixture
def follow_stock_factory(regular_user, sample_basic_info):
    """Factory fixture to create follow stocks with automatic cleanup."""
    created_ids = []

    def _create(stock_id=None, long_or_short='long', comment='Test comment', is_delete=False):
        follow = Follow_Stock(
            user_id=regular_user.id,
            stock_id=stock_id or sample_basic_info.id,
            long_or_short=long_or_short,
            comment=comment,
            is_delete=is_delete
        )
        db.session.add(follow)
        db.session.commit()
        created_ids.append(follow.id)
        return follow

    yield _create

    # Cleanup all created follow stocks
    if created_ids:
        Follow_Stock.query.filter(Follow_Stock.id.in_(created_ids)).delete(synchronize_session=False)
        db.session.commit()


@pytest.fixture
def other_user_follow_stock(admin_user, sample_basic_info):
    """Create a follow stock for another user (for IDOR tests)."""
    follow = Follow_Stock(
        user_id=admin_user.id,
        stock_id=sample_basic_info.id,
        long_or_short='long',
        comment='Admin user follow stock',
        is_delete=False
    )
    db.session.add(follow)
    db.session.commit()

    yield follow

    # Cleanup
    Follow_Stock.query.filter_by(id=follow.id).delete()
    db.session.commit()


@pytest.fixture
def clean_user_follow_stocks(regular_user):
    """Ensure user has no follow stocks before and after test."""
    Follow_Stock.query.filter_by(user_id=regular_user.id).delete()
    db.session.commit()

    yield

    Follow_Stock.query.filter_by(user_id=regular_user.id).delete()
    db.session.commit()


# ============================================================================
# Test Classes
# ============================================================================

@pytest.mark.usefixtures('test_app')
class TestFollowStockListEndpoint:
    """Tests for GET/POST /api/v0/follow_stock."""

    # ------------------------------------------------------------------------
    # GET /api/v0/follow_stock - List Follow Stocks
    # ------------------------------------------------------------------------

    def test_list_follow_stocks_empty(self, authenticated_client, clean_user_follow_stocks):
        """Should return empty list when no follow stocks exist."""
        # Act
        response = authenticated_client.get('/api/v0/follow_stock/')

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []

    def test_list_follow_stocks_returns_user_stocks(
        self, authenticated_client, follow_stock_factory
    ):
        """Should return all non-deleted follow stocks for the user."""
        # Arrange
        follow_stock_factory(long_or_short='long', comment='TSMC Long')
        follow_stock_factory(long_or_short='short', comment='TSMC Short')

        # Act
        response = authenticated_client.get('/api/v0/follow_stock/')

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 2
        comments = [item['comment'] for item in data]
        assert 'TSMC Long' in comments
        assert 'TSMC Short' in comments

    def test_list_follow_stocks_excludes_deleted_by_default(
        self, authenticated_client, follow_stock_factory
    ):
        """Should exclude soft-deleted follow stocks by default."""
        # Arrange
        follow_stock_factory(long_or_short='long', comment='Active stock')
        follow_stock_factory(long_or_short='short', comment='Deleted stock', is_delete=True)

        # Act
        response = authenticated_client.get('/api/v0/follow_stock/')

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        comments = [item['comment'] for item in data]
        assert 'Active stock' in comments
        assert 'Deleted stock' not in comments

    def test_list_follow_stocks_includes_deleted_when_requested(
        self, authenticated_client, follow_stock_factory
    ):
        """Should include soft-deleted follow stocks when show_delete=true."""
        # Arrange
        follow_stock_factory(long_or_short='long', comment='Active stock')
        follow_stock_factory(long_or_short='short', comment='Deleted stock', is_delete=True)

        # Act
        response = authenticated_client.get('/api/v0/follow_stock/?show_delete=true')

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        comments = [item['comment'] for item in data]
        assert 'Active stock' in comments
        assert 'Deleted stock' in comments

    def test_list_follow_stocks_only_returns_own_stocks(
        self, authenticated_client, follow_stock_factory, other_user_follow_stock
    ):
        """Should only return follow stocks belonging to the authenticated user."""
        # Arrange
        follow_stock_factory(comment='My stock')

        # Act
        response = authenticated_client.get('/api/v0/follow_stock/')

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)

        # Should not include other user's follow stock
        follow_ids = [item['id'] for item in data]
        assert other_user_follow_stock.id not in follow_ids

    def test_list_follow_stocks_unauthorized(self, client):
        """Should return 401 when not authenticated."""
        # Act
        response = client.get('/api/v0/follow_stock/')

        # Assert
        assert response.status_code == 401

    # ------------------------------------------------------------------------
    # POST /api/v0/follow_stock - Create Follow Stock
    # ------------------------------------------------------------------------

    def test_create_follow_stock_success(
        self, authenticated_client, sample_basic_info, clean_user_follow_stocks
    ):
        """Should create a new follow stock successfully."""
        # Arrange
        payload = {
            'stock_id': sample_basic_info.id,
            'long_or_short': 'long',
            'comment': 'New follow stock'
        }

        # Act
        response = authenticated_client.post(
            '/api/v0/follow_stock/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['long_or_short'] == 'long'
        assert data['comment'] == 'New follow stock'
        assert 'id' in data

    def test_create_follow_stock_short_position(
        self, authenticated_client, sample_basic_info, clean_user_follow_stocks
    ):
        """Should create a short position follow stock."""
        # Arrange
        payload = {
            'stock_id': sample_basic_info.id,
            'long_or_short': 'short',
            'comment': 'Short position'
        }

        # Act
        response = authenticated_client.post(
            '/api/v0/follow_stock/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['long_or_short'] == 'short'

    def test_create_follow_stock_returns_existing_if_duplicate(
        self, authenticated_client, follow_stock_factory
    ):
        """Should return existing record if user already follows the stock."""
        # Arrange - create existing follow stock
        existing = follow_stock_factory(long_or_short='long', comment='Existing')
        payload = {
            'stock_id': existing.stock_id,
            'long_or_short': 'short',
            'comment': 'New comment'
        }

        # Act
        response = authenticated_client.post(
            '/api/v0/follow_stock/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Assert - should return existing record
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == existing.id
        assert data['long_or_short'] == 'long'  # Original value
        assert data['comment'] == 'Existing'  # Original value

    def test_create_follow_stock_missing_body(self, authenticated_client):
        """Should return 400 when request body is missing."""
        # Act
        response = authenticated_client.post(
            '/api/v0/follow_stock/',
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_create_follow_stock_invalid_json(self, authenticated_client):
        """Should return 400 when request body is invalid JSON."""
        # Act
        response = authenticated_client.post(
            '/api/v0/follow_stock/',
            data='invalid json',
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 400

    def test_create_follow_stock_unauthorized(self, client, sample_basic_info):
        """Should return 401 when not authenticated."""
        # Arrange
        payload = {
            'stock_id': sample_basic_info.id,
            'long_or_short': 'long',
            'comment': 'Test'
        }

        # Act
        response = client.post(
            '/api/v0/follow_stock/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 401


@pytest.mark.usefixtures('test_app')
class TestFollowStockDetailEndpoint:
    """Tests for GET/PATCH/DELETE /api/v0/follow_stock/<id>."""

    # ------------------------------------------------------------------------
    # GET /api/v0/follow_stock/<id> - Get Single Follow Stock
    # ------------------------------------------------------------------------

    def test_get_follow_stock_success(self, authenticated_client, follow_stock_factory):
        """Should return follow stock details."""
        # Arrange
        follow = follow_stock_factory(long_or_short='long', comment='Detail test')

        # Act
        response = authenticated_client.get(f'/api/v0/follow_stock/{follow.stock_id}')

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['comment'] == 'Detail test'
        assert data['long_or_short'] == 'long'

    def test_get_follow_stock_not_found(self, authenticated_client):
        """Should return 404 for non-existent follow stock."""
        # Act
        response = authenticated_client.get('/api/v0/follow_stock/nonexistent-id')

        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    def test_get_follow_stock_unauthorized(self, client, sample_follow_stock_long):
        """Should return 401 when not authenticated."""
        # Act
        response = client.get(f'/api/v0/follow_stock/{sample_follow_stock_long.stock_id}')

        # Assert
        assert response.status_code == 401

    # ------------------------------------------------------------------------
    # PATCH /api/v0/follow_stock/<id> - Update Follow Stock
    # ------------------------------------------------------------------------

    def test_update_follow_stock_success(self, authenticated_client, follow_stock_factory):
        """Should update follow stock successfully."""
        # Arrange
        follow = follow_stock_factory(long_or_short='long', comment='Original')
        payload = {
            'long_or_short': 'short',
            'comment': 'Updated comment'
        }

        # Act
        response = authenticated_client.patch(
            f'/api/v0/follow_stock/{follow.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['long_or_short'] == 'short'
        assert data['comment'] == 'Updated comment'

        # Deep verification - check database
        db.session.refresh(follow)
        assert follow.long_or_short == 'short'
        assert follow.comment == 'Updated comment'

    def test_update_follow_stock_not_found(self, authenticated_client):
        """Should return 404 for non-existent follow stock."""
        # Arrange
        payload = {
            'long_or_short': 'short',
            'comment': 'Updated'
        }

        # Act
        response = authenticated_client.patch(
            '/api/v0/follow_stock/nonexistent-id',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 404

    def test_update_follow_stock_missing_body(self, authenticated_client, follow_stock_factory):
        """Should return 400 when request body is missing."""
        # Arrange
        follow = follow_stock_factory()

        # Act
        response = authenticated_client.patch(
            f'/api/v0/follow_stock/{follow.id}',
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 400

    def test_update_follow_stock_unauthorized(self, client, sample_follow_stock_long):
        """Should return 401 when not authenticated."""
        # Arrange
        payload = {'long_or_short': 'short', 'comment': 'Test'}

        # Act
        response = client.patch(
            f'/api/v0/follow_stock/{sample_follow_stock_long.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 401

    # ------------------------------------------------------------------------
    # DELETE /api/v0/follow_stock/<id> - Delete Follow Stock
    # ------------------------------------------------------------------------

    def test_delete_follow_stock_success(self, authenticated_client, follow_stock_factory):
        """Should soft-delete follow stock successfully."""
        # Arrange
        follow = follow_stock_factory(comment='To be deleted')
        follow_id = follow.id

        # Act
        response = authenticated_client.delete(f'/api/v0/follow_stock/{follow_id}')

        # Assert
        assert response.status_code == 204

        # Deep verification - check soft delete in database
        db.session.refresh(follow)
        assert follow.is_delete is True
        assert follow.remove_time is not None

    def test_delete_follow_stock_not_found(self, authenticated_client):
        """Should raise exception for non-existent follow stock.

        Note: The service uses .one() which raises NoResultFound when not found.
        In test mode, this exception propagates rather than returning HTTP error.
        """
        from sqlalchemy.exc import NoResultFound

        # Act & Assert - Service raises NoResultFound for non-existent record
        with pytest.raises(NoResultFound):
            authenticated_client.delete('/api/v0/follow_stock/nonexistent-id')

    def test_delete_follow_stock_unauthorized(self, client, sample_follow_stock_long):
        """Should return 401 when not authenticated."""
        # Act
        response = client.delete(f'/api/v0/follow_stock/{sample_follow_stock_long.id}')

        # Assert
        assert response.status_code == 401


@pytest.mark.usefixtures('test_app')
class TestFollowStockIDORSecurity:
    """IDOR (Insecure Direct Object Reference) security tests.

    These tests verify that users cannot access, modify, or delete
    other users' follow stock records.
    """

    def test_get_other_user_follow_stock_returns_404(
        self, authenticated_client, other_user_follow_stock
    ):
        """Should return 404 when trying to access another user's follow stock.

        Security: Returns 404 instead of 403 to avoid leaking information
        about the existence of other users' resources.
        """
        # Act
        response = authenticated_client.get(
            f'/api/v0/follow_stock/{other_user_follow_stock.stock_id}'
        )

        # Assert - should return 404, not 403 (to avoid info leakage)
        assert response.status_code == 404

    def test_update_other_user_follow_stock_returns_404(
        self, authenticated_client, other_user_follow_stock
    ):
        """Should return 404 when trying to update another user's follow stock."""
        # Arrange
        original_comment = other_user_follow_stock.comment
        payload = {
            'long_or_short': 'short',
            'comment': 'Hacked!'
        }

        # Act
        response = authenticated_client.patch(
            f'/api/v0/follow_stock/{other_user_follow_stock.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 404

        # Verify data was NOT modified
        db.session.refresh(other_user_follow_stock)
        assert other_user_follow_stock.comment == original_comment

    def test_delete_other_user_follow_stock_fails(
        self, authenticated_client, other_user_follow_stock
    ):
        """Should fail when trying to delete another user's follow stock.

        Note: The service uses .one() which raises NoResultFound when the record
        doesn't match the user_id filter (IDOR protection at service layer).
        """
        from sqlalchemy.exc import NoResultFound

        # Act & Assert - Service raises NoResultFound (user_id filter excludes other user's data)
        with pytest.raises(NoResultFound):
            authenticated_client.delete(
                f'/api/v0/follow_stock/{other_user_follow_stock.id}'
            )

        # Verify data was NOT deleted
        db.session.refresh(other_user_follow_stock)
        assert other_user_follow_stock.is_delete is False


@pytest.mark.usefixtures('test_app')
class TestFollowStockResponseStructure:
    """Tests for API response structure and serialization."""

    def test_list_response_contains_required_fields(
        self, authenticated_client, follow_stock_factory
    ):
        """Should return all required fields in list response."""
        # Arrange
        follow_stock_factory(long_or_short='long', comment='Structure test')

        # Act
        response = authenticated_client.get('/api/v0/follow_stock/')

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) > 0

        item = data[0]
        required_fields = ['id', 'long_or_short', 'comment', 'last_update_time']
        for field in required_fields:
            assert field in item, f"Missing required field: {field}"

    def test_response_includes_nested_stock_info(
        self, authenticated_client, follow_stock_factory
    ):
        """Should include nested stock information in response."""
        # Arrange
        follow_stock_factory()

        # Act
        response = authenticated_client.get('/api/v0/follow_stock/')

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) > 0

        item = data[0]
        assert 'stock' in item
        assert item['stock'] is not None

    def test_sensitive_fields_not_exposed(
        self, authenticated_client, follow_stock_factory, regular_user
    ):
        """Should not expose sensitive fields like user_id in response."""
        # Arrange
        follow_stock_factory()

        # Act
        response = authenticated_client.get('/api/v0/follow_stock/')

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)

        for item in data:
            # user_id should not be exposed in API response
            assert 'user_id' not in item


@pytest.mark.usefixtures('test_app')
class TestFollowStockEdgeCases:
    """Edge case and boundary condition tests."""

    def test_deleted_user_token_still_works(self, client, deleted_user_token, sample_basic_info):
        """JWT tokens remain valid even after user deletion.

        Note: JWTs are self-contained and stateless. The API validates the token
        signature but does not check if the user still exists in the database.
        This is expected behavior for JWT-based authentication.

        Security consideration: If immediate token invalidation is required after
        user deletion, consider implementing a token blacklist or using short-lived
        tokens with refresh token rotation.
        """
        # Act
        response = client.get(
            '/api/v0/follow_stock/',
            headers={'Authorization': f'Bearer {deleted_user_token}'}
        )

        # Assert - JWT is still valid, returns 200 with empty list
        assert response.status_code == 200

    @pytest.mark.parametrize('long_or_short', ['long', 'short'])
    def test_create_with_valid_positions(
        self, authenticated_client, sample_basic_info, clean_user_follow_stocks, long_or_short
    ):
        """Should accept both 'long' and 'short' position values."""
        # Arrange
        payload = {
            'stock_id': sample_basic_info.id,
            'long_or_short': long_or_short,
            'comment': f'Testing {long_or_short}'
        }

        # Act
        response = authenticated_client.post(
            '/api/v0/follow_stock/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['long_or_short'] == long_or_short

    def test_create_with_empty_comment(
        self, authenticated_client, sample_basic_info, clean_user_follow_stocks
    ):
        """Should allow creating follow stock with empty comment."""
        # Arrange
        payload = {
            'stock_id': sample_basic_info.id,
            'long_or_short': 'long',
            'comment': ''
        }

        # Act
        response = authenticated_client.post(
            '/api/v0/follow_stock/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 200

    def test_create_with_unicode_comment(
        self, authenticated_client, sample_basic_info, clean_user_follow_stocks
    ):
        """Should handle Unicode characters in comment."""
        # Arrange
        payload = {
            'stock_id': sample_basic_info.id,
            'long_or_short': 'long',
            'comment': '看好台積電 \U0001F680 長期成長潛力'
        }

        # Act
        response = authenticated_client.post(
            '/api/v0/follow_stock/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert '\U0001F680' in data['comment']

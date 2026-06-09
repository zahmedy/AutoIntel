import unittest
from datetime import datetime
from unittest.mock import patch

from sqlmodel import Session, SQLModel, create_engine, select

from app.api.v1.routes.admin import delete_admin_car, list_admin_cars
from app.models.activity import ActivityEvent
from app.models.car import CarListing, CarMedia, CarStatus, SavedCar
from app.models.chat import ChatMessage
from app.models.lead import Lead
from app.models.notification import Notification
from app.models.report import ReportType, UserReport
from app.models.user import User, UserRole
from app.models.vehicle_intelligence import PricePredictionRecord, VinDecodeRecord


class AdminListingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.engine)

    def _create_users_and_listing(self, session: Session) -> tuple[User, User, User, CarListing]:
        admin = User(role=UserRole.admin, name="Admin", email="admin@example.com", verified_at=datetime.utcnow())
        seller = User(role=UserRole.seller, name="Seller", email="seller@example.com", verified_at=datetime.utcnow())
        buyer = User(role=UserRole.buyer, name="Buyer", email="buyer@example.com", verified_at=datetime.utcnow())
        session.add_all([admin, seller, buyer])
        session.commit()
        session.refresh(admin)
        session.refresh(seller)
        session.refresh(buyer)

        listing = CarListing(
            owner_id=seller.id,
            status=CarStatus.active,
            city="Buffalo",
            make="Toyota",
            model="Camry",
            year=2020,
            price=25000,
            mileage=100000,
            title="Toyota Camry 2020 for sale",
            description="Clean commuter car.",
            published_at=datetime.utcnow(),
        )
        session.add(listing)
        session.commit()
        session.refresh(listing)
        return admin, seller, buyer, listing

    def test_admin_can_list_all_listings(self) -> None:
        with Session(self.engine) as session:
            admin, seller, _, listing = self._create_users_and_listing(session)
            session.add(CarMedia(car_id=listing.id, storage_key="cars/1.jpg", public_url="https://example.com/1.jpg"))
            session.commit()

            result = list_admin_cars(
                status=None,
                q="Camry",
                page=1,
                page_size=50,
                session=session,
                admin=admin,
            )

        self.assertEqual(result.total, 1)
        self.assertEqual(result.items[0].id, listing.id)
        self.assertEqual(result.items[0].owner_label, seller.name)
        self.assertEqual(result.items[0].photo_count, 1)

    def test_admin_delete_removes_listing_dependencies_and_storage_objects(self) -> None:
        with Session(self.engine) as session:
            admin, seller, buyer, listing = self._create_users_and_listing(session)
            car_id = listing.id

            media = [
                CarMedia(car_id=car_id, storage_key="cars/first.jpg", public_url="https://example.com/first.jpg"),
                CarMedia(car_id=car_id, storage_key="cars/second.jpg", public_url="https://example.com/second.jpg"),
            ]
            offer = Lead(car_id=car_id, owner_id=seller.id, buyer_user_id=buyer.id, amount=23000, channel="offer")
            session.add_all(media + [
                SavedCar(user_id=buyer.id, car_id=car_id),
                ChatMessage(car_id=car_id, sender_user_id=buyer.id, message="Still available?"),
                offer,
                Notification(user_id=seller.id, actor_user_id=buyer.id, car_id=car_id, type="offer", title="Offer", body="New offer"),
                ActivityEvent(event_type="listing_view", user_id=buyer.id, car_id=car_id),
                VinDecodeRecord(user_id=seller.id, car_id=car_id, detected_vin="1HGCM82633A004352"),
                PricePredictionRecord(user_id=seller.id, car_id=car_id, price_prediction=25000),
            ])
            session.commit()
            session.refresh(offer)
            session.add(
                UserReport(
                    report_type=ReportType.false_bid,
                    car_id=car_id,
                    offer_id=offer.id,
                    reporter_user_id=seller.id,
                    reported_user_id=buyer.id,
                    reason="fake_bid",
                )
            )
            session.commit()

            with patch("app.services.listing_deletion.delete_object") as delete_object:
                result = delete_admin_car(car_id, session=session, admin=admin)

            self.assertEqual(result["deleted_car_id"], car_id)
            self.assertEqual(result["deleted_storage_objects"], 2)
            self.assertEqual(
                {call.args[0] for call in delete_object.call_args_list},
                {"cars/first.jpg", "cars/second.jpg"},
            )
            self.assertIsNone(session.get(CarListing, car_id))

            for model in (
                UserReport,
                Notification,
                ActivityEvent,
                ChatMessage,
                SavedCar,
                VinDecodeRecord,
                PricePredictionRecord,
                CarMedia,
                Lead,
            ):
                self.assertEqual(session.exec(select(model).where(model.car_id == car_id)).all(), [])


if __name__ == "__main__":
    unittest.main()

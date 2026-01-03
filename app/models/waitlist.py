from app.extensions import db
from datetime import datetime, timedelta
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import or_, and_
from app.models.user import User
class Waitlist(db.Model):
    __tablename__ = "waitlist"

    # -------------------------
    # Core identity
    # -------------------------
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        index=True
    )

    # -------------------------
    # Points system
    # -------------------------
    referral_points = db.Column(db.Integer, nullable=False, default=0)
    contribution_points = db.Column(db.Integer, nullable=False, default=0)
    activity_points = db.Column(db.Integer, nullable=False, default=0)
    last_activity_at = db.Column(db.DateTime)
    POINTS_PER_REFERRAL = 5
    POINTS_PER_SMALL_CONTRIBUTION = 5
    POINTS_PER_CONTRIBUTION = 10
    POINTS_PER_LARGE_CONTRIBUTION = 20
    POINTS_PER_ACTIVITY = 1
    POINTS_PER_STARTUP = 30
    ACTIVITY_INTERVAL = timedelta(minutes=30)
    DISCOUNT_RANKS = {
        (1, 500): 25,
        (501, 1000): 20,
        (1001, 1500): 15,
        (1501, 2000): 10,
        (2001, 2500): 5,
    }

    BADGES = {
        1: "🔑 Keyholder",
        100: "🥇 Gold",
        300: "🥈 Silver",
        1000: "🥉 Bronze (MVP)",
    }

    # -------------------------
    # Discount calculation
    # -------------------------
    def get_discount(self):
        rank = self.get_position()
        for (lower, upper), discount in self.DISCOUNT_RANKS.items():
            if lower <= rank <= upper:
                return discount
        return 0

    # -------------------------
    # Badge assignment
    # -------------------------
    @property
    def badge(self):
        rank = self.get_position()
        for threshold, badge in self.BADGES.items():
            if rank <= threshold:
                return badge
        return None
    # -------------------------
    # Constants (business rules)
    # -------------------------
    MAX_MVP = 1000
    MAX_V1 = 2500

    JAN_10_DEADLINE = datetime(2026, 1, 10, 23, 59, 59)
    FEB_7_DEADLINE = datetime(2026, 2, 7, 23, 59, 59)

    def register_activity(self):
        now = datetime.utcnow()

        # First activity ever
        if not self.last_activity_at:
            self.last_activity_at = now
            return False  # no points yet

        # Check interval
        if now - self.last_activity_at >= Waitlist.ACTIVITY_INTERVAL:
            self.activity_points += Waitlist.POINTS_PER_ACTIVITY
            self.last_activity_at = now
            return True

        return False
    # -------------------------
    # Computed totals
    # -------------------------
    @hybrid_property
    def total_points_value(self) -> int:
        return (
            (self.referral_points or 0) * 2
            + (self.contribution_points or 0)
            + (self.activity_points or 0)
        )

    @total_points_value.expression
    def total_points_value(cls):
        return (
            (cls.referral_points * 2)
            + cls.contribution_points
            + cls.activity_points
        )

    
    @property
    def total_points(self):
        return {
            "referral": self.referral_points,
            "contribution": self.contribution_points,
            "activity": self.activity_points,
            "total": self.total_points_value,
        }

    # -------------------------
    # Waitlist logic
    # -------------------------
    def get_position(self) -> int:
        """
        Ranking position based on total points
        Higher points = better rank
        """
        return (
            Waitlist.query
            .filter(
                or_(
                    Waitlist.total_points_value > self.total_points_value,
                    and_(
                        Waitlist.total_points_value == self.total_points_value,
                        Waitlist.created_at < self.created_at
                    ),
                    and_(
                        Waitlist.total_points_value == self.total_points_value,
                        Waitlist.created_at == self.created_at,
                        Waitlist.id < self.id
                    ),
                )
            )
            .count()
            + 1
        )

    @staticmethod
    def get_max_allowed() -> int:
        now = datetime.utcnow()

        if now <= Waitlist.JAN_10_DEADLINE:
            return Waitlist.MAX_MVP
        elif now <= Waitlist.FEB_7_DEADLINE:
            return Waitlist.MAX_V1
        return 10**9  # effectively unlimited

    # -------------------------
    # Registration
    # -------------------------
    @classmethod
    def register(cls, email: str, name: str | None = None, id: int | None = None, phone: str | None = None) -> tuple[bool, str, dict | None]:
        email = email.strip().lower()

        existing = cls.query.filter_by(email=email).first()
        if existing:
            return False, "Email already registered", {
                "position": existing.get_position()
            }

        if cls.query.count() >= cls.get_max_allowed():
            return False, "Waitlist is full", None

        user = cls(
            email=email,
            name=name,
            id=id,
            referral_points=0,
            contribution_points=0,
            activity_points=0,
            created_at=datetime.utcnow(),  
        )
        db.session.add(user)
        db.session.flush()  # assigns ID without committing

        position = user.get_position()
        user.activity_points += max(0, int((Waitlist.MAX_V1 - position) / 50)) # max 2500 / 50 = 50 points

        db.session.commit()
        return True, "Successfully joined waitlist", {
            "position": position
        }

    # -------------------------
    # Points mutation
    # -------------------------
    def add_points(self, points: int, category: str):
        if category == "referral":
            self.referral_points += points
        elif category in ["contribution", "small_contribution", "medium_contribution", "large_contribution"]:
            self.contribution_points += points
        elif category == "activity":
            self.activity_points += points
        elif category == "new_startup":
            self.activity_points += points
        
        else:
            raise ValueError("Invalid point category")

        db.session.commit()
    @staticmethod
    def give_points(user_id: int, points: int, category: str):
        user = Waitlist.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        user.add_points(points, category)
    # -------------------------
    # Ranking & leaderboard
    # -------------------------
    @classmethod
    def get_rank(cls, user_id: int):
        user = cls.query.get(user_id)
        if not user:
            return None

        return (
            cls.query
            .filter(cls.total_points_value > user.total_points_value)
            .count()
            + 1
        )

    @classmethod
    def leaderboard(cls, limit=10):
        return (
            cls.query
            .order_by(cls.total_points_value.desc(), cls.created_at.asc())
            .limit(limit)
            .all()
        )

    # -------------------------
    # Helpers
    # -------------------------
    @classmethod
    def is_on_waitlist(cls, email: str):
        user = cls.query.filter_by(email=email.strip().lower()).first()
        return {
            "on_waitlist": bool(user),
            "position": user.get_position() if user else None
        }

    # -------------------------
    # Serialization
    # -------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "position": self.get_position(),
            "points": self.total_points,
        }

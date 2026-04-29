import sqlite3
from app.api.schemas.shipment import ShipmentCreate, ShipmentUpdate
from contextlib import contextmanager

# id = 12701
# status = "placed"


# cursor.execute(
#     """
#     UPDATE shipment
#     SET status = :status
#     WHERE id > :id
# """,
#     {"status": status, "id": id},
# )


####################################


class Database:
    def connect_to_db(self):
        self.connection = sqlite3.connect("sqlite.db", check_same_thread=False)
        self.cursor = self.connection.cursor()
        print("connected to the database")

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS shipment (
                id INTEGER PRIMARY KEY,
                content TEXT,
                weight REAL,
                status TEXT
            )
        """
        )

    def get(self, id: int):
        self.cursor.execute(
            """
            SELECT * FROM shipment
            WHERE id = ?
        """,
            (id,),
        )
        row = self.cursor.fetchone()
        return (
            {"id": row[0], "content": row[1], "weight": row[2], "status": row[3]}
            if row
            else None
        )

    def create(self, shipment: ShipmentCreate):
        self.cursor.execute("SELECT MAX(id) FROM shipment")
        result = self.cursor.fetchone()
        new_id = result[0] + 1

        self.cursor.execute(
            """
            INSERT INTO shipment
            VALUES (:id, :content, :weight, :status)
            """,
            {"id": new_id, **shipment.model_dump(), "status": "placed"},
        )
        self.connection.commit()

        return new_id

    def update(self, id: int, shipment: ShipmentUpdate):
        self.cursor.execute(
            """
            UPDATE shipment
            SET status=:status
            WHERE id=:id
        """,
            {**shipment.model_dump(), "id": id},
        )
        self.connection.commit()

        return self.get(id)

    def delete(self, id: int):
        self.cursor.execute(
            """
            DELETE FROM shipment
            WEHRE id = ?      
        """,
            (id,),
        )
        self.connection.commit()

    def close(self):
        print("connection closed")
        self.connection.close()

    # def __enter__(self):
    #     print("enter the context")
    #     self.connect_to_db()
    #     self.create_table()
    #     return self

    # def __exit__(self, *arg):
    #     print("exit the context")
    #     self.close()


# with Database() as db:
#     print("-result:", db.get(12701))
#     print("-result:", db.get(12702))


##############################


@contextmanager
def managed_db():
    db = Database()

    print("enter the context")
    db.connect_to_db()
    db.create_table()

    yield db

    print("exit the context")
    db.close()


with managed_db() as db:
    print("-result:", db.get(12701))
    print("-result:", db.get(12702))

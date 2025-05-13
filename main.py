import os
from peewee import SqliteDatabase, Model, CharField, FloatField, IntegerField, ForeignKeyField
from programm.reporting_gen import F1ReportGenerator, F1Processor
import datetime

db_file = 'f1_reports.db'

if os.path.exists(db_file):
    try:
        os.remove(db_file)
    except PermissionError:
        print(f"not permitted{db_file}.")
        exit(1)


db = SqliteDatabase(db_file)


class BaseModel(Model):
    class Meta:
        database = db


class Driver(BaseModel):
    driver_id = CharField(unique=True)
    driver_name = CharField()
    team = CharField()
    driver_lap_time = FloatField(null=True)


class Report(BaseModel):
    driver = ForeignKeyField(Driver, backref='reports')
    rank = IntegerField()
    status = CharField()


db.connect()
db.create_tables([Driver, Report])


folder_path = "data"
processor = F1Processor(folder_path)
report_generator = F1ReportGenerator(processor)


order = 'asc'
report_data = report_generator.build_report(order=order)


for data in report_data:
    driver_id = f"{data['name']}_{data['team']}"

    driver, created = Driver.get_or_create(
        driver_id=driver_id,
        defaults={"driver_name": data["name"], "team": data["team"], "driver_lap_time": data["time"].total_seconds() if isinstance(data["time"], datetime.timedelta) else None},
    )

    Report.create(
        driver=driver,
        rank=data["rank"],
        status=data["status"]
    )

print("drivers:")
for driver in Driver.select():
    print(f"ID: {driver.driver_id}, Name: {driver.driver_name}, Team: {driver.team}, Lap Time: {driver.driver_lap_time}")

print("\nreports:")
for report in Report.select():
    print(f"Driver: {report.driver.driver_name}, Rank: {report.rank}, Status: {report.status}")
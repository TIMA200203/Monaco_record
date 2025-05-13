import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import re


@dataclass
class DriverLapInfo:

    driver_init: str
    start_time: datetime
    end_time: datetime = field(init=False)
    driver_name: str = ""
    team: str = ""
    errors: List[str] = field(default_factory=list)

    @property
    def driver_lap_time(self) -> Optional[timedelta]:

        if not self.end_time:
            self.errors.append(f"для гонщика {self.driver_name} відсутній час")
            return None
        if self.end_time < self.start_time:
            self.errors.append(f"для гонщика {self.driver_name} час фінішу менший за час старту")
            return None
        
        return self.end_time - self.start_time


class F1Processor:

    def __init__(self, folder_path: str) -> None:

        self.start_log_path = os.path.join(folder_path, 'start.log')
        self.end_log_path = os.path.join(folder_path, 'end.log')
        self.txt_path = os.path.join(folder_path, 'abbreviations.txt')
        self.drivers = {}

    def read_log_file(self, file_path: str) -> Dict[str, datetime]:

        data = {}
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    match = re.match(
                        r"([A-Z]{3})(\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}\.\d{3})",
                        line.strip())
                    if match:
                        driver_init, timestamp_str = match.groups()
                        timestamp = datetime.strptime(
                            timestamp_str, '%Y-%m-%d_%H:%M:%S.%f')
                        data[driver_init] = timestamp
        except IOError as e:
            print(f"Error reading file {file_path}: {e}")
        return data

    def integrate_driver_info(self) -> None:

        try:
            with open(self.txt_path, 'r') as file:
                for line in file:
                    driver_init, driver_name, team = line.strip().split('_')
                    if driver_init in self.drivers:
                        self.drivers[driver_init].driver_name = driver_name
                        self.drivers[driver_init].team = team
        except IOError as e:
            print(f"Error reading file {self.txt_path}: {e}")

    def process_files(self) -> None:
        start_times = self.read_log_file(self.start_log_path)
        end_times = self.read_log_file(self.end_log_path)

        for driver_init, start_time in start_times.items():
            driver_info = DriverLapInfo(driver_init, start_time)
            if driver_init in end_times:
                driver_info.end_time = end_times[driver_init]
            self.drivers[driver_init] = driver_info

        self.integrate_driver_info()


class F1ReportGenerator:
    
    def __init__(self, processor: 'F1Processor') -> None:

        self.processor = processor
        self.processor.process_files()

    def rank_drivers(self, order: str = 'asc') -> List['DriverLapInfo']:

        drivers = [driver for driver in self.processor.drivers.values()]
        drivers.sort(
            key=lambda x: (
                x.driver_lap_time is None,  # Водії без часу кола йдуть в кінець
                x.driver_lap_time
            ),
            reverse=(order == 'desc')
        )
        return drivers

    def build_report(self, order: str = 'asc') -> List[Dict[str, str]]:
        ranked_drivers = self.rank_drivers(order)
        report_lines = []
        
        for i, driver in enumerate(ranked_drivers, start=1):

            
            qualification_status = ""
            if order == 'desc' and len(ranked_drivers) - i == 14:
                qualification_status = "ВИПАДАЄ З КВАЛІФІКАЦІЇ"
            elif order == 'asc' and i == 16:
                qualification_status = "ВИПАДАЄ З КВАЛІФІКАЦІЇ"

            time_str = driver.driver_lap_time or "час не можна визначити"
            
            report_lines.append({
                "rank": i,
                "name": driver.driver_name,
                "team": driver.team,
                "time": time_str,
                "status": qualification_status,
            })
        return report_lines

    def print_report(self, order: str = 'asc') -> None:

        report_lines = self.build_report(order)
        for line in report_lines:
            print(line)

    def driver_info(self, driver_name: str) -> str:

        for driver in self.processor.drivers.values():
            if driver.driver_name == driver_name:
                time_str = driver.driver_lap_time
                return f"{driver.driver_name:<20} | {driver.team:<30} | {time_str}"
        return f"Гонщика {driver_name} не знайдено."


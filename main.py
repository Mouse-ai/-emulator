"""
Эмулятор магистральных насосных агрегатов (МНА)
На основе реальных мнемосхем НПС
"""
import random
import json
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class AggregateStatus(Enum):
    READY = "ГОТОВ"
    RUNNING_MAIN = "ОСН"
    RUNNING_BOOST = "П"
    STOPPED = "ОСТ"
    MAINTENANCE = "Р"


class ValveState(Enum):
    OPEN = "открыта"
    CLOSED = "закрыта"
    MOVING = "движение"


@dataclass
class PumpAggregate:
    id: str
    pressure_inlet: float = 0.0
    pressure_outlet: float = 0.0
    pressure_lube: float = 0.0
    temp_bearing_front: float = 20.0
    temp_bearing_rear: float = 20.0
    temp_oil: float = 25.0
    temp_winding: float = 20.0
    vibration_horizontal: float = 0.0
    vibration_vertical: float = 0.0
    vibration_axial: float = 0.0
    flow_rate: float = 0.0
    rotation_speed: float = 0.0
    status: AggregateStatus = AggregateStatus.STOPPED
    valve_suction: ValveState = ValveState.CLOSED
    valve_discharge: ValveState = ValveState.CLOSED
    current: float = 0.0
    voltage: float = 6000.0
    power: float = 0.0
    efficiency: float = 0.0
    operating_hours: float = 0.0
    starts_count: int = 0
    timestamp: str = ""
    health_score: float = 100.0
    bearing_wear_level: float = 0.0
    start_time: datetime = None

    def update_timestamp(self):
        self.timestamp = datetime.now().isoformat()


class MainPumpStationEmulator:
    def __init__(self):
        self.aggregates: Dict[str, PumpAggregate] = {
            "МНА-21": PumpAggregate(id="МНА-21"),
            "МНА-22": PumpAggregate(id="МНА-22"),
            "МНА-23": PumpAggregate(id="МНА-23"),
            "МНА-24": PumpAggregate(id="МНА-24"),
        }

        self.normal_params = {
            "pressure_inlet": (0.25, 0.35),
            "pressure_outlet": (0.65, 0.75),
            "temp_bearing": (45.0, 55.0),
            "temp_oil": (48.0, 52.0),
            "vibration": (0.8, 1.2),
            "flow_rate": (0.28, 0.32),
            "current": (45.0, 55.0),
            "lube_pressure": (0.08, 0.12),
            "rotation_speed": (2900, 3000),
        }

        self.limits = {
            "max_temp_bearing": 80.0,
            "max_temp_oil": 75.0,
            "max_vibration": 4.5,
            "min_lube_pressure": 0.05,
            "max_pressure_outlet": 1.0,
        }

        self.station_mode = "AUTO"
        self.parameter_history: List[Dict] = []

    def start_aggregate(self, aggregate_id: str) -> bool:
        if aggregate_id not in self.aggregates:
            return False

        agg = self.aggregates[aggregate_id]

        if agg.status != AggregateStatus.STOPPED:
            print(f"{Colors.RED}[{aggregate_id}] Нельзя запустить - статус {agg.status.value}{Colors.RESET}")
            return False

        print(f"\n{Colors.GREEN}[{aggregate_id}] Запуск агрегата...{Colors.RESET}")
        time.sleep(0.5)

        agg.valve_suction = ValveState.MOVING
        print(f"  - Открытие всасывающей задвижки...")
        time.sleep(0.5)

        agg.pressure_lube = random.uniform(*self.normal_params["lube_pressure"])
        print(f"  - Давление масла: {agg.pressure_lube:.3f} МПа")
        time.sleep(0.5)

        agg.status = AggregateStatus.RUNNING_MAIN
        agg.starts_count += 1
        agg.start_time = datetime.now()
        print(f"  - Пуск двигателя...")
        time.sleep(1.0)

        self._set_operating_parameters(agg)
        print(f"  - Выход на рабочий режим...")
        time.sleep(0.5)

        agg.valve_discharge = ValveState.OPEN
        print(f"  {Colors.GREEN}[OK] Агрегат вышел на режим{Colors.RESET}")
        time.sleep(0.5)

        agg.update_timestamp()
        return True

    def stop_aggregate(self, aggregate_id: str) -> bool:
        if aggregate_id not in self.aggregates:
            return False

        agg = self.aggregates[aggregate_id]

        if agg.status not in [AggregateStatus.RUNNING_MAIN, AggregateStatus.RUNNING_BOOST]:
            print(f"{Colors.RED}[{aggregate_id}] Нельзя остановить - статус {agg.status.value}{Colors.RESET}")
            return False

        print(f"\n{Colors.YELLOW}[{aggregate_id}] Остановка агрегата...{Colors.RESET}")
        time.sleep(0.5)

        agg.valve_discharge = ValveState.CLOSED
        print(f"  - Закрытие нагнетательной задвижки...")
        time.sleep(0.5)

        agg.status = AggregateStatus.STOPPED
        print(f"  - Остановка двигателя...")
        time.sleep(1.0)

        agg.valve_suction = ValveState.CLOSED
        print(f"  - Всасывающая задвижка закрыта")
        time.sleep(0.5)

        self._set_stopped_parameters(agg)
        print(f"  {Colors.YELLOW}[OK] Агрегат остановлен{Colors.RESET}")
        time.sleep(0.5)

        agg.update_timestamp()
        return True

    def _set_operating_parameters(self, agg: PumpAggregate):
        agg.pressure_inlet = random.uniform(*self.normal_params["pressure_inlet"])
        agg.pressure_outlet = random.uniform(*self.normal_params["pressure_outlet"])
        agg.temp_bearing_front = random.uniform(*self.normal_params["temp_bearing"])
        agg.temp_bearing_rear = random.uniform(*self.normal_params["temp_bearing"])
        agg.temp_oil = random.uniform(*self.normal_params["temp_oil"])
        agg.temp_winding = random.uniform(50.0, 60.0)
        agg.vibration_horizontal = random.uniform(*self.normal_params["vibration"])
        agg.vibration_vertical = random.uniform(*self.normal_params["vibration"])
        agg.vibration_axial = random.uniform(*self.normal_params["vibration"])
        agg.flow_rate = random.uniform(*self.normal_params["flow_rate"])
        agg.current = random.uniform(*self.normal_params["current"])
        agg.rotation_speed = random.uniform(*self.normal_params["rotation_speed"])

        hydraulic_power = agg.flow_rate * (agg.pressure_outlet - agg.pressure_inlet) * 1000
        electrical_power = agg.current * agg.voltage / 1000
        agg.power = electrical_power
        agg.efficiency = (hydraulic_power / electrical_power * 100) if electrical_power > 0 else 0

    def _set_stopped_parameters(self, agg: PumpAggregate):
        agg.pressure_inlet = 0.0
        agg.pressure_outlet = 0.0
        agg.flow_rate = 0.0
        agg.current = 0.0
        agg.power = 0.0
        agg.rotation_speed = 0.0
        agg.vibration_horizontal = 0.0
        agg.vibration_vertical = 0.0
        agg.vibration_axial = 0.0

    def simulate_anomaly(self, aggregate_id: str, anomaly_type: str):
        if aggregate_id not in self.aggregates:
            return

        agg = self.aggregates[aggregate_id]

        if anomaly_type == "overheating":
            print(f"\n{Colors.RED}[{aggregate_id}] АНОМАЛИЯ: Перегрев подшипника!{Colors.RESET}")
            time.sleep(0.5)
            agg.temp_bearing_front = random.uniform(75.0, 95.0)
            agg.health_score -= 20
        elif anomaly_type == "vibration":
            print(f"\n{Colors.RED}[{aggregate_id}] АНОМАЛИЯ: Повышенная вибрация!{Colors.RESET}")
            time.sleep(0.5)
            agg.vibration_horizontal = random.uniform(4.0, 7.0)
            agg.health_score -= 15
        elif anomaly_type == "lube_pressure":
            print(f"\n{Colors.RED}[{aggregate_id}] АНОМАЛИЯ: Низкое давление масла!{Colors.RESET}")
            time.sleep(0.5)
            agg.pressure_lube = random.uniform(0.02, 0.04)
            agg.health_score -= 25
        elif anomaly_type == "bearing_wear":
            print(f"\n{Colors.YELLOW}[{aggregate_id}] АНОМАЛИЯ: Износ подшипников{Colors.RESET}")
            time.sleep(0.5)
            agg.temp_bearing_front += 15
            agg.vibration_vertical += 2.0
            agg.bearing_wear_level = random.uniform(30, 70)
            agg.health_score -= 30

    def check_protections(self, aggregate_id: str) -> List[str]:
        alerts = []
        agg = self.aggregates[aggregate_id]

        if agg.temp_bearing_front > self.limits["max_temp_bearing"]:
            alerts.append(
                f"{Colors.RED}[АВАРИЯ] Температура {agg.temp_bearing_front:.1f}°C > {self.limits['max_temp_bearing']}°C{Colors.RESET}")
        elif agg.temp_bearing_front > 70:
            alerts.append(
                f"{Colors.YELLOW}[ПРЕДУПРЕЖДЕНИЕ] Температура {agg.temp_bearing_front:.1f}°C{Colors.RESET}")

        if agg.vibration_horizontal > self.limits["max_vibration"]:
            alerts.append(
                f"{Colors.RED}[АВАРИЯ] Вибрация {agg.vibration_horizontal:.2f} мм/с{Colors.RESET}")

        if agg.pressure_lube < self.limits["min_lube_pressure"] and agg.status == AggregateStatus.RUNNING_MAIN:
            alerts.append(
                f"{Colors.RED}[АВАРИЯ] Давление масла {agg.pressure_lube:.3f} МПа{Colors.RESET}")

        return alerts

    def calculate_energy_efficiency(self, aggregate_id: str) -> Dict:
        agg = self.aggregates[aggregate_id]

        hydraulic_power = agg.flow_rate * (agg.pressure_outlet - agg.pressure_inlet) * 1000
        electrical_power = agg.current * agg.voltage / 1000
        efficiency = (hydraulic_power / electrical_power * 100) if electrical_power > 0 else 0

        elapsed_hours = 0.0
        if agg.start_time and agg.status in [AggregateStatus.RUNNING_MAIN, AggregateStatus.RUNNING_BOOST]:
            elapsed_hours = (datetime.now() - agg.start_time).total_seconds() / 3600

        return {
            "electrical_power_kw": round(electrical_power, 2),
            "hydraulic_power_kw": round(hydraulic_power, 2),
            "efficiency_percent": round(efficiency, 2),
            "energy_consumed_kwh": round(electrical_power * elapsed_hours, 2),
        }

    def predict_failure(self, aggregate_id: str) -> Dict:
        agg = self.aggregates[aggregate_id]

        temp_risk = max(0, (agg.temp_bearing_front - 60) / 40) * 100
        vibration_risk = max(0, (agg.vibration_horizontal - 3) / 3) * 100
        wear_risk = agg.bearing_wear_level

        overall_risk = (temp_risk + vibration_risk + wear_risk) / 3
        agg.health_score = max(0, 100 - overall_risk)

        prediction = {
            "health_score": round(agg.health_score, 1),
            "risk_level": "LOW",
            "estimated_hours_to_failure": None,
            "failure_probability_percent": round(overall_risk, 1),
            "recommendations": []
        }

        if overall_risk > 70:
            prediction["risk_level"] = "CRITICAL"
            prediction["estimated_hours_to_failure"] = random.randint(1, 24)
            prediction["recommendations"].append("Требуется немедленная остановка")
        elif overall_risk > 40:
            prediction["risk_level"] = "MEDIUM"
            prediction["estimated_hours_to_failure"] = random.randint(24, 168)
            prediction["recommendations"].append("Рекомендуется плановое ТО")
        elif overall_risk > 20:
            prediction["risk_level"] = "LOW"
            prediction["recommendations"].append("Продолжить мониторинг")
        else:
            prediction["recommendations"].append("Агрегат в норме")

        return prediction

    def log_parameters(self, aggregate_id: str):
        agg = self.aggregates[aggregate_id]
        record = {
            "timestamp": datetime.now().isoformat(),
            "aggregate_id": aggregate_id,
            "pressure_outlet": agg.pressure_outlet,
            "temperature": agg.temp_bearing_front,
            "vibration": agg.vibration_horizontal,
            "flow_rate": agg.flow_rate,
            "rotation_speed": agg.rotation_speed,
            "power": agg.power,
            "health_score": agg.health_score
        }
        self.parameter_history.append(record)
        return record

    def print_realtime_graph(self, aggregate_id: str, cycles: int = 10):
        print(f"\n{Colors.BLUE}График параметров в реальном времени ({cycles} циклов):{Colors.RESET}")
        print("-" * 70)

        for i in range(cycles):
            # Обновляем параметры с небольшими случайными изменениями
            agg = self.aggregates[aggregate_id]
            if agg.status in [AggregateStatus.RUNNING_MAIN, AggregateStatus.RUNNING_BOOST]:
                # Добавляем небольшие флуктуации
                agg.temp_bearing_front += random.uniform(-0.5, 0.5)
                agg.vibration_horizontal += random.uniform(-0.1, 0.1)
                agg.power += random.uniform(-5, 5)
                agg.flow_rate += random.uniform(-0.01, 0.01)
                agg.pressure_outlet += random.uniform(-0.01, 0.01)

            self.log_parameters(aggregate_id)

            temp_bar = "█" * int(agg.temp_bearing_front / 2)
            vib_bar = "█" * int(agg.vibration_horizontal * 2)
            power_bar = "█" * int(agg.power / 5)

            print(f"\r  [{i + 1:2d}] T: {temp_bar:<40} {agg.temp_bearing_front:5.1f}°C | "
                  f"V: {vib_bar:<20} {agg.vibration_horizontal:4.2f} | "
                  f"P: {power_bar:<30} {agg.power:6.1f} кВт", end="", flush=True)

            time.sleep(0.3)

        print()
    def get_mimic_diagram_data(self, aggregate_id: str) -> Dict:
        if aggregate_id not in self.aggregates:
            return {}

        agg = self.aggregates[aggregate_id]

        return {
            "aggregate_id": agg.id,
            "status": agg.status.value,
            "parameters": {
                "Давление": {
                    "Рвх": {"value": agg.pressure_inlet, "unit": "МПа"},
                    "Рвых": {"value": agg.pressure_outlet, "unit": "МПа"},
                    "Р мас": {"value": agg.pressure_lube, "unit": "МПа"},
                },
                "Температура": {
                    "Т п/ш": {"value": agg.temp_bearing_front, "unit": "°C"},
                    "Т з/ш": {"value": agg.temp_bearing_rear, "unit": "°C"},
                    "Т масла": {"value": agg.temp_oil, "unit": "°C"},
                    "Т обм": {"value": agg.temp_winding, "unit": "°C"},
                },
                "Вибрация": {
                    "V гор": {"value": agg.vibration_horizontal, "unit": "мм/с"},
                    "V верт": {"value": agg.vibration_vertical, "unit": "мм/с"},
                    "V осев": {"value": agg.vibration_axial, "unit": "мм/с"},
                },
                "Расход": {
                    "Q": {"value": agg.flow_rate, "unit": "м³/с"},
                },
                "Обороты": {
                    "N": {"value": agg.rotation_speed, "unit": "об/мин"},
                },
                "Электрика": {
                    "I": {"value": agg.current, "unit": "А"},
                    "P": {"value": agg.power, "unit": "кВт"},
                }
            },
            "valves": {
                "ВС": agg.valve_suction.value,
                "НЗ": agg.valve_discharge.value,
            },
            "counters": {
                "Часы работы": f"{agg.operating_hours:.1f} ч",
                "Пуски": agg.starts_count,
            },
            "health": {
                "Health Score": f"{agg.health_score:.1f}%",
                "Износ подшипников": f"{agg.bearing_wear_level:.1f}%",
            },
            "timestamp": agg.timestamp,
        }

    def generate_station_report(self) -> Dict:
        report = {
            "station_name": "МНС (Магистральная Насосная Станция)",
            "timestamp": datetime.now().isoformat(),
            "mode": self.station_mode,
            "aggregates": {},
            "summary": {
                "total_running": 0,
                "total_stopped": 0,
                "total_alerts": 0,
                "total_flow": 0.0,
                "total_power": 0.0,
            }
        }

        for agg_id, agg in self.aggregates.items():
            data = self.get_mimic_diagram_data(agg_id)
            alerts = self.check_protections(agg_id)
            energy = self.calculate_energy_efficiency(agg_id)
            failure_pred = self.predict_failure(agg_id)

            report["aggregates"][agg_id] = {
                "data": data,
                "alerts": alerts,
                "energy_efficiency": energy,
                "failure_prediction": failure_pred,
            }

            if agg.status in [AggregateStatus.RUNNING_MAIN, AggregateStatus.RUNNING_BOOST]:
                report["summary"]["total_running"] += 1
                report["summary"]["total_flow"] += agg.flow_rate
                report["summary"]["total_power"] += agg.power
                agg.operating_hours += 0.001
            else:
                report["summary"]["total_stopped"] += 1

            report["summary"]["total_alerts"] += len(alerts)

        return report

    def save_report_to_file(self, report: Dict, filename: str = "pump_station_report.json"):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n{Colors.GREEN}[OK] Отчёт сохранён в {filename}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[ERROR] Ошибка сохранения отчёта: {e}{Colors.RESET}")


def demo():
    print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}ЭМУЛЯТОР МАГИСТРАЛЬНЫХ НАСОСНЫХ АГРЕГАТОВ{Colors.RESET}")
    print(f"{Colors.BLUE}На основе мнемосхем МНА-21, МНА-22, МНА-23, МНА-24{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    time.sleep(1)

    station = MainPumpStationEmulator()

    print(f"\n{Colors.BOLD}1. Запуск МНА-21{Colors.RESET}")
    print("-" * 40)
    station.start_aggregate("МНА-21")

    data = station.get_mimic_diagram_data("МНА-21")
    print(f"\n{Colors.BLUE}Данные для мнемосхемы {data['aggregate_id']}:{Colors.RESET}")
    print(f"  Статус: {data['status']}")
    print(f"  Давление: Рвх={data['parameters']['Давление']['Рвх']['value']:.3f} МПа, "
          f"Рвых={data['parameters']['Давление']['Рвых']['value']:.3f} МПа")
    print(f"  Температура: {data['parameters']['Температура']['Т п/ш']['value']:.1f}°C")
    print(f"  Вибрация: {data['parameters']['Вибрация']['V гор']['value']:.2f} мм/с")
    print(f"  Обороты: {data['parameters']['Обороты']['N']['value']:.0f} об/мин")
    print(f"  Расход: {data['parameters']['Расход']['Q']['value']:.3f} м³/с")
    time.sleep(1)

    print(f"\n\n{Colors.BOLD}2. Запуск МНА-22{Colors.RESET}")
    print("-" * 40)
    station.start_aggregate("МНА-22")
    time.sleep(1)

    print(f"\n\n{Colors.BOLD}2.5. Мониторинг параметров в реальном времени{Colors.RESET}")
    print("-" * 40)
    station.print_realtime_graph("МНА-21", cycles=15)
    time.sleep(1)

    print(f"\n\n{Colors.BOLD}3. Имитация аномалии на МНА-21{Colors.RESET}")
    print("-" * 40)
    station.simulate_anomaly("МНА-21", "overheating")

    alerts = station.check_protections("МНА-21")
    print(f"\n{Colors.YELLOW}Проверка защит:{Colors.RESET}")
    for alert in alerts:
        print(f"  {alert}")
        time.sleep(0.5)

    print(f"\n\n{Colors.BOLD}3.5. Прогнозирование отказов{Colors.RESET}")
    print("-" * 40)
    prediction = station.predict_failure("МНА-21")
    print(f"  Health Score: {prediction['health_score']}%")
    print(f"  Уровень риска: {prediction['risk_level']}")
    print(f"  Вероятность отказа: {prediction['failure_probability_percent']}%")
    print(f"  Рекомендации: {prediction['recommendations']}")
    time.sleep(1)

    print(f"\n\n{Colors.BOLD}3.6. Энергопотребление и КПД{Colors.RESET}")
    print("-" * 40)
    energy = station.calculate_energy_efficiency("МНА-21")
    print(f"  Электрическая мощность: {energy['electrical_power_kw']} кВт")
    print(f"  Гидравлическая мощность: {energy['hydraulic_power_kw']} кВт")
    print(f"  КПД: {energy['efficiency_percent']}%")
    print(f"  Потреблено энергии: {energy['energy_consumed_kwh']} кВт·ч")
    time.sleep(1)

    print(f"\n\n{Colors.BOLD}4. Генерация отчёта по станции{Colors.RESET}")
    print("-" * 40)
    time.sleep(0.5)
    report = station.generate_station_report()

    print(f"\n{Colors.BLUE}Краткая сводка:{Colors.RESET}")
    print(f"  Работает агрегатов: {report['summary']['total_running']}")
    print(f"  Остановлено: {report['summary']['total_stopped']}")
    print(f"  Всего предупреждений: {report['summary']['total_alerts']}")
    print(f"  Общий расход: {report['summary']['total_flow']:.3f} м³/с")
    print(f"  Общая мощность: {report['summary']['total_power']:.1f} кВт")

    station.save_report_to_file(report)
    time.sleep(1)

    print(f"\n\n{Colors.BOLD}5. Остановка МНА-21{Colors.RESET}")
    print("-" * 40)
    station.stop_aggregate("МНА-21")

    print(f"\n{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.GREEN}[OK] Демонстрация завершена!{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}")

    return report


if __name__ == "__main__":
    demo()
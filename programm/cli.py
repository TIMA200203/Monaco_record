import argparse
import reporting_gen as rpg


def parse_arguments() -> argparse.Namespace:

    parser = argparse.ArgumentParser(description="Генерація звітів Формули 1")
    
    parser.add_argument(
        "--files",
        type=str,
        required=True,
        help="Шлях до папки, що містить файли start.log, end.log і abbreviation.txt"
    )
    parser.add_argument(
        "--order",
        choices=["asc", "desc"],
        default="asc",
        help="Порядок часу кола (зростання або спадання)"
    )
    parser.add_argument(
        "--driver",
        type=str,
        help="Отримайте інформацію про час кола для конкретного водія"
    )

    return parser.parse_args()


def generate_report(files_path: str, order: str, driver: str = None) -> None:

    processor = rpg.F1Processor(files_path)
    report_generator = rpg.F1ReportGenerator(processor)

    if driver:
        print(report_generator.driver_info(driver))
    else:
        report_generator.print_report(order)


def main() -> None:

    args = parse_arguments()
    generate_report(args.files, args.order, args.driver)


if __name__ == "__main__":
    main()
